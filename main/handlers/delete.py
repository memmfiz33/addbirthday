from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from databaseOperations.models import create_conn

def delete_command(update: Update, context: CallbackContext) -> None:
    # Устанавливаем смещение в 0 только при вызове команды /delete
    if update.message and update.message.text == '/delete':
        context.user_data['record_offset'] = 0

    # Устанавливаем смещение в зависимости от выбранной страницы
    if update.callback_query and update.callback_query.data.startswith('page:'):
        page = int(update.callback_query.data.replace("page:", ""))
        context.user_data['record_offset'] = (page - 1) * 10

    conn = create_conn()
    cur = conn.cursor()

    user_id = update.effective_user.id

    # Получаем текущее смещение, если оно есть, иначе устанавливаем его в 0
    record_offset = context.user_data.get('record_offset', 0)

    # Получаем 10 записей из БД, начиная с текущего смещения
    cur.execute("SELECT id, birth_person FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s ORDER BY id DESC LIMIT 10 OFFSET %s", (user_id, record_offset))

    keyboard = []

    # Для каждой записи создаем кнопку с id и именем
    records = cur.fetchall()
    for id, name in records:
        keyboard.append([InlineKeyboardButton(f"{name} (ID: {id})",
                                              callback_data=f"confirm_delete:{id}")])  # Измените callback_data на "confirm_delete:{id}"

    # Добавляем кнопки страниц
    keyboard.append([InlineKeyboardButton(f"Стр. {i}" if i != (record_offset // 10) + 1 else f"*Стр. {i}*", callback_data=f"page:{i}") for i in range(1, 5)])

    # Если мы получили меньше 10 записей, делаем последующие кнопки страниц неактивными
    if len(records) < 10:
        for i in range((record_offset // 10) + 2, 5):
            keyboard[-1][i - 1] = InlineKeyboardButton(f"Стр. {i}", callback_data="noop")

    # Добавляем кнопку "Отмена"
    keyboard.append([InlineKeyboardButton('==ОТМЕНА==', callback_data='start')])

    # Закрываем соединение
    cur.close()
    conn.close()

    # Отправляем сообщение с кнопками
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    message.reply_text('Какую запись удалить?', reply_markup=InlineKeyboardMarkup(keyboard))