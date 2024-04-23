from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Filters
from datetime import datetime
import logging
import psycopg2

TOKEN: Final = '6948226088:AAEotmW-2QhzP4SyzIz0biORxpB-0nv4nkY'
BOT_USERNAME: Final = '@memmfiz01'
state = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def create_conn():
    conn = psycopg2.connect(
        dbname="addbirthday",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    return conn


def start_command(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton('Добавить ДР!', callback_data='addbirthday')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)


def info_command(update: Update, context: CallbackContext) -> None:
    info_text = """
    Этот бот поможет вам запомнить и отслеживать дни рождения.
    Вот что я могу:
    /start - начать работу со мной
    /addbirthday - добавить новый день рождения
    /info - показать эту помощь
    """
    update.message.reply_text(info_text)


def save_text(user_id: int, first_name: str, last_name: str, username: str, messages: dict) -> None:
    conn = create_conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM birthdays')
    messages['id'] = cur.fetchone()[0] + 1
    messages['user_name'] = f"{first_name} {last_name}" if last_name else first_name
    messages['user_telegram_id'] = user_id
    messages['user_telegram_name'] = username
    messages['last_modified'] = datetime.now().isoformat(timespec='seconds')
    insert_query = f"""
        INSERT INTO birthdays (birth_person, birth_month, birth_date, birth_age, sex, id, user_name, user_telegram_id, user_telegram_name, last_modified)
        VALUES ('{messages['birth_person']}', '{messages['birth_month']}', {messages['birth_date']}, {messages['birth_age']}, 
        '{messages['sex']}',  {messages['id']}, '{messages['user_name']}', {messages['user_telegram_id']}, 
        '{messages['user_telegram_name']}', '{messages['last_modified']}');
    """
    cur.execute(insert_query)
    conn.commit()
    cur.close()
    conn.close()

def addbirthday_command(update: Update, context: CallbackContext) -> None:
    state[update.effective_user.id] = ['awaiting_birth_person']
    context.bot.send_message(chat_id=update.effective_chat.id, text='Как зовут именинника?')


def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.effective_user.id
    if user_id in state:
        if state[user_id][0] == 'awaiting_birth_person':
            state[user_id] = ['awaiting_birth_month', {'birth_person': text}]
            keyboard = [
                [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                     reply_markup=reply_markup)
        elif state[user_id][0] == 'awaiting_birth_date':
            state[user_id][1]['birth_date'] = text
            state[user_id][0] = 'awaiting_birth_age'
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите год рождения')
        elif state[user_id][0] == 'awaiting_birth_age':
            state[user_id][1]['birth_age'] = text
            state[user_id][0] = 'awaiting_sex'
            keyboard = [
                [InlineKeyboardButton(option, callback_data=option) for option in ['М', 'Ж']],
                [InlineKeyboardButton("Пропустить", callback_data='Пропустить')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите пол', reply_markup=reply_markup)


def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()
    if query.data == 'addbirthday':
        addbirthday_command(update, context)
    elif state[user_id][0] == 'awaiting_birth_month':
        state[user_id][1]['birth_month'] = query.data
        state[user_id][0] = 'awaiting_birth_date'
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите дату рождения')
    elif state[user_id][0] == 'awaiting_sex':
        state[user_id][1]['sex'] = query.data
        save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                  update.effective_user.username, state[user_id][1])
        del state[user_id]
        context.bot.send_message(chat_id=update.effective_chat.id, text='Спасибо, данные сохранены')


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