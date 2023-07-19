from aiogram import types
from sqlalchemy import select

from database import async_session
from models import Task, TaskList
from app.keyboards import create_lists_or_tasks_markup


async def show_tasks_for_list(user_id: int, list_name: str) -> types.InlineKeyboardMarkup:
    source = 'tasks'
    async with async_session() as session:
        stmt = select(TaskList.id).filter_by(user_tg_id=user_id, name=list_name)
        list_id = await session.scalar(stmt)
        stmt = select(Task.name).filter_by(list_id=list_id)
        task_names = await session.scalars(stmt)
        tasks_markup = create_lists_or_tasks_markup(source, task_names)
    return tasks_markup
