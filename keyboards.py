from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# keyboard after start command
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Получить ссылку"],
              ["Отправить ссылку"],
              ["Личный кабинет"]],
    one_time_keyboard=True,
    is_persistent=False)


def first_start_keyboard(step: int = 1):

    return ReplyKeyboardMarkup(keyboard=[[f"Шаг {step}"]], one_time_keyboard=True, is_persistent=False)


# keyboard in account
account_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Пополнить баланс"], ["Назад"]],
    one_time_keyboard=True,
    is_persistent=False)

account_add_balance = ReplyKeyboardMarkup(
    keyboard=[["Пополнить на 50 рублей"],
              ["Пополнить на 250 рублей"],
              ["Пополнить на 500 рублей"],
              ["Пополнить на 1000 рублей"],
              ["Назад"]],
    one_time_keyboard=True,
    is_persistent=False)

# back button for return in start
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Назад"]],
    one_time_keyboard=True,
    is_persistent=False)

# choose paying method keyboard
confirm_add_keyboard = ReplyKeyboardMarkup(
    keyboard=[['Добавить за 50 рублей и 10 ХЛБаллов'],
              ['Добавить за 10 рублей и 100 ХЛБаллов'],
              ['Назад']],
    one_time_keyboard=True,
    is_persistent=False)

confirm_invoice_keyboard = ReplyKeyboardMarkup(
    keyboard=[['Назад'],['Оплачено']],
    one_time_keyboard=True,
    is_persistent=False
)


def pays_keyboard(url):
    return InlineKeyboardMarkup( [
        [
            InlineKeyboardButton(text="Оплатить", url=url),

        ],
    ])


if __name__ == '__main__':
    print(account_add_balance.keyboard[1][0].text)
    pass
