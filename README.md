# Nürnberg Kino Bot

Cinema program monitoring bot for Nuremberg with Telegram notifications.

## Features

- **Multi-source monitoring**: Meisengeige (Cinecitta) and Kinderkino (Filmhaus)
- **Daily automated checks** via GitHub Actions
- **Independent subscriptions**: Users can subscribe to specific cinema sources
- **Rich film information**: Posters, descriptions, showtimes, FSK ratings
- **Multi-language support**: Russian, German, English
- **Interactive bot commands** with inline keyboards
- **State persistence** to avoid duplicate notifications

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

Run the monitoring script:
```bash
poetry run python -m src.main
```

Run the bot locally:
```bash
poetry run python -m src.run_bot
```

## Bot Commands

- `/films` - View current cinema programs
- `/sources` - Manage cinema source subscriptions
- `/start` - Subscribe to notifications
- `/status` - Check subscription status
- `/language` - Change bot language
- `/stop` - Unsubscribe from notifications

## GitHub Actions

The bot runs daily at 9:00 AM UTC via GitHub Actions. Configure secrets in repository settings:
- `TELEGRAM_BOT_TOKEN`
- `MONGODB_URI` (for persistent storage)

## License

MIT
