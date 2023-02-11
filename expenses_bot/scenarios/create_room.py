import expenses_bot.api
import expenses_bot.runtime_constants


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
        self.bot.send_message(message.from_user.id,
                              f"Вы действительно хотите создать комнату "
                              f"{self.room_name} с паролем {self.room_password} "
                              f"и именем {self.user_name}?",
                              reply_markup=expenses_bot.runtime_constants.YES_NO_MARKUP
                              )

        self.bot.register_next_step_handler(message, self.finish)

    def finish(self, message):
        if message.text == "Да":
            result = expenses_bot.api.create_room(self.room_name, self.room_password, message.from_user.id,
                                                  self.user_name)
            if 'errors' in result:
                print("[CREATE_ROOM] [!ERROR!]", result['errors'])
                errors = "\n".join(map(lambda err: err['message'], result['errors']))
                self.bot.send_message(message.from_user.id, f"При попытке создать комнату возникли ошибки:\n{errors}")
            else:
                room_id = result['data']['createRoom']['roomId']
                self.bot.send_message(message.from_user.id, f"Комната создана успешно! id для входа: {room_id}")
        self.bot.send_message(message.from_user.id, "Выбери действие:",
                              reply_markup=expenses_bot.runtime_constants.START_MSG)
        del self
