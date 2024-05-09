from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .support import support_command

def info_command(update: Update, context: CallbackContext) -> None:
    info_text = """
    ТортоБот 🎂🤖 - это маленький помощник, никогда не забывающий о важных датах. 

    С его помощью вы всегда будете помнить о днях рождения ваших друзей и близких, и получать напоминания.

    Основные команды:

        /start - Стартовое меню
        /addbirthday - Добавить новый день рождения
        /showall - Показать все записи
        /delete - Удалить запись
        /info - Справочная информация
        /support - Написать автору об ошибке или пожелание
    """

    keyboard = [
        [InlineKeyboardButton("Написать автору", callback_data='support'),
         InlineKeyboardButton("Сообщить о проблеме", callback_data='support')],
        [InlineKeyboardButton("Отмена", callback_data='start')]  # новая кнопка
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query is not None:
        update.callback_query.message.reply_text(info_text, reply_markup=reply_markup)
    else:
        update.message.reply_text(info_text, reply_markup=reply_markup)