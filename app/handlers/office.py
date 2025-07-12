from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards.inline import office_selection_kb
from app.db.enums import Office
from app.db import SessionLocal
from app.db.models import User
from sqlalchemy import select
from app.keyboards.reply import main_buttons

router = Router()

@router.message(F.text == 'Выбрать офис 🏢')
async def select_office(msg : Message):
    await msg.answer('Выберите офис:', reply_markup=office_selection_kb())

@router.callback_query(F.data.startswith('office:'))
async def office_selected(cb : CallbackQuery):
    office_name = cb.data.split(':')[1]
    office = Office[office_name]

    async with SessionLocal.begin() as db:
        user: User = await db.scalar(select(User).where(User.tg_id == cb.from_user.id))
        user.office = office

    await cb.answer()
    await cb.message.edit_text(text=f'🏢 Вы выбрали: *{office.value}*', parse_mode='Markdown', reply_markup=None)
    await cb.message.answer('Теперь вы будете встречать людей только из выбранного офиса. 😀', reply_markup=main_buttons)