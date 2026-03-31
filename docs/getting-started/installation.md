# Installation

## Docker (recommended)

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/dream-x/tscraper.git
cd tscraper

# Create configuration files
cp config.yaml.example config.yaml
cp .env.example .env
# Edit .env with your Telegram API credentials

# Start the scraper
docker-compose up -d
```

### Using Docker directly

```bash
# Build the image
docker build -t tscraper .

# Run the container
docker run -d \
  --name tscraper \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/my_user_session.session:/app/my_user_session.session \
  -p 8000:8000 \
  tscraper
```

### Using a pre-built image

```bash
docker pull kinetik/tscraper:latest

docker run -d \
  --name tscraper \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/my_user_session.session:/app/my_user_session.session \
  -p 8000:8000 \
  kinetik/tscraper:latest
```

## Manual Installation

!!! note "Requirements"
    Python 3.13+ and [Poetry](https://python-poetry.org/) are required.

```bash
# Clone the repository
git clone https://github.com/dream-x/tscraper.git
cd tscraper

# Install dependencies
poetry install

# Run the scraper
poetry run tscraper
# or
python -m tscraper.tscraper
```

## Verify Installation

Check that the health endpoint is running:

```bash
curl localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "scraper_connected": true,
  "uptime": "0:01:23",
  "timestamp": "2026-03-31T12:00:00"
}
```
