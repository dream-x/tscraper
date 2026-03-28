# Monitoring Guide

TScraper exposes Prometheus metrics at `/metrics` and ships with a ready-made Grafana dashboard.

## Quick Start (standalone stack)

```bash
# Start the scraper
docker-compose up -d

# Start Prometheus + Grafana + Alertmanager
docker-compose -f docker-compose.monitoring.yml up -d
```

Open Grafana at [http://localhost:3000](http://localhost:3000) (login: `admin` / `admin`).
The **TScraper** dashboard is provisioned automatically.

## Connecting to an existing Grafana

If you already have a shared Grafana instance, you only need to:

### 1. Point Prometheus at TScraper

Add a scrape job to your existing `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "tscraper"
    metrics_path: /metrics
    static_configs:
      - targets: ["<tscraper-host>:8000"]
        labels:
          instance: "tscraper"
```

Reload Prometheus (`POST /-/reload` or send SIGHUP).

### 2. Import the dashboard

In Grafana: **Dashboards > New > Import**, then paste the contents of
[`monitoring/grafana/dashboards/tscraper.json`](monitoring/grafana/dashboards/tscraper.json)
or upload the file directly.

Select your Prometheus datasource when prompted.

### 3. Import alert rules (optional)

Copy [`monitoring/alerts.yml`](monitoring/alerts.yml) into your Prometheus
rules directory, or convert the rules to Grafana Alerting format via
**Alerting > Alert rules > New alert rule** using the PromQL expressions from the file.

## Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `tscraper_connected` | Gauge | `1` if connected to Telegram, `0` otherwise |
| `tscraper_uptime_seconds` | Gauge | Seconds since last successful connection |
| `tscraper_reconnects_total` | Counter | Total reconnection attempts |
| `tscraper_messages_received_total` | Counter | Messages received (label: `category`) |
| `tscraper_messages_forwarded_total` | Counter | Messages forwarded (label: `category`) |
| `tscraper_messages_failed_total` | Counter | Messages failed (label: `category`) |
| `tscraper_albums_forwarded_total` | Counter | Albums forwarded (label: `category`) |
| `tscraper_forward_duration_seconds` | Histogram | Forwarding latency (p50/p95/p99) |
| `tscraper_info` | Info | Build version and config |

## Alerts

Pre-configured alert rules in `monitoring/alerts.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| **ScraperDisconnected** | `tscraper_connected == 0` for 2 min | critical |
| **ScraperHighFailRate** | Failure rate > 10% for 5 min | warning |
| **ScraperNoMessages** | No messages for 30 min while connected | warning |
| **ScraperFrequentReconnects** | > 5 reconnects in 10 min | warning |

Configure notification channels in `monitoring/alertmanager/alertmanager.yml`
(Slack, webhook, email, etc.).

## Health Endpoint

`GET /health` now reflects the real scraper state:

```json
// Connected
{"status": "healthy", "scraper_connected": true, "uptime": "1:23:45", "timestamp": "..."}

// Disconnected (returns HTTP 503)
{"status": "degraded", "scraper_connected": false, "last_error": "...", "uptime": "...", "timestamp": "..."}
```

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
