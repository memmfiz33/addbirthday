from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from sqlalchemy import create_engine, text, and_
from databaseOperations.models import Birthdays, Notification  # замените на имя вашего модуля
import datetime
import threading
from databaseOperations.models import get_session

# Импортируйте настроенный логгер
from logger.logger import logger

# Создайте подключение к базе данных
def create_notifications():
    session = get_session()
    try:
        # Найдите все активные записи в таблице birthdays
        active_birthdays = session.query(Birthdays).filter(and_(Birthdays.record_status=='ACTIVE', Birthdays.is_scheduled==False)).all()

        for birthday in active_birthdays:
            # Логируем информацию о записи перед созданием даты
            logger.info(f'Processing birthday {birthday.id} with date {birthday.birth_date}')

            # Получите текущую дату и время
            now = datetime.datetime.now()

            try:
                # Если дата рождения - 29 февраля
                if birthday.birth_date.month == 2 and birthday.birth_date.day == 29:
                    # Найдите ближайший високосный год, начиная с следующего года
                    leap_year = now.year + 1
                    while not (leap_year % 4 == 0 and (leap_year % 100 != 0 or leap_year % 400 == 0)):
                        leap_year += 1

                    # Установите scheduled_time на 29 февраля ближайшего високосного года
                    scheduled_time = now.replace(year=leap_year, month=2, day=29, hour=9, minute=0, second=0)
                else:
                    # Создайте дату рождения для текущего года
                    birth_date_this_year = now.replace(month=birthday.birth_date.month, day=birthday.birth_date.day)

                    # Если дата рождения уже прошла в этом году, установите scheduled_time на следующий год
                    if now > birth_date_this_year:
                        scheduled_time = now.replace(year=now.year + 1, month=birthday.birth_date.month, day=birthday.birth_date.day,
                                                     hour=7, minute=0, second=0)
                    # В противном случае установите scheduled_time на текущий год
                    else:
                        scheduled_time = now.replace(year=now.year, month=birthday.birth_date.month, day=birthday.birth_date.day,
                                                     hour=7, minute=0, second=0)
            except Exception as e:
                logger.error(f'Error processing birthday {birthday.id}: {e}')
                continue

            # Создайте новую запись в таблице notifications
            if birthday.birth_date.year == 1900:
                notification_text = f'Сегодня {birthday.birth_person} празднует свой день рождения, не забудьте поздравить!'
            else:
                age = now.year - birthday.birth_date.year
                notification_text = f'Сегодня {birthday.birth_person} празднует {age} день рождения, не забудьте поздравить!'

            notification = Notification(
                user_telegram_id=birthday.user_telegram_id,
                birthdays_id=birthday.id,
                birth_date=birthday.birth_date,
                scheduled_time=scheduled_time,
                notification_status='CREATED',
                lastmodified=datetime.datetime.now(),
                notification_text=notification_text
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
scheduler.add_job(create_notifications, 'interval', minutes=1)

# Запустите планировщик в отдельном потоке
scheduler_thread = threading.Thread(target=scheduler.start)
scheduler_thread.start()