"""Vercel serverless function for Telegram webhook."""

import json
import os
import sys
from pathlib import Path

from telegram import Update, Bot
from telegram.error import TelegramError
from typing import Set


# Inline SubscriberManager (copied from src/subscribers.py)
class SubscriberManager:
    """Manages the list of subscribers for notifications."""

    def __init__(self, storage_file: str = "/tmp/subscribers.json"):
        """Initialize subscriber manager with /tmp storage for Vercel."""
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(exist_ok=True)
        self._subscribers: Set[int] = self._load_subscribers()

    def _load_subscribers(self) -> Set[int]:
        """Load subscribers from storage file."""
        if not self.storage_file.exists():
            return set()
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('subscribers', []))
        except (json.JSONDecodeError, OSError):
            return set()

    def _save_subscribers(self) -> None:
        """Save subscribers to storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {'subscribers': list(self._subscribers)},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except OSError:
            pass

    def add_subscriber(self, chat_id: int) -> bool:
        """Add a new subscriber."""
        if chat_id in self._subscribers:
            return False
        self._subscribers.add(chat_id)
        self._save_subscribers()
        return True

    def remove_subscriber(self, chat_id: int) -> bool:
        """Remove a subscriber."""
        if chat_id not in self._subscribers:
            return False
        self._subscribers.remove(chat_id)
        self._save_subscribers()
        return True

    def is_subscribed(self, chat_id: int) -> bool:
        """Check if a chat ID is subscribed."""
        return chat_id in self._subscribers

    def get_subscriber_count(self) -> int:
        """Get the number of subscribers."""
        return len(self._subscribers)


# Initialize bot and subscriber manager
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

bot = Bot(token=BOT_TOKEN)
subscriber_manager = SubscriberManager()


async def handle_start_command(chat_id: int, user_first_name: str) -> str:
    """
    Handle /start command.

    Args:
        chat_id: User's chat ID
        user_first_name: User's first name

    Returns:
        Message to send
    """
    if subscriber_manager.add_subscriber(chat_id):
        return (
            f"🎬 Welcome, {user_first_name}!\n\n"
            "You're now subscribed to Meisengeige program updates.\n\n"
            "You'll receive notifications when:\n"
            "✨ New films are added\n"
            "🔄 Film showtimes are updated\n"
            "❌ Films are removed\n\n"
            "Commands:\n"
            "/stop - Unsubscribe from notifications\n"
            "/status - Check your subscription status"
        )
    else:
        return (
            f"👋 Hi {user_first_name}!\n\n"
            "You're already subscribed to notifications.\n\n"
            "Use /status to check your subscription or /stop to unsubscribe."
        )


async def handle_stop_command(chat_id: int) -> str:
    """
    Handle /stop command.

    Args:
        chat_id: User's chat ID

    Returns:
        Message to send
    """
    if subscriber_manager.remove_subscriber(chat_id):
        return (
            "👋 You've been unsubscribed from Meisengeige notifications.\n\n"
            "You can subscribe again anytime with /start"
        )
    else:
        return (
            "You're not currently subscribed.\n\n"
            "Use /start to subscribe to notifications."
        )


async def handle_status_command(chat_id: int) -> str:
    """
    Handle /status command.

    Args:
        chat_id: User's chat ID

    Returns:
        Message to send (with HTML formatting)
    """
    is_subscribed = subscriber_manager.is_subscribed(chat_id)
    total_subscribers = subscriber_manager.get_subscriber_count()

    if is_subscribed:
        return (
            "✅ <b>Subscription Active</b>\n\n"
            f"You're receiving Meisengeige program updates.\n"
            f"Total subscribers: {total_subscribers}\n\n"
            "Commands:\n"
            "/stop - Unsubscribe"
        )
    else:
        return (
            "❌ <b>Not Subscribed</b>\n\n"
            "You're not receiving notifications.\n\n"
            "Use /start to subscribe."
        )


async def process_update(update_data: dict) -> dict:
    """
    Process incoming Telegram update.

    Args:
        update_data: JSON data from Telegram

    Returns:
        Response dict
    """
    try:
        update = Update.de_json(update_data, bot)

        if not update.message or not update.message.text:
            return {'status': 'ignored', 'reason': 'no text message'}

        chat_id = update.message.chat.id
        text = update.message.text.strip()
        user_first_name = update.message.from_user.first_name or "there"

        # Route command
        response_text = None
        parse_mode = None

        if text == '/start':
            response_text = await handle_start_command(chat_id, user_first_name)
        elif text == '/stop':
            response_text = await handle_stop_command(chat_id)
        elif text == '/status':
            response_text = await handle_status_command(chat_id)
            parse_mode = 'HTML'
        else:
            # Unknown command
            response_text = (
                "Unknown command. Available commands:\n"
                "/start - Subscribe to notifications\n"
                "/stop - Unsubscribe\n"
                "/status - Check subscription status"
            )

        # Send response
        if response_text:
            await bot.send_message(
                chat_id=chat_id,
                text=response_text,
                parse_mode=parse_mode
            )

        return {'status': 'success', 'command': text}

    except TelegramError as e:
        print(f"Telegram error: {e}")
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        print(f"Error processing update: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'error': str(e)}


# Vercel serverless function handler
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Main handler for Vercel serverless function."""

    def do_GET(self):
        """Handle GET requests (health check)."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(
            json.dumps({'status': 'healthy', 'bot': 'meisengeige'}).encode()
        )

    def do_POST(self):
        """Handle POST requests (webhook)."""
        try:
            # Read body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            if not data:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    json.dumps({'status': 'error', 'message': 'No data'}).encode()
                )
                return

            # Process update
            import asyncio
            result = asyncio.run(process_update(data))

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            print(f"Handler error: {e}")
            import traceback
            traceback.print_exc()

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(
                json.dumps({'status': 'error', 'message': str(e)}).encode()
            )
