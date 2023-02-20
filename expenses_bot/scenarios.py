import telebot
from telebot import types

import expenses_bot.api
from expenses_bot import private_constants, runtime_constants, api
from expenses_bot.database.buy import BuyStorage
from expenses_bot.database.create_room import CreateRoomStorage
from expenses_bot.database.pay import PayStorage
from expenses_bot.database.sign_in_room import SignInRoomStorage
from expenses_bot.database.user_state import UserStateStorage
from expenses_bot.utils import send_action_keyboard, check_cancel, show_money

idx = 0


def next_idx():
    global idx
    result = idx
    idx += 1
    return result


FUNCTION_NAME_TO_STATE = {
    "start": next_idx(),
    "create_room_get_room_name": next_idx(),
    "create_room_get_room_password": next_idx(),
    "create_room_get_user_name": next_idx(),
    "create_room_finish": next_idx(),
    "sign_in_room_get_room_id": next_idx(),
    "sign_in_room_get_room_password": next_idx(),
    "sign_in_room_get_user_name": next_idx(),
    "sign_out_room_get_room_id": next_idx(),
    "buy_get_room_id": next_idx(),
    "buy_get_members": next_idx(),
    "buy_get_name": next_idx(),
    "buy_get_cost": next_idx(),
    "buy_finish": next_idx(),
    "pay_get_room_id": next_idx(),
    "pay_get_user_id": next_idx(),
    "pay_get_value": next_idx(),
    "pay_finish": next_idx(),
    "balance_get_balance": next_idx(),
    "debts_get_debts": next_idx(),
}


def get_rooms(user_id: int) -> [str]:
    result = api.get_user_rooms(user_id)
    if 'errors' in result:
        print("[GET_ROOMS] [!ERROR!]", result['errors'])
        return "Error"
    rooms = result['data']['getRooms']
    return list(map(lambda room: room['roomName'] + ", id" + room['roomId'], rooms))


def send_rooms_keyboard(bot: telebot.TeleBot, user_id: int, action: str, next_state: int) -> None:
    rooms = get_rooms(user_id)
    if rooms == "Error":
        bot.send_message(user_id, "Не получилось узнать список твоих комнат. К сожалению, "
                                  "в данный момент ты не можешь " + action)
        send_action_keyboard(bot, user_id)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(user_id, 0)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for room in rooms:
            markup.add(types.KeyboardButton(room))
        markup.add(runtime_constants.BUTTON_CANCEL)
        bot.send_message(user_id, "Выбери комнату:", reply_markup=markup)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(user_id, next_state)


def start(bot: telebot.TeleBot, message: types.Message) -> None:
    if message.text == runtime_constants.BUTTON_CREATE_ROOM.text:
        bot.send_message(message.from_user.id, "Введи название комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["create_room_get_room_name"])
        with CreateRoomStorage(private_constants.DB_NAME) as create_room:
            create_room.add_user(message.from_user.id)
    elif message.text == runtime_constants.BUTTON_SIGN_IN_ROOM.text:
        bot.send_message(message.from_user.id, "Введи id комнаты:", reply_markup=runtime_constants.CANCEL_MARKUP)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["sign_in_room_get_room_id"])
        with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
            sign_in_room.add_user(message.from_user.id)
    elif message.text == runtime_constants.BUTTON_SIGN_OUT_ROOM.text:
        send_rooms_keyboard(bot, message.from_user.id, "выйти из комнаты",
                            FUNCTION_NAME_TO_STATE["sign_out_room_get_room_id"])
    elif message.text == runtime_constants.BUTTON_BUY.text:
        send_rooms_keyboard(bot, message.from_user.id, "сообщить о покупке", FUNCTION_NAME_TO_STATE["buy_get_room_id"])
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.add_user(message.from_user.id)
    elif message.text == runtime_constants.BUTTON_PAY.text:
        send_rooms_keyboard(bot, message.from_user.id, "сообщить о переводе", FUNCTION_NAME_TO_STATE["pay_get_room_id"])
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.add_user(message.from_user.id)
    elif message.text == runtime_constants.BUTTON_BALANCE.text:
        send_rooms_keyboard(bot, message.from_user.id, "узнать свой баланс",
                            FUNCTION_NAME_TO_STATE["balance_get_balance"])
    elif message.text == runtime_constants.BUTTON_DEBTS.text:
        send_rooms_keyboard(bot, message.from_user.id, "узнать кому ты должен перевести деньги",
                            FUNCTION_NAME_TO_STATE["debts_get_debts"])
    elif message.text == "/start":
        send_action_keyboard(bot, message.from_user.id)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда")
        send_action_keyboard(bot, message.from_user.id)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)


