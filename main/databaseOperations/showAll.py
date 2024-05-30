from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .models import create_conn
import html
import logging
from AI.gpt_request import generate_birthday_message

logging.basicConfig(level=logging.DEBUG)

def escape_html(text):
    return html.escape(text)

def get_months():
    return {
        "January": "ЯНВ",
        "February": "ФЕВ",
        "March": "МАР",
        "April": "АПР",
        "May": "МАЙ",
        "June": "ИЮН",
        "July": "ИЮЛ",
        "August": "АВГ",
        "September": "СЕН",
        "October": "ОКТ",
        "November": "НОЯ",
        "December": "ДЕК",
    }

def showall_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = create_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        b.birth_date,
        b.birth_person,
        COALESCE(b.sex, '-') 
    FROM birthdays b
    WHERE user_telegram_id = %s
    AND record_status = 'ACTIVE'
    ORDER BY SUBSTR(birth_date::text, 6, 5), SUBSTR(birth_date::text, 1, 5) DESC
    LIMIT 40
    """, (user_id,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    months = get_months()

    response = "===============================\n"
    response += "Дата рождения, Имя именинника, Пол\n"
    response += "===============================\n"

    current_month = None
    for row in results:
        if row[0].year >= 1901:
            formatted_date = f"{row[0].day:02d} {months[row[0].strftime('%B')]} {row[0].year}"
        else:
            formatted_date = f"{row[0].day:02d} {months[row[0].strftime('%B')]}"

        month_name = months[row[0].strftime('%B')]
        if month_name != current_month:
            response += f"===={month_name}====\n"
            current_month = month_name

        response += f"{escape_html(formatted_date)}, {escape_html(row[1])}, {escape_html(row[2])}\n"

    keyboard = [
        [InlineKeyboardButton('🚫 Отмена', callback_data='start'),
         InlineKeyboardButton('🗑️ Перейти к удалению', callback_data='delete')],
        [InlineKeyboardButton('Сгенерировать поздравления', callback_data='generate_greetings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(response, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    logging.info("Button clicked with callback data: %s", query.data)

    if query.data == 'generate_greetings':
        try:
            name = "Папа"
            age = 50
            gender = "М"
            category = "Родители"
            context = "Это любимый папуля у него юбилей"

            logging.info("Generating birthday message for: Name=%s, Age=%d, Gender=%s, Category=%s, Context=%s", name, age, gender, category, context)

            message = generate_birthday_message(name, age, gender, category, context)

            if message:
                logging.info("Generated message: %s", message)
                query.edit_message_text(text=f"Поздравительное сообщение: {message}")
            else:
                logging.error("Generated message is None")
                query.edit_message_text(text="Не удалось сгенерировать сообщение.")
        except Exception as e:
            logging.error("Error generating message: %s", str(e))
            query.edit_message_text(text="Произошла ошибка при генерации сообщения.")
    elif query.data == 'start':
        query.edit_message_text(text="Отмена.")
    elif query.data == 'delete':
        query.edit_message_text(text="Перейти к удалению.")

def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("showall", showall_command))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
