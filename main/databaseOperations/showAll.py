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
    ORDER BY b.birth_date DESC
    LIMIT 100
    """, (user_id,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    response = 'Номер записи | Имя именинника | Пол | Дата рождения\n'

    for row in results:
        response += f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n"

    update.message.reply_text(response)