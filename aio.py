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

from database import create_db, create_triggers_db, ban_table
from handlers import (start, first_start,
                      task_complete,
                      personal_account, back,
                      account_payment, account_send_invoice, account_invoice_confirm,
                      to_ban,
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
    await ban_table(user_id=None)

    rows = await ban_table(user_id=0)
    if rows:
        specs.filter.chat_ids = set([i[0] for i in rows])



def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder()
    application = application.token(specs.token)
    application = application.post_init(post_init=db_init)
    application = application.build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='start', callback=start, filters=~specs.filter)],
        states={
            states.START: [
                CommandHandler(command='start', callback=start, filters=~specs.filter),
                MessageHandler(filters=filters.Text(
                    ['Шаг 1', 'Шаг 2', 'Шаг 3', 'Шаг 4', 'Шаг 5', 'Шаг 6', 'Шаг 7']) & ~specs.filter,
                               callback=first_start),
                MessageHandler(filters=filters.Text(['Получить ссылку']) & ~specs.filter,
                               callback=get_link),
                MessageHandler(filters=filters.Text(['Отправить ссылку']) & ~specs.filter,
                               callback=send_link),
                MessageHandler(filters=filters.Text(['Личный кабинет']) & ~specs.filter,
                               callback=personal_account),

            ],
            states.ACCOUNT: [
                CommandHandler(command='start', callback=start,
                               filters=~specs.filter),
                MessageHandler(filters=filters.Text(['Назад']) & ~specs.filter,
                               callback=back),
                MessageHandler(filters=filters.Text(['Пополнить баланс']) & ~specs.filter,
                               callback=account_payment),
                MessageHandler(filters=~specs.filter, callback=to_ban)

            ],
            states.ACCOUNT_ADD_BALANCE: [
                MessageHandler(filters=filters.Text(['Назад']) & ~specs.filter, callback=back),
                MessageHandler(filters=filters.Text([account_add_balance.keyboard[0][0].text,
                                                     account_add_balance.keyboard[1][0].text,
                                                     account_add_balance.keyboard[2][0].text,
                                                     account_add_balance.keyboard[3][0].text,
                                                     ]) & ~specs.filter,
                               callback=account_send_invoice),

            ],

            states.ACCOUNT_CONFIRM_ADD: [
                MessageHandler(filters=filters.Text(['Назад']) & ~specs.filter,
                               callback=back),
                MessageHandler(filters=filters.Text(['Оплачено']) & ~specs.filter,
                               callback=account_invoice_confirm)

            ],

            states.SEND_LINK: [
                CommandHandler(command='start', callback=start, filters=~specs.filter),
                MessageHandler(filters=filters.Text(['Назад']) & ~specs.filter, callback=back),
                MessageHandler(filters=filters.Text(['Добавить за 50 рублей и 10 ХЛБаллов',
                                                     'Добавить за 10 рублей и 100 ХЛБаллов']) & ~specs.filter,
                callback=confirm_add),

            ],
            states.ACCEPT_LINK: [
                MessageHandler(filters=filters.Text(['Назад']), callback=back),
                MessageHandler(filters=filters.TEXT, callback=add_link),

            ],

            states.GET_LINK: [
                CommandHandler(command='start', callback=start, filters=~specs.filter),
                MessageHandler(filters=filters.Text(['Назад']) & ~specs.filter, callback=back),
                MessageHandler(filters=filters.PHOTO & ~specs.filter, callback=task_complete)

            ]

        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
