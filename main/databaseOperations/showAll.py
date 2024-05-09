from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .models import create_conn
import html

def escape_html(text):
    # Экранировать специальные символы HTML
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
        COALESCE(b.sex, '-') -- Если пол отсутствует, заменяем на дефис
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

        # Формирование строки ответа в соответствии с предложенным форматом
        response += f"{escape_html(formatted_date)}, {escape_html(row[1])}, {escape_html(row[2])}\n"

    keyboard = [
        [InlineKeyboardButton('Отмена', callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(response, reply_markup=reply_markup)