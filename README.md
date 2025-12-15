# Meisengeige Bot

Daily monitoring bot for Meisengeige events at Cinecitta with Telegram notifications.

## Features

- Daily automated check of https://www.cinecitta.de/programm/meisengeige/
- Detects new events and sends Telegram notifications
- State persistence to avoid duplicate notifications
- Runs automatically via GitHub Actions

## Setup

### Prerequisites

- Python 3.14+
- Poetry
- Telegram Bot Token

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   mise install
   poetry install
   ```

3. Set up environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID

### Local Development

```bash
mise exec -- poetry run python src/check_meisengeige.py
```

## GitHub Actions

The bot runs daily at 10:00 AM UTC via GitHub Actions. Configure secrets in repository settings:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## License

MIT
