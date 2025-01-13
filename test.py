from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
import pandas as pd
import os
from datetime import datetime

DATA_FILE = 'Old_dates.csv'

application = ApplicationBuilder().token(
    '5727798773:AAHZXJfbg054rdwf4mux5OeCyXj0weoBqpI').build()

# Словарь для хранения состояния пользователей
user_states = {}

async def say_hi(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id
    if chat_id == 792230644:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, Алена, есть новые даты?')
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, я бот для записи!')

async def wake_up(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup(
        [['Посмотреть свободные даты'], ['Добавить дату']])  # Изменяем текст кнопки на команду
    await context.bot.send_message(chat_id=chat.id,
                                   text='Спасибо, что включили меня',
                                   reply_markup=buttons)

async def add_date(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id

    # Устанавливаем состояние пользователя в режим добавления даты
    user_states[chat_id] = 'adding_date'
    await context.bot.send_message(chat_id=chat.id,
                                   text='Пожалуйста, введите дату и время в формате DD.MM HH:MM.')

async def handle_date_input(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id

    # Проверяем, находится ли пользователь в режиме добавления даты
    if user_states.get(chat_id) == 'adding_date':
        date_time = update.message.text  # Получаем текст сообщения
        name = "Неизвестно"  # Имя пользователя или "Неизвестно"

        # Проверяем, существует ли файл, и создаем его, если нет
        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame(columns=['Дата', 'Время', 'Имя', 'Подтверждение'])
            df.to_csv(DATA_FILE, index=False)

        # Загружаем существующие данные
        df = pd.read_csv(DATA_FILE)

        # Добавляем новую запись
        try:
            # Извлекаем текущий год
            current_year = datetime.now().year
            date_str, time_str = date_time.split()  # Ожидаем, что пользователь введет дату и время
            date_with_year = f"{date_str}.{current_year}"  # Добавляем текущий год к дате
            new_entry = pd.DataFrame(
                {'Дата': [date_with_year], 'Время': [time_str], 'Имя': [name],
                 'Подтверждение': [0]})
            df = pd.concat([df, new_entry],
                           ignore_index=True)  # Используем pd.concat для добавления новой записи

            # Сохраняем обновленные данные обратно в файл
            df.to_csv(DATA_FILE, index=False)

            await context.bot.send_message(chat_id=chat.id,
                                           text='Дата успешно добавлена!')
        except ValueError:
            await context.bot.send_message(chat_id=chat.id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.')

        # Сбрасываем состояние пользователя
        user_states[chat_id] = None
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Сначала нажмите "Добавить дату".')

# Обработчики команд и сообщений
application.add_handler(CommandHandler('start', wake_up))
application.add_handler(CommandHandler('add_date', add_date))
# Обработка нажатия кнопки "Добавить дату"
application.add_handler(
    MessageHandler(filters.TEXT & filters.Regex("Добавить дату"), add_date))

application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input))

application.run_polling()
application.idle()