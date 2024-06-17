import requests
import logging
import json
from databaseOperations.models import create_conn
from dotenv import load_dotenv
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

YGPT_TOKEN = os.getenv('YGPT_TOKEN')


def calculate_age(birth_date):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def get_last_response(user_telegram_id):
    conn = create_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT full_response_text 
        FROM gpt_requests 
        WHERE user_telegram_id = %s 
        ORDER BY last_modified_date DESC 
        LIMIT 1
    """, (user_telegram_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


def get_category_context(category):
    return category


def generate_birthday_message(record_id, user_telegram_id, user_context):
    conn = create_conn()
    cur = conn.cursor()
    cur.execute("SELECT birth_person, birth_date, category FROM birthdays WHERE id = %s", (record_id,))
    record = cur.fetchone()
    cur.close()
    conn.close()

    if not record:
        logging.error("Record with id %s not found", record_id)
        return None

    birth_person, birth_date, category = record
    age = calculate_age(birth_date)

    messages = [
        {
            "role": "system",
            "text": ("Ты ассистент, специализирующийся на создании уникальных поздравлений с днем рождения. "
                     "Твоя задача - создать персонализированное поздравление, используя предоставленную информацию и контекст от пользователя. "
                     "Список правил при генерации сообщений:\n"
                     "1. Сообщение должно быть от первого лица и не включать подписи.\n"
                     "2. При обращении должно быть или имя, или имя и отчество (при наличии), но не должно быть фамилии.\n"
                     "3. Игнорируй информацию, не относящуюся к поздравлениям.\n"
                     "4. Поздравление должно быть содержательным и учитывать категорию.\n"
                     "5. По умолчанию, поздравление должно быть неформальным, если указано имя или имя+фамилия.\n"
                     "6. По умолчанию, поздравление должно быть более формальным, если указано имя и отчество или фамилия, имя и отчество.\n"
                     "7. Если дата рождения 123 или более лет, не указывать её в поздравлении.\n"
                     "8. Если дата не юбилейная и до 40 лет, не указывать её в поздравлении.\n"
                     "9. Сообщение должно адаптироваться под категорию человека, если нет предыдущего сообщения.\n"
                     "10. Если контекст и имя не позволяют сгененрировать поздравление ответить: Генерация поздравления для данной записи невозможна"
                     "11. Если есть сообщение '#SYS-Предыдущее сообщение:', игнорировать категорию и изменять предыдущее сообщение."
                     )
        }
    ]

    previous_message = get_last_response(user_telegram_id)
    if previous_message:
        messages.append({
            "role": "user",
            "text": f"#SYS-Предыдущее сообщение: {previous_message}"
        })

    messages.append({
        "role": "user",
        "text": user_context
    })

    messages.append({
        "role": "user",
        "text": f"Имя: {birth_person}; Возраст: {age}, Категория: {category}"
    })

    prompt = {
        "modelUri": "gpt://b1gdrj9d7rqov4qcij8m/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 1.0,
            "maxTokens": "500"
        },
        "messages": messages
    }

    readable_request = "\n".join([f"{msg['role']}: {msg['text']}" for msg in messages if msg["role"] == "user"])

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": YGPT_TOKEN
    }

    logging.info("Sending request to Yandex API with prompt: %s", prompt)

    result = None

    try:
        response = requests.post(url, headers=headers, json=prompt, timeout=60)
        response.raise_for_status()
        logging.info("Received response: %s", response.text)
        result = response.json()["result"]["alternatives"][0]["message"]["text"].strip()
        logging.debug("Parsed result: %s", result)
        status = "GENERATED"

        # Проверка на неподходящий контент
        if "К сожалению, я не могу ничего сказать об этом. Давайте сменим тему?" in result:
            result = ("Извините, но ваш запрос содержит недопустимый или неподходящий контент. "
                      "Давайте попробуем сформулировать ваш запрос по-другому.")

    except requests.exceptions.RequestException as e:
        logging.error("Request to Yandex API failed: %s", e)
        status = "ERROR"
    except (KeyError, IndexError, ValueError) as e:
        logging.error("Failed to parse response from Yandex API: %s", e)
        status = "ERROR"

    conn = create_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO gpt_requests (user_telegram_id, full_request_text, full_response_text, status) VALUES (%s, %s, %s, %s)",
            (user_telegram_id, readable_request, result if result else '', status))
        conn.commit()
    except Exception as e:
        logging.error("Failed to insert into database: %s", e)
    finally:
        cur.close()
        conn.close()

    return result


if __name__ == "__main__":
    message = generate_birthday_message(1, 319661378,
                                        "Это тестовый контекст")  # Replace 1 with the actual record_id and user_id for testing
    if message:
        logging.info("Generated birthday message: %s", message)
    else:
        logging.error("Failed to generate birthday message")