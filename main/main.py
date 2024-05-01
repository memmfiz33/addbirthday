from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from handlers import start_command, addbirthday_command, info_command, handle_message, handle_button, delete_command
from databaseOperations.showAll import showall_command
from notifications.notify import scheduler_for_notifications
from notifications.create_notifications import create_notifications  # импортируйте вашу функцию
from notifications.delete_notifications import delete_notifications  # импортируйте вашу функцию
from handlers.support import support_command, handle_support  # импортируйте обработчики команды /support
from typing import Final
import threading
import logging

TOKEN: Final = '6948226088:AAEotmW-2QhzP4SyzIz0biORxpB-0nv4nkY'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    logging.info('Starting bot....')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('addbirthday', addbirthday_command))
    dp.add_handler(CommandHandler('info', info_command))
    dp.add_handler(CommandHandler('showall', showall_command))
    dp.add_handler(CommandHandler('delete', delete_command))
    dp.add_handler(CommandHandler('support', support_command))  # добавьте обработчик команды /support
    dp.add_handler(MessageHandler(Filters.text & Filters.reply, handle_support))  # добавьте обработчик ответа на команду /support
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
 # нотификации
    notification_thread = threading.Thread(target=scheduler_for_notifications, args=(TOKEN,), daemon=True)
    notification_thread.start()

# создание уведомлений
    create_notifications_thread = threading.Thread(target=create_notifications, daemon=True)
    create_notifications_thread.start()

# удаление уведомлений
    delete_notifications_thread = threading.Thread(target=delete_notifications, daemon=True)
    delete_notifications_thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()