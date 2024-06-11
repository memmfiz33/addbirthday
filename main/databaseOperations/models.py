from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, TIMESTAMP, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

Base = declarative_base()

def create_conn():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
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
    lastmodified = Column(TIMESTAMP)
    error_logs = Column(Text)


class Birthdays(Base):
    __tablename__ = 'birthdays'

    id = Column(Integer, primary_key=True)
    user_name = Column(Text)
    user_telegram_id = Column(Integer)
    user_telegram_name = Column(Text)
    birth_person = Column(DateTime)
    last_modified = Column(DateTime)
    category = Column(Text)
    birth_date = Column(DateTime)
    record_status = Column(Text)
    is_scheduled = Column(Boolean)


class Support(Base):
    __tablename__ = 'support'

    id = Column(Integer, primary_key=True)
    user_name = Column(Text)
    user_telegram_id = Column(Integer)
    user_telegram_name = Column(Text)
    support_text = Column(Text)
    timestamp = Column(DateTime)
    is_sent = Column(Boolean)


class GptRequests(Base):
    __tablename__ = 'gpt_requests'

    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(BigInteger, nullable=False)
    full_request_text = Column(Text, nullable=False)
    full_response_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    last_modified_date = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')