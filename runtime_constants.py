from telebot import types

START_MSG = types.InlineKeyboardMarkup()
BUTTON_CREATE_ROOM = types.InlineKeyboardButton("Создать комнату", callback_data="createRoom")
START_MSG.add(BUTTON_CREATE_ROOM)
