from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
from datetime import datetime
from databaseOperations.models import create_conn

def support_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🚫 Отмена", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message is not None:
        update.message.reply_text('👋 Привет! Чтобы отправить сообщение, выполните следующие шаги:\n\n'
                                  '1️⃣ Нажмите на "Ответить" (reply) к этому сообщению.\n\n'
                                  '2️⃣ Напишите свое обращение и отправьте его.', reply_markup=reply_markup)
    elif update.callback_query is not None:
        update.callback_query.message.reply_text('👋 Привет! Чтобы отправить сообщение, выполните следующие шаги:\n\n'
                                                 '1️⃣ Нажмите на "Ответить" (reply) к этому сообщению.\n\n'
                                                 '2️⃣ Напишите свое обращение и отправьте его.', reply_markup=reply_markup)

def handle_support(update: Update, context: CallbackContext) -> None:
    print("handle_support called")  # Добавим сообщение для отладки
    if update.message.reply_to_message:
        if update.message.reply_to_message.text == '👋 Привет! Чтобы отправить сообщение, выполните следующие шаги:\n\n' \
                                                   '1️⃣ Нажмите на "Ответить" (reply) к этому сообщению.\n\n' \
                                                   '2️⃣ Напишите свое обращение и отправьте его.':
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

            update.message.reply_text('Спасибо за обращение! 📬')

support_handler = CommandHandler('support', support_command)
support_reply_handler = MessageHandler(Filters.text & Filters.reply, handle_support)