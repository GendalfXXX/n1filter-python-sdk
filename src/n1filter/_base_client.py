"""Shared logic for synchronous and asynchronous N1Filter clients.

This module is internal. Import :class:`N1FilterClient` or
:class:`AsyncN1FilterClient` from the top-level ``n1filter`` package instead.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from n1filter._constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, USER_AGENT
from n1filter._exceptions import (
    AuthenticationError,
    InsufficientBalanceError,
    N1FilterError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from n1filter._types import FileInput


class BaseClient:
    """Common base class for :class:`N1FilterClient` and :class:`AsyncN1FilterClient`.

    Handles authentication headers, HTTP status-to-exception mapping, and
    file input normalization. Not intended for direct use.
    """

    __slots__ = ("_api_key", "_base_url", "_timeout")

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: Your N1Filter API key (format: ``sk-...``).
            base_url: Base URL of the N1Filter API. Override for self-hosted
                instances or testing. Trailing slash is stripped automatically.
            timeout: Default HTTP request timeout in seconds.

        Raises:
            ValueError: If *api_key* is empty.
        """
        if not api_key:
            raise ValueError("api_key must not be empty")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def _headers(self) -> dict[str, str]:
        """HTTP headers attached to every request.

        Includes:
        - ``Authorization: Bearer <api_key>``
        - ``User-Agent: n1filter-python/<version>``
        """
        return {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": USER_AGENT,
        }

    @staticmethod
    def _check_status(status_code: int, body: Any) -> None:
        """Map an HTTP status code to the appropriate SDK exception.

        Does nothing for 2xx responses. For error responses, extracts the
        ``detail`` field from the JSON body (FastAPI convention) and raises
        the matching exception type.

        Args:
            status_code: HTTP response status code.
            body: Parsed JSON body (``dict``), raw text (``str``), or any
                fallback value.

        Raises:
            AuthenticationError: On 401 or 403.
            InsufficientBalanceError: On 402.
            NotFoundError: On 404.
            ValidationError: On 400 or 422.
            RateLimitError: On 429.
            ServerError: On 5xx.
            N1FilterError: On any other non-2xx status.
        """
        if 200 <= status_code < 300:
            return

        detail = ""
        if isinstance(body, dict):
            detail = body.get("detail", str(body))
        elif isinstance(body, str):
            detail = body
        else:
            detail = str(body)

        if status_code in (401, 403):
            raise AuthenticationError(detail or "Invalid API key", status_code)
        if status_code == 402:
            raise InsufficientBalanceError(
                detail or "Insufficient token balance", status_code
            )
        if status_code == 404:
            raise NotFoundError(detail or "Resource not found", status_code)
        if status_code in (400, 422):
            raise ValidationError(detail or "Invalid request", status_code)
        if status_code == 429:
            retry_after: float | None = None
            if isinstance(body, dict) and "retry_after" in body:
                try:
                    retry_after = float(body["retry_after"])
                except (TypeError, ValueError):
                    pass
            raise RateLimitError(
                detail or "Rate limit exceeded", status_code, retry_after
            )
        if status_code >= 500:
            raise ServerError(detail or "Server error", status_code)

        raise N1FilterError(f"HTTP {status_code}: {detail}", status_code)

    @staticmethod
    def _prepare_file(image: FileInput) -> tuple[str, bytes, str]:
        """Normalize a file input into an upload-ready tuple.

        Args:
            image: Image to upload — file path (``str`` or :class:`~pathlib.Path`)
                or raw ``bytes``.

        Returns:
            A tuple of ``(filename, content_bytes, content_type)``:

            - For file paths: reads the file, detects MIME type from extension.
            - For raw bytes: uses ``"image.jpg"`` as filename and
              ``"image/jpeg"`` as content type.

        Raises:
            FileNotFoundError: If the file path does not exist.
            TypeError: If *image* is not ``str``, ``Path``, or ``bytes``.
        """
        if isinstance(image, (str, Path)):
            path = Path(image)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            content = path.read_bytes()
            filename = path.name
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        elif isinstance(image, bytes):
            content = image
            filename = "image.jpg"
            content_type = "image/jpeg"
        else:
            raise TypeError(
                f"image must be str, Path, or bytes, got {type(image).__name__}"
            )
        return filename, content, content_type
