from telegram import Update
from telegram.ext import CallbackContext
from databaseOperations.addNewRecord import create_conn
from telegram import ParseMode
import psycopg2
from prettytable import PrettyTable

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

    # Создание объекта таблицы
    table = PrettyTable(['Номер записи', 'Дата рождения', 'Имя именинника', 'Пол'])

    for row in results:
        # Добавляем каждую запись в таблицу
        table.add_row(row)

    # преобразуем таблицу в строку и отправляем пользователю
    update.message.reply_text(f"```{str(table)}```", parse_mode=ParseMode.MARKDOWN)