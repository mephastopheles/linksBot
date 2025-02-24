import logging
from logging.handlers import RotatingFileHandler


from time import time
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

from specs import specs, states
from database import update_users_db
from keyboards import account_keyboard, start_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{specs.logs_path}{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def start_without_shipping_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice"""
    chat_id = update.message.chat_id
    title = "Пополнение баланса"
    description = "Пополнение баланса для выгрузки ссылок"
    # Unique payload to identify this payment request as being from your bot
    user_id = update.message.from_user.id
    payload = f'{user_id}{time()}'
    specs.transaction_id.update({user_id: payload})
    currency = specs.currency
    # Price in rub
    price = specs.price[0]
    # Convert price to cents from dollars.
    prices = [LabeledPrice("Стоимость", price)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id=chat_id, title=title, description=description, payload=payload,
        provider_token=specs.payment_token, currency=currency, prices=prices
    )
    return states.ACCOUNT


# After (optional) shipping, process the pre-checkout step
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds to the PreCheckoutQuery as the final confirmation for checkout."""
    query = update.pre_checkout_query
    user_id = query.from_user.id
    payload = specs.transaction_id.get(user_id, None)
    # Verify if the payload matches, ensure it's from your bot
    if query.invoice_payload != payload:
        # If not, respond with an error
        await query.answer(ok=False, error_message="Что-то пошло не так...")
        specs.transaction_id.pop(user_id, None)
        return states.ACCOUNT
    else:
        balance: int = query.total_amount
        await update_users_db(user_id=query.from_user.id, balance=balance)
        await query.answer(ok=True)
        specs.transaction_id.pop(user_id, None)
        return states.ACCOUNT



# Final callback after successful payment
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Acknowledges successful payment and thanks the user."""

    await update.message.reply_text(text="Спасибо за оплату",
                                    reply_to_message_id=update.message.message_id,
                                    reply_markup=account_keyboard)
    context.user_data['state'] = states.START
    return states.ACCOUNT


if __name__ == '__main__':
    pass
