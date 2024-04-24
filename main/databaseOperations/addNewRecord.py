import psycopg2
from datetime import datetime

def create_conn():
    conn = psycopg2.connect(
        dbname="addbirthday",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    return conn

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

    # формирование даты рождения
    birth_date = messages.get('birth_date')

    # Сохраняем дату в базе данных
    query = """
        INSERT INTO birthdays (
            birth_person, birth_date, sex, id, user_name, 
            user_telegram_id, user_telegram_name, last_modified, record_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        messages['birth_person'], birth_date, messages['sex'],
        messages['id'], messages['user_name'], messages['user_telegram_id'],
        messages['user_telegram_name'], messages['last_modified'], messages['record_status']
    )
    cur.execute(query, values)
    conn.commit()

    cur.close()
    conn.close()