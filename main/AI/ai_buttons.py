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

    cur.execute(
        "SELECT id, birth_person, birth_date FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s ORDER BY birth_person ASC LIMIT 10 OFFSET %s",
        (user_id, record_offset))

    keyboard = []
    records = cur.fetchall()

    for id, name, birth_date in records:
        month_name_russian = get_months()[birth_date.strftime("%B")]
        if birth_date.year != 1900:
            formatted_date = f"{birth_date.day} {month_name_russian} {birth_date.year}"
        else:
            formatted_date = f"{birth_date.day} {month_name_russian}"

        keyboard.append([InlineKeyboardButton(f"{name}, {formatted_date}", callback_data=f"generate:{id}")])

    keyboard.append([InlineKeyboardButton(f"⚪ Стр. {i}" if i != (record_offset // 10) + 1 else f"🟢 Стр. {i}",
                                          callback_data=f"generate_page:{i}") for i in range(1, 5)])

    if len(records) < 10:
        for i in range((record_offset // 10) + 2, 5):
            keyboard[-1][i - 1] = InlineKeyboardButton(f"⚪ Стр. {i}", callback_data="noop")

    keyboard.append([InlineKeyboardButton('🚫 Отмена', callback_data='start')])

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
    context.user_data['record_id'] = record_id
    context.user_data['stage'] = 'awaiting_user_context'

    query.message.reply_text(
        "Напишите что-то интересное о человеке, это может быть общее увлечение, интересная история или что-то еще. Если нечего добавить, напишите 'Нет' и отправьте.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Отмена", callback_data="start")]
        ]))

def handle_message(update: Update, context: CallbackContext) -> None:
    logging.debug(f"Received message: {update.message.text}")
    logging.debug(f"User data: {context.user_data}")
    if context.user_data.get('stage') == 'awaiting_user_context':
        logging.debug("Stage is awaiting_user_context")
        context.user_data['user_context'] = update.message.text
        context.user_data['stage'] = ''
        update.message.reply_text("Подождите минутку, пока идет генерация сообщения ⏳")
        send_generate_request(update, context)
    else:
        logging.debug("Stage is not awaiting_user_context")

def send_generate_request(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    record_id = context.user_data.get('record_id')
    user_context = context.user_data.get('user_context', '-')

    logging.debug(f"Sending request with user_id: {user_id}, record_id: {record_id}, user_context: {user_context}")

    from AI.gpt_request import generate_birthday_message
    message = generate_birthday_message(record_id, user_id, user_context)
    if message:
        logging.debug("Message generated successfully")
        update.message.reply_text(message)
    else:
        logging.error("Failed to generate message")
        update.message.reply_text("Ошибка при создании поздравления. Попробуйте снова позже.")
