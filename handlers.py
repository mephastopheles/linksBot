from telegram import Update
from telegram.ext import (

    ContextTypes,

)


import logging
from logging.handlers import RotatingFileHandler

import re
from random import choices as random_choices


from keyboards import start_keyboard, account_keyboard, send_link_keyboard
from database import insert_tasks_db, insert_users_db, update_users_db, select_users_db, update_time_weight_links, select_links
from specs import specs

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
        await update_time_weight_links()
        user_id = update.message.from_user.id
        rows = await select_links(user_id=user_id)
        links = []
        weights = []
        for row in rows:
            links.append(row[0])
            weights.append(row[1])

        link = random_choices(population=links, weights=weights)[0]

        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Задача: {link}',
            reply_markup=start_keyboard
        )

        # обновить временные веса у ссылок
        # выгрузить все по условию ссылки и веса
        # выбрать случайно ссылку с приоритетом по весам

        logger.info(msg=f'Succeed to get link')
    except Exception as e:
        logger.exception(msg=f'Failed to get link: {e}')


async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Отправь ссылку с небольшим описанием того, что нужно сделать в форме.',
            reply_markup=send_link_keyboard
        )
        logger.info(msg=f'Succeed to send link')
    except Exception as e:
        logger.exception(msg=f'Failed to send link: {e}')


async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pattern = r'<<<((https?://)[\s\S]*?)>>>'
    message = update.message.text

    match = re.search(pattern, message)
    if not match:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Ссылка не найдена',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'Rejected to add link by link not found')
        return

    try:
        user_id = update.message.from_user.id
        balance = await select_users_db(user_id=user_id, column=0)
        if balance > specs.price:
            await update_users_db(user_id=user_id, balance=-specs.price)

            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Ссылка добавлена.',
                reply_markup=start_keyboard
            )
            logger.info(msg=f'Succeed to add link')

        else:
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Недостаточно денег на счёте. Баланс: {balance}',
                reply_markup=start_keyboard
            )
            logger.info(msg=f'Rejected to add link by low balance')
            return


    except Exception as e:
        logger.exception(msg=f'Failed to add link: {e}')


async def personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    try:
        balance, balance_hl = await select_users_db(user_id=user_id, column=-1)
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Ваш id: {user_id}'
                 f'Баланс: у вас {balance} рублей\n'
                 f'ХЛ: у вас {balance_hl} хлбаллов ',
            reply_markup=account_keyboard
        )
        logger.info(msg=f'Succeed check personal account')
    except Exception as e:
        logger.exception(msg=f'Failed to check personal account: {e}')


if __name__ == '__main__':
    pass
