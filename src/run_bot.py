"""Run Telegram bot to handle subscription commands."""

import asyncio
import sys
from dotenv import load_dotenv

from .bot_commands import MeisengeigeBotCommands

# Load environment variables
load_dotenv()


async def main() -> int:
    """
    Run the Telegram bot in polling mode.

    Returns:
        Exit code
    """
    try:
        print("🤖 Starting Meisengeige subscription bot...")
        print("Bot will listen for /start, /stop, and /status commands")
        print("Press Ctrl+C to stop\n")

        bot = MeisengeigeBotCommands()
        await bot.run()

        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error running bot: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