def create_room_get_room_name(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with CreateRoomStorage(private_constants.DB_NAME) as create_room:
            create_room.delete(message.from_user.id)
        return
    with CreateRoomStorage(private_constants.DB_NAME) as create_room:
        create_room.set_room_name(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Введи пароль для комнаты")
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["create_room_get_room_password"])


def create_room_get_room_password(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with CreateRoomStorage(private_constants.DB_NAME) as create_room:
            create_room.delete(message.from_user.id)
        return
    with CreateRoomStorage(private_constants.DB_NAME) as create_room:
        create_room.set_room_password(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Введи своё имя")
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["create_room_get_user_name"])


def create_room_get_user_name(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with CreateRoomStorage(private_constants.DB_NAME) as create_room:
            create_room.delete(message.from_user.id)
        return
    with CreateRoomStorage(private_constants.DB_NAME) as create_room:
        create_room.set_user_name(message.from_user.id, message.text)
        result = create_room.get(message.from_user.id)

    bot.send_message(message.from_user.id,
                     f"Ты действительно хочешь создать комнату "
                     f"{result[0]} с паролем {result[1]} "
                     f"и именем {result[2]}?",
                     reply_markup=runtime_constants.YES_NO_MARKUP
                     )
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["create_room_finish"])


def create_room_finish(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with CreateRoomStorage(private_constants.DB_NAME) as create_room:
            create_room.delete(message.from_user.id)
        return
    with CreateRoomStorage(private_constants.DB_NAME) as create_room:
        if message.text == "Да":
            result = create_room.get(message.from_user.id)
            result = expenses_bot.api.create_room(result[0], result[1], message.from_user.id, result[2])
            if 'errors' in result:
                print("[CREATE_ROOM] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                bot.send_message(message.from_user.id, f"При попытке создать комнату возникли ошибки:\n{errors}")
            else:
                room_id = result['data']['createRoom']['roomId']
                bot.send_message(message.from_user.id, f"Комната создана успешно! id для входа: {room_id}")
        send_action_keyboard(bot, message.from_user.id)
        create_room.delete(message.from_user.id)
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, 0)


def sign_in_room_get_room_id(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
            sign_in_room.delete(message.from_user.id)
        return
    with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
        sign_in_room.set_room_id(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Введи пароль")
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["sign_in_room_get_room_password"])


def sign_in_room_get_room_password(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
            sign_in_room.delete(message.from_user.id)
        return
    with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
        sign_in_room.set_room_password(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Введи своё имя")
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["sign_in_room_get_user_name"])


def sign_in_room_get_user_name(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
            sign_in_room.delete(message.from_user.id)
        return
    with SignInRoomStorage(private_constants.DB_NAME) as sign_in_room:
        sign_in_room.set_user_name(message.from_user.id, message.text)
        result = sign_in_room.get(message.from_user.id)
        result = expenses_bot.api.sign_in_room(result[0], result[1], message.from_user.id, result[2])
        if 'errors' in result:
            print("[SIGN_IN_ROOM] [!ERROR!]", result['errors'])
            errors = "\n".join(map(lambda err: err['message'], result['errors']))
            bot.send_message(message.from_user.id, f"Не удалось присоединиться к комнате:\n{errors}")
        else:
            bot.send_message(message.from_user.id, f"Ты успешно присоединился к комнате!")
        send_action_keyboard(bot, message.from_user.id)
        sign_in_room.delete(message.from_user.id)
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, 0)


def sign_out_room_get_room_id(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        return
    room_id = message.text.split("id")[-1]
    result = api.sign_out_room(room_id, message.from_user.id)
    if 'errors' in result:
        print("[SIGN_OUT_ROOM] [!ERROR!]", result['errors'])
        errors = "\n".join(map(lambda err: err['message'], result['errors']))
        bot.send_message(message.from_user.id, f"Не удалось выйти из комнаты:\n{errors}")
    else:
        bot.send_message(message.from_user.id, f"Ты успешно вышел из комнаты")
    send_action_keyboard(bot, message.from_user.id)
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, 0)


def buy_get_room_id(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.delete(message.from_user.id)
        return
    with BuyStorage(private_constants.DB_NAME) as buy:
        room_id = message.text.split("id")[-1]
        buy.set_room_id(message.from_user.id, room_id)
        room = expenses_bot.api.get_room(room_id)
        if 'errors' in room:
            bot.send_message(message.from_user.id,
                             "Произошла ошибка. К сожалению, в данный момент ты не можешь сообщить о покупке")
            send_action_keyboard(bot, message.from_user.id)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, 0)
            buy.delete(message.from_user.id)
        else:
            room_members = room['data']['getRoom']['members']
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Перейти к следующему шагу"))
            for member in room_members:
                if member['id'] != str(message.from_user.id):
                    markup.add(types.KeyboardButton(member['name']))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери людей, между которыми разделить покупку:",
                             reply_markup=markup)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["buy_get_members"])


def buy_get_members(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.delete(message.from_user.id)
        return
    if message.text == "Перейти к следующему шагу":
        bot.send_message(message.from_user.id, "Введи название покупки:", reply_markup=runtime_constants.CANCEL_MARKUP)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["buy_get_name"])
        return
    with BuyStorage(private_constants.DB_NAME) as buy:
        (room_id, members, _, _) = buy.get(message.from_user.id)
        room = expenses_bot.api.get_room(room_id)
        if 'errors' in room:
            bot.send_message(message.from_user.id,
                             "Произошла ошибка. К сожалению, в данный момент ты не можешь сообщить о покупке")
            send_action_keyboard(bot, message.from_user.id)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, 0)
            buy.delete(message.from_user.id)
        else:
            room_members = room['data']['getRoom']['members']
            found = False
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Перейти к следующему шагу"))
            for room_member in room_members:
                if room_member['name'] == message.text:
                    if room_member['id'] == str(message.from_user.id):
                        bot.send_message(message.from_user.id, "Нельзя добавить себя в список")
                        return
                    elif int(room_member['id']) in members:
                        bot.send_message(message.from_user.id, f"{room_member['name']} уже добавлен")
                        return
                    chosen_member = room_member
                    found = True
                elif room_member['id'] != str(message.from_user.id) and int(room_member['id']) not in members:
                    markup.add(types.KeyboardButton(room_member['name']))
            markup.add(runtime_constants.BUTTON_CANCEL)
            if found:
                buy.add_member(message.from_user.id, int(chosen_member['id']))
                bot.send_message(message.from_user.id, f"{message.text} добавлен", reply_markup=markup)
            else:
                bot.send_message(message.from_user.id, f"В комнате нет человека с именем \"{message.text}\"",
                                 reply_markup=markup)


def buy_get_name(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.delete(message.from_user.id)
        return
    with BuyStorage(private_constants.DB_NAME) as buy:
        buy.set_name(message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Введи стоимость покупки:")
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["buy_get_cost"])


def buy_get_cost(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.delete(message.from_user.id)
        return
    split = message.text.strip().split('.')
    if len(split) > 2:
        bot.send_message(message.from_user.id,
                         "Неверный формат. Стоимость указывается так: 200, или так: 92.53")
        return
    try:
        if len(split) == 2:
            if len(split[1]) > 2:
                bot.send_message(message.from_user.id,
                                 "Неверный формат. Стоимость указывается так: 200, или так: 92.53")
                return
            elif len(split[1]) == 2:
                rub = int(split[0])
                cop = int(split[1])
            else:
                rub = int(split[0])
                cop = int(split[1]) * 10
        elif len(split) == 1:
            rub = int(split[0])
            cop = 0
        else:
            print("[BUY] Empty telegram message")
            bot.send_message(message.from_user.id, "Введи стоимость покупки:")
            return
        sign = -1 if split[0].startswith("-") else 1
        cost = rub * 100 + cop * sign
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.set_cost(message.from_user.id, cost)
            (room_id, members, buy_name, cost) = buy.get(message.from_user.id)
            bot.send_message(message.from_user.id,
                             f"Ты действительно хочешь сообщить о покупке {buy_name}"
                             f" за {show_money(cost)}руб., разделенной между тобой "
                             f"и выбранными {len(members)} пользователями?",
                             reply_markup=expenses_bot.runtime_constants.YES_NO_MARKUP
                             )
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["buy_finish"])
    except ValueError as _:
        bot.send_message(message.from_user.id,
                         "Неверный формат. Стоимость указывается так: 200, или так: 92.53")


def buy_finish(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with BuyStorage(private_constants.DB_NAME) as buy:
            buy.delete(message.from_user.id)
        return
    with BuyStorage(private_constants.DB_NAME) as buy:
        if message.text == "Да":
            (room_id, members, buy_name, cost) = buy.get(message.from_user.id)
            print(
                f"[BUY] Buy info: user_id: {message.from_user.id}, "
                f"members: {members}, name: {buy_name}, cost: {cost}")
            result = expenses_bot.api.buy(room_id, message.from_user.id,
                                          list(map(str, members)) +
                                          [str(message.from_user.id)],
                                          cost)
            if 'errors' in result:
                print("[BUY] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                bot.send_message(message.from_user.id,
                                 f"При попытке сообщить о покупке возникли ошибки:\n{errors}")
            else:
                if 'extensions' in result and result['extensions'] == "error on saving log":
                    bot.send_message(private_constants.OWNER_TELEGRAM_ID, "ERROR ON SAVING LOG:\n" + str(result))
                bot.send_message(message.from_user.id, "Информация о покупке успешно добавлена")
                buyer_name = "Неизвестен"
                room = expenses_bot.api.get_room(room_id)
                if 'errors' in room:
                    print("[BUY] [!ERROR!] Unable to get room, should be unreachable")
                else:
                    room_members = room['data']['getRoom']['members']
                    for member in room_members:
                        if member['id'] == str(message.from_user.id):
                            buyer_name = member['name']
                            break
                    for member in members:
                        try:
                            bot.send_message(member,
                                             f"Пользователь {buyer_name} купил {buy_name} "
                                             f"за {show_money(cost)}руб. и "
                                             f"разделил эту покупку между собой, тобой и ещё "
                                             f"{len(members) - 1} людьми"
                                             )
                        except Exception as e:
                            print("[BUY] [!ERROR!]", e)
        buy.delete(message.from_user.id)
        send_action_keyboard(bot, message.from_user.id)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)


def pay_get_room_id(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.delete(message.from_user.id)
        return
    with PayStorage(private_constants.DB_NAME) as pay:
        room_id = message.text.split("id")[-1]
        pay.set_room_id(message.from_user.id, room_id)
        room = expenses_bot.api.get_room(room_id)
        if 'errors' in room:
            bot.send_message(message.from_user.id,
                             "Произошла ошибка. К сожалению, в данный момент ты не можешь сообщить о переводе")
            send_action_keyboard(bot, message.from_user.id)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, 0)
            pay.delete(message.from_user.id)
        else:
            room_members = room['data']['getRoom']['members']
            if len(room_members) == 1:
                bot.send_message(message.from_user.id, "В этой комнате ты один, нельзя перевести кому-то деньги")
                send_action_keyboard(bot, message.from_user.id)
                with UserStateStorage(private_constants.DB_NAME) as user_state:
                    user_state.set_state(message.from_user.id, 0)
                pay.delete(message.from_user.id)
                return
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for member in room_members:
                if member['id'] != str(message.from_user.id):
                    markup.add(types.KeyboardButton(member['name']))
            markup.add(runtime_constants.BUTTON_CANCEL)
            bot.send_message(message.from_user.id, "Выбери человека, которому ты перевёл деньги:",
                             reply_markup=markup)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["pay_get_user_id"])


def pay_get_user_id(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.delete(message.from_user.id)
        return
    with PayStorage(private_constants.DB_NAME) as pay:
        room_id = pay.get(message.from_user.id)[0]
        room = expenses_bot.api.get_room(room_id)
        if 'errors' in room:
            bot.send_message(message.from_user.id,
                             "Произошла ошибка. К сожалению, в данный момент ты не можешь сообщить о переводе")
            send_action_keyboard(bot, message.from_user.id)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, 0)
            pay.delete(message.from_user.id)
        else:
            room_members = room['data']['getRoom']['members']
            for room_member in room_members:
                if room_member['name'] == message.text:
                    if room_member['id'] == str(message.from_user.id):
                        bot.send_message(message.from_user.id, "Нельзя перевести деньги себе")
                        return
                    pay.set_receiver(message.from_user.id, int(room_member['id']), room_member['name'])
                    bot.send_message(message.from_user.id, "Введи переведенную сумму:",
                                     reply_markup=runtime_constants.CANCEL_MARKUP)
                    with UserStateStorage(private_constants.DB_NAME) as user_state:
                        user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["pay_get_value"])
                    return
            bot.send_message(message.from_user.id, f"В комнате нет человека с именем \"{message.text}\"")


def pay_get_value(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.delete(message.from_user.id)
        return
    split = message.text.strip().split('.')
    if len(split) > 2:
        bot.send_message(message.from_user.id,
                         "Неверный формат. Стоимость указывается так: 2000, или так: 923.53")
        return
    try:
        if len(split) == 2:
            if len(split[1]) > 2:
                bot.send_message(message.from_user.id,
                                 "Неверный формат. Стоимость указывается так: 2000, или так: 923.53")
                return
            elif len(split[1]) == 2:
                rub = int(split[0])
                cop = int(split[1])
            else:
                rub = int(split[0])
                cop = int(split[1]) * 10
        elif len(split) == 1:
            rub = int(split[0])
            cop = 0
        else:
            print("[BUY] Empty telegram message")
            bot.send_message(message.from_user.id, "Введи стоимость покупки:")
            return
        sign = -1 if split[0].startswith("-") else 1
        value = rub * 100 + cop * sign
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.set_value(message.from_user.id, value)
            (room_id, (receiver_id, receiver_name), value) = pay.get(message.from_user.id)
            bot.send_message(message.from_user.id,
                             f"Ты действительно хочешь сообщить о переводе "
                             f"{show_money(value)}руб. пользователю {receiver_name}?",
                             reply_markup=expenses_bot.runtime_constants.YES_NO_MARKUP)
            with UserStateStorage(private_constants.DB_NAME) as user_state:
                user_state.set_state(message.from_user.id, FUNCTION_NAME_TO_STATE["pay_finish"])
    except ValueError as _:
        bot.send_message(message.from_user.id,
                         "Неверный формат. Стоимость указывается так: 2000, или так: 923.53")


def pay_finish(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        with PayStorage(private_constants.DB_NAME) as pay:
            pay.delete(message.from_user.id)
        return
    with PayStorage(private_constants.DB_NAME) as pay:
        if message.text == "Да":
            (room_id, (receiver_id, receiver_name), value) = pay.get(message.from_user.id)
            print(
                f"[PAY] Pay info: room_id: {room_id}, "
                f"sender_id: {message.from_user.id}, receiver_id: {receiver_id}, value: {value}")
            result = expenses_bot.api.pay(room_id, message.from_user.id,
                                          str(receiver_id),
                                          value)
            if 'errors' in result:
                print("[PAY] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                bot.send_message(message.from_user.id,
                                 f"При попытке сообщить о переводе возникли ошибки:\n{errors}")
            else:
                if 'extensions' in result and result['extensions'] == "error on saving log":
                    bot.send_message(private_constants.OWNER_TELEGRAM_ID, "ERROR ON SAVING LOG:\n" + str(result))
                bot.send_message(message.from_user.id, "Информация о переводе успешно добавлена")
                sender_name = "Неизвестен"
                room = expenses_bot.api.get_room(room_id)
                if 'errors' in room:
                    print("PAY [!ERROR!] Unable to get room, should be unreachable")
                else:
                    room_members = room['data']['getRoom']['members']
                for member in room_members:
                    if member['id'] == str(message.from_user.id):
                        sender_name = member['name']
                        break
                try:
                    bot.send_message(receiver_id,
                                     f"Пользователь {sender_name} перевел тебе {show_money(value)}руб.")
                except Exception as e:
                    print("[PAY] [!ERROR!]", e)
        pay.delete(message.from_user.id)
        send_action_keyboard(bot, message.from_user.id)
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)


def balance_get_balance(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        return
    room_id = message.text.split("id")[-1]
    room = expenses_bot.api.get_room(room_id)
    if 'errors' in room:
        bot.send_message(message.from_user.id,
                         "Произошла ошибка. К сожалению, в данный момент ты не можешь узнать свой баланс")
    else:
        for member in room['data']['getRoom']['members']:
            if member['id'] == str(message.from_user.id):
                balance = member['debit']
                text = show_money(balance) + "руб."
                description = f"Тебе должны {show_money(-balance)}" if member['debit'] < 0 else (
                    "Ты ничего не должен и тебе ничего не должны" if balance == 0 else
                    f"Ты должен {show_money(balance)}")
                bot.send_message(message.from_user.id,
                                 f"Твой баланс: {text}({description})")
    send_action_keyboard(bot, message.from_user.id)
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, 0)


def debts_get_debts(bot: telebot.TeleBot, message: types.Message) -> None:
    if check_cancel(bot, message):
        with UserStateStorage(private_constants.DB_NAME) as user_state:
            user_state.set_state(message.from_user.id, 0)
        return
    room_id = message.text.split("id")[-1]
    room = expenses_bot.api.get_room(room_id)
    if 'errors' in room:
        bot.send_message(message.from_user.id,
                         "Произошла ошибка. К сожалению, в данный момент ты "
                         "не можешь узнать кому ты должен перевести деньги")
    else:
        members = room['data']['getRoom']['members']
        user = list(filter(lambda member: member['id'] == str(message.from_user.id), members))[0]
        if user['debit'] > 0:
            members.sort(key=lambda x: x['debit'])
            current = user['debit']
            result = []
            for member in members:
                if member['debit'] + current > 0:
                    result.append((member['name'], -member['debit']))
                    current += member['debit']
                else:
                    result.append((member['name'], current))
                    break
            text = "\n".join(map(lambda member: f"{member[0]}: {show_money(member[1])}", result))
            bot.send_message(message.from_user.id, f"Ты должен заплатить:\n{text}")
        else:
            bot.send_message(message.from_user.id, "Ты никому не должен ничего платить")
    send_action_keyboard(bot, message.from_user.id)
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        user_state.set_state(message.from_user.id, 0)


STATE_TO_FUNCTION = {}
for name in FUNCTION_NAME_TO_STATE:
    index = FUNCTION_NAME_TO_STATE[name]
    STATE_TO_FUNCTION[index] = globals()[name]
