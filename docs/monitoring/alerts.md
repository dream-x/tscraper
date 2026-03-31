# Alert Rules

Pre-configured Prometheus alert rules are in `monitoring/alerts.yml`.

## Alerts Overview

| Alert | Condition | For | Severity |
|-------|-----------|-----|----------|
| **ScraperDisconnected** | `tscraper_connected == 0` | 2 min | critical |
| **ScraperHighFailRate** | Failure rate > 10% | 5 min | warning |
| **ScraperNoMessages** | No messages while connected | 30 min | warning |
| **ScraperFrequentReconnects** | > 5 reconnects in 10 min | 1 min | warning |

## Alert Details

### ScraperDisconnected

```yaml
alert: ScraperDisconnected
expr: tscraper_connected == 0
for: 2m
```

Fires when the scraper loses connection to Telegram for more than 2 minutes. This is a **critical** alert — the scraper is not forwarding messages.

### ScraperHighFailRate

```yaml
alert: ScraperHighFailRate
expr: >
  rate(tscraper_messages_failed_total[5m])
  / (rate(tscraper_messages_forwarded_total[5m]) + rate(tscraper_messages_failed_total[5m]))
  > 0.1
for: 5m
```

Fires when more than 10% of messages fail to forward over a 5-minute window.

### ScraperNoMessages

```yaml
alert: ScraperNoMessages
expr: >
  increase(tscraper_messages_received_total[30m]) == 0
  and tscraper_connected == 1
for: 30m
```

Fires when the scraper is connected but receives no messages for 30 minutes. This may indicate a configuration issue or that monitored channels are inactive.

### ScraperFrequentReconnects

```yaml
alert: ScraperFrequentReconnects
expr: increase(tscraper_reconnects_total[10m]) > 5
for: 1m
```

Fires on connection instability — too many reconnection attempts in a short period.

## Configuring Notifications

Edit `monitoring/alertmanager/alertmanager.yml` to configure where alerts are sent:

=== "Slack"

    ```yaml
    receivers:
      - name: 'default'
        slack_configs:
          - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
            channel: '#alerts'
            title: '{{ .GroupLabels.alertname }}'
            text: '{{ .CommonAnnotations.description }}'
    ```

=== "Webhook"

    ```yaml
    receivers:
      - name: 'default'
        webhook_configs:
          - url: 'http://your-service:5001/alert'
    ```

=== "Email"

    ```yaml
    global:
      smtp_smarthost: 'smtp.gmail.com:587'
      smtp_from: 'alerts@example.com'
      smtp_auth_username: 'alerts@example.com'
      smtp_auth_password: 'app-password'

    receivers:
      - name: 'default'
        email_configs:
          - to: 'team@example.com'
    ```
