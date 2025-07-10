from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

reg_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Регистрация 🚀')]],
    resize_keyboard=True
)

main_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Встретиться ☕️')], [KeyboardButton(text='Профиль')]],
    resize_keyboard=True
)

def meet_candidate_kb(partner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Назначить встречу',callback_data=f'meet_request:{partner_id}')], [InlineKeyboardButton(text='Выбрать другого', callback_data='meet_other')]]
    )

def answer_request_kb(meet_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='✅ Согласиться', callback_data=f"meet_accept:{meet_id}")], [InlineKeyboardButton(text='❌ Отказаться', callback_data=f"meet_decline:{meet_id}")]]
    )