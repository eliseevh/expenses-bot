import telebot
from telebot import types

import api
import private_constants
import runtime_constants
from expenses_bot.scenarios.balance import Balance
from expenses_bot.scenarios.buy import Buy
from expenses_bot.scenarios.create_room import CreateRoom
from expenses_bot.scenarios.debts import Debts
from expenses_bot.scenarios.pay import Pay
from expenses_bot.scenarios.sign_in_room import SignInRoom
from expenses_bot.utils import send_action_keyboard

bot = telebot.TeleBot(private_constants.TOKEN)


def get_rooms(user_id: int) -> [str]:
    result = api.get_user_rooms(user_id)
    if 'errors' in result:
        print("[GET_ROOMS] [!ERROR!]", result['errors'])
        return "Error"
    rooms = result['data']['getRooms']
    return list(map(lambda room: room['roomName'] + ", id" + room['roomId'], rooms))


@bot.callback_query_handler(lambda x: True)
def callback_handler(callback):
    if callback.data == runtime_constants.BUTTON_CREATE_ROOM.callback_data:
        bot.send_message(callback.from_user.id, "Введи название комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, CreateRoom(bot).start)
    elif callback.data == runtime_constants.BUTTON_SIGN_IN_ROOM.callback_data:
        bot.send_message(callback.from_user.id, "Введи id комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, SignInRoom(bot).start)
    elif callback.data == runtime_constants.BUTTON_BUY.callback_data:
        rooms = get_rooms(callback.from_user.id)
        if rooms == "Error":
            bot.send_message(callback.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете сообщить о покупке"
                             )
            send_action_keyboard(bot, callback.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(callback.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, Buy(bot).start)
    elif callback.data == runtime_constants.BUTTON_PAY.callback_data:
        rooms = get_rooms(callback.from_user.id)
        if rooms == "Error":
            bot.send_message(callback.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете сообщить о переводе"
                             )
            send_action_keyboard(bot, callback.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(callback.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, Pay(bot).start)
    elif callback.data == runtime_constants.BUTTON_BALANCE.callback_data:
        rooms = get_rooms(callback.from_user.id)
        if rooms == "Error":
            bot.send_message(callback.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете узнать свой баланс"
                             )
            send_action_keyboard(bot, callback.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(callback.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, Balance(bot).start)
    elif callback.data == runtime_constants.BUTTON_DEBTS.callback_data:
        rooms = get_rooms(callback.from_user.id)
        if rooms == "Error":
            bot.send_message(callback.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете узнать кому вы должны перевести деньги"
                             )
            send_action_keyboard(bot, callback.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(callback.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, Debts(bot).start)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    send_action_keyboard(bot, message.from_user.id)


if __name__ == "__main__":
    bot.polling(non_stop=False)
