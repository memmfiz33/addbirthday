from telegram import Update
from telegram.ext import CallbackContext

def addbirthday_command(update: Update, context: CallbackContext) -> None:
    context.user_data['stage'] = 'awaiting_birth_person'
    context.bot.send_message(chat_id=update.effective_chat.id, text='Как зовут именинника?')