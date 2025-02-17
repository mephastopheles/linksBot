import logging
from os import getenv
from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,

    MessageHandler,
    filters,
)
from handlers import start, task_complete

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN = getenv('LINKS_BOT_TOKEN')
TOKEN = '7808848463:AAGSecDwo25vqu-Y2VdR0AblCh-L8RHNJ6k'


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, task_complete))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
