from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from databaseOperations.models import create_conn
from databaseOperations.showAll import get_months
import logging

logging.basicConfig(level=logging.DEBUG)

def generate_message(update: Update, context: CallbackContext) -> None:
    conn = create_conn()
    cur = conn.cursor()

    user_id = update.effective_user.id
    record_offset = context.user_data.get('record_offset', 0)

    cur.execute("SELECT id, birth_person, birth_date FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s ORDER BY birth_person ASC LIMIT 10 OFFSET %s", (user_id, record_offset))

    keyboard = []
    records = cur.fetchall()

    for id, name, birth_date in records:
        month_name_russian = get_months()[birth_date.strftime("%B")]
        if birth_date.year != 1900:
            formatted_date = f"{birth_date.day} {month_name_russian} {birth_date.year}"
        else:
            formatted_date = f"{birth_date.day} {month_name_russian}"

        keyboard.append([InlineKeyboardButton(f"{name}, {formatted_date}", callback_data=f"generate:{id}")])

    keyboard.append([InlineKeyboardButton(f"⚪ Стр. {i}" if i != (record_offset // 10) + 1 else f"🟢 Стр. {i}", callback_data=f"generate_page:{i}") for i in range(1, 5)])

    if len(records) < 10:
        for i in range((record_offset // 10) + 2, 5):
            keyboard[-1][i - 1] = InlineKeyboardButton(f"⚪ Стр. {i}", callback_data="noop")

    keyboard.append([InlineKeyboardButton('🚫 ОТМЕНА', callback_data='start')])

    cur.close()
    conn.close()

    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    message.reply_text('Выберите запись для создания поздравления', reply_markup=InlineKeyboardMarkup(keyboard))

def handle_generate_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    record_id = query.data.split(':')[1]

    query.message.reply_text("Подождите минутку, пока идет генерация сообщения ⏳")
    from AI.gpt_request import generate_birthday_message
    message = generate_birthday_message(record_id, user_id)
    if message:
        query.message.reply_text(message)
    else:
        query.message.reply_text("Ошибка при создании поздравления. Попробуйте снова позже.")
