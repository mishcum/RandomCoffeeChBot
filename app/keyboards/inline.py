from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db.enums import Office

def meet_candidate_kb(partner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Назначить встречу', callback_data=f'meet_request:{partner_id}')],
                        [InlineKeyboardButton(text='Выбрать другого', callback_data='meet_other')]]
    )


def answer_request_kb(meet_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='✅ Согласиться', callback_data=f'meet_accept:{meet_id}')],
                        [InlineKeyboardButton(text='❌ Отказаться', callback_data=f'meet_decline:{meet_id}')]]
    )

def office_selection_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=Office.all_.value, callback_data=f'office:{Office.all_.name}')],
            [InlineKeyboardButton(text=Office.office1.value, callback_data=f'office:{Office.office1.name}')],
            [InlineKeyboardButton(text=Office.office2.value, callback_data=f'office:{Office.office2.name}')],
            [InlineKeyboardButton(text=Office.office3.value, callback_data=f'office:{Office.office3.name}')]
        ]
    )