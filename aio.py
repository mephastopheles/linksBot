import logging

from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    JobQueue

)

# specification
from specs import specs
# states
from specs import states

from database import create_db, create_triggers_db
from handlers import (start, task_complete,
                      personal_account,back,
                      account_payment, account_send_invoice, account_invoice_confirm,

                      get_link, add_link, send_link, confirm_add)
from keyboards import account_add_balance


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

    await create_db(users=True, tasks=True, links=True)
    await create_triggers_db()


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder()
    application = application.token(specs.token)
    application = application.post_init(post_init=db_init)
    application = application.build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            states.START: [
                CommandHandler('start', start),
                MessageHandler(filters.Text(['Получить ссылку']), get_link),
                MessageHandler(filters.Text(['Отправить ссылку']), send_link),
                MessageHandler(filters.Text(['Личный кабинет']), personal_account),

            ],
            states.ACCOUNT: [
                CommandHandler('start', start),
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.Text(['Пополнить баланс']), account_payment),

                #
                # PreCheckoutQueryHandler(precheckout_callback),
                # MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback),

            ],
            states.ACCOUNT_ADD_BALANCE: [
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.Text([account_add_balance.keyboard[0][0].text,
                                             account_add_balance.keyboard[1][0].text,
                                             account_add_balance.keyboard[2][0].text,
                                             account_add_balance.keyboard[3][0].text,
                                             ]), account_send_invoice),


            ],

            states.ACCOUNT_CONFIRM_ADD: [
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.Text(['Оплачено']), account_invoice_confirm)


            ],

            states.SEND_LINK: [
                CommandHandler('start', start),
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.Text(['Добавить за 50 рублей и 10 ХЛБаллов',
                                             'Добавить за 10 рублей и 100 ХЛБаллов']), confirm_add),

            ],
            states.ACCEPT_LINK: [
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.TEXT, add_link),

            ],

            states.GET_LINK: [
                CommandHandler('start', start),
                MessageHandler(filters.Text(['Назад']), back),
                MessageHandler(filters.PHOTO, task_complete)

            ]

        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
