from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


def start_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('🎂 Добавить ДР!', callback_data='addbirthday')],
        [InlineKeyboardButton('📖 Показать все записи', callback_data='showall')],
        [InlineKeyboardButton('🗑️ Удалить запись', callback_data='delete')],
        [InlineKeyboardButton('🎉 Создать поздравление', callback_data='generate_message')],  # Добавляем эту строку
        [InlineKeyboardButton('💡 Инфо и помощь', callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Если это обновление сообщения, используем update.message
    if update.message is not None:
        update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    # Если это обновление callback-запроса, используем update.callback_query.message
    elif update.callback_query is not None:
        update.callback_query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
