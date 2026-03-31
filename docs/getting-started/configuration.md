# Configuration

TScraper uses two configuration sources: environment variables and a YAML config file.

## Environment Variables

Create a `.env` file (see `.env.example`):

```bash
API_ID=12345678          # Telegram API ID (required, integer)
API_HASH=abcdef1234...   # Telegram API hash (required)
CONFIG_PATH=config.yaml  # Path to YAML config (default: config.yaml)
HEALTH_PORT=8000         # Health/metrics endpoint port (default: 8000)
```

!!! warning "Getting API credentials"
    Get your `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org).
    Never commit the `.env` file to version control.

## YAML Config

Create `config.yaml` from the example:

```bash
cp config.yaml.example config.yaml
```

### Structure

```yaml
channels:
  crypto:                    # Category name
    - "@crypto_news"         # Source channels (username format)
    - "@bitcoin_updates"
    - "-1001234567890"       # Or numeric channel ID format
  news:
    - "@world_news"
    - "@tech_daily"
  target_channels:           # Where to forward messages
    crypto: "@my_crypto"     # category -> target channel
    news: "@my_news"
```

### Channel Formats

Sources and targets can use these formats:

| Format | Example | Description |
|--------|---------|-------------|
| `@username` | `@crypto_news` | Public channel username |
| `-100...` | `-1001234567890` | Full numeric channel ID |
| Plain digits | `1234567890` | Auto-prefixed with `-100` |

### Adding a New Category

1. Add a new key under `channels` with a list of source channels
2. Add a corresponding entry under `target_channels`

```yaml
channels:
  # ... existing categories ...
  sports:
    - "@sports_live"
    - "@football_news"
  target_channels:
    # ... existing targets ...
    sports: "@my_sports_feed"
```

No restart is needed if you are using Docker with a volume mount — but you need to restart the scraper process.
