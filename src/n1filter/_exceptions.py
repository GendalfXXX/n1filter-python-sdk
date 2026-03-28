"""Exception hierarchy for the N1Filter SDK.

All exceptions raised by this library inherit from :class:`N1FilterError`,
so you can catch that single type to handle any SDK error.
"""

from __future__ import annotations


class N1FilterError(Exception):
    """Base exception for all N1Filter SDK errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code that triggered the error, or ``None``
            if the error did not originate from an HTTP response.
    """

    message: str
    status_code: int | None

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.message!r})"


class AuthenticationError(N1FilterError):
    """Raised on HTTP 401/403 — invalid or missing API key."""


class InsufficientBalanceError(N1FilterError):
    """Raised on HTTP 402 — not enough tokens to perform the generation."""


class NotFoundError(N1FilterError):
    """Raised on HTTP 404 — order not found or does not belong to the user."""


class ValidationError(N1FilterError):
    """Raised on HTTP 400/422 — invalid request parameters.

    Common causes: unsupported image format, file too large, invalid preset.
    """


class RateLimitError(N1FilterError):
    """Raised on HTTP 429 — too many requests.

    Attributes:
        retry_after: Suggested wait time in seconds before the next request,
            or ``None`` if the server did not provide a ``Retry-After`` value.
    """

    retry_after: float | None

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code)
        self.retry_after = retry_after


class ServerError(N1FilterError):
    """Raised on HTTP 5xx — server-side error."""


class TimeoutError(N1FilterError):
    """Raised when polling exceeds *max_wait* seconds.

    Attributes:
        order_id: The order that was being polled.
        last_status: The last observed status before the timeout.
    """

    order_id: int
    last_status: str

    def __init__(self, message: str, order_id: int, last_status: str) -> None:
        super().__init__(message, status_code=None)
        self.order_id = order_id
        self.last_status = last_status


class DownloadError(N1FilterError):
    """Raised when the result file download fails.

    Common causes: empty response body, file expired, server error during transfer.
    """
