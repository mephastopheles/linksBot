from telegram import Update
from telegram.ext import (

    ContextTypes,

)

from keyboards import start_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    await update.message.reply_text(
        reply_to_message_id=update.message.message_id,
        text='Привет, я бот для ссылок!',
        reply_markup=start_keyboard
    )


async def task_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get screenshot of completed task and add points"""

    balance = 1
    print(update.message.caption)
    print(update.message.photo[-1].file_id)
    await update.message.reply_text(
        reply_to_message_id=update.message.message_id,
        text=f'{update.message.from_user.username} получили 1 хлбалл! Ваш баланс: {balance}',
        reply_markup=start_keyboard
    )

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        reply_to_message_id=update.message.message_id,
        text=f'Отправь ссылку с небольшим описанием того, что нужно сделать',
        reply_markup=start_keyboard
    )

