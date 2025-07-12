from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reg_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Регистрация 🚀')]],
    resize_keyboard=True
)

main_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Встретиться ☕️')],
        [KeyboardButton(text='Профиль 👥'), KeyboardButton(text='Инфо ℹ️')],
        [KeyboardButton(text='Выбрать офис 🏢')]
    ],
    resize_keyboard=True,
)