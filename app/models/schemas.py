from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class FetchRequest(BaseModel):
    """Request body for fetching multiple URLs."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    urls: list[HttpUrl] = Field(
        min_length=1,
        max_length=1000,
        description="URLs that should be fetched.",
    )


class FetchResult(BaseModel):
    """Result of fetching a single URL."""

    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl

    status_code: int | None = Field(
        default=None,
        ge=100,
        le=599,
    )

    success: bool

    content_length: int | None = Field(
        default=None,
        ge=0,
    )

    error: str | None = None

    attempts: int = Field(
        default=1,
        ge=1,
    )


class FetchResponse(BaseModel):
    """Response containing the results of all URL fetches."""

    model_config = ConfigDict(
        extra="forbid",
    )

    results: list[FetchResult]

    total: int = Field(
        ge=0,
    )

    successful: int = Field(
        ge=0,
    )

    failed: int = Field(
        ge=0,
    )
