from typing import Callable

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


def send_rooms_keyboard(user_id: int, action_name: str, next_message_handler: Callable) -> None:
    rooms = get_rooms(user_id)
    if rooms == "Error":
        bot.send_message(user_id, "Не получилось узнать список ваших комнат. К сожалению, "
                                  "в данный момент вы не можете " + action_name)
        send_action_keyboard(bot, user_id)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for room in rooms:
            markup.add(types.KeyboardButton(room))
        markup.add(runtime_constants.BUTTON_CANCEL)
        bot.send_message(user_id, "Выбери комнату:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(user_id, next_message_handler)


def get_rooms(user_id: int) -> [str]:
    result = api.get_user_rooms(user_id)
    if 'errors' in result:
        print("[GET_ROOMS] [!ERROR!]", result['errors'])
        return "Error"
    rooms = result['data']['getRooms']
    return list(map(lambda room: room['roomName'] + ", id" + room['roomId'], rooms))


@bot.message_handler(content_types=["text"])
def get_text_messages(message: types.Message) -> None:
    if message.text == runtime_constants.BUTTON_CREATE_ROOM.text:
        bot.send_message(message.from_user.id, "Введи название комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler(message, CreateRoom(bot).start)
    elif message.text == runtime_constants.BUTTON_SIGN_IN_ROOM.text:
        bot.send_message(message.from_user.id, "Введи id комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        bot.register_next_step_handler(message, SignInRoom(bot).start)
    elif message.text == runtime_constants.BUTTON_BUY.text:
        send_rooms_keyboard(message.from_user.id,
                            "сообщить о покупке",
                            Buy(bot).start
                            )
    elif message.text == runtime_constants.BUTTON_PAY.text:
        send_rooms_keyboard(message.from_user.id,
                            "сообщить о переводе",
                            Pay(bot).start
                            )
    elif message.text == runtime_constants.BUTTON_BALANCE.text:
        send_rooms_keyboard(message.from_user.id,
                            "узнать свой баланс",
                            Balance(bot).start)
    elif message.text == runtime_constants.BUTTON_DEBTS.text:
        send_rooms_keyboard(message.from_user.id,
                            "узнать кому вы должны перевести деньги",
                            Debts(bot).start)
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда")
        send_action_keyboard(bot, message.from_user.id)


if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            print("[MAIN LOOP] [!ERROR!]", e)
            print("Restarting bot")
