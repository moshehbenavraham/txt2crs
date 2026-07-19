"""Fail-closed tests for lifespan-owned course-system dependencies."""

from collections.abc import Callable
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import Request
from txt2crs.application import Txt2CrsApplication

from app.api.deps import (
    get_txt2crs_application,
    get_txt2crs_submission,
    get_txt2crs_worker,
)
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.services.txt2crs_submission import Txt2CrsSubmissionService
from app.services.txt2crs_worker import SerialTxt2CrsWorker


def _request(**state_values: object) -> Request:
    """Build one request with only explicitly supplied app state."""

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/jobs",
            "headers": [],
            "app": SimpleNamespace(state=SimpleNamespace(**state_values)),
        }
    )


@pytest.mark.parametrize(
    "dependency",
    [
        get_txt2crs_application,
        get_txt2crs_worker,
        get_txt2crs_submission,
    ],
)
def test_course_dependencies_fail_closed_for_missing_or_wrong_state(
    dependency: Callable[[Request], object],
) -> None:
    for request in (
        _request(),
        _request(
            txt2crs_lifecycle=SimpleNamespace(application=object()),
            txt2crs_worker=object(),
            txt2crs_submission=object(),
        ),
    ):
        with pytest.raises(AppException) as captured_error:
            dependency(request)
        assert captured_error.value.code is ErrorCode.SYSTEM_NOT_READY


def test_course_dependencies_return_only_typed_lifespan_services() -> None:
    application = object.__new__(Txt2CrsApplication)
    worker = object.__new__(SerialTxt2CrsWorker)
    submission = object.__new__(Txt2CrsSubmissionService)
    request = _request(
        txt2crs_lifecycle=SimpleNamespace(application=application),
        txt2crs_worker=worker,
        txt2crs_submission=submission,
    )

    assert get_txt2crs_application(request) is application
    assert get_txt2crs_worker(request) is worker
    assert get_txt2crs_submission(request) is submission
    assert isinstance(
        cast(Txt2CrsSubmissionService, get_txt2crs_submission(request)),
        Txt2CrsSubmissionService,
    )
