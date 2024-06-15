import time
import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from databaseOperations.models import Notification, Birthdays, get_session
from logger.logger import logger  # Импортируйте настроенный логгер


def send_notification(bot: Bot, notification: Notification, session):
    try:
        now = datetime.datetime.now()
        time_difference = now - notification.scheduled_time
        if time_difference.total_seconds() > 15 * 60 * 60:  # 15 hours in seconds
            month_names = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября",
                           "Октября", "Ноября", "Декабря"]
            birthday = session.query(Birthdays).filter(Birthdays.id == notification.birthdays_id).first()
            if birthday:
                birth_person = birthday.birth_person
                notification.notification_text = f"{notification.birth_date.day} {month_names[notification.birth_date.month - 1]} был день рождения у контакта {birth_person}. Можете поздравить, если это еще актуально"

        keyboard = [
            [InlineKeyboardButton("🎉 Сгенерировать сообщение", callback_data=f"generate:{notification.birthdays_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=notification.user_telegram_id, text=notification.notification_text,
                         reply_markup=reply_markup)

        notification.notification_status = 'SENT'
        notification.lastmodified = datetime.datetime.now()
        session.commit()
        logger.info(f'Successfully sent notification to {notification.user_telegram_id}')
    except Exception as e:
        notification.notification_status = 'ERROR'
        session.commit()
        logger.error(f'Failed to send notification to {notification.user_telegram_id} due to {e}')


def scheduler_for_notifications(bot_token: str):
    bot = Bot(bot_token)
    session = get_session()
    while True:
        now = datetime.datetime.now()
        notifications = session.query(Notification).filter(Notification.notification_status == 'CREATED').all()
        for notification in notifications:
            if notification.scheduled_time <= now:
                send_notification(bot, notification, session)
        if not any(notification.scheduled_time > now for notification in notifications):
            break
        time.sleep(60)  # Pause to avoid unnecessary CPU usage
