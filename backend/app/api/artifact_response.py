"""ASGI streaming response that owns one entered package artifact context."""

from collections.abc import Iterator, Mapping
from contextlib import AbstractContextManager
from threading import Lock

import anyio
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

from app.core.logging import get_logger

logger = get_logger(__name__)


class EnteredArtifactBody(Iterator[bytes]):
    """Pair one already-entered package context with its verified iterator.

    The package verifies authorization, manifest topology, size, hash, and the
    open file descriptor during ``__enter__``. FastAPI must enter that context
    before sending headers so any verification failure can still become a
    normal Problem Detail. Once entered, this object is the single cleanup
    owner transferred to :class:`ArtifactStreamingResponse`.
    """

    def __init__(
        self,
        *,
        context: AbstractContextManager[Iterator[bytes]],
        iterator: Iterator[bytes],
    ) -> None:
        self._context = context
        self._iterator = iterator
        self._lock = Lock()
        self._is_closed = False

    @classmethod
    def enter(
        cls,
        context: AbstractContextManager[Iterator[bytes]],
    ) -> EnteredArtifactBody:
        """Enter and verify a package stream before a response can send headers."""

        # If ``__enter__`` raises, Python context-manager semantics do not call
        # ``__exit__`` because ownership was never acquired. The route can
        # therefore translate that package error as an ordinary HTTP problem.
        iterator = context.__enter__()
        try:
            return cls(context=context, iterator=iterator)
        except BaseException:
            # Ownership has already transferred from the package. A rare local
            # allocation failure must therefore settle the entered context,
            # while the construction error remains the authoritative failure.
            try:
                context.__exit__(None, None, None)
            except BaseException:
                _log_cleanup_failure_safely()
            raise

    def __iter__(self) -> EnteredArtifactBody:
        """Return the one response-owned iterator."""

        return self

    def __next__(self) -> bytes:
        """Read one package-bounded chunk unless cleanup already won the race."""

        # A disconnect can race with a thread-pool ``next`` call. Holding the
        # lock makes close wait for that finite read instead of closing the
        # file descriptor underneath it.
        with self._lock:
            if self._is_closed:
                raise StopIteration
            return next(self._iterator)

    def close(self) -> None:
        """Exit the package context at most once across every caller."""

        with self._lock:
            if self._is_closed:
                return
            self._is_closed = True
            # Mark closed before calling package cleanup. Even if a low-level
            # close reports failure, a second caller must not close the same
            # descriptor/context again.
            self._context.__exit__(None, None, None)


class ArtifactStreamingResponse(StreamingResponse):
    """Stream verified chunks and close their package context on every ASGI exit."""

    def __init__(
        self,
        body: EnteredArtifactBody,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        self._entered_artifact_body = body
        try:
            super().__init__(
                content=body,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )
        except BaseException:
            # Construction happens after context entry. If Starlette rejects a
            # future option or header, no ASGI ``__call__`` exists to run the
            # normal finally block, so settle ownership here.
            try:
                body.close()
            except BaseException:
                # Keep the Starlette construction error authoritative just as
                # ``__call__`` keeps a send or iterator error authoritative.
                _log_cleanup_failure_safely()
            raise

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Delegate streaming while shielding exact-once cleanup in ``finally``."""

        response_error: BaseException | None = None
        try:
            await super().__call__(scope, receive, send)
        except BaseException as error:
            response_error = error
            raise
        finally:
            try:
                # A cancelled legacy ASGI stream must still close its verified
                # descriptor. Shield only this finite synchronous close call.
                with anyio.CancelScope(shield=True):
                    await run_in_threadpool(self._entered_artifact_body.close)
            except BaseException:
                if response_error is None:
                    raise
                # Preserve the original send/iterator/disconnect failure. Log
                # only a fixed event name; cleanup exceptions may hold paths.
                _log_cleanup_failure_safely()


def _log_cleanup_failure_safely() -> None:
    """Emit fixed diagnostic copy without letting an observer mask cleanup."""

    try:
        logger.error("artifact.stream_cleanup_failed")
    except BaseException:
        return


__all__ = [
    "ArtifactStreamingResponse",
    "EnteredArtifactBody",
]
