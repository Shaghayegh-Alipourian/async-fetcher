class FetchError(Exception):
    """Base exception for all fetch-related errors."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.url = url

    def __str__(self) -> str:
        if self.url is not None:
            return f"{self.message} [url={self.url}]"

        return self.message


class RetryableFetchError(FetchError):
    """Error that may succeed if the request is retried."""


class NonRetryableFetchError(FetchError):
    """Error that should not be retried."""


class FetchTimeoutError(RetryableFetchError):
    """Raised when a request times out."""


class FetchConnectionError(RetryableFetchError):
    """Raised when a connection cannot be established."""


class RetryableFetchHTTPError(RetryableFetchError):
    """Raised when an HTTP error may succeed after retry."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        url: str | None = None,
    ) -> None:
        super().__init__(
            message,
            url=url,
        )
        self.status_code = status_code


class NonRetryableFetchHTTPError(NonRetryableFetchError):
    """Raised when an HTTP error should not be retried."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        url: str | None = None,
    ) -> None:
        super().__init__(
            message,
            url=url,
        )
        self.status_code = status_code


class RetryExhaustedError(FetchError):
    """Raised when all retry attempts have failed."""

    def __init__(
        self,
        message: str,
        *,
        attempts: int,
        url: str | None = None,
    ) -> None:
        super().__init__(
            message,
            url=url,
        )
        self.attempts = attempts
