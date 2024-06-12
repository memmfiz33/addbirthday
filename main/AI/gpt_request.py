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

def generate_birthday_message(record_id, user_telegram_id, user_context):
    conn = create_conn()
    cur = conn.cursor()
    # Обновляем запрос, чтобы использовать столбец category вместо sex
    cur.execute("SELECT birth_person, birth_date, category FROM birthdays WHERE id = %s", (record_id,))
    record = cur.fetchone()
    cur.close()
    conn.close()

    if not record:
        logging.error("Record with id %s not found", record_id)
        return None

    birth_person, birth_date, category = record
    age = calculate_age(birth_date)

    prompt = {
        "modelUri": "gpt://b1gdrj9d7rqov4qcij8m/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 1.0,
            "maxTokens": "500"
        },
        "messages": [
            {
                "role": "system",
                "text": ("Ты ассистент, специализирующийся на создании уникальных поздравлений с днем рождения. "
                         "Твоя задача - создать персонализированное поздравление, используя предоставленную информацию и контекст от пользователя. "
                         "Игнорируй информацию, не относящуюся к поздравлениям. Поздравление должно быть содержательным и учитывать категорию.")
            },
            {
                "role": "user",
                "text": user_context
            },
            {
                "role": "user",
                "text": f"Имя: {birth_person}; Возраст: {age}, Категория: {category}"
            }
        ]
    }

    readable_request = "\n".join(
        [f"{msg['role']}: {msg['text']}" for msg in prompt["messages"] if msg["role"] == "user"])

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": YGPT_TOKEN
    }

    logging.info("Sending request to Yandex API with prompt: %s", prompt)

    result = None

    try:
        # Устанавливаем таймаут в 60 секунд
        response = requests.post(url, headers=headers, json=prompt, timeout=60)
        response.raise_for_status()
        logging.info("Received response: %s", response.text)
        result = response.json()["result"]["alternatives"][0]["message"]["text"].strip()
        logging.debug("Parsed result: %s", result)
        status = "GENERATED"
    except requests.exceptions.RequestException as e:
        logging.error("Request to Yandex API failed: %s", e)
        status = "ERROR"
    except (KeyError, IndexError, ValueError) as e:
        logging.error("Failed to parse response from Yandex API: %s", e)
        status = "ERROR"

    # Вставка в базу данных должна быть в блоке finally, чтобы всегда выполняться, независимо от того, была ли ошибка
    conn = create_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO gpt_requests (user_telegram_id, full_request_text, full_response_text, status) VALUES (%s, %s, %s, %s)",
            (user_telegram_id,
             readable_request,
             result if result else '',
             status))
        conn.commit()
    except Exception as e:
        logging.error("Failed to insert into database: %s", e)
    finally:
        cur.close()
        conn.close()

    return result

if __name__ == "__main__":
    message = generate_birthday_message(1, 319661378, "Это тестовый контекст")  # Replace 1 with the actual record_id and user_id for testing
    if message:
        logging.info("Generated birthday message: %s", message)
    else:
        logging.error("Failed to generate birthday message")
