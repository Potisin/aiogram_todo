from aiogram import types

from app.database import Database
from app.keyboards import create_lists_or_tasks_markup


async def show_tasks_for_list(user_id: int, list_name: str, db: Database) -> types.InlineKeyboardMarkup:
    source = 'tasks'
    tasks = await db.get_tasks(user_id, list_name)
    tasks_markup = create_lists_or_tasks_markup(source, tasks)
    return tasks_markup
