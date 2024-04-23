import locale
from telegram import Update
from telegram.ext import CallbackContext
from databaseOperations.addNewRecord import create_conn
import psycopg2

def showall_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    conn = create_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        b.id AS "Номер записи",
        b.birth_date AS "Дата рождения",
        b.birth_person AS "Имя именинника",
        b.sex AS "Пол"
    FROM birthdays b
    WHERE user_telegram_id = %s
    ORDER BY b.id DESC
    LIMIT 100
    """, (user_id,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    response = 'Номер записи | Дата рождения | Имя именинника | Пол\n'

    # Словарь для перевода названий месяцев
    months = {
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

    for row in results:
        # Форматирование даты с учетом условий
        if row[1].year >= 1901:
            formatted_date = f"{row[1].day} {months[row[1].strftime('%B')]} {row[1].year}"
        else:
            formatted_date = f"{row[1].day} {months[row[1].strftime('%B')]}"

        response += f"{row[0]} | {formatted_date} | {row[2]} | {row[3]}\n"

    update.message.reply_text(response)