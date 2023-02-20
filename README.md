# Telegram бот для отслеживания долгов при совместных покупках

## Ссылки
[Начать пользоваться](http://t.me/cooperative_expenses_bot)

[Серверная часть бота](https://github.com/KPaderin/server-expenses-bot)

## Запуск
Чтобы запустить собственный аналог бота необходимо:
1. Запустите сервер по гайду из [репозитория](https://github.com/KPaderin/server-expenses-bot)
2. В директории `expenses_bot/` создайте файл `private_constants.py` и определите в нем следующие константы:
   1. `TOKEN` - токен telegram-бота
   2. `API_URL` - URL запущенного сервера из пункта 1.
   3. `DB_NAME` - Название базы данных sqlite, которая будет использоваться для хранения состояния бота
3. Установите зависимости: `python3 -m pip install -r requirements.txt`
4. `python3 expenses_bot/bot.py`