# Repository Guidelines

## Project Structure & Modules
- `tscraper/`: Python package
  - `tscraper.py`: main scraper (Telethon) and entrypoint
  - `health.py`: FastAPI health endpoint
- `tests/`: pytest suite (`test_*.py`, fixtures in `conftest.py`)
- Root configs: `config.yaml` (runtime), `.env` (API keys), `pyproject.toml` (Poetry), `Dockerfile`, `docker-compose.yml`, `auth.py` (session bootstrap)

## Build, Test, and Dev Commands
- Install (Poetry): `poetry install`
- Run scraper (local): `python -m tscraper.tscraper` or `poetry run tscraper`
- Auth first-time: `python auth.py` (creates `my_user_session.session`)
- Run tests: `pytest -q` or `poetry run pytest -q`
- Docker build/run:
  - `docker build -t tscraper .`
  - `docker run -d -p 8000:8000 --env-file .env -v $(pwd)/config.yaml:/app/config.yaml -v $(pwd)/my_user_session.session:/app/my_user_session.session tscraper`
- Health check: `curl localhost:8000/health`

## Coding Style & Naming
- Language: Python 3.13; follow PEP 8, 4-space indentation, type hints where practical.
- File names: modules `snake_case.py`; tests `tests/test_<module>.py`.
- Logging: use module-level `logging.getLogger(__name__)` (consistent with existing code).
- Config access: prefer env vars via `dotenv`; load YAML via helpers in `tscraper.tscraper`.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `pytest-mock`.
- Async tests: mark with `@pytest.mark.asyncio`.
- Coverage: aim to exercise critical paths (config loading, connection flow, message handling and albums).
- Run specific file: `pytest tests/test_scraper.py -q`.

## Commit & Pull Requests
- Commit style (observed): prefixes like `fix:`, `docs:`, `add:` (Conventional-Commits‑like). Keep scope concise, imperative.
- PRs must include:
  - Summary, motivation, and linked issue (if any)
  - Screens/logs for behavior changes (e.g., forwarding/health output)
  - Test updates or rationale for no tests
  - Config/ops notes (env vars, ports, volumes)

## Security & Configuration
- Secrets: keep `API_ID`, `API_HASH` in `.env` (never commit). Session file `*.session` is git‑ignored; persist it in Docker via a volume.
- Config: set `CONFIG_PATH` if not using root `config.yaml`.
- Ports: health service defaults to `8000` (`HEALTH_PORT`).

## Architecture Overview
- Core: `TelegramScraper` (Telethon client) subscribes to source channels and forwards to category targets; supports albums.
- Sidecar: FastAPI app exposes `/health`; scraper and health server run together via `asyncio.gather`.
