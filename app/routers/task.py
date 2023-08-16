from typing import Optional

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy import select

from database import async_session
from keyboards import skip_markup, deadline_or_skip_markup
from models import Task
from routers.catalog import show_catalog_detail
from states import CreatingTask, CreatingCatalog

router = Router()


@router.callback_query(Text(startswith='Создать задачу'))
@router.message(CreatingCatalog.created_catalog)  # если создаем задачу после создания списка
async def request_task_name(callback: Optional[CallbackQuery], state: Optional[FSMContext] = None) -> None:
    data = callback.data.split('&')
    await state.set_state(CreatingTask.request_task_name)
    if len(data) > 1:
        await state.set_data({'catalog_id': int(data[1])})
    await callback.message.answer('Введите название задачи')


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
    async with async_session() as session:
        new_task = Task(**data)
        session.add(new_task)
        await session.commit()
    await message.answer('Задача успешно создана!✅', reply_markup=ReplyKeyboardRemove())
    await show_catalog_detail(message, state)


@router.callback_query(Text(startswith="tasks"))  # передается название задачи
async def task_detail(callback: CallbackQuery) -> None:
    task_name = callback.data.split(': ')[1]
    catalog_id = callback.data.split(': ')[2]
    async with async_session as session:
        stmt = select(Task).filter_by(name=task_name, catalog_id=catalog_id)
        task = await session.scalar(stmt)
    await callback.message.answer(text=f'b><i>{task.name}</i></b>\n\n'
                                       f'{task.description}\n\n'
                                       f'Дедлайн: {task.deadline}')
