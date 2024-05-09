from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from databaseOperations.models import create_conn
from databaseOperations.showAll import get_months

def delete_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text == '/delete':
        context.user_data['record_offset'] = 0

    if update.callback_query and update.callback_query.data.startswith('page:'):
        page = int(update.callback_query.data.replace("page:", ""))
        context.user_data['record_offset'] = (page - 1) * 10

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

        keyboard.append([InlineKeyboardButton(f"{name}, {formatted_date}", callback_data=f"confirm_delete:{id}")])

    keyboard.append([InlineKeyboardButton(f"⚪ Стр. {i}" if i != (record_offset // 10) + 1 else f"🟢 Стр. {i}", callback_data=f"page:{i}") for i in range(1, 5)])

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

    message.reply_text('Какую запись удалить?', reply_markup=InlineKeyboardMarkup(keyboard))