# Connecting to an External Grafana

If you already have a shared Grafana instance, you don't need the bundled monitoring stack. Just connect your existing Prometheus to TScraper and import the dashboard.

## Step 1: Configure Prometheus

Add a scrape job to your existing `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "tscraper"
    metrics_path: /metrics
    scrape_interval: 15s
    static_configs:
      - targets: ["<tscraper-host>:8000"]
        labels:
          instance: "tscraper"
```

Replace `<tscraper-host>` with the hostname or IP where TScraper is running.

Reload Prometheus:

```bash
# Via HTTP API (if --web.enable-lifecycle is set)
curl -X POST http://prometheus:9090/-/reload

# Or via signal
kill -HUP $(pidof prometheus)
```

## Step 2: Import the Dashboard

1. Open Grafana: **Dashboards > New > Import**
2. Upload `monitoring/grafana/dashboards/tscraper.json` or paste its contents
3. Select your Prometheus datasource when prompted
4. Click **Import**

The dashboard UID is `tscraper-overview`.

!!! tip "Dashboard JSON"
    The dashboard JSON file is at
    [`monitoring/grafana/dashboards/tscraper.json`](https://github.com/dream-x/tscraper/blob/main/monitoring/grafana/dashboards/tscraper.json)
    in the repository.

## Step 3: Import Alert Rules (Optional)

You have two options:

### Option A: Prometheus alert rules

Copy `monitoring/alerts.yml` into your Prometheus rules directory and reload.

### Option B: Grafana Alerting

Create Grafana alert rules using the PromQL expressions:

| Alert | PromQL |
|-------|--------|
| Disconnected | `tscraper_connected == 0` |
| High fail rate | `rate(tscraper_messages_failed_total[5m]) / (rate(tscraper_messages_forwarded_total[5m]) + rate(tscraper_messages_failed_total[5m])) > 0.1` |
| No messages | `increase(tscraper_messages_received_total[30m]) == 0 and tscraper_connected == 1` |
| Frequent reconnects | `increase(tscraper_reconnects_total[10m]) > 5` |

Go to **Alerting > Alert rules > New alert rule** and configure each one with the appropriate PromQL query, evaluation interval, and notification channel.

## Step 4: Verify

After configuration, check that metrics are flowing:

```bash
# Verify the metrics endpoint is reachable
curl http://<tscraper-host>:8000/metrics

# Check Prometheus targets page
# http://prometheus:9090/targets — tscraper should show as UP
```

In Grafana, open the TScraper dashboard and verify that panels display data.
