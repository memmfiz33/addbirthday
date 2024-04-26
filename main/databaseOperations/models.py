from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer)
    birthdays_id = Column(Integer)
    birth_date = Column(DateTime)
    scheduled_time = Column(DateTime)
    notification_text = Column(Text)
    notification_status = Column(String)
    lastmodified = Column(DateTime)
    error_logs = Column(Text)