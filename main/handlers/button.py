from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .addbirthday import addbirthday_command
from .delete import delete_command
from databaseOperations.showAll import showall_command
from databaseOperations.addNewRecord import save_text
from databaseOperations.models import create_conn
from .start import start_command
from .info import info_command

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

    elif query.data.startswith('confirm_delete:'):  # Добавьте этот блок кода
        id_to_delete = query.data.replace("confirm_delete:", "")

        # Получаем имя человека из БД
        conn = create_conn()
        cur = conn.cursor()
        cur.execute("SELECT birth_person FROM birthdays WHERE id = %s", (id_to_delete,))
        name = cur.fetchone()[0]
        cur.close()
        conn.close()

        keyboard = []  # Определяем keyboard как пустой список

        keyboard.append([InlineKeyboardButton(f"🧹 Удалить", callback_data=f"delete:{id_to_delete}"),
                         InlineKeyboardButton("🚫 Отмена", callback_data="start")])

        query.message.reply_text(f"Вы уверены, что хотите удалить запись {name}?",
                                 reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('delete:'):
        id_to_delete = query.data.replace("delete:", "")

        conn = create_conn()
        cur = conn.cursor()

        # Получаем имя человека из БД
        cur.execute("SELECT birth_person FROM birthdays WHERE id = %s", (id_to_delete,))
        name = cur.fetchone()[0]

        cur.execute("UPDATE birthdays SET record_status = 'DELETED' WHERE id = %s", (id_to_delete,))

        conn.commit()
        cur.close()
        conn.close()

        query.message.reply_text(f"Запись {name} удалена.")
        start_command(update, context)  # Вызываем start_command
        return

    elif query.data.startswith('page:'):  # Обрабатываем нажатие на кнопки страниц
        delete_command(update, context)

    elif query.data == 'noop':  # Обрабатываем нажатие на неактивные кнопки страниц
        pass

    elif query.data == 'start':  # Обрабатываем нажатие кнопки "Отмена"
        query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
        start_command(update, context)  # Вызываем start_command
        return

    elif context.user_data['stage'] == 'awaiting_birth_age':
        if query.data == 'start':  # Обрабатываем нажатие кнопки "Отмена"
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)  # Вызываем start_command
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
        if query.data == 'start':  # Обрабатываем нажатие кнопки "Отмена"
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)  # Вызываем start_command
            return
        else:
            context.user_data['birth_month'] = query.data
            context.user_data['stage'] = 'awaiting_birth_date'
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите ЧИСЛО рождения')

    elif context.user_data['stage'] == 'awaiting_birth_date':
        if query.data == 'start':  # Обрабатываем нажатие кнопки "Отмена"
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)  # Вызываем start_command
            return

    elif context.user_data['stage'] == 'awaiting_sex':
        if query.data == 'start':  # Обрабатываем нажатие кнопки "Отмена"
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)  # Вызываем start_command
            return
        else:
            context.user_data['sex'] = query.data
            save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                      update.effective_user.username, context.user_data)
            del context.user_data['stage']
            context.bot.send_message(chat_id=update.effective_chat.id, text='Данные успешно сохранены!')
            start_command(update, context)  # Вызываем start
