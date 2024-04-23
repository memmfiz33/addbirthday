from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from handlers import start_command, addbirthday_command, info_command, handle_message, handle_button
from typing import Final
import logging

TOKEN: Final = '6948226088:AAEotmW-2QhzP4SyzIz0biORxpB-0nv4nkY'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    logging.info('Starting bot....')
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('addbirthday', addbirthday_command))
    dp.add_handler(CommandHandler('info', info_command))
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()