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

bot = telebot.TeleBot(private_constants.TOKEN, suppress_middleware_excepions=True)


def get_rooms(user_id: int) -> [str]:
    result = api.get_user_rooms(user_id)
    if 'errors' in result:
        print("[GET_ROOMS] [!ERROR!]", result['errors'])
        return "Error"
    rooms = result['data']['getRooms']
    return list(map(lambda room: room['roomName'] + ", id" + room['roomId'], rooms))


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    if message.text == runtime_constants.BUTTON_CREATE_ROOM.text:
        bot.send_message(message.from_user.id, "Введи название комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler(message, CreateRoom(bot).start)
    elif message.text == runtime_constants.BUTTON_SIGN_IN_ROOM.text:
        bot.send_message(message.from_user.id, "Введи id комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler(message, SignInRoom(bot).start)
    elif message.text == runtime_constants.BUTTON_BUY.text:
        rooms = get_rooms(message.from_user.id)
        if rooms == "Error":
            bot.send_message(message.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете сообщить о покупке"
                             )
            send_action_keyboard(bot, message.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler(message, Buy(bot).start)
    elif message.text == runtime_constants.BUTTON_PAY.text:
        rooms = get_rooms(message.from_user.id)
        if rooms == "Error":
            bot.send_message(message.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете сообщить о переводе"
                             )
            send_action_keyboard(bot, message.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler(message, Pay(bot).start)
    elif message.text == runtime_constants.BUTTON_BALANCE.text:
        rooms = get_rooms(message.from_user.id)
        if rooms == "Error":
            bot.send_message(message.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете узнать свой баланс"
                             )
            send_action_keyboard(bot, message.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler(message, Balance(bot).start)
    elif message.text == runtime_constants.BUTTON_DEBTS.text:
        rooms = get_rooms(message.from_user.id)
        if rooms == "Error":
            bot.send_message(message.from_user.id,
                             "Не получилось узнать список ваших комнат. К сожалению, "
                             "в данный момент вы не можете узнать кому вы должны перевести деньги"
                             )
            send_action_keyboard(bot, message.from_user.id)
            return
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for room in rooms:
                markup.add(types.KeyboardButton(room))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(message.from_user.id, Debts(bot).start)
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда")
        send_action_keyboard(bot, message.from_user.id)


if __name__ == "__main__":
    while True:
        try:
            bot.polling(non_stop=False)
        except Exception as e:
            print("[MAIN LOOP] [!ERROR!]", e)
            print("Restarting bot")
