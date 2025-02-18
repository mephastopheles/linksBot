import logging
from logging.handlers import RotatingFileHandler
from asyncio import run

from os import getenv
from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    Updater
)
from handlers import start, task_complete

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))

TOKEN = getenv('LINKS_BOT_TOKEN')
TOKEN = '7808848463:AAGSecDwo25vqu-Y2VdR0AblCh-L8RHNJ6k'  # for test ONLY

from database import create_tasks_db


async def db_init(application: Application):

    await create_tasks_db()
    await application.initialize()





def main() -> None:
    """Run the bot."""

    # create_tasks_db()

    # Create the Application and pass it your bot's token.

    application = Application.builder()
    application = application.token(TOKEN)
    application = application.post_init(post_init=db_init)
    application = application.build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, task_complete))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)




if __name__ == "__main__":
    main()
