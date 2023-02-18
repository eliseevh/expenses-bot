import telebot
from telebot import types

import expenses_bot.api
import expenses_bot.runtime_constants
from expenses_bot import runtime_constants, private_constants
from expenses_bot.utils import show_money, check_cancel, send_action_keyboard


class Pay:
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot
        self.room_id = ""
        self.room_members = []
        self.user = {}
        self.value = 0
        self.start = self.get_room_id

    def get_room_id(self, message: types.Message) -> None:
        if check_cancel(self.bot, message):
            del self
            return
        self.room_id = message.text.split("id")[-1]
        room = expenses_bot.api.get_room(self.room_id)
        if 'errors' in room:
            self.bot.send_message(message.from_user.id,
                                  "Произошла ошибка. К сожалению, в данный момент вы не можете сообщить о переводе")
            send_action_keyboard(self.bot, message.from_user.id)
        else:
            self.room_members = room['data']['getRoom']['members']
            if len(self.room_members) == 1:
                self.bot.send_message(message.from_user.id, "В этой комнате ты один, нельзя перевести кому-то деньги")
                return
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for member in self.room_members:
                if member['id'] != str(message.from_user.id):
                    markup.add(types.KeyboardButton(member['name']))
            markup.add(runtime_constants.BUTTON_CANCEL)
            self.bot.send_message(message.from_user.id, "Выбери человека, которому ты перевёл деньги:",
                                  reply_markup=markup)
            self.bot.register_next_step_handler(message, self.get_user_id)

    def get_user_id(self, message: types.Message) -> None:
        if check_cancel(self.bot, message):
            del self
            return
        for room_member in self.room_members:
            if room_member['name'] == message.text:
                if room_member['id'] == str(message.from_user.id):
                    self.bot.send_message(message.from_user.id, "Нельзя перевести деньги себе")
                    self.bot.register_next_step_handler(message, self.get_user_id)
                    return
                self.user = room_member
                self.bot.send_message(message.from_user.id, "Введите переведенную сумму:")
                self.bot.register_next_step_handler(message, self.get_value)
                return
        self.bot.send_message(message.from_user.id, f"В комнате нет человека с именем \"{message.text}\"")
        self.bot.register_next_step_handler(message, self.get_user_id)

    def get_value(self, message: types.Message) -> None:
        if check_cancel(self.bot, message):
            del self
            return
        split = message.text.split('.')
        if len(split) > 2:
            self.bot.send_message(message.from_user.id,
                                  "Неверный формат. Сумма указывается так: 2000, или так: 923.53")
            self.bot.register_next_step_handler(message, self.get_value)
            return
        try:
            if len(split) == 2:
                if len(split[1]) > 2:
                    self.bot.send_message(message.from_user.id,
                                          "Неверный формат. Сумма указывается так: 2000, или так: 923.53")
                    self.bot.register_next_step_handler(message, self.get_value)
                    return
                elif len(split[1]) == 2:
                    value = int(split[0]) * 100 + int(split[1])
                else:
                    value = int(split[0]) * 100 + int(split[1]) * 10
            elif len(split) == 1:
                value = int(split[0]) * 100
            else:
                print("[PAY] Empty telegram message")
                self.bot.send_message(message.from_user.id, "Введите переведенную сумму:")
                self.bot.register_next_step_handler(message, self.get_value)
                return
            self.value = value
        except ValueError as _:
            self.bot.send_message(message.from_user.id,
                                  "Неверный формат. Стоимость указывается так: 2000, или так: 923.53")
            self.bot.register_next_step_handler(message, self.get_value)
            return
        self.bot.send_message(message.from_user.id,
                              f"Вы действительно хотите сообщить о переводе "
                              f"{show_money(self.value)}руб. пользователю {self.user['name']}?",
                              reply_markup=expenses_bot.runtime_constants.YES_NO_MARKUP)
        self.bot.register_next_step_handler(message, self.finish)

    def finish(self, message: types.Message) -> None:
        if check_cancel(self.bot, message):
            del self
            return
        if message.text == "Да":
            print(
                f"[PAY] Pay info: room_id: {self.room_id}, "
                f"sender_id: {message.from_user.id}, receiver_id: {self.user['id']}, value: {self.value}")
            result = expenses_bot.api.pay(self.room_id, message.from_user.id, self.user['id'], self.value)
            if 'errors' in result:
                print("[PAY] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                self.bot.send_message(message.from_user.id,
                                      f"При попытке сообщить о переводе возникли ошибки:\n{errors}")
            else:
                if 'extensions' in result and result['extensions'] == "error on saving log":
                    self.bot.send_message(private_constants.OWNER_TELEGRAM_ID, "ERROR ON SAVING LOG:\n" + str(result))

                self.bot.send_message(message.from_user.id, "Информация о переводе успешно добавлена")
                sender_name = "Неизвестен"
                for member in self.room_members:
                    if member['id'] == str(message.from_user.id):
                        sender_name = member['name']
                        break
                try:
                    self.bot.send_message(int(self.user['id']),
                                          f"Пользователь {sender_name} перевел вам {show_money(self.value)}руб.")
                except Exception as e:
                    print("[PAY] [!ERROR!]", e)
        send_action_keyboard(self.bot, message.from_user.id)
        del self
