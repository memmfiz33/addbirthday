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

    records = cur.fetchall()

    keyboard = []

    for id, name, birth_date in records:
        month_name_russian = get_months()[birth_date.strftime("%B")]
        if birth_date.year != 1900:
            formatted_date = f"{birth_date.day} {month_name_russian} {birth_date.year}"
        else:
            formatted_date = f"{birth_date.day} {month_name_russian}"

        keyboard.append([InlineKeyboardButton(f"{name}, {formatted_date}", callback_data=f"confirm_delete:{id}")])

    # Рассчитать общее количество записей, чтобы корректно настроить пагинацию
    cur.execute("SELECT COUNT(*) FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s", (user_id,))
    total_records = cur.fetchone()[0]
    total_pages = (total_records + 9) // 10  # Округление вверх

    # Создать кнопки страниц
    pagination_buttons = []
    for i in range(1, total_pages + 1):
        if i == (record_offset // 10) + 1:
            pagination_buttons.append(InlineKeyboardButton(f"🟢 Стр. {i}", callback_data=f"page:{i}"))
        else:
            pagination_buttons.append(InlineKeyboardButton(f"⚪ Стр. {i}", callback_data=f"page:{i}"))

    keyboard.append(pagination_buttons)
    keyboard.append([InlineKeyboardButton('🚫 ОТМЕНА', callback_data='start')])

    cur.close()
    conn.close()

    if update.callback_query:
        update.callback_query.message.reply_text('Нажмите на запись для удаления', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text('Нажмите на запись для удаления', reply_markup=InlineKeyboardMarkup(keyboard))
