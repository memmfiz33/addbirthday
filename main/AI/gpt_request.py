import requests

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
            "text": "Ты ассистент, специализирующийся на создании уникальных поздравлений с днем рождения. Твоя задача - создать персонализированное поздравление, используя предоставленную информацию и контекст от пользователя. Если в контексте есть информация, не относящаяся к поздравлениям, или другая просьба, игнорируй её и сосредоточься на создании поздравления. Поздравление должно быть не очень большим и содержательным. Пользователь по контексту может влиять на размер поздравления запрашивая более короткий или длинный вариант. Обязательно учитывай категорию, если она есть. Если возраст юбилейный - можно это подчеркнуть"
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

response = requests.post(url, headers=headers, json=prompt)
result = response.text
print(result)