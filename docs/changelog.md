# Changelog

## 0.2.0

### Monitoring & Observability

- Added Prometheus metrics endpoint (`GET /metrics`)
- Added pre-built Grafana dashboard with 7 panels
- Added Alertmanager configuration with 4 alert rules
- Added `docker-compose.monitoring.yml` for the full monitoring stack
- Added `MONITORING.md` guide for standalone and external Grafana setup
- Health endpoint now reflects real scraper connection state (200/503)

### Metrics

- `tscraper_connected` — connection status gauge
- `tscraper_uptime_seconds` — uptime gauge
- `tscraper_reconnects_total` — reconnection counter
- `tscraper_messages_received_total` — received messages by category
- `tscraper_messages_forwarded_total` — forwarded messages by category
- `tscraper_messages_failed_total` — failed messages by category
- `tscraper_albums_forwarded_total` — forwarded albums by category
- `tscraper_forward_duration_seconds` — forwarding latency histogram

### Reliability Fixes

- Fixed scraper silently stopping after `run_until_disconnected()` returns
- Added exponential backoff sleep in exception handler (was tight-looping)
- Fixed fallback forwarding: now uses `send_message` with text + media instead of retrying `forward_messages`
- Fixed `TypeNotFoundError` handler referencing potentially undefined `source` variable
- Safe disconnect in exception handler (wrapped in try/except)

### CI/CD

- Added pytest step before Docker image build
- Added automatic GitHub Release creation with changelog on tag push
- Fixed `container_name` typo in docker-compose.yml (`tscrapper` -> `tscraper`)

### Documentation

- Added MkDocs site with Material theme (GitHub Pages)
- Added `CLAUDE.md` for AI assistant context
- Updated `CLAUDE.md` with monitoring section

## 0.1.0

- Initial release
- Telegram channel monitoring and message forwarding
- Media album support
- Auto-reconnection with exponential backoff
- FastAPI health endpoint
- Docker and Docker Compose support
- GitHub Actions CI/CD pipeline
