# CLAUDE.md

## Project Overview

TScraper is a Telegram channel monitoring and message forwarding tool. It watches configured source channels and automatically forwards messages (including media albums) to category-based target channels. A FastAPI health endpoint runs alongside the scraper.

- **Language:** Python 3.13
- **Package manager:** Poetry (`pyproject.toml`)
- **Telegram client:** Telethon (user session, not bot)
- **Web framework:** FastAPI + Uvicorn (health endpoint only)

## Quick Reference

```bash
# Install dependencies
poetry install

# Run tests
pytest -q

# Run specific test file
pytest tests/test_scraper.py -q

# Run scraper locally (requires .env and config.yaml)
python -m tscraper.tscraper
# or
poetry run tscraper

# First-time Telegram auth (creates my_user_session.session)
python auth.py

# Docker
docker build -t tscraper .
docker-compose up -d

# Health check
curl localhost:8000/health
```

## Project Structure

```
tscraper/
  tscraper.py      # Main TelegramScraper class and entry point
  health.py        # FastAPI /health endpoint
  __init__.py
tests/
  conftest.py      # Shared fixtures (config, mock_message, mock_channel, mock_client)
  test_scraper.py  # Scraper unit tests
  test_config.py   # Config loading tests
auth.py            # Telegram session bootstrapper
config.yaml.example
.env.example
pyproject.toml
Dockerfile
docker-compose.yml
AGENTS.md          # Repository guidelines and architecture
BUGS.md            # Known issues and suggested fixes
```

## Configuration

**Environment variables** (`.env`):
- `API_ID` — Telegram API ID (required, must be integer)
- `API_HASH` — Telegram API hash (required)
- `CONFIG_PATH` — Path to YAML config (default: `config.yaml`)
- `HEALTH_PORT` — Health endpoint port (default: `8000`)

**YAML config** (`config.yaml`): maps category names to source channel lists, plus a `target_channels` mapping of category to target channel.

```yaml
channels:
  crypto:
    - "@channel1"
    - "@channel2"
  news:
    - "@channel3"
  target_channels:
    crypto: "@crypto_target"
    news: "@news_target"
```

## Coding Conventions

- **Style:** PEP 8, 4-space indentation, type hints where practical
- **Naming:** snake_case for functions/variables, PascalCase for classes, private methods prefixed with `_`
- **Logging:** module-level `logging.getLogger(__name__)` — do not use `print()`
- **Async:** use `async/await` throughout; `asyncio.gather()` for concurrent tasks
- **Config access:** env vars via `dotenv`, YAML via `load_yaml_config()` in `tscraper.tscraper`
- **Error handling:** raise `ConfigError` for configuration issues; use try-except with logging for runtime errors

## Testing

- **Frameworks:** pytest, pytest-asyncio, pytest-mock
- **Async tests:** decorate with `@pytest.mark.asyncio`
- **Mocking:** use `AsyncMock` for async Telethon client calls, `MagicMock` for sync objects
- **Fixtures:** defined in `tests/conftest.py` — `config`, `mock_message`, `mock_channel`, `mock_client`
- **Coverage focus:** config loading, connection flow, message handling, album forwarding

Always run `pytest -q` before committing to verify nothing is broken.

## Commit Style

Use Conventional Commits-style prefixes: `fix:`, `add:`, `docs:`, `refactor:`, etc. Keep messages concise and imperative.

## Known Issues

See `BUGS.md` for tracked bugs including:
- Numeric channel ID normalization (prefixing with `@` breaks matching)
- Config vs event ID format mismatch
- Fallback forwarding retries the same method
- Dev dependencies in main poetry group (should be in `[tool.poetry.group.dev.dependencies]`)
- README references outdated Python version and missing `requirements.txt`

## Security

- **Never commit** `.env`, `*.session` files, or API credentials
- Session file `my_user_session.session` must persist across Docker restarts (mounted as volume)
- The Dockerfile hardcodes `TZ=Europe/Moscow`

## Deployment

- Docker image published to `kinetik/tscraper` via GitHub Actions on semver tags (`*.*.*`)
- Multi-platform: linux/amd64, linux/arm64
- Health check: `GET /health` returns `{"status": "healthy", "uptime": "...", "timestamp": "..."}`
