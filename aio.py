import logging
from logging.handlers import RotatingFileHandler

from os import path as os_path
from os import makedirs as os_makedirs

from telegram import Update, Message
from telegram.ext import (
    Application,
    PreCheckoutQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    Updater
)

from specs import specs

from database import create_tasks_db
from handlers import start, task_complete, get_link
from payment import start_without_shipping_callback, precheckout_callback, successful_payment_callback

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{specs.logs_path}{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def db_init(application: Application):
    """Create db"""

    await create_tasks_db(users=True, tasks=True)


def create_directory(db_path: str = f'{specs.db_path}', image_path: str = f'{specs.image_path}') -> None:
    """Check and make directories"""

    if not os_path.exists(db_path):
        os_makedirs(db_path)
        logger.info(f'Directory {db_path} successfully created')
    else:
        logger.info(f'Directory {db_path} already exists')
    if not os_path.exists(image_path):
        os_makedirs(image_path)
        logger.info(f'Directory {image_path} successfully created')
    else:
        logger.info(f'Directory {image_path} already exists')


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder()
    application = application.token(specs.token)
    application = application.post_init(post_init=db_init)
    application = application.build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, task_complete))
    application.add_handler(MessageHandler(filters.Text(['Получить ссылку']), get_link))

    # Payment handlers
    application.add_handler(CommandHandler("pay", start_without_shipping_callback))
    # Pre-checkout handler for verifying payment details.
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    # Handler for successful payment. Notify the user that the payment was successful.
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
