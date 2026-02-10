from binascii import b2a_uu
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class FinanceCallBack(CallbackData, prefix='finance'):
    action: str
    type: str
    period: Optional[str] = None

def get_main_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text = "💵 Доходы",
        callback_data=FinanceCallBack(action='add', type='income').pack()
    )

    builder.button(
        text = "💸 Расходы",
        callback_data=FinanceCallBack(action='add', type='cost').pack()
    )

    builder.adjust(2)

    return builder.as_markup()

def get_categories_keyboard():
    categories = [
        "Еда 🍔",
        "Транспорт 🚗",
        "Жилье 🏠",
        "Одежда 👕",
        "Здоровье 💊",
        "Развлечения 🎉",
        "Связь 📱",
        "Прочее 💡"
    ]

    builder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(text=cat, callback_data=f'cat_{cat}')
    builder.adjust(2)

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data='back'))

    return builder.as_markup()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Назад ◀️', callback_data='back')

    return builder.as_markup()