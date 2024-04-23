from telegram import Update
from telegram.ext import CallbackContext

def info_command(update: Update, context: CallbackContext) -> None:
    info_text = """
    Этот бот поможет вам запомнить и отслеживать дни рождения.
    Вот что я могу:
    /start - начать работу со мной
    /addbirthday - добавить новый день рождения
    /info - показать эту помощь
    """
    update.message.reply_text(info_text)