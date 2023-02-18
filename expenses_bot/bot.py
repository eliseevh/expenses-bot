import telebot
from telebot import types

import private_constants
from expenses_bot.database.user_state import UserStateStorage
from expenses_bot.scenarios import STATE_TO_FUNCTION

bot = telebot.TeleBot(private_constants.TOKEN, suppress_middleware_excepions=True)


@bot.message_handler(content_types=["text"])
def message_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    with UserStateStorage(private_constants.DB_NAME) as user_state:
        state = user_state.get_state(user_id)
        if state == -1:
            user_state.set_state(user_id, 0)
            state = 0
    STATE_TO_FUNCTION[state](bot, message)


if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            print("[MAIN LOOP] [!ERROR!]", e)
            print("Restarting bot")
