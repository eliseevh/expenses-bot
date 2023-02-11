from telebot import types

ACTION_MARKUP = types.InlineKeyboardMarkup(row_width=2)
BUTTON_CREATE_ROOM = types.InlineKeyboardButton("Создать комнату", callback_data="createRoom")
BUTTON_SIGN_IN_ROOM = types.InlineKeyboardButton("Присоединиться к комнате", callback_data="signInRoom")
BUTTON_BUY = types.InlineKeyboardButton("Сообщить о покупке", callback_data="buy")
BUTTON_PAY = types.InlineKeyboardButton("Сообщить о переводе", callback_data="pay")
BUTTON_BALANCE = types.InlineKeyboardButton("Узнать свой баланс", callback_data="balance")
BUTTON_DEBTS = types.InlineKeyboardButton("Узнать, кому платить", callback_data="debts")
ACTION_MARKUP.add(BUTTON_CREATE_ROOM, BUTTON_SIGN_IN_ROOM, BUTTON_BUY, BUTTON_PAY, BUTTON_BALANCE, BUTTON_DEBTS)

YES_NO_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
BUTTON_YES = types.KeyboardButton("Да")
BUTTON_NO = types.KeyboardButton("Нет")
YES_NO_MARKUP.add(BUTTON_YES, BUTTON_NO)

BUTTON_CANCEL = types.KeyboardButton("Отмена")

CANCEL_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
CANCEL_MARKUP.add(BUTTON_CANCEL)
