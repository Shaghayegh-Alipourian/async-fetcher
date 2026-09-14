import asyncio

import pytest
from pydantic import HttpUrl

from app.models.schemas import FetchResult
from app.services.service import FetchService


class FakeFetcher:
    """Fake fetcher used for deterministic service tests."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def __aenter__(self) -> "FakeFetcher":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        return None

    async def fetch(self, url: str) -> FetchResult:
        self.calls.append(url)

        return FetchResult(
            url=url,
            status_code=200,
            success=True,
            content_length=10,
            error=None,
            attempts=1,
        )


class SlowFakeFetcher(FakeFetcher):
    """Fake fetcher that simulates slow requests."""

    def __init__(self) -> None:
        super().__init__()
        self.active_requests = 0
        self.max_active_requests = 0

    async def fetch(self, url: str) -> FetchResult:
        self.calls.append(url)

        self.active_requests += 1
        self.max_active_requests = max(
            self.max_active_requests,
            self.active_requests,
        )

        try:
            await asyncio.sleep(0.01)

            return FetchResult(
                url=url,
                status_code=200,
                success=True,
                content_length=10,
                error=None,
                attempts=1,
            )
        finally:
            self.active_requests -= 1


@pytest.mark.asyncio
async def test_fetch_many_fetches_all_urls() -> None:
    """Service should fetch every requested URL."""

    fetcher = FakeFetcher()

    service = FetchService(
        fetcher=fetcher,  # type: ignore[arg-type]
        max_concurrency=2,
    )

    urls = [
        HttpUrl("https://example.com"),
        HttpUrl("https://example.org"),
        HttpUrl("https://example.net"),
    ]

    async with service:
        results = await service.fetch_many(urls)

    assert len(results) == 3
    assert all(result.success for result in results)
    assert len(fetcher.calls) == 3


@pytest.mark.asyncio
async def test_fetch_many_respects_concurrency_limit() -> None:
    """Service should never exceed the configured concurrency."""

    fetcher = SlowFakeFetcher()

    service = FetchService(
        fetcher=fetcher,  # type: ignore[arg-type]
        max_concurrency=2,
    )

    urls = [
        HttpUrl("https://example.com"),
        HttpUrl("https://example.org"),
        HttpUrl("https://example.net"),
        HttpUrl("https://example.edu"),
    ]

    async with service:
        results = await service.fetch_many(urls)

    assert len(results) == 4
    assert fetcher.max_active_requests <= 2
