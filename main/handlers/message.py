from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, date


def is_leap(year: int) -> bool:
    # функция проверки на високосный год
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return True
    return False


def handle_message(update, context):
    text = update.message.text
    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    # условие обработки ввода имени
    if context.user_data['stage'] == 'awaiting_birth_person':
        if len(text) > 100:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Ваше имя слишком длинное')
        else:
            context.user_data['birth_person'] = text
            context.user_data['stage'] = 'awaiting_birth_age'
            keyboard = [[InlineKeyboardButton("Пропустить", callback_data='skip')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите ГОД рождения',
                                     reply_markup=reply_markup)

    # условие обработки ввода года рождения
    elif context.user_data['stage'] == 'awaiting_birth_age':
        if text == 'Пропустить':
            context.user_data['birth_age'] = 1900
        elif text.isdigit() and 1901 <= int(text) <= datetime.now().year:
            context.user_data['birth_age'] = int(text)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Неверный формат данных. Пожалуйста введите год от 1901 до текущего года. Пример: 1991')
            return

        context.user_data['stage'] = 'awaiting_birth_month'
        context.user_data['is_leap'] = is_leap(context.user_data['birth_age'])

        keyboard = [
            [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите МЕСЯЦ рождения',
                                 reply_markup=reply_markup)

    # условие обработки ввода даты рождения
    elif context.user_data['stage'] == 'awaiting_birth_date':
        month_days = {
            'Апрель': 30, 'Июнь': 30, 'Сентябрь': 30, 'Ноябрь': 30,
            'Январь': 31, 'Март': 31, 'Май': 31, 'Июль': 31, 'Август': 31, 'Октябрь': 31, 'Декабрь': 31
        }
        month_days['Февраль'] = 29 if context.user_data['is_leap'] else 28

        if not text.isdigit() or not 1 <= int(text) <= month_days[context.user_data['birth_month']]:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Неверный формат данных. В выбранном месяце {context.user_data["birth_month"]} {month_days[context.user_data["birth_month"]]} дней.'
            )
        else:
            month_list = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            # формирование даты рождения - получаем год, месяц и день, затем создаем объект date
            birth_year = context.user_data.get('birth_age')
            birth_month = month_list.index(
                context.user_data.get('birth_month')) + 1  # учет того, что в Python отсчет начинается с 0
            birth_day = int(text)
            context.user_data['birth_date'] = date(birth_year, birth_month, birth_day)
            context.user_data['stage'] = 'awaiting_sex'

            keyboard = [
                [InlineKeyboardButton(option, callback_data=option) for option in ['М', 'Ж']],
                [InlineKeyboardButton("Пропустить", callback_data='-')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите пол', reply_markup=reply_markup)