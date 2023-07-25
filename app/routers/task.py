from typing import Optional

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database import async_session
from keyboards import skip_markup, deadline_or_skip_markup
from models import Task
from routers.catalog import CreatingCatalog
from utils import get_tasks_by_catalog

router = Router()


class CreatingTask(StatesGroup):
    request_task_name = State()
    request_task_description = State()
    request_task_deadline = State()
    create_task = State()
    show_tasks_by_catalog = State()


@router.callback_query(Text('Создать задачу'))
@router.message(CreatingCatalog.created_catalog) #  если создаем задачу после создания списка
async def request_task_name(callback: Optional[CallbackQuery], state: Optional[FSMContext] = None) -> None:
    await callback.message.answer('Введите название задачи')
    data = await state.get_data()
    await state.clear()
    await state.set_state(CreatingTask.request_task_name)
    await state.set_data(data)


@router.message(CreatingTask.request_task_name)
async def request_task_description(message: Message, state: FSMContext) -> None:
    await state.update_data({'name': message.text})
    await message.answer('Введите описание или нажмите кнопку "Пропустить"', reply_markup=skip_markup)
    await state.set_state(CreatingTask.request_task_description)


@router.message(CreatingTask.request_task_description)
async def request_task_deadline(message: Message, state: FSMContext) -> None:
    if message.text != 'Пропустить':
        await state.update_data({'description': message.text})
    await message.answer('Укажите дедлайн или нажмите кнопку "Пропустить"', reply_markup=deadline_or_skip_markup)
    await state.set_state(CreatingTask.request_task_deadline)


@router.message(CreatingTask.request_task_deadline)
async def create_task(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if message.text != 'Пропустить':
        data['deadline'] = message.text
    catalog_name = data.pop('catalog_name')
    async with async_session() as session:
        new_task = Task(**data)
        session.add(new_task)
        await session.commit()
    task_names_markup = await get_tasks_by_catalog(catalog_name, message.from_user.id)
    await message.answer('Выберите задачу или создайте новую', reply_markup=task_names_markup)
    await state.clear()


@router.callback_query(Text(startswith="tasks: "))  # передается название задачи
async def task_detail(callback: CallbackQuery) -> None:
    task_name = callback.data.split(': ')[1]
    catalog_id = callback.data.split(': ')[2]
    async with async_session as session:
        stmt = select(Task).filter_by(name=task_name, catalog_id=catalog_id)
        task = await session.scalar(stmt)
    await callback.message.answer(text=f'b><i>{task.name}</i></b>\n\n'
                                       f'{task.description}\n\n'
                                       f'Дедлайн: {task.deadline}')
