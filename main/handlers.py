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
            state[user_id] = ['awaiting_birth_month', {'birth_person': text}]
            keyboard = [
                [InlineKeyboardButton(m, callback_data=m) for m in ["Январь", "Февраль", "Март"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Апрель", "Май", "Июнь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Июль", "Август", "Сентябрь"]],
                [InlineKeyboardButton(m, callback_data=m) for m in ["Октябрь", "Ноябрь", "Декабрь"]],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите месяц рождения',
                                     reply_markup=reply_markup)
        elif state[user_id][0] == 'awaiting_birth_date':
            state[user_id][1]['birth_date'] = text
            state[user_id][0] = 'awaiting_birth_age'
            context.bot.send_message(chat_id=update.effective_chat.id, text='Введите год рождения')
        elif state[user_id][0] == 'awaiting_birth_age':
            state[user_id][1]['birth_age'] = text
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