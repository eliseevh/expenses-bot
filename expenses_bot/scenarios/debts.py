import expenses_bot.api
import expenses_bot.runtime_constants
from expenses_bot.utils import show_money


class Debts:
    def __init__(self, bot):
        self.bot = bot
        self.room_id = ""
        self.start = self.get_debts

    def get_debts(self, message):
        self.room_id = message.text.split("id")[-1]
        room = expenses_bot.api.get_room(self.room_id)
        if 'errors' in room:
            self.bot.send_message(message.from_user.id,
                                  "Произошла ошибка. К сожалению, в данный момент вы "
                                  "не можете узнать кому вы должны перевести деньги")
        else:
            members = room['data']['getRoom']['members']
            user = list(filter(lambda member: member['id'] == str(message.from_user.id), members))[0]
            if user['debit'] < 0:
                members.sort(key=lambda x: x['debit'], reverse=True)
                current = user['debit']
                result = []
                for member in members:
                    if member['debit'] + current < 0:
                        result.append((member['name'], member['debit']))
                        current += member['debit']
                    else:
                        result.append((member['name'], -current))
                        break
                text = "\n".join(map(lambda member: f"{member[0]}: {show_money(member[1])}", result))
                self.bot.send_message(message.from_user.id, f"Вы должны заплатить:\n{text}")
            else:
                self.bot.send_message(message.from_user.id, "Вы никому не должны ничего платить")
        self.bot.send_message(message.from_user.id, "Выбери действие:",
                              reply_markup=expenses_bot.runtime_constants.START_MSG)
