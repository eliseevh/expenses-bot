from telebot import types

import api
import runtime_constants


class CreateRoom:
    def __init__(self, bot):
        self.bot = bot
        self.start = self.get_room_name
        self.room_name = ""
        self.room_password = ""
        self.user_name = ""

    def get_room_name(self, message):
        self.room_name = message.text
        self.bot.send_message(message.from_user.id, "Введи пароль для комнаты")
        self.bot.register_next_step_handler(message, self.get_room_password)

    def get_room_password(self, message):
        self.room_password = message.text
        self.bot.send_message(message.from_user.id, "Введи своё имя")
        self.bot.register_next_step_handler(message, self.get_user_name_in_room)

    def get_user_name_in_room(self, message):
        self.user_name = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_yes = types.KeyboardButton("Да")
        button_no = types.KeyboardButton("Нет")
        markup.add(button_yes, button_no)
        self.bot.send_message(message.from_user.id,
                              f"Вы действительно хотите создать комнату "
                              f"{self.room_name} с паролем {self.user_name} "
                              f"и именем {self.user_name}?",
                              reply_markup=markup
                              )

        self.bot.register_next_step_handler(message, self.finish)

    def finish(self, message):
        if message.text == "Да":
            result = api.create_room(self.room_name, self.room_password, message.from_user.id, self.user_name)
            if 'errors' in result:
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                self.bot.send_message(message.from_user.id, f"При попытке создать комнату возникили ошибки:\n{errors}")
            else:
                room_id = result['data']['createRoom']['roomId']
                self.bot.send_message(message.from_user.id, f"Комната создана успешно! id для входа: {room_id}")
        self.bot.send_message(message.from_user.id, "Выберите действие:", reply_markup=runtime_constants.START_MSG)
        del self
