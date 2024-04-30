import time
import datetime
from telegram import Bot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseOperations.models import Notification, Birthdays

engine = create_engine('postgresql://postgres:postgres@localhost:5432/addbirthday')
Session = sessionmaker(bind=engine)

def send_notification(bot: Bot, notification: Notification, session):
    now = datetime.datetime.now()
    time_difference = now - notification.scheduled_time
    if time_difference.total_seconds() > 15 * 60 * 60:  # 15 hours in seconds
        month_names = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        birthday = session.query(Birthdays).filter(Birthdays.id == notification.birthdays_id).first()
        if birthday:
            birth_person = birthday.birth_person
            notification.notification_text = f"{notification.birth_date.day} {month_names[notification.birth_date.month - 1]} был день рождения у контакта {birth_person}. Можете поздравить, если это еще актуально"
    bot.send_message(chat_id=notification.user_telegram_id, text=notification.notification_text)
    notification.notification_status = 'SENT'
    notification.lastmodified = datetime.datetime.now()
    session.commit()

def scheduler_for_notifications(bot_token: str):
    bot = Bot(bot_token)
    session = Session()
    while True:
        now = datetime.datetime.now()
        notifications = session.query(Notification).filter(Notification.notification_status == 'CREATED').all()
        for notification in notifications:
            if notification.scheduled_time <= now:
                send_notification(bot, notification, session)
        if not any(notification.scheduled_time > now for notification in notifications):
            break
        time.sleep(60)  # Pause to avoid unnecessary CPU usage