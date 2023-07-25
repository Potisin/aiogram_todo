from typing import Tuple, List

from sqlalchemy import select

from database import async_session
from keyboards import create_catalogs_or_tasks_markup
from models import Task, Catalog


async def get_task_names_and_catalog_id(catalog_name: str, user_id: int) -> Tuple[List[str], int]:
    async with async_session() as session:
        stmt = select(Catalog.id).filter_by(user_tg_id=user_id, name=catalog_name)
        catalog_id = await session.scalar(stmt)
        stmt = select(Task.name).filter_by(catalog_id=catalog_id)
        task_names = await session.scalars(stmt)
    return task_names, catalog_id


async def get_tasks_by_catalog(catalog_name: str, user_id: int):
    source = 'tasks'
    task_names, catalog_id = await get_task_names_and_catalog_id(catalog_name, user_id)
    markup = create_catalogs_or_tasks_markup(source, task_names, catalog_id)
    return markup
