import psycopg2
from datetime import datetime
from .models import create_conn

def save_text(user_id: int, first_name: str, last_name: str, username: str, messages: dict) -> None:
    conn = create_conn()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM birthdays')
    count = cur.fetchone()
    if count is not None:
        messages['id'] = count[0] + 1

    messages['record_status'] = 'ACTIVE'  # добавляем статус ACTIVE
    messages['user_name'] = f"{first_name} {last_name}" if last_name else first_name
    messages['user_telegram_id'] = user_id
    messages['user_telegram_name'] = username
    messages['last_modified'] = datetime.now().isoformat(timespec='seconds')
    messages['is_scheduled'] = False  # set is_scheduled to False

    # формирование даты рождения
    birth_date = messages.get('birth_date')

    # Сохраняем дату в базе данных
    query = """
        INSERT INTO birthdays (
            birth_person, birth_date, category, id, user_name, 
            user_telegram_id, user_telegram_name, last_modified, record_status, is_scheduled
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        messages['birth_person'], birth_date, messages['category'],
        messages['id'], messages['user_name'], messages['user_telegram_id'],
        messages['user_telegram_name'], messages['last_modified'], messages['record_status'], messages['is_scheduled']
    )
    cur.execute(query, values)
    conn.commit()

    cur.close()
    conn.close()
