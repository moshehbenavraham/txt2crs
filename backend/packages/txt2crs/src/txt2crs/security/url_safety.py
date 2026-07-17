# SPDX-License-Identifier: MIT

"""Fail-closed URL, DNS-answer, and redirect validation for research.

The threat cases and canonicalization approach were adapted from Hermes'
MIT-licensed ``tools/url_safety.py`` at commit
``0f102fa4dc04b7dfdab048169aaaa640d09d7523``. Provider exceptions and
fail-open compatibility paths were intentionally removed.
"""

import ipaddress
import posixpath
import re
import socket
from collections.abc import Callable
from urllib.parse import (
    parse_qsl,
    quote,
    unquote,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)

Resolver = Callable[[str], tuple[str, ...]]

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata",
        "metadata.google.internal",
        "metadata.azure.internal",
        "169.254.169.254",
    }
)
_BLOCKED_HOST_SUFFIXES = (".localhost", ".local", ".internal")
_SENSITIVE_QUERY_MARKERS = (
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "credential",
    "password",
    "secret",
    "signature",
    "token",
)
_NUMERIC_HOST_PATTERN = re.compile(r"^[0-9a-fA-FxX.]+$")


class UnsafeUrlError(ValueError):
    """Raised before a URL could cross the public-network boundary."""


def _default_resolver(hostname: str) -> tuple[str, ...]:
    """Resolve every address family for a hostname."""

    try:
        address_info = socket.getaddrinfo(
            hostname,
            None,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except OSError as resolution_error:
        raise UnsafeUrlError(
            "The research hostname could not resolve."
        ) from resolution_error
    return tuple(sorted({str(address[4][0]) for address in address_info}))


def _parse_ip_address(
    hostname: str,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Recognize canonical and legacy alternate IP spellings."""

    normalized_hostname = hostname.strip("[]")
    try:
        return ipaddress.ip_address(normalized_hostname)
    except ValueError:
        pass

    # ``inet_aton`` recognizes old decimal, hexadecimal, octal, and shortened
    # IPv4 forms such as ``2130706433`` and ``0x7f000001``. Treating these as
    # hostnames would let them bypass a straightforward ``ipaddress`` check.
    if _NUMERIC_HOST_PATTERN.fullmatch(normalized_hostname):
        try:
            packed_address = socket.inet_aton(normalized_hostname)
        except OSError:
            return None
        return ipaddress.ip_address(packed_address)
    return None


def _require_global_address(address_text: str) -> None:
    """Allow only globally routable unicast addresses."""

    try:
        parsed_address = ipaddress.ip_address(address_text)
    except ValueError as address_error:
        raise UnsafeUrlError("DNS returned an invalid address.") from address_error
    if (
        not parsed_address.is_global
        or parsed_address.is_link_local
        or parsed_address.is_loopback
        or parsed_address.is_multicast
        or parsed_address.is_private
        or parsed_address.is_reserved
        or parsed_address.is_unspecified
    ):
        raise UnsafeUrlError("The URL resolves to a blocked network address.")


def _query_contains_secret(query: str) -> bool:
    """Detect credential-shaped query parameter names."""

    for parameter_name, _value in parse_qsl(query, keep_blank_values=True):
        normalized_name = parameter_name.casefold().replace("-", "_")
        if any(marker in normalized_name for marker in _SENSITIVE_QUERY_MARKERS):
            return True
    return False


def normalize_public_url(
    url: str,
    *,
    resolver: Resolver = _default_resolver,
) -> str:
    """Return one canonical public HTTP(S) URL or fail before network access."""

    if not url or len(url) > 2_048:
        raise UnsafeUrlError("The URL is empty or too long.")
    try:
        parsed_url = urlsplit(url)
        port = parsed_url.port
    except ValueError as parsing_error:
        raise UnsafeUrlError("The URL authority is malformed.") from parsing_error

    scheme = parsed_url.scheme.casefold()
    if scheme not in _ALLOWED_SCHEMES:
        raise UnsafeUrlError("Only public HTTP(S) URLs are allowed.")
    if parsed_url.username is not None or parsed_url.password is not None:
        raise UnsafeUrlError("Credentials are forbidden in research URLs.")
    if parsed_url.hostname is None:
        raise UnsafeUrlError("The URL must contain a hostname.")

    try:
        hostname = (
            parsed_url.hostname.rstrip(".").encode("idna").decode("ascii").casefold()
        )
    except UnicodeError as hostname_error:
        raise UnsafeUrlError("The URL hostname is invalid.") from hostname_error
    if hostname in _BLOCKED_HOSTNAMES or any(
        hostname.endswith(suffix) for suffix in _BLOCKED_HOST_SUFFIXES
    ):
        raise UnsafeUrlError("The URL hostname is blocked.")
    if _query_contains_secret(parsed_url.query):
        raise UnsafeUrlError("Secret-bearing query parameters are forbidden.")

    direct_address = _parse_ip_address(hostname)
    if direct_address is not None:
        _require_global_address(str(direct_address))
        canonical_hostname = (
            f"[{direct_address.compressed}]"
            if isinstance(direct_address, ipaddress.IPv6Address)
            else direct_address.compressed
        )
    else:
        resolved_addresses = resolver(hostname)
        if not resolved_addresses:
            raise UnsafeUrlError("The research hostname did not resolve.")
        for resolved_address in resolved_addresses:
            _require_global_address(resolved_address)
        canonical_hostname = hostname

    if port is not None and not 1 <= port <= 65_535:
        raise UnsafeUrlError("The URL port is invalid.")
    default_port = (scheme == "https" and port == 443) or (
        scheme == "http" and port == 80
    )
    canonical_authority = canonical_hostname
    if port is not None and not default_port:
        canonical_authority = f"{canonical_hostname}:{port}"

    decoded_path = unquote(parsed_url.path or "/")
    canonical_path = posixpath.normpath(decoded_path)
    if not canonical_path.startswith("/"):
        canonical_path = f"/{canonical_path}"
    if decoded_path.endswith("/") and canonical_path != "/":
        canonical_path = f"{canonical_path}/"
    canonical_path = quote(canonical_path, safe="/:@!$&'()*+,;=-._~")
    canonical_query = urlencode(
        parse_qsl(parsed_url.query, keep_blank_values=True),
        doseq=True,
    )
    return urlunsplit(
        (
            scheme,
            canonical_authority,
            canonical_path,
            canonical_query,
            "",
        )
    )


def validate_redirect_target(
    *,
    current_url: str,
    location_header: str,
    resolver: Resolver = _default_resolver,
) -> str:
    """Resolve a relative redirect and run the complete URL policy again."""

    if not location_header:
        raise UnsafeUrlError("A redirect response omitted its target.")
    redirect_target = urljoin(current_url, location_header)
    return normalize_public_url(redirect_target, resolver=resolver)
