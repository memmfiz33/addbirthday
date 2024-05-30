import requests
import logging

logging.basicConfig(level=logging.DEBUG)

def generate_birthday_message(name, age, gender, category, context=""):
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
                         "Если в контексте есть информация, не относящаяся к поздравлениям, или другая просьба, игнорируй её и сосредоточься на создании поздравления. "
                         "Поздравление должно быть не очень большим и содержательным. Пользователь по контексту может влиять на размер поздравления запрашивая более короткий или длинный вариант. "
                         "Обязательно учитывай категорию, если она есть. Если возраст юбилейный - можно это подчеркнуть")
            },
            {
                "role": "user",
                "text": context
            },
            {
                "role": "user",
                "text": f"Имя: {name}; Возраст: {age}, Пол: {gender}"
            },
            {
                "role": "user",
                "text": f"Категория: {category}"
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key YOUR_YANDEX_API_KEY"
    }

    logging.info("Sending request to Yandex API with prompt: %s", prompt)

    try:
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()  # Проверка наличия ошибок HTTP
        logging.info("Received response: %s", response.text)
    except requests.exceptions.RequestException as e:
        logging.error("Request to Yandex API failed: %s", e)
        return None

    try:
        result = response.json().get("choices", [{}])[0].get("text", "").strip()
        logging.debug("Parsed result: %s", result)
    except (KeyError, IndexError, ValueError) as e:
        logging.error("Failed to parse response from Yandex API: %s", e)
        return None

    return result
