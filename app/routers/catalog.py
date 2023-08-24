from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database import async_session
from keyboards import create_catalogs_or_tasks_markup, create_reply_markup, create_simple_inline_markup
from models import Catalog, Task
from states import CreatingCatalog

router = Router()


@router.callback_query(Text('my_catalogs'))
async def show_catalogs(callback: CallbackQuery) -> None:
    source = 'catalogs'
    async with async_session() as session:
        stmt = select(Catalog).filter_by(user_tg_id=callback.from_user.id)
        result = await session.scalars(stmt)
        catalogs = result.all()
    if catalogs:
        reply_markup = create_catalogs_or_tasks_markup(source, catalogs)
        await callback.message.answer('Выберите список', reply_markup=reply_markup)
    else:
        reply_markup = create_simple_inline_markup({'Создать список': 'Создать список'})
        await callback.message.answer('У вас еще нет списков', reply_markup=reply_markup)


@router.callback_query(Text(startswith="catalogs"))
async def show_catalog_detail(callback_or_message: CallbackQuery | Message,
                              state: FSMContext = None, catalog_id: int = None) -> None:
    """Функция вызывается или по кнопке <Название списка> в чате, или после создания задачи. От этого зависит,
    что придет на вход: или CallbackQuery, или Message """

    source = 'tasks'
    try:
        message = callback_or_message.message
        if not catalog_id:
            catalog_id = int(callback_or_message.data.split('_')[1])
    except AttributeError:
        message = callback_or_message
        data = await state.get_data()
        catalog_id = data['catalog_id']

    async with async_session() as session:
        stmt = select(Task).filter_by(catalog_id=catalog_id)
        result = await session.scalars(stmt)
        tasks = result.all()
    task_names_markup = create_catalogs_or_tasks_markup(source, tasks, catalog_id)
    await message.answer(
        f'{"Выберите задачу или создайте новую" if tasks else "У вас пока нет задач😔 Создайте новую"}',
        reply_markup=task_names_markup)


@router.callback_query(Text('create_catalog'))
async def request_catalog_name(callback: CallbackQuery, state: FSMContext) -> None:
    reply_markup = create_reply_markup(['Отмена'])
    await callback.message.answer('Введите название списка задач. Например "Работа" или "Дом"',
                                  reply_markup=reply_markup)
    await state.set_state(CreatingCatalog.request_catalog_name)


@router.message(CreatingCatalog.request_catalog_name)
async def create_catalog(message: Message, state: FSMContext) -> None:
    buttons = {'Создать задачу': 'create_task',
               'Мои списки': 'my_catalogs',
               }
    reply_markup = create_simple_inline_markup(buttons, 1)
    catalog_name = message.text
    async with async_session() as session:
        new_catalog = Catalog(name=catalog_name, user_tg_id=message.from_user.id)
        session.add(new_catalog)
        await session.flush()
        await session.refresh(new_catalog)
        await session.commit()
    await message.answer('Отлично, список создан! Теперь вы можете создать задачу.', reply_markup=reply_markup)
    await state.set_data({'catalog_id': new_catalog.id})
    await state.set_state(CreatingCatalog.created_catalog)
