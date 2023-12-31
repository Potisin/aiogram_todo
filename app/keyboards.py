from aiogram import types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# keyboard = [
#     [types.KeyboardButton(text='Мои списки')],
#     [types.KeyboardButton(text='Создать список')]
# ]
# default_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
#
# cancel_markup = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Отмена')]], resize_keyboard=True)

# skip_markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton('Пропустить', callback_data='skip')]])

skip_markup = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Пропустить')]], resize_keyboard=True)
deadline_or_skip_markup = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text='Установить дедлайн', web_app=WebAppInfo(url='https://www.google.com'))],
              [types.KeyboardButton(text='Пропустить')]], resize_keyboard=True)


def create_catalogs_or_tasks_markup(source: str, objects,
                                    catalog_id: int | None = None) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру, кнопками являются названия Списков или Задач"""
    builder = InlineKeyboardBuilder()
    for obj in objects:
        builder.add(
            types.InlineKeyboardButton(text=obj.name, callback_data=f'{source}_{obj.id}'))
    if source == 'catalogs':
        builder.adjust(2)
    else:
        builder.row(types.InlineKeyboardButton(text='Создать задачу', callback_data=f'create_task_{catalog_id}'))
        builder.row(types.InlineKeyboardButton(text='Удалить список', callback_data=f'delete_catalog_{catalog_id}'))

    return builder.as_markup()


def create_simple_inline_markup(buttons: dict,
                                *rows: int) -> types.InlineKeyboardMarkup:
    """ Создает инлайн клавиатуру из переданных в списке названий кнопок и
    размером рядов, переданных цифровыми значениями"""
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons.items():
        builder.add(types.InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.adjust(*rows)
    return builder.as_markup()


def create_reply_markup(buttons: list) -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for button in buttons:
        builder.add(types.KeyboardButton(text=button))
    builder.adjust(1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

