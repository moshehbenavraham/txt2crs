# SPDX-License-Identifier: MIT-0

"""Tests for fail-closed public-web URL validation."""

from collections.abc import Callable

import pytest

from txt2crs.security.url_safety import (
    UnsafeUrlError,
    normalize_public_url,
    validate_redirect_target,
)

PublicResolver = Callable[[str], tuple[str, ...]]


def public_resolver(hostname: str) -> tuple[str, ...]:
    """Resolve test public names without touching the real network."""

    assert hostname
    return ("93.184.216.34",)


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "file:///etc/passwd",
        "ftp://example.com/course",
        "https://user:password@example.com/course",
        "https://localhost/course",
        "https://127.0.0.1/course",
        "https://2130706433/course",
        "https://0x7f000001/course",
        "https://[::1]/course",
        "https://169.254.169.254/latest/meta-data/",
        "https://metadata.google.internal/computeMetadata/v1/",
        "https://example.com/course?access_token=secret",
    ],
)
def test_unsafe_urls_are_rejected_before_network_access(
    unsafe_url: str,
) -> None:
    """Credentials, local targets, metadata, and secret queries fail closed."""

    with pytest.raises(UnsafeUrlError):
        normalize_public_url(unsafe_url, resolver=public_resolver)


@pytest.mark.parametrize(
    "blocked_address",
    [
        "10.0.0.1",
        "100.64.0.1",
        "172.16.0.1",
        "192.168.1.1",
        "224.0.0.1",
        "fc00::1",
        "fe80::1",
    ],
)
def test_any_blocked_dns_answer_rejects_the_hostname(blocked_address: str) -> None:
    """One private answer is enough to reject a possible DNS-rebinding target."""

    def rebinding_resolver(_hostname: str) -> tuple[str, ...]:
        return ("93.184.216.34", blocked_address)

    with pytest.raises(UnsafeUrlError, match="blocked"):
        normalize_public_url(
            "https://research.example/course",
            resolver=rebinding_resolver,
        )


def test_public_url_is_canonicalized_without_a_fragment() -> None:
    """Equivalent public URLs receive a stable value for IDs and caching."""

    canonical_url = normalize_public_url(
        "HTTPS://Example.COM:443/a/../course?q=python#private-fragment",
        resolver=public_resolver,
    )

    assert canonical_url == "https://example.com/course?q=python"


def test_redirects_are_resolved_and_revalidated() -> None:
    """A safe first URL cannot redirect into a private network."""

    with pytest.raises(UnsafeUrlError):
        validate_redirect_target(
            current_url="https://example.com/start",
            location_header="http://127.0.0.1/admin",
            resolver=public_resolver,
        )

    safe_target = validate_redirect_target(
        current_url="https://example.com/start",
        location_header="/course",
        resolver=public_resolver,
    )
    assert safe_target == "https://example.com/course"


def test_dns_failure_is_not_treated_as_safe() -> None:
    """Unresolvable hosts fail closed instead of skipping address policy."""

    def empty_resolver(_hostname: str) -> tuple[str, ...]:
        return ()

    with pytest.raises(UnsafeUrlError, match="resolve"):
        normalize_public_url("https://missing.example/course", resolver=empty_resolver)
