import logging
import boto3
import os
from botocore.exceptions import NoCredentialsError
import datetime

# Отключите логи от urllib3
logging.getLogger('urllib3').setLevel(logging.WARNING)
# Отключите логи от botocore
logging.getLogger('botocore').setLevel(logging.WARNING)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = datetime.datetime.now()
        self.filename = self.start_time.strftime("%d%m%Y-%H-%M-%S.txt")
        self.log_data = ""

        # Создайте файл сразу после старта приложения
        s3.put_object(Bucket='memmfiz-logs-01', Key='logs/' + self.filename, Body=self.log_data)
        logger.info("Successfully created log file on Yandex Object Storage")

    def emit(self, record):
        log_entry = self.format(record)
        try:
            # Если прошло более 24 часов с начала сессии, начните новую сессию
            if datetime.datetime.now() - self.start_time > datetime.timedelta(hours=24):
                self.start_time = datetime.datetime.now()
                self.filename = self.start_time.strftime("%d%m%Y-%H-%M-%S.txt")
                self.log_data = ""

            # Добавьте новую запись к существующим данным
            self.log_data += log_entry + "\n"

            # Загрузите данные на S3 каждые 100 записей
            if len(self.log_data.split("\n")) >= 100:
                s3.put_object(Bucket='memmfiz-logs-01', Key='logs/' + self.filename, Body=self.log_data)
                self.log_data = ""
                logger.info("Successfully uploaded logs to Yandex Object Storage")
        except Exception as e:
            logger.error(f"Error writing to Yandex Object Storage: {e}")

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