from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# sqlalchemy db connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/addbirthday')
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

Base = declarative_base()

# Функция для создания низкоуровневого подключения к базе данных
def create_conn():
    conn = psycopg2.connect(
        dbname="addbirthday",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    return conn

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer)
    birthdays_id = Column(Integer)
    birth_date = Column(DateTime)
    scheduled_time = Column(DateTime)
    notification_text = Column(Text)
    notification_status = Column(String)
    lastmodified = Column(TIMESTAMP)  # Используйте TIMESTAMP вместо Timestamp
    error_logs = Column(Text)

class Birthdays(Base):
    __tablename__ = 'birthdays'

    id = Column(Integer, primary_key=True)  # Добавьте знак равенства (=)
    user_name = Column(Text)
    user_telegram_id = Column(Integer)
    user_telegram_name = Column(Text)
    birth_person = Column(DateTime)
    last_modified = Column(DateTime)
    sex = Column(Text)
    birth_date = Column(DateTime)
    record_status = Column(Text)
    is_scheduled = Column(Boolean)