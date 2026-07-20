"""Allowlist for server-side remote URL fetches (SSRF defense).

Phase M execution does not fetch remote URLs today (``fixture:`` /
``artifact:`` only). This module is the gate for any future STAC asset
download or remote input_ref, and is tested as a hard deny for private /
metadata / unknown hosts.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

# Explicit hosts used by Microsoft Planetary Computer STAC + common
# Azure Blob endpoints that host Sentinel assets.
_EXACT_HOSTS = frozenset(
    {
        "planetarycomputer.microsoft.com",
        "westus2.api.cognitive.microsoft.com",
    }
)

# Suffix allowlist for PC / Azure blob storage (Sentinel-1/2 assets).
_HOST_SUFFIXES = (
    ".blob.core.windows.net",
    ".data.microsoft.com",
)


class RemoteUrlError(ValueError):
    """Raised when a URL fails the remote-fetch allowlist."""

    def __init__(self, message: str, *, code: str = "remote_url_blocked") -> None:
        super().__init__(message)
        self.code = code


def is_remote_url_allowed(url: str) -> bool:
    try:
        assert_remote_url_allowed(url)
        return True
    except RemoteUrlError:
        return False


def assert_remote_url_allowed(url: str) -> str:
    """Validate ``url`` for a future server-side fetch.

    Returns the normalized URL on success. Raises ``RemoteUrlError`` when
    the scheme, host, or resolved address is not allowlisted.
    """
    if not isinstance(url, str) or not url.strip():
        raise RemoteUrlError("URL is required")

    parsed = urlparse(url.strip())
    if parsed.scheme != "https":
        raise RemoteUrlError("Only https remote URLs are allowed")
    if parsed.username or parsed.password:
        raise RemoteUrlError("Remote URLs must not include credentials")
    host = (parsed.hostname or "").lower()
    if not host:
        raise RemoteUrlError("Remote URL host is required")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise RemoteUrlError("Localhost remote URLs are blocked")
    if not _host_is_allowlisted(host):
        raise RemoteUrlError(f"Host is not on the remote fetch allowlist: {host}")

    _assert_host_not_private(host)
    return url.strip()


def _host_is_allowlisted(host: str) -> bool:
    if host in _EXACT_HOSTS:
        return True
    return any(host.endswith(suffix) for suffix in _HOST_SUFFIXES)


def _assert_host_not_private(host: str) -> None:
    """Resolve host and reject private / link-local / metadata addresses."""
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise RemoteUrlError(f"Remote URL host could not be resolved: {host}") from exc

    for info in infos:
        sockaddr = info[4]
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise RemoteUrlError(
                f"Remote URL resolves to a blocked address ({ip_str})"
            )
        # Cloud metadata endpoints often sit on link-local; also block the
        # well-known AWS/GCP/Azure metadata IP explicitly.
        if ip_str in {"169.254.169.254", "fd00:ec2::254"}:
            raise RemoteUrlError("Cloud metadata endpoints are blocked")
