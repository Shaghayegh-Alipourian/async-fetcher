import asyncio
from collections.abc import Sequence
from types import TracebackType
from typing import Self

import structlog
from pydantic import HttpUrl

from app.models.schemas import FetchResult
from app.services.fetcher import HTTPFetcher

logger = structlog.get_logger(__name__)


class FetchService:
    """Orchestrates concurrent fetching of multiple URLs."""

    def __init__(
        self,
        fetcher: HTTPFetcher,
        *,
        max_concurrency: int,
    ) -> None:
        self._fetcher = fetcher
        self._max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def __aenter__(self) -> Self:
        """Enter the service context and initialize the fetcher."""

        await self._fetcher.__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the service context and close the fetcher."""

        await self._fetcher.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )

    async def fetch_many(
        self,
        urls: Sequence[HttpUrl],
    ) -> list[FetchResult]:
        """Fetch multiple URLs with bounded concurrency."""

        logger.info(
            "batch_fetch_started",
            url_count=len(urls),
        )

        tasks = [asyncio.create_task(self._fetch_with_limit(str(url))) for url in urls]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

        logger.info(
            "batch_fetch_completed",
            url_count=len(urls),
            successful=sum(result.success for result in results),
            failed=sum(not result.success for result in results),
        )

        return results

    async def _fetch_with_limit(
        self,
        url: str,
    ) -> FetchResult:
        """Fetch one URL while respecting the concurrency limit."""

        async with self._semaphore:
            logger.debug(
                "concurrency_slot_acquired",
                url=url,
            )

            try:
                return await self._fetcher.fetch(url)

            except asyncio.CancelledError:
                logger.warning(
                    "fetch_task_cancelled",
                    url=url,
                )
                raise

            finally:
                logger.debug(
                    "concurrency_slot_released",
                    url=url,
                )
