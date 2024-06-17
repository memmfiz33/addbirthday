import psycopg2
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, date
from AI import generate_birthday_message  # Используем абсолютный импорт

def is_leap(year: int) -> bool:
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return True
    return False

def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    if 'stage' not in context.user_data:
        context.user_data['stage'] = ''

    if context.user_data['stage'] == 'awaiting_user_context':
        user_context = text
        context.user_data['user_context'] = user_context
        context.user_data['stage'] = ''

        context.bot.send_message(chat_id=update.effective_chat.id, text='🧙‍♂️ Мы колдуем для вас, минутка терпения ⌛️')

        message = generate_birthday_message(context.user_data['record_id'], user_id, user_context)
        context.user_data['previous_message'] = message
        keyboard = [
            [InlineKeyboardButton("✅️ Завершить", callback_data='cancel')],
            [InlineKeyboardButton("✏️ Изменить", callback_data='edit')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message if message else '🧙‍♂️ Сервис волшебства временно недоступен, попробуйте позже ', reply_markup=reply_markup)
        return

    if context.user_data['stage'] == 'awaiting_birth_person':
        if len(text) > 100:
            keyboard = [[InlineKeyboardButton('Отмена', callback_data='start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Ваше имя слишком длинное. Введите еще раз',
                                     reply_markup=reply_markup)
        else:
            context.user_data['birth_person'] = text
            context.user_data['stage'] = 'awaiting_birth_age'
            keyboard = [[InlineKeyboardButton("Пропустить", callback_data='skip'),
                         InlineKeyboardButton('Отмена', callback_data='start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите ГОД рождения',
                                     reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_age':
        if text == 'Пропустить':
            context.user_data['birth_age'] = 1900
        elif text.isdigit() and 1901 <= int(text) <= datetime.now().year:
            context.user_data['birth_age'] = int(text)
        else:
            keyboard = [[InlineKeyboardButton('Отмена', callback_data='start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Пожалуйста введите год от 1901 до текущего года. Пример: 1991',
                reply_markup=reply_markup
            )
            return

        context.user_data['stage'] = 'awaiting_birth_month'
        context.user_data['is_leap'] = is_leap(context.user_data['birth_age'])

        keyboard = [
            [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
            [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
            [InlineKeyboardButton('Отмена', callback_data='start')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите МЕСЯЦ рождения',
                                 reply_markup=reply_markup)

    elif context.user_data['stage'] == 'awaiting_birth_date':
        month_days = {
            'Апрель': 30, 'Июнь': 30, 'Сентябрь': 30, 'Ноябрь': 30,
            'Январь': 31, 'Март': 31, 'Май': 31, 'Июль': 31, 'Август': 31, 'Октябрь': 31, 'Декабрь': 31
        }
        if context.user_data.get('birth_age') != 1900 and context.user_data.get('is_leap'):
            month_days['Февраль'] = 29
        else:
            month_days['Февраль'] = 28

        if not text.isdigit() or not 1 <= int(text) <= month_days[context.user_data['birth_month']]:
            keyboard = [[InlineKeyboardButton('Отмена', callback_data='start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'В выбранном месяце {context.user_data["birth_month"]} {month_days[context.user_data["birth_month"]]} дней. Введите корректную дату или отмените действие',
                reply_markup=reply_markup
            )
        else:
            month_list = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

            birth_year = context.user_data.get('birth_age')
            birth_month = month_list.index(context.user_data.get('birth_month')) + 1
            birth_day = int(text)
            context.user_data['birth_date'] = date(birth_year, birth_month, birth_day)
            context.user_data['stage'] = 'awaiting_category'

            categories = [
                ("Друзья 👬", "Друзья"),
                ("Работа 💼", "Работа"),
                ("Учёба 📚", "Учёба"),
                ("Родственники 👪", "Родственники"),
                ("Преподаватели 👩‍🏫", "Преподаватели"),
                ("Хобби 🎨", "Хобби"),
                ("Знакомые 👋", "Знакомые")
            ]
            keyboard = [
                [InlineKeyboardButton(categories[i][0], callback_data=categories[i][1]),
                 InlineKeyboardButton(categories[i+1][0], callback_data=categories[i+1][1])]
                for i in range(0, len(categories)-1, 2)
            ]
            if len(categories) % 2 == 1:
                keyboard.append([InlineKeyboardButton(categories[-1][0], callback_data=categories[-1][1]),
                                 InlineKeyboardButton("Пропустить", callback_data='-')])
            else:
                keyboard.append([InlineKeyboardButton("Пропустить", callback_data='-')])
            keyboard.append([InlineKeyboardButton('Отмена', callback_data='start')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите категорию, которая лучше подходит под человека', reply_markup=reply_markup)
