from telegram import Update
from telegram.ext import (

    ContextTypes,

)

import logging
from logging.handlers import RotatingFileHandler

import re
from random import choices as random_choices

from keyboards import start_keyboard, account_keyboard, back_keyboard, confirm_add_keyboard
from database import insert_tasks_db, insert_users_db, update_users_db, select_users_db, update_time_weight_links, \
    select_tasks, insert_links_db, select_links, insert_link_transitions_db, select_pays

from specs import specs, states

logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        user_id = update.message.from_user.id
        await insert_users_db(user_id=user_id,balance_hl=10,balance=5000)
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text='Привет, я бот для ссылок!',
            reply_markup=start_keyboard
        )
        logger.info(msg=f'Succeed to start')

        return states.START
    except Exception as e:
        logger.exception(msg=f'Failed to start: {e}')


import openpyxl


async def task_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get screenshot of completed task and add points"""

    user_id = update.message.from_user.id

    photo_id = update.message.photo[-1].file_id
    try:
        new_photo = await context.bot.get_file(file_id=photo_id)
        await new_photo.download_to_drive(f'images/{photo_id}.jpg')
    except Exception as e:
        logger.exception(msg=f'Failed to download photo: {e}')

    try:
        task = await select_users_db(user_id=user_id, column=2)
        if task:

            await update_users_db(user_id=user_id, balance_hl=1, task='')
            balance_hl = await select_users_db(user_id=user_id, column=1)
            await insert_tasks_db(user_id=user_id, task=task, photo_id=photo_id)
            count_pays = await select_pays(user_id=user_id)
            if not count_pays:
                count_pays = 0
            try:
                wb = openpyxl.load_workbook('excel/db.xlsx')
            except FileNotFoundError:
                wb = openpyxl.Workbook()
            ws = wb.worksheets[0]
            index = ws.max_row + 1
            ws.cell(row=index, column=1, value=f'{user_id}')
            ws.cell(row=index, column=2, value=f'{task}')
            ws.cell(row=index, column=3, value=f'{photo_id}')

            ws.cell(row=index, column=4, value=f'{count_pays}')
            wb.save('excel/db.xlsx')
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'{update.message.from_user.username} получили 1 ХЛБалл! Ваш баланс: {balance_hl}',
                reply_markup=back_keyboard
            )

            logger.info(msg=f'Succeed to task complete 0')
            return states.GET_LINK

        else:
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'У тебя нет задания',
                reply_markup=start_keyboard
            )
            logger.warning(msg=f'Rejected to task complete by empty task')
            return states.START
    except Exception as e:
        logger.exception(msg=f'Failed to task complete: {e}')


async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update_time_weight_links()
        user_id = update.message.from_user.id
        if await select_users_db(user_id=user_id, column=2):
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Сначала выполни текущее задание',
                reply_markup=back_keyboard
            )
            return states.GET_LINK

        rows = await select_tasks(user_id=user_id)
        links = []
        weights = []
        if rows:
            for row in rows:
                links.append(row[0])
                weights.append(row[1] + 1)
        else:
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Пока что нет задач',
                reply_markup=start_keyboard
            )
            return states.START

        task = random_choices(population=links, weights=weights)[0]

        await update_users_db(user_id=user_id, task=task)
        link_id = await select_links(user_id=user_id, link=task)
        link_id = link_id[0]
        await insert_link_transitions_db(link_id=link_id)
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Задача: {task}',
            reply_markup=back_keyboard
        )

        logger.info(msg=f'Succeed to get link')
        return states.GET_LINK
    except Exception as e:
        logger.exception(msg=f'Failed to get link: {e}')


async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Выбери оплату',
            reply_markup=confirm_add_keyboard
        )

        logger.info(msg=f'Succeed to send link')
        return states.SEND_LINK
    except Exception as e:
        logger.exception(msg=f'Failed to send link: {e}')


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = update.message.text
        user_id = update.message.from_user.id
        if message == 'Добавить за 50 рублей и 10 ХЛБаллов':
            specs.choose_cost.update({user_id: 1})
        else:
            specs.choose_cost.update({user_id: 2})

        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Отправь ссылку с небольшим описанием того, что нужно сделать в форме: <<<тут ссылка и описание>>>',
            reply_markup=back_keyboard
        )

        logger.exception(msg=f'Succeed to comfirm_add')
    except Exception as e:
        logger.exception(msg=f'Failed to comfirm_add: {e}')


async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pattern = r'((https?://)[\s\S]*?)'
    message = update.message.text

    match = re.search(pattern, message)

    if not match:
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Ссылка не найдена'
        )
        logger.info(msg=f'Rejected to add link by link not found')
        return

    try:
        user_id = update.message.from_user.id
        balance, balance_hl, _ = await select_users_db(user_id=user_id, column=-1)
        if specs.choose_cost.get(user_id) == 1 and balance >= specs.price[0] and balance_hl >= specs.price_hl[0]:
            await update_users_db(user_id=user_id, balance=-specs.price[0], balance_hl=-specs.price_hl[0])
            _start, _end = match.span()
            link = f'{message[_start:_end]}'
            await insert_links_db(user_id=user_id, link=link)

            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Ссылка добавлена',
                reply_markup=start_keyboard
            )
            logger.info(msg=f'Succeed to add link')
            return states.START
        elif specs.choose_cost.get(user_id) == 2 and balance >= specs.price[1] and balance_hl >= specs.price_hl[1]:
            await update_users_db(user_id=user_id, balance=-specs.price[1], balance_hl=-specs.price_hl[1])
            _start, _end = match.span()
            link = f'{message[_start:_end]}'
            await insert_links_db(user_id=user_id, link=link)

            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Ссылка добавлена',
                reply_markup=start_keyboard
            )
            logger.info(msg=f'Succeed to add link')
            return states.START

        else:
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=f'Недостаточно денег на счёте. Баланс: {balance}',
                reply_markup=start_keyboard
            )
            logger.info(msg=f'Rejected to add link by low balance')
            return states.START

    except Exception as e:
        logger.exception(msg=f'Failed to add link: {e}')


async def personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    try:
        balance, balance_hl, task = await select_users_db(user_id=user_id, column=-1)

        if task is None:
            task = 'нет'
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text=f'Ваш id: {user_id}\n'
                 f'Баланс: у вас {balance // 100}.{balance % 100} рублей\n'
                 f'ХЛ: у вас {balance_hl} ХЛБаллов\n'
                 f'Задание для выполнения: {task}\n',
            reply_markup=account_keyboard
        )
        links = await select_links(user_id=user_id)
        if links:
            answer = f'{links[0][0]}'
            for link in links[1::]:
                answer = f'{answer} ||| {link[0]}'
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id,
                text=answer,
                reply_markup=account_keyboard
            )
        logger.info(msg=f'Succeed check personal account')
        return states.ACCOUNT
    except Exception as e:
        logger.exception(msg=f'Failed to check personal account: {e}')


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        specs.choose_cost.pop(user_id, 0)
        await update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text='Вернулись в меню',
            reply_markup=start_keyboard
        )

        logger.info(msg=f'Succeed to back')
        return states.START
    except Exception as e:
        logger.exception(msg=f'Failed to back: {e}')


if __name__ == '__main__':
    pass
