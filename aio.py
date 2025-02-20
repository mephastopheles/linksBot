import logging

from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.ext import (
    Application,
    PreCheckoutQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,

)

from specs import specs
from database import create_db
from handlers import (start, task_complete,
                      personal_account, back,
                      get_link, add_link, send_link)
from payment import start_without_shipping_callback, precheckout_callback, successful_payment_callback

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{specs.logs_path}{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))

# states
from specs import states


async def db_init(application: Application):
    """Create db"""

    await create_db(users=True, tasks=True, links=True)


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder()
    application = application.token(specs.token)
    application = application.post_init(post_init=db_init)
    application = application.build()

    # Add handlers
    # application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, task_complete))
    # application.add_handler(MessageHandler(filters.Text(['Получить ссылку']), get_link))
    # application.add_handler(MessageHandler(filters.Text(['Отправить ссылку']), send_link))
    # application.add_handler(MessageHandler(filters.TEXT, add_link))
    # application.add_handler(MessageHandler(filters.Text(['Личный кабинет']), personal_account))

    # Payment handlers
    application.add_handler(CommandHandler("pay", start_without_shipping_callback))
    # Pre-checkout handler for verifying payment details.
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    # Handler for successful payment. Notify the user that the payment was successful.
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            states.START: [
                MessageHandler(filters.Text(['Получить ссылку']), get_link),
                MessageHandler(filters.Text(['Отправить ссылку']), send_link),
                MessageHandler(filters.Text(['Личный кабинет']), personal_account)
            ],
            states.ACCOUNT: [
                MessageHandler(filters.Text(['Пополнить баланс']), start_without_shipping_callback),
                PreCheckoutQueryHandler(precheckout_callback),
                MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback),
                MessageHandler(filters.Text(['Назад']), back)
            ],
            states.SEND_LINK: [
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.TEXT, add_link),

            ],
            states.GET_LINK: [
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.PHOTO, task_complete)

            ]


        },
        fallbacks=[],

    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
