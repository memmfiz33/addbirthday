from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .addbirthday import addbirthday_command
from databaseOperations.addNewRecord import save_text

def is_leap(year: int) -> bool:
    # функция проверки на високосный год
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return True
    return False


def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    if query.data == 'addbirthday':
        addbirthday_command(update, context)

    elif context.user_data['stage'] == 'awaiting_birth_age' and query.data == 'skip':
        context.user_data['birth_age'] = 1900
        context.user_data['stage'] = 'awaiting_birth_month'
        context.user_data['is_leap'] = is_leap(context.user_data['birth_age'])

        keyboard = [
            [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                 reply_markup=reply_markup)

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