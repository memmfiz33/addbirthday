from telegram import Update
from telegram.ext import CallbackContext
from databaseOperations.models import create_conn


def addbirthday_command(update: Update, context: CallbackContext) -> None:
    conn = create_conn()
    cur = conn.cursor()

    user_id = update.effective_user.id

    # Получаем количество записей для текущего пользователя
    cur.execute("SELECT COUNT(id) FROM birthdays WHERE user_telegram_id = %s AND record_status = 'ACTIVE'", (user_id,))
    record_count = cur.fetchone()[0]

    # Закрываем соединение
    cur.close()
    conn.close()

    # Если количество записей меньше 40, переходим к следующему шагу
    if record_count < 40:
        context.user_data['stage'] = 'awaiting_birth_person'
        context.bot.send_message(chat_id=update.effective_chat.id, text='Как зовут именинника?')
    else:
        # Иначе выводим сообщение об ошибке
        context.bot.send_message(chat_id=update.effective_chat.id, text='Вы достигли максимума записей')