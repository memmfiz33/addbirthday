from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker
from databaseOperations.models import Birthdays, Notification  # замените на имя вашего модуля
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

def create_notifications():
    # Создайте новую сессию
    session = Session()

    try:
        session = Session()
        session.execute(text('SELECT 1'))
        session.close()
        print('Database connection successful')
    except Exception as e:
        print('Failed to connect to database:', e)
    try:
        # Найдите все активные записи в таблице birthdays
        active_birthdays = session.query(Birthdays).filter(and_(Birthdays.record_status=='ACTIVE', Birthdays.is_scheduled==False)).all()

        for birthday in active_birthdays:
            # Создайте новую запись в таблице notifications
            notification = Notification(
                user_telegram_id=birthday.user_telegram_id,
                birthdays_id=birthday.id,
                birth_date=birthday.birth_date,
                scheduled_time=datetime.datetime.now().replace(month=birthday.birth_date.month, day=birthday.birth_date.day, hour=9, minute=0, second=0),
                notification_status='CREATED',
                lastmodified=datetime.datetime.now(),
                notification_text=f'Сегодня у {birthday.birth_person} день рождения, не забудьте поздравить!'
                # добавьте это поле
            )

            # Добавьте новую запись в сессию
            session.add(notification)

            # Обновите запись birthdays
            birthday.is_scheduled = True
            birthday.lastmodified=datetime.datetime.now()
            session.add(birthday)

            # Сохраните изменения
            session.commit()

            logger.info(f'Notification created for birthday {birthday.id}')
    except Exception as e:
        logger.error(f'Error in create_notifications: {e}')
    finally:
        # Закройте сессию
        session.close()

# Создайте планировщик задач
scheduler = BackgroundScheduler(timezone=utc)

# Вызовите функцию сразу при запуске
create_notifications()

# Добавьте функцию в планировщик
scheduler.add_job(create_notifications, 'interval', hours=24)

# Запустите планировщик в отдельном потоке
scheduler_thread = threading.Thread(target=scheduler.start)
scheduler_thread.start()