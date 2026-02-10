from binascii import b2a_uu
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class FinanceCallBack(CallbackData, prefix='finance'):
    action: str
    type: str
    period: Optional[str] = None

class MainCallBack(CallbackData, prefix='main'):
    action: str #add, show, balance, question

def get_main_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Внести в систему",
        callback_data=MainCallBack(action='main_add')
    )

    builder.button(
        text="Показать данные",
        callback_data=MainCallBack(action='main_show')
    )

    builder.button(
        text='Баланс',
        callback_data=MainCallBack(action='balance_show')
    )

    builder.adjust(1)
    return builder.as_markup()

def get_add_keyboard():
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

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data='back'))
    return builder.as_markup()

def get_show_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="💵 Доходы",
        callback_data=FinanceCallBack(action='show', type='income').pack()
    )

    builder.button(
        text="💸 Расходы",
        callback_data=FinanceCallBack(action='show', type='cost').pack()
    )

    builder.adjust(2)

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data='back'))
    return builder.as_markup()

def get_period_keyboard(report_type: str):
    periods = [
        'Сегодня',
        'Вчера',
        'Неделя',
        'Месяц'
    ]
    builder = InlineKeyboardBuilder()

    for period in periods:
        builder.button(text=period, callback_data=FinanceCallBack(action='report', type=report_type, period=period))
    builder.adjust(1)

    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data='back'))

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

def get_back_to_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Вернуться ◀️', callback_data='back_to_menu')

    return builder.as_markup()