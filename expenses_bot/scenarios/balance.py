import expenses_bot.api
import expenses_bot.runtime_constants
from expenses_bot.utils import show_money


class Balance:
    def __init__(self, bot):
        self.bot = bot
        self.room_id = ""
        self.start = self.get_balance

    def get_balance(self, message):
        self.room_id = message.text.split("id")[-1]
        room = expenses_bot.api.get_room(self.room_id)
        if 'errors' in room:
            self.bot.send_message(message.from_user.id,
                                  "Произошла ошибка. К сожалению, в данный момент вы не можете узнать свой баланс")
        else:
            for member in room['data']['getRoom']['members']:
                if member['id'] == str(message.from_user.id):
                    balance = member['debit']
                    text = show_money(balance) + "руб."
                    description = f"Вам должны {show_money(-balance)}" if member['debit'] < 0 else (
                        "Вы ничего не должны и вам ничего не должны" if balance == 0 else
                        f"Вы должны {show_money(balance)}")
                    self.bot.send_message(message.from_user.id,
                                          f"Ваш баланс: {text}({description})")
        self.bot.send_message(message.from_user.id, "Выбери действие:",
                              reply_markup=expenses_bot.runtime_constants.START_MSG)
