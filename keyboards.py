from telegram import ReplyKeyboardMarkup

# keyboard after start command
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Получить ссылку"], ["Отправить ссылку"], ["Личный кабинет"]],
    one_time_keyboard=True,
    is_persistent=True,
    input_field_placeholder="Boy or Girl?"
)
