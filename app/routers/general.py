from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy import select

from app.keyboards import create_simple_inline_markup
from database import async_session
from models import User, Task, Catalog
from routers.catalog import router as catalog_router, show_catalog_detail, show_catalogs
from routers.task import router as task_router

router = Router()
router.include_router(catalog_router)
router.include_router(task_router)

ACTIONS_MAP = {
    'task': {
        'model': Task,
        'message': 'Задача успешно удалена',
        'action': show_catalog_detail
    },
    'catalog': {
        'model': Catalog,
        'message': 'Список успешно удален',
        'action': show_catalogs
    }
}


@router.message(Command(commands='start', ignore_case=True))
async def start(message: Message) -> None:
    buttons = {'Мои списки': 'my_catalogs',
               'Создать список': 'create_catalog'}
    reply_markup = create_simple_inline_markup(buttons, 2)
    await message.answer('Привет! Я твой бот-ассистент. '
                         'Я помогу тебе не забыть о всех твоих задачах и делах ☺', reply_markup=reply_markup)
    async with async_session() as session:
        stmt = select(User).filter_by(tg_id=message.from_user.id)
        user = await session.scalar(stmt)
        if not user:
            user = User(tg_id=message.from_user.id)
            session.add(user)
            await session.commit()


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.callback_query(Text(startswith='delete'))
async def delete_catalog_or_task(callback: CallbackQuery) -> None:
    """Функция динамически определяем необходимую модель, удаляет объект,
    вызывает соответсвующие функции для редиректа и сообщения"""
    model_name = callback.data.split('_')[1].lower()
    Model = ACTIONS_MAP.get(model_name).get('model')
    obj_id = int(callback.data.split('_')[2])

    if not Model:
        await callback.message.answer('Нет такого объекта')
        return

    async with async_session() as session:
        stmt = select(Model).filter_by(id=obj_id)
        obj = await session.scalar(stmt)
        if model_name == 'task':
            catalog_id = obj.catalog_id
        await session.delete(obj)
        await session.commit()

    action_info = ACTIONS_MAP.get(model_name)
    if action_info:
        await callback.message.answer(text=action_info['message'])
        if 'action' in action_info:
            if model_name == 'task':
                await action_info['action'](callback, catalog_id=catalog_id)
            else:
                await action_info['action'](callback)
