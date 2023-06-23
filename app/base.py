from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from app.database import get_db
from app.keyboards import default_markup, cancel_markup

router = Router()

db = get_db()


class CreatingList(StatesGroup):
    get_lists_name = State()
    create_list = State()
    redirect_to_tasks = State()


@router.message(Command(commands='start', ignore_case=True))
async def start(message: Message) -> None:
    await message.answer('Привет! Я твой бот-ассистент. '
                         'Я помогу тебе не забыть о всех твоих задачах и делах ☺', reply_markup=default_markup)
    await db.add_user(message.from_user.id, message.from_user.username)


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Text('Мои списки'))
async def my_lists(message: Message) -> None:
    await message.answer('вот и ваши списки')


@router.message(Text('Создать список', ))
async def get_list_name(message: Message, state: FSMContext) -> None:
    await message.answer('Введите название списка задач. Например "Работа" или "Дом"', reply_markup=cancel_markup)
    await state.set_state(CreatingList.get_lists_name)


@router.message(CreatingList.get_lists_name)
async def create_list(message: Message, state: FSMContext) -> None:
    await db.create_list(message.from_user.id, message.text)
    await message.answer('Отлично, список создан! Теперь вы можете создать задачу.')
    await state.set_state(CreatingList.create_list)


@router.message(CreatingList.create_list)
async def create_task(message: Message, state: FSMContext) -> None:
    await message.answer('Пук-среньк')
    await state.clear()
