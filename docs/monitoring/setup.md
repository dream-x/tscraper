# Monitoring Setup

TScraper includes a full monitoring stack: Prometheus, Grafana, and Alertmanager.

## Quick Start

```bash
# Start the scraper
docker-compose up -d

# Start the monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

This starts:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | [localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **Prometheus** | [localhost:9090](http://localhost:9090) | — |
| **Alertmanager** | [localhost:9093](http://localhost:9093) | — |

The **TScraper** dashboard is provisioned automatically in Grafana.

## Architecture

```
┌──────────┐   scrape /metrics   ┌────────────┐   query   ┌─────────┐
│ TScraper  │◄────────────────────│ Prometheus │──────────►│ Grafana │
│ :8000     │                     │ :9090      │           │ :3000   │
└──────────┘                     └─────┬──────┘           └─────────┘
                                       │ alerts
                                 ┌─────▼────────┐
                                 │ Alertmanager │
                                 │ :9093        │
                                 └──────────────┘
```

## Dashboard Panels

The pre-built Grafana dashboard includes:

- **Connection Status** — real-time connected/disconnected indicator
- **Uptime** — time since last successful connection
- **Reconnects** — total reconnection attempts
- **Messages Forwarded / Failed** — rate per minute, time series
- **Messages by Category** — stacked bar chart by category
- **Forward Latency** — p50, p95, p99 percentiles
- **Albums Forwarded** — rate per minute by category

## Health Endpoint

`GET /health` reflects the real scraper state:

=== "Connected"

    ```json
    {
      "status": "healthy",
      "scraper_connected": true,
      "uptime": "1:23:45",
      "timestamp": "2026-03-31T12:00:00"
    }
    ```
    HTTP 200

=== "Disconnected"

    ```json
    {
      "status": "degraded",
      "scraper_connected": false,
      "last_error": "Connection lost",
      "uptime": "0:05:30",
      "timestamp": "2026-03-31T12:00:00"
    }
    ```
    HTTP 503
