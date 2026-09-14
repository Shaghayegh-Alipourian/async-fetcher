import httpx
import pytest
import respx

from app.services.fetcher import HTTPFetcher


@pytest.mark.asyncio
@respx.mock
async def test_fetch_success() -> None:
    """Fetcher should return a successful result for HTTP 200."""

    route = respx.get("https://example.com")
    route.mock(
        return_value=httpx.Response(
            200,
            content=b"hello world",
        )
    )

    async with HTTPFetcher(
        timeout=5,
        max_retries=2,
        retry_base_delay=0.01,
    ) as fetcher:
        result = await fetcher.fetch("https://example.com")

    assert result.success is True
    assert result.status_code == 200
    assert result.content_length == 11
    assert result.error is None
    assert result.attempts == 1


@pytest.mark.asyncio
@respx.mock
async def test_fetch_404_is_not_retried() -> None:
    """A 404 response should not trigger retries."""

    route = respx.get("https://example.com")
    route.mock(
        return_value=httpx.Response(
            404,
            content=b"not found",
        )
    )

    async with HTTPFetcher(
        timeout=5,
        max_retries=3,
        retry_base_delay=0.01,
    ) as fetcher:
        result = await fetcher.fetch("https://example.com")

    assert result.success is False
    assert result.status_code == 404
    assert result.attempts == 1


@pytest.mark.asyncio
@respx.mock
async def test_fetch_retries_server_error() -> None:
    """A 500 response should be retried."""

    route = respx.get("https://example.com")

    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(
            200,
            content=b"success",
        ),
    ]

    async with HTTPFetcher(
        timeout=5,
        max_retries=3,
        retry_base_delay=0.01,
    ) as fetcher:
        result = await fetcher.fetch("https://example.com")

    assert result.success is True
    assert result.status_code == 200
    assert result.attempts == 3


@pytest.mark.asyncio
@respx.mock
async def test_fetch_retry_exhaustion() -> None:
    """Fetcher should stop after the configured retry limit."""

    route = respx.get("https://example.com")
    route.mock(return_value=httpx.Response(503))

    async with HTTPFetcher(
        timeout=5,
        max_retries=2,
        retry_base_delay=0.01,
    ) as fetcher:
        result = await fetcher.fetch("https://example.com")

    assert result.success is False
    assert result.status_code is None
    assert result.attempts == 3
