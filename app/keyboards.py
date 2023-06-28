from typing import List

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

keyboard = [
    [types.KeyboardButton(text='Мои списки')],
    [types.KeyboardButton(text='Создать список')]
]
default_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


cancel_markup = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Отмена')]], resize_keyboard=True)


def create_inline_markup(source: str, lists_name: List) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name in lists_name:
        builder.add(types.InlineKeyboardButton(text=name[0], callback_data=f'{source}: {name[0]}'))
    if source == 'lists':
        builder.adjust(2)
    return builder.as_markup()


def create_reply_markup(button_names: List) -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for name in button_names:
        builder.add(types.KeyboardButton(text=name))
    builder.adjust(1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
