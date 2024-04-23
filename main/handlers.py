from typing import Final
from db import save_text
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

state = {}

def start_command(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton('Добавить ДР!', callback_data='addbirthday')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

def info_command(update: Update, context: CallbackContext) -> None:
    info_text = """
    Этот бот поможет вам запомнить и отслеживать дни рождения.
    Вот что я могу:
    /start - начать работу со мной
    /addbirthday - добавить новый день рождения
    /info - показать эту помощь
    """
    update.message.reply_text(info_text)
def addbirthday_command(update: Update, context: CallbackContext) -> None:
    state[update.effective_user.id] = ['awaiting_birth_person']
    context.bot.send_message(chat_id=update.effective_chat.id, text='Как зовут именинника?')

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.effective_user.id
    if user_id in state:
        if state[user_id][0] == 'awaiting_birth_person':
            state[user_id] = ['awaiting_birth_age', {'birth_person': text}]
            keyboard = [[InlineKeyboardButton("Пропустить", callback_data='skip')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите год рождения', reply_markup=reply_markup)
        elif state[user_id][0] == 'awaiting_birth_age':
            if text == 'Пропустить':
                state[user_id][1]['birth_age'] = None
                state[user_id][0] = 'awaiting_birth_month'
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
                return
            else:
                state[user_id][1]['birth_age'] = int(text)
                state[user_id][0] = 'awaiting_birth_month'
                keyboard = [
                    [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                    [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                    [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                    [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                         reply_markup=reply_markup)
        elif state[user_id][0] == 'awaiting_birth_month':
            state[user_id][1]['birth_month'] = text
            state[user_id][0] = 'awaiting_birth_date'
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите день рождения')
        elif state[user_id][0] == 'awaiting_birth_date':
            month_days = {
                'Апрель': 30, 'Июнь': 30, 'Сентябрь': 30, 'Ноябрь': 30,
                'Январь': 31, 'Март': 31, 'Май': 31, 'Июль': 31, 'Август': 31, 'Октябрь': 31, 'Декабрь': 31
            }
            month_days['Февраль'] = 29 if state[user_id][1]['birth_age'] % 4 == 0 and (state[user_id][1]['birth_age'] % 100 != 0 or state[user_id][1]['birth_age'] % 400 == 0) else 28
            if not text.isdigit() or not 1 <= int(text) <= month_days[state[user_id][1]['birth_month']]:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Неверный формат данных. В выбранном месяце {month_days[state[user_id][1]["birth_month"]]} дней. Пример: {min(7, month_days[state[user_id][1]["birth_month"]])}')
                return
            state[user_id][1]['birth_date'] = int(text)
            state[user_id][0] = 'awaiting_sex'
            keyboard = [
                [InlineKeyboardButton(option, callback_data=option) for option in ['М', 'Ж']],
                [InlineKeyboardButton("Пропустить", callback_data='Пропустить')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите пол', reply_markup=reply_markup)

def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()
    if query.data == 'addbirthday':
        addbirthday_command(update, context)
    elif state[user_id][0] == 'awaiting_birth_month':
        state[user_id][1]['birth_month'] = query.data
        state[user_id][0] = 'awaiting_birth_date'
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите дату рождения')
    elif state[user_id][0] == 'awaiting_sex':
        state[user_id][1]['sex'] = query.data
        save_text(user_id, update.effective_user.first_name, update.effective_user.last_name,
                  update.effective_user.username, state[user_id][1])
        del state[user_id]
        context.bot.send_message(chat_id=update.effective_chat.id, text='Спасибо, данные сохранены')