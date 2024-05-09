from databaseOperations.models import Support, get_session
from telegram import Bot
from logger.logger import logger  # Импортируйте настроенный логгер
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

def start_support_notifications_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.UTC)  # указываем часовой пояс
    scheduler.add_job(create_support_notifications, 'interval', minutes=1)
    scheduler.start()

def create_support_notifications():
    logger.info("create_support_notifications called")  # добавьте это
    session = get_session()
    try:
        # Найдите все записи в таблице support, которые еще не были отправлены
        unsent_support_messages = session.query(Support).filter(Support.is_sent == False).all()

        # Проверьте, что unsent_support_messages не None
        if unsent_support_messages is not None:
            for message in unsent_support_messages:
                # Форматируйте сообщение
                user_name = message.user_name if message.user_name is not None else "-"
                user_telegram_name = message.user_telegram_name if message.user_telegram_name is not None else "-"
                user_telegram_id = message.user_telegram_id if message.user_telegram_id is not None else "-"
                timestamp = message.timestamp if message.timestamp is not None else "-"
                support_text = message.support_text if message.support_text is not None else "-"

                formatted_message = f"""
Новое сообщение от пользователя

Имя: {user_name}
Telegram имя: @{user_telegram_name}
User Telegram ID: {user_telegram_id}
Время: {timestamp}

Сообщение: {support_text}
"""

                # Отправьте сообщение админу
                bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                bot.send_message(chat_id=os.getenv('SUPPORT_ADMIN'), text=formatted_message)

                # Обновите запись в таблице support
                message.is_sent = True
                session.add(message)

                # Сохраните изменения
                session.commit()

                # Логирование
                logger.info(f"Отправлено сообщение поддержки от пользователя {user_telegram_id}")
    except Exception as e:
        # Логирование ошибок
        logger.error(f"Ошибка при отправке сообщения поддержки: {e}")
    finally:
        # Закройте сессию
        session.close()