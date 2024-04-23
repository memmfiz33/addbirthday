from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def start_command(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton('Добавить ДР!', callback_data='addbirthday')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)