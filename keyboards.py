from telegram import ReplyKeyboardMarkup

# keyboard after start command
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Получить ссылку"], ["Отправить ссылку"], ["Личный кабинет"]],
    one_time_keyboard=True,
    is_persistent=False,
)

account_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Пополнить баланс"], ["Назад"]],
    one_time_keyboard=True,
    is_persistent=False,
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Назад"]],
    one_time_keyboard=True,
    is_persistent=False,
)

confirm_add_keyboard = ReplyKeyboardMarkup(
    keyboard=[['Добавить за 50 рублей и 10 ХЛБаллов'],['Добавить за 10 рублей и 100 ХЛБаллов'],['Назад']],
    one_time_keyboard=True,
    is_persistent=False,
)

