# Async Fetcher

A production-oriented asynchronous URL fetcher built with Python, FastAPI,
HTTPX, Pydantic, asyncio, pytest, Ruff, and mypy.

## Requirements

* Python 3.12+
* uv
* Git

## Project Goals

The project demonstrates production-oriented Python development:

* FastAPI
* Pydantic v2
* Pydantic Settings
* asyncio
* concurrency limiting
* HTTP timeouts
* retry with exponential backoff
* structured logging
* dependency injection
* error classification
* unit and integration testing
* static type checking
* linting and formatting
* pre-commit hooks
* CI with GitHub Actions

## Setup

Create the environment and install dependencies:

```bash
uv sync
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

Run the test suite:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

Format the project:

```bash
uv run ruff format .
```

Run mypy:

```bash
uv run mypy app
```

## Development

The application exposes a FastAPI endpoint for asynchronously fetching
multiple URLs.

The maximum concurrency, timeout, retry count, and retry delay are configurable
through environment variables.

## Configuration

Create a `.env` file based on `.env.example`:

```env
APP_NAME=async-fetcher
ENVIRONMENT=development
DEBUG=false

REQUEST_TIMEOUT=10
MAX_CONCURRENCY=20
MAX_RETRIES=3
RETRY_BASE_DELAY=0.5
```

## Project Structure

```text
async-fetcher/
|
+-- app/
|   |
|   +-- api/
|   |
|   +-- core/
|   |
|   +-- models/
|   |
|   +-- services/
|
+-- tests/
|
+-- .github/
|   |
|   +-- workflows/
|
+-- .pre-commit-config.yaml
+-- .gitignore
+-- Dockerfile
+-- pyproject.toml
+-- README.md
+-- uv.lock
```

## Architecture

The application follows a layered architecture:

```text
Client
  |
  v
FastAPI Route
  |
  v
FetchService
  |
  v
Concurrency Limiter
  |
  v
HTTP Fetcher
  |
  +-- Success
  |
  +-- Error
        |
        v
      Retry
        |
        v
   Final Result
```

The HTTP fetching layer is separated from the service layer so that external
HTTP calls can be replaced with fake implementations during testing.

## Quality Checks

Before creating a pull request, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest
```

The project targets at least 80% test coverage.

## Development Workflow

Feature development follows a Git-based workflow:

```text
main
 |
 +-- feature/<name>
       |
       +-- commit
       |
       +-- rebase
       |
       +-- pull request
       |
       +-- review
       |
       +-- merge
```

Changes should pass linting, formatting, type checking, and tests before being
merged into `main`.

## Production Flow

The complete application flow will be:

```text
1000 URLs
    |
    v
FastAPI
    |
    v
FetchService
    |
    v
Concurrency Limiter
    |
    v
HTTP Fetcher
    |
    +------------------+
    |                  |
    v                  v
 HTTP Success       HTTP Error
    |                  |
    |                  v
    |                Retry
    |                  |
    |                  v
    |             Exponential
    |               Backoff
    |                  |
    +--------+---------+
             |
             v
        FetchResult
             |
             v
      Pydantic Response
             |
             v
            JSON
```

## Testing Strategy

External HTTP calls are not required for unit tests.

The architecture allows the real fetcher to be replaced with a fake:

```text
FetchService
     |
     +----> RealFetcher
     |
     +----> FakeFetcher
```

This makes the service layer deterministic and easy to test.

## Error Handling

Errors will be classified into meaningful categories such as:

```text
FetchError
 |
 +-- TimeoutError
 |
 +-- ConnectionError
 |
 +-- HTTPError
 |
 +-- RetryExhaustedError
```

The exact exception hierarchy will be implemented in the core layer.

## Git Workflow

The recommended workflow is:

```text
1. Create feature branch
        |
        v
2. Implement feature
        |
        v
3. Run tests
        |
        v
4. Run Ruff
        |
        v
5. Run mypy
        |
        v
6. Commit
        |
        v
7. Rebase with main
        |
        v
8. Push branch
        |
        v
9. Create Pull Request
        |
        v
10. Review
        |
        v
11. Merge into main
```
