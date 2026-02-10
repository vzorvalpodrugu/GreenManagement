from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import keyboards as kb
from database import db

router = Router()

class AddIncome(StatesGroup):
    waiting_for_amount = State()

class AddCost(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()

@router.message(Command('start'))
async def cmd_start(message: Message):
    welcome_text = (
        "💰 <b>Финансовый помощник</b>\n\n"
        "Я помогу вам вести учет доходов и расходов.\n"
        "Выберите действие:"
    )

    await message.answer(
        welcome_text,
        reply_markup=kb.get_main_keyboard(),
        parse_mode='HTML'
    )

# Кнопка вернуться в зависимости от состояния
@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    # Добавить сумму дохода
    if current_state == AddIncome.waiting_for_amount.state:
        await callback.message.edit_text(
            "💰 <b>Финансовый помощник</b>\n\n"
            "Я помогу вам вести учет доходов и расходов.\n"
            "Выберите действие:",
            reply_markup=kb.get_main_keyboard(),
            parse_mode='HTML'
        )
        await state.clear()

    # Выбрать категорию расхода
    elif current_state == AddCost.waiting_for_category.state:
        await callback.message.edit_text(
            "💰 <b>Финансовый помощник</b>\n\n"
            "Я помогу вам вести учет доходов и расходов.\n"
            "Выберите действие:",
            reply_markup=kb.get_main_keyboard(),
            parse_mode='HTML'
        )
        await state.clear()

    # Добавить сумму расхода
    elif current_state == AddCost.waiting_for_amount:
        await state.set_state(AddCost.waiting_for_category.state)

        await callback.message.edit_text(
            "💵 <b>Добавление дохода</b>\n\nВыберите категорию:",
            reply_markup=kb.get_categories_keyboard(),
            parse_mode='HTML'
        )

    await callback.answer()

# Логика добавления чего-то в ДБ
@router.callback_query(kb.FinanceCallBack.filter(F.action == 'add'))
async def add_record(
        callback: CallbackQuery,
        callback_data: kb.FinanceCallBack,
        state: FSMContext
):
    if callback_data.type == 'income':
        await state.set_state(AddIncome.waiting_for_amount)
        await state.update_data(record_type='income')

        text = "💵 <b>Добавление дохода</b>\n\nВведите сумму:"
        keyboard = kb.get_back_keyboard()

    elif callback_data.type == 'cost':
        await state.set_state(AddCost.waiting_for_category)
        await state.update_data(record_type='cost')

        text = "💵 <b>Добавление дохода</b>\n\nВыберите категорию:"
        keyboard = kb.get_categories_keyboard()


    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AddIncome.waiting_for_amount)
async def process_income_amount(message: Message, state: FSMContext):
    """Обработка суммы дохода"""
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError

        await db.add_income(amount)
        # Сохраняем сумму
        await state.update_data(amount=amount)

        await message.answer(
            f"✅ Доход {amount} руб успешно добавлен!",
            reply_markup=kb.get_main_keyboard()
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректную сумму (например: 1500 или 99.99):")

@router.callback_query(F.data.startswith('cat_'))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace('cat_', '')

    await state.update_data(category=category)

    await state.set_state(AddCost.waiting_for_amount)

    await callback.message.edit_text(
        f"✅ Категория: <b>{category}</b>\n\n"
        "💰 Введите сумму расхода:",
        reply_markup=kb.get_back_keyboard(),
        parse_mode="HTML"

    )
    await callback.answer()

@router.message(AddCost.waiting_for_amount)
async def process_cost_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',' , '.'))
        if amount <= 0:
            raise ValueError
        data = await state.get_data()
        category = data['category'][:-2:]

        await db.add_cost(category, amount)
        print(category)
        await message.answer(
            f"✅ Расход добавлен!\n"
            f"📂 Категория: <b>{category}</b>\n"
            f"💰 Сумма: <b>{amount}</b> руб",
            reply_markup=kb.get_main_keyboard(),
            parse_mode="HTML"
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректную сумму (например: 1500 или 99.99):")
