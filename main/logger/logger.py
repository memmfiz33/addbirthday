import logging
import os
import datetime
import atexit

# Отключите логи от urllib3
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Создайте объект logger с именем вашего приложения
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)

# Создайте обработчик, который записывает сообщения лога в файл
class FileHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = datetime.datetime.now()
        self.session_number = self.get_session_number()
        # Путь для ВМ
        self.filename = f"/home/memmfiz_admin/addbirthday/main/logger/logs/{str(self.session_number).zfill(4)}_{self.start_time.strftime('%d%m%Y-%H-%M-%S')}.txt"
        # Путь, который был ранее (закомментирован)
        # self.filename = f"logger/logs/{str(self.session_number).zfill(4)}_{self.start_time.strftime('%d%m%Y-%H-%M-%S')}.txt"
        self.log_count = 0
        self.internal_logger = logging.getLogger('FileHandler')
        self.internal_logger.addHandler(logging.StreamHandler())
        atexit.register(self.close_file)

    def get_session_number(self):
        try:
            with open('/home/memmfiz_admin/addbirthday/main/logger/logs/session_number.txt', 'r') as f:
                session_number = int(f.read().strip())
        except FileNotFoundError:
            session_number = 0
        session_number += 1
        with open('/home/memmfiz_admin/addbirthday/main/logger/logs/session_number.txt', 'w') as f:
            f.write(str(session_number))
        return session_number

    def emit(self, record):
        log_entry = self.format(record)
        try:
            if datetime.datetime.now() - self.start_time > datetime.timedelta(hours=24):
                self.start_time = datetime.datetime.now()
                self.session_number = self.get_session_number()
                self.filename = f"/home/memmfiz_admin/addbirthday/main/logger/logs/{str(self.session_number).zfill(4)}_{self.start_time.strftime('%d%m%Y-%H-%M-%S')}.txt"
                self.log_count = 0

            with open(self.filename, 'a', encoding='utf-8') as f:  # Добавьте кодировку 'utf-8' здесь
                f.write(log_entry + "\n")
            self.log_count += 1
        except Exception as e:
            self.internal_logger.error(f"Error writing to file: {e}")
            raise e  # Добавлено: повторно поднимаем исключение, чтобы увидеть его в консоли

    def close_file(self):
        try:
            with open(self.filename, 'a') as f:
                f.close()
            self.internal_logger.info("Successfully closed log file")
        except Exception as e:
            self.internal_logger.error(f"Error closing log file: {e}")
            raise e  # Добавлено: повторно поднимаем исключение, чтобы увидеть его в консоли

if not os.path.exists('/home/memmfiz_admin/addbirthday/main/logger/logs'):
    os.makedirs('/home/memmfiz_admin/addbirthday/main/logger/logs')

handler = FileHandler()
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