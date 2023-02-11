from telebot import types

import expenses_bot.api
import expenses_bot.runtime_constants
from expenses_bot import runtime_constants, private_constants
from expenses_bot.utils import show_money, check_cancel, send_action_keyboard


class Buy:
    def __init__(self, bot):
        self.bot = bot
        self.room_id = ""
        self.room_members = []
        self.members = []
        self.name = ""
        self.cost = 0
        self.start = self.get_room_id

    def get_room_id(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        self.room_id = message.text.split("id")[-1]
        room = expenses_bot.api.get_room(self.room_id)
        if 'errors' in room:
            self.bot.send_message(message.from_user.id,
                                  "Произошла ошибка. К сожалению, в данный момент вы не можете сообщить о покупке")
            send_action_keyboard(self.bot, message.from_user.id)
        else:
            self.room_members = room['data']['getRoom']['members']
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Перейти к следующему шагу"))
            for member in self.room_members:
                if member['id'] != str(message.from_user.id):
                    markup.add(types.KeyboardButton(member['name']))
            markup.add(runtime_constants.BUTTON_CANCEL)
            self.bot.send_message(message.from_user.id, "Выбери людей, между которыми разделить покупку:",
                                  reply_markup=markup)
            self.bot.register_next_step_handler(message, self.get_members)

    def get_members(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        if message.text == "Перейти к следующему шагу":
            self.bot.send_message(message.from_user.id, "Введи название покупки:")
            self.bot.register_next_step_handler(message, self.get_name)
            return
        for room_member in self.room_members:
            if room_member['name'] == message.text:
                if room_member['id'] == str(message.from_user.id):
                    self.bot.send_message(message.from_user.id, "Нельзя добавить себя в список")
                    self.bot.register_next_step_handler(message, self.get_members)
                    return
                self.members.append(room_member)
                self.bot.send_message(message.from_user.id, f"{message.text} добавлен")
                self.bot.register_next_step_handler(message, self.get_members)
                return
        self.bot.send_message(message.from_user.id, f"В комнате нет человека с именем \"{message.text}\"")
        self.bot.register_next_step_handler(message, self.get_members)

    def get_name(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        self.name = message.text
        self.bot.send_message(message.from_user.id, "Введи стоимость покупки:")
        self.bot.register_next_step_handler(message, self.get_cost)

    def get_cost(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        split = message.text.split('.')
        if len(split) > 2:
            self.bot.send_message(message.from_user.id,
                                  "Неверный формат. Стоимость указывается так: 200, или так: 92.53")
            self.bot.register_next_step_handler(message, self.get_cost)
            return
        try:
            if len(split) == 2:
                if len(split[1]) > 2:
                    self.bot.send_message(message.from_user.id,
                                          "Неверный формат. Стоимость указывается так: 200, или так: 92.53")
                    self.bot.register_next_step_handler(message, self.get_cost)
                    return

                cost = int(split[0]) * 100 + int(split[1])
            elif len(split) == 1:
                cost = int(split[0]) * 100
            else:
                print("[BUY] Empty telegram message")
                self.bot.send_message(message.from_user.id, "Введите стоимость покупки:")
                self.bot.register_next_step_handler(message, self.get_cost)
                return
            self.cost = cost
            users = ", ".join(map(lambda member: member['name'], self.members))
            self.bot.send_message(message.from_user.id,
                                  f"Вы действительно хотите сообщить о покупке {self.name}"
                                  f" за {show_money(self.cost)}руб., разделенной между {users} и вами?",
                                  reply_markup=expenses_bot.runtime_constants.YES_NO_MARKUP
                                  )
            self.bot.register_next_step_handler(message, self.finish)
        except ValueError as _:
            self.bot.send_message(message.from_user.id,
                                  "Неверный формат. Стоимость указывается так: 200, или так: 92.53")
            self.bot.register_next_step_handler(message, self.get_cost)
            return

    def finish(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        if message.text == "Да":
            print(
                f"[BUY] Buy info: user_id: {message.from_user.id}, "
                f"members: {self.members}, name: {self.name}, cost: {self.cost}")
            result = expenses_bot.api.buy(self.room_id, message.from_user.id,
                                          list(map(lambda member: member['id'], self.members)) + [
                                              str(message.from_user.id)],
                                          self.cost)
            if 'errors' in result:
                print("[BUY] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                self.bot.send_message(message.from_user.id,
                                      f"При попытке сообщить о покупке возникли ошибки:\n{errors}")
            else:
                if 'extensions' in result and result['extensions'] == "error on saving log":
                    self.bot.send_message(private_constants.OWNER_TELEGRAM_ID, "ERROR ON SAVING LOG:\n" + str(result))
                self.bot.send_message(message.from_user.id, "Информация о покупке успешно добавлена")
                buyer_name = "Неизвестен"
                for member in self.room_members:
                    if member['id'] == str(message.from_user.id):
                        buyer_name = member['name']
                        break
                for member in self.members:
                    try:
                        self.bot.send_message(int(member['id']),
                                              f"Пользователь {buyer_name} купил {self.name} "
                                              f"за {show_money(self.cost)}руб. и "
                                              f"разделил эту покупку между собой, вами и ещё "
                                              f"{len(self.members) - 1} людьми"
                                              )
                    except Exception as e:
                        print("[BUY] [!ERROR!]", e)
        send_action_keyboard(self.bot, message.from_user.id)
        del self
