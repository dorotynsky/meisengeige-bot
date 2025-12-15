"""Vercel serverless function for Telegram webhook."""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update, Bot
from telegram.error import TelegramError

from src.subscribers import SubscriberManager


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
def handler(request):
    """
    Main handler for Vercel serverless function.

    Args:
        request: Vercel request object

    Returns:
        Response tuple (body, status_code, headers)
    """
    # Handle health check
    if request.method == 'GET':
        return (
            json.dumps({'status': 'healthy', 'bot': 'meisengeige'}),
            200,
            {'Content-Type': 'application/json'}
        )

    # Handle webhook POST
    if request.method == 'POST':
        try:
            # Get JSON data
            if hasattr(request, 'get_json'):
                data = request.get_json()
            elif hasattr(request, 'json'):
                data = request.json
            else:
                # Try to parse body
                import json as json_lib
                data = json_lib.loads(request.body)

            if not data:
                return (
                    json.dumps({'status': 'error', 'message': 'No data'}),
                    400,
                    {'Content-Type': 'application/json'}
                )

            # Process update (synchronously wrap async)
            import asyncio
            result = asyncio.run(process_update(data))

            return (
                json.dumps(result),
                200,
                {'Content-Type': 'application/json'}
            )

        except Exception as e:
            print(f"Handler error: {e}")
            import traceback
            traceback.print_exc()
            return (
                json.dumps({'status': 'error', 'message': str(e)}),
                500,
                {'Content-Type': 'application/json'}
            )

    # Method not allowed
    return (
        json.dumps({'status': 'error', 'message': 'Method not allowed'}),
        405,
        {'Content-Type': 'application/json'}
    )
