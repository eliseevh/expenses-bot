import telebot

from expenses_bot import runtime_constants


def show_money(cost: int) -> str:
    if cost < 0:
        sign = "-"
        cost = -cost
    else:
        sign = ""
    higher = str(cost // 100)
    lower = str(cost % 100)
    if len(lower) == 1:
        lower = "0" + lower
    return sign + higher + "." + lower


def check_cancel(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    if message.text == runtime_constants.BUTTON_CANCEL.text:
        send_action_keyboard(bot, message.from_user.id)
        return True
    return False


def send_action_keyboard(bot: telebot.TeleBot, user_id: int) -> None:
    bot.send_message(user_id, "Выбери действие:", reply_markup=runtime_constants.ACTION_MARKUP)
