from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.database import get_db
from app.keyboards import create_lists_or_tasks_markup, create_reply_markup, \
    create_simple_inline_markup, skip_markup, deadline_or_skip_markup
from app.utils import show_tasks_for_list

router = Router()

db = get_db()


class CreatingList(StatesGroup):
    request_list_name = State()
    create_list = State()
    redirect_to_tasks = State()


class CreatingTask(StatesGroup):
    request_task_name = State()
    request_task_description = State()
    request_task_deadline = State()
    create_task = State()


@router.message(Command(commands='start', ignore_case=True))
async def start(message: Message) -> None:
    markup = create_simple_inline_markup(['Мои списки', 'Создать список'], 2)
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


@router.callback_query(Text('Мои списки'))
async def show_lists(callback: CallbackQuery) -> None:
    source = 'lists'
    lists = await db.get_task_list_names(callback.from_user.id)
    lists_markup = create_lists_or_tasks_markup(source, lists)
    await callback.message.answer('Выберите список', reply_markup=lists_markup)


@router.callback_query(Text(startswith="lists: "))  # передается название списка
async def show_tasks(callback: CallbackQuery):
    list_name = callback.data.split(': ')[1]
    markup = await show_tasks_for_list(callback.from_user.id, list_name, db)
    await callback.message.answer('Выберите задачу', reply_markup=markup)


@router.callback_query(Text('Создать список'))
async def request_list_name(callback: CallbackQuery, state: FSMContext) -> None:
    markup = create_reply_markup(['Отмена'])
    await callback.message.answer('Введите название списка задач. Например "Работа" или "Дом"', reply_markup=markup)
    await state.set_state(CreatingList.request_list_name)


@router.message(CreatingList.request_list_name)
async def create_list(message: Message, state: FSMContext) -> None:
    markup = create_simple_inline_markup(['Создать задачу', 'Мои списки', 'Отмена'], 1)
    list_name = message.text
    list_id = await db.create_list(message.from_user.id, list_name)
    await message.answer('Отлично, список создан! Теперь вы можете создать задачу.', reply_markup=markup)
    await state.set_data({
        'list_id': list_id,
        'list_name': list_name
    })
    await state.set_state(CreatingList.create_list)


@router.callback_query(Text('Создать задачу'))
@router.message(CreatingList.create_list)
async def request_task_name(callback: Optional[CallbackQuery] = None, message: Optional[Message] = None,
                            state: Optional[FSMContext] = None) -> None:
    message = callback.message if callback else message
    await message.answer('Введите название задачи')
    data = await state.get_data()
    await state.clear()
    await state.set_state(CreatingTask.request_task_name)
    await state.set_data(data)


@router.message(CreatingTask.request_task_name)
async def request_task_description(message: Message, state: FSMContext) -> None:
    await state.update_data({'task_name': message.text})
    await message.answer('Введите описание или нажмите кнопку "Пропустить"', reply_markup=skip_markup)
    await state.set_state(CreatingTask.request_task_description)

@router.message(CreatingTask.request_task_description)
async def request_task_deadline(message: Message, state: FSMContext) -> None:
    if message.text != 'Пропустить':
        await state.update_data({'task_description': message.text})
    await message.answer('Укажите дедлайн или нажмите кнопку "Пропустить"', reply_markup=deadline_or_skip_markup)
    await state.set_state(CreatingTask.request_task_deadline)


@router.message(CreatingTask.request_task_deadline)
async def create_task(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await db.create_task(data['list_id'], data['task_name'])
    markup = await show_tasks_for_list(message.from_user.id, data['list_name'], db)
    await message.answer(text=f'<b><i>{data["list_name"]}</i></b>', reply_markup=markup)
    await message.answer(text='Задач больше нет', reply_markup=ReplyKeyboardRemove())
    

    await state.clear()
    # здесь хотел бы отобразить все задачи из списка, включая новую
