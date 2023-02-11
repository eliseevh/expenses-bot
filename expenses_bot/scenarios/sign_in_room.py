import expenses_bot.api
import expenses_bot.runtime_constants
from expenses_bot.utils import check_cancel, send_action_keyboard


class SignInRoom:
    def __init__(self, bot):
        self.bot = bot
        self.start = self.get_room_id
        self.room_id = ""
        self.room_password = ""
        self.user_name = ""

    def get_room_id(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        self.room_id = message.text
        self.bot.send_message(message.from_user.id, "Введи пароль")
        self.bot.register_next_step_handler(message, self.get_room_password)

    def get_room_password(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        self.room_password = message.text
        self.bot.send_message(message.from_user.id, "Введи своё имя")
        self.bot.register_next_step_handler(message, self.get_user_name)

    def get_user_name(self, message):
        if check_cancel(self.bot, message):
            del self
            return
        self.user_name = message.text
        result = expenses_bot.api.sign_in_room(self.room_id, self.room_password, message.from_user.id, self.user_name)
        if 'errors' in result:
            print("[SIGN_IN_ROOM] [!ERROR!]", result['errors'])
            errors = "\n".join(map(lambda err: err['message'], result['errors']))
            self.bot.send_message(message.from_user.id, f"Не удалось присоединиться к комнате:\n{errors}")
        else:
            self.bot.send_message(message.from_user.id, f"Вы успешно присоединились к комнате!")
        send_action_keyboard(self.bot, message.from_user.id)
        del self
