from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .addbirthday import addbirthday_command
from .delete import delete_command
from databaseOperations.showAll import showall_command, get_months
from databaseOperations.addNewRecord import save_text
from databaseOperations.models import create_conn
from .start import start_command
from .info import info_command
from .support import support_command

def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    if query.data == 'addbirthday':
        addbirthday_command(update, context)

    elif query.data == 'showall':
        showall_command(update, context)

    elif query.data == 'delete':
        delete_command(update, context)

    elif query.data == 'info':
        info_command(update, context)

    elif query.data == 'support':
        support_command(update, context)

    elif query.data == 'generate_message':
        context.user_data['record_offset'] = 0
        generate_message(update, context)

    elif query.data.startswith('generate_page:'):
        page = int(query.data.replace("generate_page:", ""))
        context.user_data['record_offset'] = (page - 1) * 10
        generate_message(update, context)

    elif query.data.startswith('generate:'):
        record_id = query.data.split(':')[1]
        query.message.reply_text("Подождите минутку, пока идет генерация сообщения ⏳")
        from AI.gpt_request import generate_birthday_message
        message = generate_birthday_message(record_id, user_id)
        if message:
            query.message.reply_text(message)
        else:
            query.message.reply_text("Ошибка при создании поздравления. Попробуйте снова позже.")

    elif query.data.startswith('confirm_delete:'):
        id_to_delete = query.data.replace("confirm_delete:", "")

        conn = create_conn()
        cur = conn.cursor()
        cur.execute("SELECT birth_person FROM birthdays WHERE id = %s", (id_to_delete,))
        name = cur.fetchone()[0]
        cur.close()
        conn.close()

        keyboard = []

        keyboard.append([InlineKeyboardButton(f"🧹 Удалить", callback_data=f"delete:{id_to_delete}"),
                         InlineKeyboardButton("🚫 Отмена", callback_data="start")])

        query.message.reply_text(f"Вы уверены, что хотите удалить запись {name}?",
                                 reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('delete:'):
        id_to_delete = query.data.replace("delete:", "")

        conn = create_conn()
        cur = conn.cursor()

        cur.execute("SELECT birth_person FROM birthdays WHERE id = %s", (id_to_delete,))
        name = cur.fetchone()[0]

        cur.execute("UPDATE birthdays SET record_status = 'DELETED' WHERE id = %s", (id_to_delete,))

        conn.commit()
        cur.close()
        conn.close()

        query.message.reply_text(f"Запись {name} удалена.")
        start_command(update, context)
        return

    elif query.data.startswith('page:'):
        delete_command(update, context)

    elif query.data == 'noop':
        pass

    elif query.data == 'start':
        query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
        start_command(update, context)
        return

    elif context.user_data['stage'] == 'awaiting_birth_age':
        if query.data == 'start':
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)
            return
        elif query.data == 'skip':
            context.user_data['birth_age'] = 1900
            context.user_data['stage'] = 'awaiting_birth_month'

            keyboard = [
                [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
                [InlineKeyboardButton('Отмена', callback_data='start')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                     reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_month':
        if query.data == 'start':
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)
            return
        else:
            context.user_data['birth_month'] = query.data
            context.user_data['stage'] = 'awaiting_birth_date'
            keyboard = [[InlineKeyboardButton('Отмена', callback_data='start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите ЧИСЛО рождения',
                                     reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_date':
        if query.data == 'start':
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)
            return

    elif context.user_data['stage'] == 'awaiting_sex':
        if query.data == 'start':
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)
            return
        else:
            context.user_data['sex'] = query.data
            save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                      update.effective_user.username, context.user_data)
            del context.user_data['stage']
            context.bot.send_message(chat_id=update.effective_chat.id, text='Данные успешно сохранены! 🎉')
            start_command(update, context)

def generate_message(update: Update, context: CallbackContext) -> None:
    conn = create_conn()
    cur = conn.cursor()

    user_id = update.effective_user.id
    record_offset = context.user_data.get('record_offset', 0)

    cur.execute("SELECT id, birth_person, birth_date FROM birthdays WHERE record_status = 'ACTIVE' AND user_telegram_id = %s ORDER BY birth_person ASC LIMIT 10 OFFSET %s", (user_id, record_offset))

    keyboard = []
    records = cur.fetchall()

    for id, name, birth_date in records:
        month_name_russian = get_months()[birth_date.strftime("%B")]
        if birth_date.year != 1900:
            formatted_date = f"{birth_date.day} {month_name_russian} {birth_date.year}"
        else:
            formatted_date = f"{birth_date.day} {month_name_russian}"

        keyboard.append([InlineKeyboardButton(f"{name}, {formatted_date}", callback_data=f"generate:{id}")])

    keyboard.append([InlineKeyboardButton(f"⚪ Стр. {i}" if i != (record_offset // 10) + 1 else f"🟢 Стр. {i}", callback_data=f"generate_page:{i}") for i in range(1, 5)])

    if len(records) < 10:
        for i in range((record_offset // 10) + 2, 5):
            keyboard[-1][i - 1] = InlineKeyboardButton(f"⚪ Стр. {i}", callback_data="noop")

    keyboard.append([InlineKeyboardButton('🚫 ОТМЕНА', callback_data='start')])

    cur.close()
    conn.close()

    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    message.reply_text('Выберите запись для создания поздравления', reply_markup=InlineKeyboardMarkup(keyboard))
