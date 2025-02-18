from telegram import Update
from telegram.ext import (

    ContextTypes,

)
import logging
from logging.handlers import RotatingFileHandler

from keyboards import start_keyboard

from database import insert_tasks_db

logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text='Привет, я бот для ссылок!',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'command start')
    except Exception as e:
        logger.exception(msg=f'Failed to start, {e}')


async def task_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get screenshot of completed task and add points"""

    username = update.message.from_user.username
    link = 'xui'
    photo_id = update.message.photo[-1].file_id
    try:
        await insert_tasks_db(username=username, link=link, photo_id=photo_id)
        await insert_tasks_db()
        balance = 4
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'{update.message.from_user.username} получили 1 хлбалл! Ваш баланс: {balance}',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'function task complete')
    except Exception as e:
        logger.exception(msg=f'Failed to task complete, {e}')




async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        reply_to_message_id=update.message.message_id,
        text=f'Отправь ссылку с небольшим описанием того, что нужно сделать',
        reply_markup=start_keyboard
    )
