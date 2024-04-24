import time
import datetime
from telegram import Bot


def notification_type1(bot: Bot):
    message = 'Привет-Медвед!'
    user_telegram_id = '319661378'  # укажите здесь существующий ID пользователя
    bot.send_message(chat_id=user_telegram_id, text=message)

def scheduler_for_notifications(bot_token: str):
    bot = Bot(bot_token)
    while True:
        now = datetime.datetime.now()
        if now.hour == 21 and now.minute == 25:
            notification_type1(bot)
        time.sleep(60)  # Приостановка для избежания ненужного использования CPU


# scheduler_for_notifications('ваш_токен_здесь')  # замените 'ваш_токен_здесь' на ваш собственный токен