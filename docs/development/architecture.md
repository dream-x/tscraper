# Architecture

## Overview

TScraper is a single-process Python application that runs two concurrent services:

1. **Telegram Scraper** — Telethon client that monitors source channels and forwards messages
2. **Health/Metrics Server** — FastAPI app serving `/health` and `/metrics` endpoints

Both run in the same event loop via `asyncio.gather()`.

## Module Structure

```
tscraper/
├── tscraper.py   # Main entry point and TelegramScraper class
├── health.py     # FastAPI app with /health and /metrics
├── metrics.py    # Prometheus metric definitions
└── __init__.py
```

### `tscraper.py`

- `load_yaml_config()` — loads and validates YAML configuration
- `TelegramScraper` — main class:
    - `start()` — main loop with reconnection logic
    - `_connect()` — establishes Telegram connection
    - `_handle_message()` — processes and forwards messages
    - `_get_target_for_source()` — resolves category routing
    - `_update_uptime()` — background task for uptime metric
- `run_services()` — launches scraper + HTTP server concurrently
- `main()` — entry point, loads config and starts services

### `health.py`

- `/health` — returns connection status (200 OK or 503 degraded)
- `/metrics` — Prometheus text format metrics
- `set_scraper_status()` — called by the scraper to update health state

### `metrics.py`

Defines all Prometheus counters, gauges, and histograms. Imported by `tscraper.py`.

## Message Flow

```
Source Channel
    │
    ▼
events.NewMessage(chats=sources)
    │
    ▼
_handle_message(event)
    │
    ├── get_chat() → resolve source
    ├── _get_target_for_source() → find target
    │
    ├── grouped_id? ──yes──► iter_messages() → collect album
    │                              │
    │                              ▼
    │                    forward_messages(target, album)
    │
    └── single message ──► forward_messages(target, message)
                                   │
                                   ▼ on failure
                           send_message(target, text, file=media)
```

## Reconnection Logic

The scraper uses exponential backoff for reconnection:

1. Initial delay: 1 second
2. On failure: delay doubles (max 30 seconds)
3. On success: delay resets to 1 second
4. `run_until_disconnected()` return triggers reconnection
5. Exceptions trigger disconnect + backoff + retry

## Configuration Loading

```
.env (API_ID, API_HASH, HEALTH_PORT, CONFIG_PATH)
  │
  ▼
load_dotenv()
  │
  ▼
config.yaml
  │
  ▼
load_yaml_config() → validates structure
  │
  ▼
TelegramScraper(api_id, api_hash, config)
```
