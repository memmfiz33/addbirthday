from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.effective_user.id

    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    if context.user_data['stage'] == 'awaiting_birth_person':
        context.user_data['stage'] = 'awaiting_birth_age'
        context.user_data['birth_person'] = text
        keyboard = [[InlineKeyboardButton("Пропустить", callback_data='skip')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите год рождения',
                                 reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_age':
        if text == 'Пропустить':
            context.user_data['birth_age'] = None
            context.user_data['stage'] = 'awaiting_birth_month'

            keyboard = [
                [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                     reply_markup=reply_markup)

        elif not text.isdigit() or not 1901 <= int(text) <= 2024:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Неверный формат данных. Пожалуйста введите год от 1901 до 2024. Пример: 1991')

        else:
            context.user_data['birth_age'] = int(text)
            context.user_data['stage'] = 'awaiting_birth_month'
            keyboard = [
                [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                     reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_month':
        context.user_data['birth_month'] = text
        context.user_data['stage'] = 'awaiting_birth_date'
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите день рождения')

    elif context.user_data['stage'] == 'awaiting_birth_date':
        month_days = {
            'Апрель': 30, 'Июнь': 30, 'Сентябрь': 30, 'Ноябрь': 30,
            'Январь': 31, 'Март': 31, 'Май': 31, 'Июль': 31, 'Август': 31, 'Октябрь': 31, 'Декабрь': 31
        }
        month_days['Февраль'] = 29 if context.user_data['birth_age'] % 4 == 0 and (
            context.user_data['birth_age'] % 100 != 0 or context.user_data['birth_age'] % 400 == 0) else 28

        if not text.isdigit() or not 1 <= int(text) <= month_days[context.user_data['birth_month']]:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Неверный формат данных. В выбранном месяце {month_days[context.user_data["birth_month"]]} дней. Пример: {min(7, month_days[context.user_data["birth_month"]])}')

        else:
            context.user_data['birth_date'] = int(text)
            context.user_data['stage'] = 'awaiting_sex'
            keyboard = [
                [InlineKeyboardButton(option, callback_data=option) for option in ['М', 'Ж']],
                [InlineKeyboardButton("Пропустить", callback_data='Пропустить')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите пол', reply_markup=reply_markup)