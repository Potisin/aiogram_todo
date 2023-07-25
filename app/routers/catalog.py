from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database import async_session
from keyboards import create_catalogs_or_tasks_markup, create_reply_markup, create_simple_inline_markup
from models import Catalog
from utils import get_tasks_by_catalog

router = Router()


class CreatingCatalog(StatesGroup):
    request_catalog_name = State()
    created_catalog = State()


@router.callback_query(Text('Мои списки'))
async def show_catalogs(callback: CallbackQuery) -> None:
    source = 'catalogs'
    async with async_session() as session:
        stmt = select(Catalog.name).filter_by(user_tg_id=callback.from_user.id)
        catalog_names = await session.scalars(stmt)
        catalog_names = list(catalog_names)
    if catalog_names:
        catalogs_markup = create_catalogs_or_tasks_markup(source, catalog_names)
        await callback.message.answer('Выберите список', reply_markup=catalogs_markup)
    else:
        await callback.message.answer('У вас еще нет списков')


@router.callback_query(Text(startswith="catalogs: "))
async def show_catalog_detail(callback: CallbackQuery) -> None:
    catalog_name = callback.data.split(': ')[1]
    task_names_markup = await get_tasks_by_catalog(catalog_name, callback.from_user.id)
    await callback.message.answer('Выберите задачу или создайте новую', reply_markup=task_names_markup)


@router.callback_query(Text('Создать список'))
async def request_catalog_name(callback: CallbackQuery, state: FSMContext) -> None:
    markup = create_reply_markup(['Отмена'])
    await callback.message.answer('Введите название списка задач. Например "Работа" или "Дом"', reply_markup=markup)
    await state.set_state(CreatingCatalog.request_catalog_name)


@router.message(CreatingCatalog.request_catalog_name)
async def create_catalog(message: Message, state: FSMContext) -> None:
    markup = create_simple_inline_markup(['Создать задачу', 'Мои списки', 'Отмена'], 1)
    catalog_name = message.text
    async with async_session() as session:
        new_catalog = Catalog(name=catalog_name, user_tg_id=message.from_user.id)
        session.add(new_catalog)
        await session.flush()
        await session.refresh(new_catalog)
        await session.commit()
    await message.answer('Отлично, список создан! Теперь вы можете создать задачу.', reply_markup=markup)
    await state.set_data({
        'catalog_id': new_catalog.id,
        'catalog_name': catalog_name
    })
    await state.set_state(CreatingCatalog.created_catalog)
