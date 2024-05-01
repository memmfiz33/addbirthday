from telegram import Update, ForceReply
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
import psycopg2
from datetime import datetime

def create_conn():
    conn = psycopg2.connect(
        dbname="addbirthday",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    return conn

def support_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('1.Сделайте Reply/Ответить действие для этого сообщения. 2.Напишите и отправьте ваще обращение', reply_markup=ForceReply())

def handle_support(update: Update, context: CallbackContext) -> None:
    print("handle_support called")  # Добавим сообщение для отладки
    if update.message.reply_to_message:
        if update.message.reply_to_message.text == '1.Сделайте Reply/Ответить действие для этого сообщения. 2.Напишите и отправьте ваще обращение':
            user = update.effective_user
            text = update.message.text

            conn = create_conn()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM support')
            count = cur.fetchone()
            if count is not None:
                id = count[0] + 1

            user_name = f"{user.first_name}"
            user_telegram_id = user.id
            user_telegram_name = user.username
            support_text = text
            timestamp = datetime.now().isoformat(timespec='seconds')

            query = """
                INSERT INTO support (
                    id, user_name, user_telegram_id, user_telegram_name, support_text, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                id, user_name, user_telegram_id, user_telegram_name, support_text, timestamp
            )
            print("Executing SQL query")  # Добавим сообщение для отладки
            cur.execute(query, values)
            conn.commit()
            print("SQL query executed")  # Добавим сообщение для отладки

            cur.close()
            conn.close()

            update.message.reply_text('Спасибо за обращение!')

support_handler = CommandHandler('support', support_command)
support_reply_handler = MessageHandler(Filters.text & Filters.reply, handle_support)