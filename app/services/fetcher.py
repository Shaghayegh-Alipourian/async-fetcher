import asyncio
from types import TracebackType
from typing import Self

import httpx
import structlog

from app.core.exceptions import (
    FetchConnectionError,
    FetchTimeoutError,
    NonRetryableFetchHTTPError,
    RetryableFetchHTTPError,
)
from app.models.schemas import FetchResult

logger = structlog.get_logger(__name__)


class HTTPFetcher:
    """Asynchronous HTTP client responsible for fetching a single URL."""

    def __init__(
        self,
        *,
        timeout: float,
        max_retries: int,
        retry_base_delay: float,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        """Create the HTTP client when entering the context manager."""

        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
        )

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the HTTP client when leaving the context manager."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch(self, url: str) -> FetchResult:
        """Fetch a single URL with retry and exponential backoff."""

        if self._client is None:
            raise RuntimeError(
                "HTTPFetcher must be used inside an async context manager."
            )

        attempts = 0

        while attempts <= self._max_retries:
            attempts += 1

            try:
                logger.info(
                    "fetch_started",
                    url=url,
                    attempt=attempts,
                )

                result = await self._fetch_once(
                    url=url,
                    attempts=attempts,
                )

                logger.info(
                    "fetch_completed",
                    url=url,
                    status_code=result.status_code,
                    attempt=attempts,
                )

                return result

            except (
                FetchTimeoutError,
                FetchConnectionError,
                RetryableFetchHTTPError,
            ) as exc:
                logger.warning(
                    "fetch_retryable_error",
                    url=url,
                    attempt=attempts,
                    error=str(exc),
                )

                if attempts > self._max_retries:
                    logger.error(
                        "fetch_retry_exhausted",
                        url=url,
                        attempts=attempts,
                    )

                    return FetchResult(
                        url=url,
                        status_code=None,
                        success=False,
                        content_length=None,
                        error=str(exc),
                        attempts=attempts,
                    )

                delay = self._calculate_backoff(attempts)

                logger.info(
                    "fetch_retry_scheduled",
                    url=url,
                    attempt=attempts,
                    delay_seconds=delay,
                )

                await asyncio.sleep(delay)

            except NonRetryableFetchHTTPError as exc:
                logger.error(
                    "fetch_non_retryable_error",
                    url=url,
                    attempt=attempts,
                    error=str(exc),
                )

                return FetchResult(
                    url=url,
                    status_code=exc.status_code,
                    success=False,
                    content_length=None,
                    error=str(exc),
                    attempts=attempts,
                )

            except asyncio.CancelledError:
                logger.warning(
                    "fetch_cancelled",
                    url=url,
                    attempt=attempts,
                )
                raise

        raise RuntimeError("Unexpected retry loop termination.")

    async def _fetch_once(
        self,
        *,
        url: str,
        attempts: int,
    ) -> FetchResult:
        """Perform exactly one HTTP request."""

        if self._client is None:
            raise RuntimeError(
                "HTTPFetcher must be used inside an async context manager."
            )

        try:
            async with asyncio.timeout(self._timeout):
                response = await self._client.get(url)

        except TimeoutError as exc:
            raise FetchTimeoutError(
                "Request timed out.",
                url=url,
            ) from exc

        except httpx.TimeoutException as exc:
            raise FetchTimeoutError(
                "HTTP client timeout.",
                url=url,
            ) from exc

        except httpx.ConnectError as exc:
            raise FetchConnectionError(
                "Could not connect to remote server.",
                url=url,
            ) from exc

        except httpx.RequestError as exc:
            raise FetchConnectionError(
                "HTTP request failed.",
                url=url,
            ) from exc

        except asyncio.CancelledError:
            logger.warning(
                "fetch_cancelled",
                url=url,
                attempt=attempts,
            )
            raise

        status_code = response.status_code

        if 200 <= status_code < 400:
            return FetchResult(
                url=url,
                status_code=status_code,
                success=True,
                content_length=len(response.content),
                error=None,
                attempts=attempts,
            )

        if status_code == 429 or status_code >= 500:
            raise RetryableFetchHTTPError(
                f"Retryable HTTP status: {status_code}",
                status_code=status_code,
                url=url,
            )

        raise NonRetryableFetchHTTPError(
            f"Non-retryable HTTP status: {status_code}",
            status_code=status_code,
            url=url,
        )

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""

        return float(self._retry_base_delay * (2 ** (attempt - 1)))
