from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.schemas import FetchRequest, FetchResponse
from app.services.fetcher import HTTPFetcher
from app.services.service import FetchService

router = APIRouter()


async def get_fetch_service() -> FetchService:
    """Create a FetchService dependency for a request."""

    from app.core.config import get_settings

    settings = get_settings()

    fetcher = HTTPFetcher(
        timeout=settings.request_timeout,
        max_retries=settings.max_retries,
        retry_base_delay=settings.retry_base_delay,
    )

    return FetchService(
        fetcher=fetcher,
        max_concurrency=settings.max_concurrency,
    )


FetchServiceDependency = Annotated[
    FetchService,
    Depends(get_fetch_service),
]


@router.post(
    "/fetch",
    response_model=FetchResponse,
)
async def fetch_urls(
    request: FetchRequest,
    service: FetchServiceDependency,
) -> FetchResponse:
    """Fetch all requested URLs."""

    async with service:
        results = await service.fetch_many(request.urls)

    successful = sum(result.success for result in results)
    failed = len(results) - successful

    return FetchResponse(
        results=results,
        total=len(results),
        successful=successful,
        failed=failed,
    )
