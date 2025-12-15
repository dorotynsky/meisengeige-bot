"""Telegram bot command handlers."""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .subscribers import SubscriberManager


class MeisengeigeBotCommands:
    """Handles Telegram bot commands for subscription management."""

    def __init__(self, bot_token: str = None):
        """
        Initialize bot command handler.

        Args:
            bot_token: Telegram bot token (from BotFather)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not provided")

        self.subscriber_manager = SubscriberManager()
        self.application = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command - subscribe to notifications.

        Args:
            update: Telegram update object
            context: Bot context
        """
        chat_id = update.effective_chat.id
        user = update.effective_user

        if self.subscriber_manager.add_subscriber(chat_id):
            message = (
                f"🎬 Welcome, {user.first_name}!\n\n"
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
            message = (
                f"👋 Hi {user.first_name}!\n\n"
                "You're already subscribed to notifications.\n\n"
                "Use /status to check your subscription or /stop to unsubscribe."
            )

        await update.message.reply_text(message)

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /stop command - unsubscribe from notifications.

        Args:
            update: Telegram update object
            context: Bot context
        """
        chat_id = update.effective_chat.id

        if self.subscriber_manager.remove_subscriber(chat_id):
            message = (
                "👋 You've been unsubscribed from Meisengeige notifications.\n\n"
                "You can subscribe again anytime with /start"
            )
        else:
            message = (
                "You're not currently subscribed.\n\n"
                "Use /start to subscribe to notifications."
            )

        await update.message.reply_text(message)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /status command - show subscription status.

        Args:
            update: Telegram update object
            context: Bot context
        """
        chat_id = update.effective_chat.id
        is_subscribed = self.subscriber_manager.is_subscribed(chat_id)
        total_subscribers = self.subscriber_manager.get_subscriber_count()

        if is_subscribed:
            message = (
                "✅ <b>Subscription Active</b>\n\n"
                f"You're receiving Meisengeige program updates.\n"
                f"Total subscribers: {total_subscribers}\n\n"
                "Commands:\n"
                "/stop - Unsubscribe"
            )
        else:
            message = (
                "❌ <b>Not Subscribed</b>\n\n"
                "You're not receiving notifications.\n\n"
                "Use /start to subscribe."
            )

        await update.message.reply_text(message, parse_mode='HTML')

    def setup_handlers(self) -> Application:
        """
        Set up command handlers and return application.

        Returns:
            Configured Application instance
        """
        self.application = Application.builder().token(self.bot_token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("status", self.status_command))

        return self.application

    async def run(self) -> None:
        """Run the bot in polling mode."""
        if not self.application:
            self.setup_handlers()

        print("🤖 Bot started. Press Ctrl+C to stop.")

        # Initialize and start
        async with self.application:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            # Keep running
            try:
                import asyncio
                await asyncio.Event().wait()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
