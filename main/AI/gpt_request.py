import requests
import logging
import json
from databaseOperations.models import create_conn
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.DEBUG)
load_dotenv()  # вызовите эту функцию, чтобы загрузить переменные окружения из .env файла

YGPT_TOKEN = os.getenv('YGPT_TOKEN')  # получение значения токена из .env файла


def generate_birthday_message():
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
                "text": "Это любимый папуля у него юбилей"
            },
            {
                "role": "user",
                "text": "Имя: Папа; Возраст: 50, Пол: М"
            },
            {
                "role": "user",
                "text": "Категория: Родители"
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": YGPT_TOKEN
    }

    logging.info("Sending request to Yandex API with prompt: %s", prompt)

    try:
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()
        logging.info("Received response: %s", response.text)
    except requests.exceptions.RequestException as e:
        logging.error("Request to Yandex API failed: %s", e)
        return None

    try:
        result = response.json()["result"]["alternatives"][0]["message"]["text"].strip()
        logging.debug("Parsed result: %s", result)
    except (KeyError, IndexError, ValueError) as e:
        logging.error("Failed to parse response from Yandex API: %s", e)
        return None

    # Save to the database
    conn = create_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO gpt_requests (user_telegram_id, full_request_text, full_response_text, status) VALUES (%s, %s, %s, %s)",
                (123456,  # replace with actual user id
                 json.dumps(prompt),  # convert dict to string before save
                 result,
                 response.status_code))
    conn.commit()  # don't forget to commit the changes
    cur.close()
    conn.close()

    return result


if __name__ == "__main__":
    message = generate_birthday_message()
    if message:
        logging.info("Generated birthday message: %s", message)
    else:
        logging.error("Failed to generate birthday message")