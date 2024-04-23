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
    messages['id'] = cur.fetchone()[0] + 1
    messages['user_name'] = f"{first_name} {last_name}" if last_name else first_name
    messages['user_telegram_id'] = user_id
    messages['user_telegram_name'] = username
    messages['last_modified'] = datetime.now().isoformat(timespec='seconds')
    insert_query = f"""
        INSERT INTO birthdays (birth_person, birth_month, birth_date, birth_age, sex, id, user_name, user_telegram_id, user_telegram_name, last_modified)
        VALUES ('{messages['birth_person']}', '{messages['birth_month']}', {messages['birth_date']}, {messages['birth_age']}, 
        '{messages['sex']}',  {messages['id']}, '{messages['user_name']}', {messages['user_telegram_id']}, 
        '{messages['user_telegram_name']}', '{messages['last_modified']}');
    """
    cur.execute(insert_query)
    conn.commit()
    cur.close()
    conn.close()