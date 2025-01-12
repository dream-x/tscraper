# TScraper

TScraper is a Telegram channel monitoring and message forwarding tool. It allows you to automatically forward messages from multiple source channels to designated target channels based on predefined categories.

## Features

- Monitor multiple Telegram channels simultaneously
- Forward messages to specific target channels based on categories
- Preserve full media albums when forwarding
- Automatic reconnection with exponential backoff
- Health check endpoint
- Easy configuration using YAML

## Requirements

- Python 3.7+
- Telegram API credentials (api_id and api_hash)
- Required Python packages (see requirements.txt)

## Docker Installation

The easiest way to run TScraper is using Docker.

1. Build the Docker image:
```bash
docker build -t tscraper .
```

2. Create your configuration files:
```bash
# Create and edit config.yaml
cp config.yaml.example config.yaml

# Create .env file with your credentials
echo "API_ID=your_api_id" > .env
echo "API_HASH=your_api_hash" >> .env
```

3. Run the container:
```bash
docker run -d \
  --name tscraper \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/my_user_session.session:/app/my_user_session.session \
  -p 8000:8000 \
  tscraper
```

Note: The session file (`my_user_session.session`) will be created on first run. It's important to persist this file using a volume mount to avoid re-authentication.

### Docker Compose

You can also use Docker Compose. Create a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  scraper:
    build: .
    container_name: tscrapper
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./my_user_session.session:/app/my_user_session.session
    environment:
      - HEALTH_PORT=8000
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/dream-x/tscraper.git
cd tscraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy example configuration:
```bash
cp config.yaml.example config.yaml
```

4. Create `.env` file with your Telegram API credentials:
```bash
API_ID=your_api_id # my.telegram.org
API_HASH=your_api_hash # my.telegram.org
HEALTH_PORT=8000  # optional, default is 8000
CONFIG_PATH=config.yaml  # optional, default is config.yaml
```

## Configuration

Configure your channels in `config.yaml`:

```yaml
channels:
  crypto:  # category name
    - "@channel1"  # source channels
    - "@channel2"
  news:
    - "@channel3"
    - "@channel4"
  target_channels:  # target channels for each category
    crypto: "@crypto_target"
    news: "@news_target"
```

Each category in the configuration can contain:
- List of source channels (using @ or channel IDs)
- Target channel in target_channels section

## Usage

Run the scraper:
```bash
python -m tscraper
```

The scraper will:
1. Connect to Telegram using your API credentials
2. Monitor all configured source channels
3. Forward messages to appropriate target channels based on the configuration
4. Automatically reconnect if connection is lost
5. Provide health check endpoint at http://localhost:8000/health

## Features in Detail

### Media Handling
- Supports forwarding of single messages
- Correctly handles media albums (multiple photos/videos)
- Preserves message order in media groups

### Error Handling
- Automatic reconnection with exponential backoff
- Comprehensive logging
- Graceful handling of network issues

### Health Checks
- HTTP endpoint for monitoring service health
- Returns service uptime and connection status

## Error Codes and Troubleshooting

Common issues and solutions:

1. `ConfigError: Config file not found`
   - Ensure config.yaml exists in the working directory
   - Check CONFIG_PATH environment variable

2. `ConfigError: Missing target_channels in config`
   - Verify your config.yaml includes target_channels section
   - Check yaml formatting

3. Connection errors
   - Verify your internet connection
   - Check API credentials
   - Ensure you're not rate limited by Telegram

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
