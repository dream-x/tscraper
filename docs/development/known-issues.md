# Known Issues

## Critical Code Bugs

### Numeric channel ID normalization

**Problem:** Numeric channel IDs (e.g., `-100123...`) are prefixed with `@` in `_get_target_for_source`, preventing matches with config.

**Fix:** Only add `@` for non-numeric usernames; normalize IDs consistently (retain `-100...`).

### Config vs event ID format mismatch

**Problem:** Config may include plain numeric IDs (`123...`) while events provide `-100...` or usernames; direct string compare fails.

**Fix:** Canonicalize both sides using a helper (convert bare digits to `-100{digits}`, keep usernames with optional `@`).

### Event subscription normalization

**Problem:** Subscribing with a mixed list of `'@username'` and numeric strings can be brittle.

**Fix:** Build `sources` with canonical forms (strip `@` for usernames, keep `-100...` for IDs) before `events.NewMessage(chats=...)`.

## Documentation & Project Hygiene

### Python version mismatch

**Problem:** README claims Python 3.7+, but `pyproject.toml` requires 3.13.

### Dev dependencies in main group

**Problem:** `pytest*` packages are listed as main dependencies; production image installs them.

**Fix:** Move to `[tool.poetry.group.dev.dependencies]` and use `poetry install --only=main` in Docker.

See [`BUGS.md`](https://github.com/dream-x/tscraper/blob/main/BUGS.md) in the repository for the full list.
