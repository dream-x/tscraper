# TScraper

Telegram channel monitoring and message forwarding tool.

TScraper watches configured source channels and automatically forwards messages (including media albums) to category-based target channels.

## Features

- **Multi-channel monitoring** — watch multiple Telegram channels simultaneously
- **Category-based routing** — forward messages to target channels by category
- **Album support** — preserve full media albums when forwarding
- **Auto-reconnection** — exponential backoff on connection loss
- **Prometheus metrics** — built-in `/metrics` endpoint for observability
- **Grafana dashboard** — pre-built dashboard with alerting rules
- **Health checks** — `GET /health` returns real connection state
- **Docker-ready** — multi-platform images (amd64/arm64)

## Quick Start

```bash
# Clone and install
git clone https://github.com/dream-x/tscraper.git
cd tscraper
poetry install

# Configure
cp config.yaml.example config.yaml
cp .env.example .env
# Edit .env with your API_ID and API_HASH from my.telegram.org

# Authenticate with Telegram
python auth.py

# Run
poetry run tscraper
```

Or with Docker:

```bash
docker-compose up -d
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Telegram client | Telethon (user session) |
| HTTP server | FastAPI + Uvicorn |
| Metrics | prometheus-client |
| Package manager | Poetry |
| Container | Docker (multi-platform) |
| CI/CD | GitHub Actions |

## Version

Current version: **0.2.0**
