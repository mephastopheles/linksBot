from telegram import Update
from telegram.ext import (

    ContextTypes,

)
import logging
from logging.handlers import RotatingFileHandler

from keyboards import start_keyboard

from database import insert_tasks_db, insert_users_db, update_users_db, select_users_db

logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        user_id = update.message.from_user.id
        await insert_users_db(user_id=user_id)
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text='Привет, я бот для ссылок!',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'Succeed to start')
    except Exception as e:
        logger.exception(msg=f'Failed to start: {e}')


async def task_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get screenshot of completed task and add points"""

    user_id = update.message.from_user.id
    link = 'xui'
    photo_id = update.message.photo[-1].file_id
    try:
        new_photo = await context.bot.get_file(file_id=photo_id)
        await new_photo.download_to_drive(f'images/{photo_id}.jpg')
    except Exception as e:
        logger.exception(msg=f'Failed to download photo: {e}')

    try:
        await update_users_db(user_id=user_id, balance_hl=1)
        balance_hl = await select_users_db(user_id=user_id, column=1)

        await insert_tasks_db(user_id=user_id, link=link, photo_id=photo_id)

        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'{update.message.from_user.username} получили 1 хлбалл! Ваш баланс: {balance_hl}',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'Succeed to task complete')
    except Exception as e:
        logger.exception(msg=f'Failed to task complete: {e}')


async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Отправь ссылку с небольшим описанием того, что нужно сделать',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'Succeed to get link')
    except Exception as e:
        logger.exception(msg=f'Failed to get link: {e}')



if __name__ == '__main__':
    pass
