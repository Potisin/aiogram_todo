from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.database import get_db
from app.keyboards import default_markup, cancel_markup, create_inline_markup, create_reply_markup

router = Router()

db = get_db()


class CreatingList(StatesGroup):
    get_lists_name = State()
    create_list = State()
    redirect_to_tasks = State()


class CreatingTask(StatesGroup):
    get_task_name = State()
    create_task = State()
    redirect_to_parent_list = State()


@router.message(Command(commands='start', ignore_case=True))
async def start(message: Message) -> None:
    markup = create_reply_markup(['Мои списки', 'Создать список'])
    await message.answer('Привет! Я твой бот-ассистент. '
                         'Я помогу тебе не забыть о всех твоих задачах и делах ☺', reply_markup=markup)
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
async def show_lists(message: Message) -> None:
    source = 'lists'
    lists = await db.get_task_list_names(message.from_user.id)
    lists_markup = create_inline_markup(source, lists)
    await message.answer('Выберите список', reply_markup=lists_markup)


@router.callback_query(Text(startswith="lists: "))
async def show_tasks(callback: CallbackQuery):
    source = 'tasks'
    list_name = callback.data.split(': ')[1]
    tasks = await db.get_tasks(callback.from_user.id, list_name)
    tasks_markup = create_inline_markup(source, tasks)
    await callback.message.answer('Выберите задачу', reply_markup=tasks_markup)



@router.message(Text('Создать список'))
async def get_list_name(message: Message, state: FSMContext) -> None:
    markup = create_reply_markup(['Отмена'])
    await message.answer('Введите название списка задач. Например "Работа" или "Дом"', reply_markup=markup)
    await state.set_state(CreatingList.get_lists_name)


@router.message(CreatingList.get_lists_name)
async def create_list(message: Message, state: FSMContext) -> None:
    markup = create_reply_markup(['Создать задачу', 'Мои списки', 'Отмена'])
    list_id = await db.create_list(message.from_user.id, message.text)
    await message.answer('Отлично, список создан! Теперь вы можете создать задачу.', reply_markup=markup)
    await state.set_data({'list_id': list_id})
    await state.set_state(CreatingList.create_list)


@router.message(CreatingList.create_list)
async def create_task(message: Message, state: FSMContext) -> None:
    await message.answer('Введите название задачи')
    list_id = await state.get_data()
    await state.clear()
