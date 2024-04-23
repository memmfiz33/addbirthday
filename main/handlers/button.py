from telegram import Update
from telegram.ext import CallbackContext
from .addbirthday import addbirthday_command
from db import save_text


def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    if query.data == 'addbirthday':
        addbirthday_command(update, context)
    elif context.user_data['stage'] == 'awaiting_birth_month':
        context.user_data['birth_month'] = query.data
        context.user_data['stage'] = 'awaiting_birth_date'
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите дату рождения')
    elif context.user_data['stage'] == 'awaiting_sex':
        context.user_data['sex'] = query.data
        save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                  update.effective_user.username, context.user_data)
        del context.user_data['stage']
        context.bot.send_message(chat_id=update.effective_chat.id, text='Спасибо, данные сохранены')