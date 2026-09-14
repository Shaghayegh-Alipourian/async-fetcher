from httpx import AsyncClient


async def test_health_check(
    api_client: AsyncClient,
) -> None:
    """Health endpoint should return OK."""

    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


async def test_fetch_rejects_empty_url_list(
    api_client: AsyncClient,
) -> None:
    """API should reject an empty URL list."""

    response = await api_client.post(
        "/api/v1/fetch",
        json={
            "urls": [],
        },
    )

    assert response.status_code == 422


async def test_fetch_rejects_more_than_1000_urls(
    api_client: AsyncClient,
) -> None:
    """API should reject more than 1000 URLs."""

    urls = [f"https://example.com/{index}" for index in range(1001)]

    response = await api_client.post(
        "/api/v1/fetch",
        json={
            "urls": urls,
        },
    )

    assert response.status_code == 422
