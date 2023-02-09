import telebot
import private_constants
import runtime_constants
from create_room import CreateRoom

bot = telebot.TeleBot(private_constants.TOKEN)


@bot.callback_query_handler(lambda x: True)
def callback_handler(callback):
    if callback.data == runtime_constants.BUTTON_CREATE_ROOM.callback_data:
        bot.send_message(callback.from_user.id, "Введи название комнаты:")
        bot.register_next_step_handler_by_chat_id(callback.from_user.id, CreateRoom(bot).start)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Выбери действие:", reply_markup=runtime_constants.START_MSG)


if __name__ == "__main__":
    bot.polling(non_stop=False)
