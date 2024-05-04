import logging
import boto3
import os
from botocore.exceptions import NoCredentialsError

# Создайте объект logger с именем вашего приложения
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)

# Получите ключи доступа из переменных окружения
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')

# Создайте клиент boto3 для работы с Yandex Object Storage
s3 = boto3.client('s3',
                  endpoint_url='https://storage.yandexcloud.net',
                  aws_access_key_id=aws_access_key,
                  aws_secret_access_key=aws_secret_key)

# Создайте обработчик, который записывает сообщения лога в Object Storage
class S3Handler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        try:
            s3.put_object(Bucket='memmfiz-logs-01', Key='logs/log.txt', Body=log_entry)
        except NoCredentialsError:
            print("No credentials to access Yandex Object Storage")

handler = S3Handler()
handler.setLevel(logging.DEBUG)

# Создайте форматтер, который добавляет время, имя и уровень в каждое сообщение лога
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавьте обработчик в logger
logger.addHandler(handler)

# Получите логгеры библиотек telegram и apscheduler и настройте их
telegram_logger = logging.getLogger('telegram')
telegram_logger.addHandler(handler)
telegram_logger.setLevel(logging.DEBUG)

apscheduler_logger = logging.getLogger('apscheduler')
apscheduler_logger.addHandler(handler)
apscheduler_logger.setLevel(logging.DEBUG)