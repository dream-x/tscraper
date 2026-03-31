# Metrics Reference

All metrics are exposed at `GET /metrics` in Prometheus text format.

## Connection Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `tscraper_connected` | Gauge | `1` if connected to Telegram, `0` otherwise |
| `tscraper_uptime_seconds` | Gauge | Seconds since last successful connection |
| `tscraper_reconnects_total` | Counter | Total number of reconnection attempts |

## Message Metrics

All message metrics have a `category` label matching the YAML config category name.

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `tscraper_messages_received_total` | Counter | `category` | Messages received from source channels |
| `tscraper_messages_forwarded_total` | Counter | `category` | Messages successfully forwarded |
| `tscraper_messages_failed_total` | Counter | `category` | Messages that failed to forward |
| `tscraper_albums_forwarded_total` | Counter | `category` | Media albums forwarded |

## Latency Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `tscraper_forward_duration_seconds` | Histogram | Time to forward a message (buckets: 0.1s - 10s) |

Useful PromQL queries:

```promql
# p95 forwarding latency over the last 5 minutes
histogram_quantile(0.95, rate(tscraper_forward_duration_seconds_bucket[5m]))

# Messages per minute by category
rate(tscraper_messages_forwarded_total[1m]) * 60

# Failure rate percentage
rate(tscraper_messages_failed_total[5m])
/ (rate(tscraper_messages_forwarded_total[5m]) + rate(tscraper_messages_failed_total[5m]))
* 100
```

## Info Metric

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `tscraper_info` | Info | `version`, `health_port` | Build and config information |
