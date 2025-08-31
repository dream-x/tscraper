# Known Issues and Suggested Fixes

## Critical Code Bugs
- Incorrect source normalization in `TelegramScraper._get_target_for_source`:
  - Problem: Numeric channel IDs (e.g., `-100123…`) are prefixed with `@`, preventing matches with config.
  - Fix: Only add `@` for non-numeric usernames; normalize IDs consistently (retain `-100…`).
- Exception path may reference undefined `source`:
  - Problem: In the `TypeNotFoundError` handler, `source` might not yet be set.
  - Fix: Use a safe `source_repr = locals().get('source', '<unknown>')` or log without it.
- Fallback forwarding retries the same method:
  - Problem: On failure, code calls `forward_messages` again.
  - Fix: Use a true fallback: `send_message(target, event.message.message, file=event.message.media)`; for albums, recompose list and send once.

## Reliability / Behavior
- Config vs event ID mismatch:
  - Problem: Config may include plain numeric IDs (`123…`) while events provide `-100…` or usernames; direct string compare fails.
  - Fix: Canonicalize both sides using a helper (e.g., convert bare digits to `-100{digits}`, keep usernames with optional `@`). Compare canonical forms.
- Event subscription normalization:
  - Problem: Subscribing with a mixed list of `'@username'` and numeric strings can be brittle.
  - Fix: Build `sources` with canonical forms (strip `@` for usernames, keep `-100…` for IDs) before `events.NewMessage(chats=…)`.

## Documentation & Project Hygiene
- Python version mismatch:
  - Problem: README claims Python 3.7+, but `pyproject.toml` requires 3.13.
  - Fix: Update README to 3.13+ or relax `pyproject` if broader support is intended.
- Install/run instructions drift:
  - Problem: README references `requirements.txt` (not present) and `python -m tscraper` (no package `__main__`).
  - Fix: Recommend Poetry (`poetry install`) and `python -m tscraper.tscraper` or `poetry run tscraper`.
- Docker Compose naming:
  - Problem: Uses `container_name: tscrapper` (typo).
  - Fix: Align to `tscraper`.
- `.gitignore` typo:
  - Problem: Has `.ropenproject`; repository actually uses `.ropeproject`.
  - Fix: Add `.ropeproject` (retain the existing entry if desired).
- Dev dependencies in main:
  - Problem: `pytest*` listed as main dependencies; production image installs them.
  - Fix: Move to `[tool.poetry.group.dev.dependencies]` and keep `poetry install --only=main` in Docker.

## Optional / Minor
- `auth.py` user display:
  - Problem: `@{me.username}` may be `@None`.
  - Fix: Use `me.username or me.id`.
- Dockerfile `EXPOSE`:
  - Note: `EXPOSE ${HEALTH_PORT}` can confuse some tooling.
  - Fix: Consider `EXPOSE 8000` and rely on env for binding.
