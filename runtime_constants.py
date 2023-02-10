from telebot import types

START_MSG = types.InlineKeyboardMarkup()
BUTTON_CREATE_ROOM = types.InlineKeyboardButton("Создать комнату", callback_data="createRoom")
BUTTON_SIGN_IN_ROOM = types.InlineKeyboardButton("Присоединиться к комнате", callback_data="signInRoom")
BUTTON_BUY = types.InlineKeyboardButton("Сообщить о покупке", callback_data="Buy")
START_MSG.add(BUTTON_CREATE_ROOM, BUTTON_SIGN_IN_ROOM, BUTTON_BUY)

YES_NO_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
BUTTON_YES = types.KeyboardButton("Да")
BUTTON_NO = types.KeyboardButton("Нет")
YES_NO_MARKUP.add(BUTTON_YES, BUTTON_NO)

