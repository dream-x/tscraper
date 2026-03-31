# Contributing

## Development Setup

```bash
git clone https://github.com/dream-x/tscraper.git
cd tscraper
poetry install
```

## Running Tests

```bash
# All tests
pytest -q

# Specific file
pytest tests/test_scraper.py -q

# Verbose output
pytest -v
```

Always run tests before committing.

## Code Style

- **PEP 8** with 4-space indentation
- **Type hints** where practical
- **snake_case** for functions/variables, **PascalCase** for classes
- Private methods prefixed with `_`
- Logging via `logging.getLogger(__name__)` — no `print()`
- `async/await` throughout, `asyncio.gather()` for concurrency
- Raise `ConfigError` for configuration issues

## Commit Style

Use [Conventional Commits](https://www.conventionalcommits.org/) prefixes:

```
add: new feature description
fix: bug fix description
docs: documentation change
refactor: code restructuring
```

Keep messages concise and imperative.

## Testing Guidelines

- Use `pytest`, `pytest-asyncio`, `pytest-mock`
- Async tests: `@pytest.mark.asyncio`
- Mock Telethon calls with `AsyncMock`, sync objects with `MagicMock`
- Shared fixtures in `tests/conftest.py`

## Pull Requests

PRs should include:

- Summary and motivation
- Linked issue (if applicable)
- Test updates or rationale for no tests
- Config/ops notes (new env vars, ports, volumes)
