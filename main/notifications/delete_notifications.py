from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker
from databaseOperations.models import Birthdays, Notification, get_session
import datetime
import threading

# Создайте и настройте логгер
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Создайте подключение к базе данных
engine = create_engine('postgresql://postgres:postgres@localhost:5432/addbirthday')  # замените на вашу строку подключения
Session = sessionmaker(bind=engine)

def delete_notifications():
    session = get_session()
    try:
        # Найдите все удаленные записи в таблице birthdays, которые все еще запланированы
        deleted_birthdays = session.query(Birthdays).filter(and_(Birthdays.record_status=='DELETED', Birthdays.is_scheduled==True)).all()

        for birthday in deleted_birthdays:
            # Найдите соответствующую запись в таблице notifications
            notification = session.query(Notification).filter(Notification.birthdays_id==birthday.id).first()

            if notification:
                # Обновите запись в таблице notifications
                notification.notification_status = 'DELETED'
                notification.lastmodified = datetime.datetime.now()
                session.add(notification)

            # Обновите запись birthdays
            birthday.is_scheduled = False
            birthday.last_modified = datetime.datetime.now()
            session.add(birthday)

            # Сохраните изменения
            session.commit()

            logger.info(f'Notification deleted for birthday {birthday.id}')
    except Exception as e:
        logger.error(f'Error in delete_notifications: {e}')
    finally:
        # Закройте сессию
        session.close()

# Создайте планировщик задач
scheduler = BackgroundScheduler(timezone=utc)

# Вызовите функцию сразу при запуске
delete_notifications()

# Добавьте функцию в планировщик
scheduler.add_job(delete_notifications, 'interval', minutes=1)

# Запустите планировщик в отдельном потоке
scheduler_thread = threading.Thread(target=scheduler.start)
scheduler_thread.start()