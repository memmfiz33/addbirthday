from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from databaseOperations.addNewRecord import create_conn

def delete_command(update: Update, context: CallbackContext) -> None:
    conn = create_conn()
    cur = conn.cursor()

    user_id = update.effective_user.id

    # Получаем первые 10 записей из БД ограничено по user_id.
    cur.execute("SELECT id, birth_person FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s ORDER BY id DESC LIMIT 10", (user_id,))

    keyboard = []

    # Для каждой записи создаем кнопку с id и именем
    for id, name in cur.fetchall():
        keyboard.append([InlineKeyboardButton(f"{name} (ID: {id})", callback_data=f"delete:{id}")])

    # Закрываем соединение
    cur.close()
    conn.close()

    # Отправляем сообщение с кнопками
    update.message.reply_text('Какую запись удалить?', reply_markup=InlineKeyboardMarkup(keyboard))