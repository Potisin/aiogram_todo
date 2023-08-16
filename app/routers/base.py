from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy import select

from app.keyboards import create_simple_inline_markup
from database import async_session
from models import User
from routers.catalog import router as catalog_router
from routers.task import router as task_router

router = Router()
router.include_router(catalog_router)
router.include_router(task_router)


@router.message(Command(commands='start', ignore_case=True))
async def start(message: Message) -> None:
    markup = create_simple_inline_markup(['Мои списки', 'Создать список'], 2)
    await message.answer('Привет! Я твой бот-ассистент. '
                         'Я помогу тебе не забыть о всех твоих задачах и делах ☺', reply_markup=markup)
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
