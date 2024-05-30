import requests
import logging

logging.basicConfig(level=logging.DEBUG)

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
        "Authorization": "Api-Key AQVN0EQVoGHolgHAkPr3d9CMaDfD1zPH-ieawoNk"
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

    return result

if __name__ == "__main__":
    message = generate_birthday_message()
    if message:
        logging.info("Generated birthday message: %s", message)
    else:
        logging.error("Failed to generate birthday message")
