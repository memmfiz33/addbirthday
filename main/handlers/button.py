import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .addbirthday import addbirthday_command
from .delete import delete_command
from databaseOperations.showAll import showall_command
from databaseOperations.addNewRecord import save_text
from databaseOperations.models import create_conn
from .start import start_command
from .info import info_command
from .support import support_command
from AI.ai_buttons import generate_message, handle_generate_callback

logging.basicConfig(level=logging.DEBUG)

def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    logging.debug(f"Button clicked with data: {query.data}")

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

    elif query.data == 'cancel':
        start_command(update, context)

    elif query.data == 'edit':
        context.user_data['stage'] = 'awaiting_user_context'
        query.message.reply_text("Напишите что-то интересное о человеке, это может быть общее увлечение, интересная история или что-то еще. Если нечего добавить, напишите 'Нет' и отправьте.",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton("🚫 Отмена", callback_data="start")]
                                 ]))
        return

    elif query.data.startswith('confirm_delete:'):
        id_to_delete = query.data.replace("confirm_delete:", "")

        conn = create_conn()
        cur = conn.cursor()
        cur.execute("SELECT birth_person FROM birthdays WHERE id = %s", (id_to_delete,))
        name = cur.fetchone()[0]
        cur.close()
        conn.close()

        keyboard = [
            [InlineKeyboardButton(f"🧹 Удалить", callback_data=f"delete:{id_to_delete}"),
             InlineKeyboardButton("🚫 Отмена", callback_data="start")]
        ]

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

    elif query.data == 'generate_message':
        logging.debug("generate_message triggered")
        generate_message(update, context)

    elif query.data.startswith('generate:'):
        logging.debug("handle_generate_callback triggered")
        handle_generate_callback(update, context)

    elif query.data.startswith('generate_page:'):
        logging.debug("handle_generate_callback for pagination triggered")
        handle_generate_callback(update, context)

    elif context.user_data['stage'] == 'awaiting_user_context':
        if query.data == 'start':
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

    elif context.user_data['stage'] == 'awaiting_category':
        if query.data == 'start':
            query.message.reply_text('Отмена действия. Вы перемещены на главный экран')
            start_command(update, context)
            return
        elif query.data == '-':
            context.user_data['category'] = '-'
        else:
            context.user_data['category'] = query.data

        save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                  update.effective_user.username, context.user_data)
        del context.user_data['stage']
        context.bot.send_message(chat_id=update.effective_chat.id, text='Данные успешно сохранены! 🎉')
        start_command(update, context)
        return
