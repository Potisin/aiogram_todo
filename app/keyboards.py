from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = [
    [KeyboardButton(text='Мои списки')],
    [KeyboardButton(text='Создать список')]
    ]
default_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

cancel_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True)

