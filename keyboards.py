from telegram import ReplyKeyboardMarkup

# keyboard after start command
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Получить ссылку"], ["Отправить ссылку"], ["Личный кабинет"]],
    one_time_keyboard=True,
    is_persistent=False,
)

account_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Получить ссылку"], ["Отправить ссылку"]],
    one_time_keyboard=True,
    is_persistent=False,
)

send_link_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Добавить ссылку"]],
    one_time_keyboard=True,
    is_persistent=False,
)


