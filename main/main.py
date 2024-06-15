import os
import sys
import threading
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logger.logger import logger

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from handlers import start_command, addbirthday_command, info_command, handle_message, handle_button, delete_command
from handlers.support import support_command, handle_support

from databaseOperations.showAll import showall_command

from notifications.notify import scheduler_for_notifications
from notifications.create_notifications import create_notifications
from notifications.delete_notifications import delete_notifications
from notifications.support_notifications import create_support_notifications, start_support_notifications_scheduler

from AI.ai_buttons import generate_message, handle_generate_callback, generate_birthday_message_handler

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def main() -> None:
    logger.info('Starting bot....')

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('addbirthday', addbirthday_command))
    dp.add_handler(CommandHandler('info', info_command))
    dp.add_handler(CommandHandler('showall', showall_command))
    dp.add_handler(CommandHandler('delete', delete_command))
    dp.add_handler(CommandHandler('support', support_command))

    dp.add_handler(MessageHandler(Filters.text & Filters.reply, handle_support))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    dp.add_handler(CallbackQueryHandler(generate_message, pattern='^generate_message$'))
    dp.add_handler(CallbackQueryHandler(handle_generate_callback, pattern='^generate:'))
    dp.add_handler(CallbackQueryHandler(handle_generate_callback, pattern='^generate_page:'))

    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text & Filters.reply, generate_birthday_message_handler))

    notification_thread = threading.Thread(target=scheduler_for_notifications, args=(TOKEN,), daemon=True)
    notification_thread.start()

    create_notifications_thread = threading.Thread(target=create_notifications, daemon=True)
    create_notifications_thread.start()

    delete_notifications_thread = threading.Thread(target=delete_notifications, daemon=True)
    delete_notifications_thread.start()

    start_support_notifications_scheduler()

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
