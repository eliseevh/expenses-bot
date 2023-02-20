from telebot import types

ACTION_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
BUTTON_CREATE_ROOM = types.KeyboardButton("Создать комнату")
BUTTON_SIGN_IN_ROOM = types.KeyboardButton("Присоединиться к комнате")
BUTTON_SIGN_OUT_ROOM = types.KeyboardButton("Выйти из комнаты")
BUTTON_BUY = types.KeyboardButton("Сообщить о покупке")
BUTTON_PAY = types.KeyboardButton("Сообщить о переводе")
BUTTON_BALANCE = types.KeyboardButton("Узнать свой баланс")
BUTTON_DEBTS = types.KeyboardButton("Узнать, кому платить")
ACTION_MARKUP.add(BUTTON_CREATE_ROOM)
ACTION_MARKUP.add(BUTTON_SIGN_IN_ROOM, BUTTON_SIGN_OUT_ROOM)
ACTION_MARKUP.add(BUTTON_BUY, BUTTON_PAY)
ACTION_MARKUP.add(BUTTON_BALANCE, BUTTON_DEBTS)

YES_NO_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
BUTTON_YES = types.KeyboardButton("Да")
BUTTON_NO = types.KeyboardButton("Нет")
YES_NO_MARKUP.add(BUTTON_YES, BUTTON_NO)

BUTTON_CANCEL = types.KeyboardButton("Отмена")

CANCEL_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
CANCEL_MARKUP.add(BUTTON_CANCEL)
