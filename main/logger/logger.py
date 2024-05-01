import logging
import os
from datetime import datetime

# Создайте объект logger с именем вашего приложения
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)

# Получите текущую дату и время
now = datetime.now()

# Создайте уникальное имя файла с текущей датой и временем
filename = f'logs{now.strftime("%Y%m%d")}-{now.strftime("%H-%M-%S")}.log'

# Создайте путь к файлу лога
log_path = os.path.join('logger', 'logs', filename)

# Создайте путь к папке лога, если он еще не существует
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Создайте обработчик, который записывает сообщения лога в файл
handler = logging.FileHandler(log_path, encoding='utf-8')  # Добавьте аргумент encoding='utf-8'
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