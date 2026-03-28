from prometheus_client import Counter, Gauge, Histogram, Info

# Connection metrics
scraper_connected = Gauge(
    'tscraper_connected',
    'Whether the scraper is currently connected to Telegram (1=yes, 0=no)'
)
scraper_uptime_seconds = Gauge(
    'tscraper_uptime_seconds',
    'Seconds since the scraper last connected'
)
reconnect_total = Counter(
    'tscraper_reconnects_total',
    'Total number of reconnection attempts'
)

# Message metrics
messages_received_total = Counter(
    'tscraper_messages_received_total',
    'Total messages received from source channels',
    ['category']
)
messages_forwarded_total = Counter(
    'tscraper_messages_forwarded_total',
    'Total messages successfully forwarded',
    ['category']
)
messages_failed_total = Counter(
    'tscraper_messages_failed_total',
    'Total messages that failed to forward',
    ['category']
)
albums_forwarded_total = Counter(
    'tscraper_albums_forwarded_total',
    'Total albums successfully forwarded',
    ['category']
)

# Forwarding latency
forward_duration_seconds = Histogram(
    'tscraper_forward_duration_seconds',
    'Time spent forwarding a message',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Info
scraper_info = Info(
    'tscraper',
    'TScraper build and config information'
)
