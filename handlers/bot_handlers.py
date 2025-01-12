from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from services.date_service import add_date

import pandas as pd
import os


DATA_FILE = 'dates.csv'
# Словарь для хранения состояний пользователей
user_states = {}

async def wake_up(update, context) -> None:
    """Отправляет сообщение о том, что бот активирован, с кнопками."""
    chat = update.effective_chat
    chat_id = update.message.chat.id
    name = update.message.chat.first_name
    if chat_id == 792230644:  # Проверка на конкретного пользователя
        buttons = ReplyKeyboardMarkup(
            [['Посмотреть записи', 'Добавить свободную дату'], ['Отмена']])
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, {}, есть новые даты? Можешь посмотреть имеющиеся записи.'.format(name),
                                       reply_markup=buttons)
    else:
        buttons = ReplyKeyboardMarkup(
            [['Посмотреть свободные записи', 'Записаться на свободную дату'], ['Отмена']])
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, {}! Я бот для записи.\nМожешь посмотреть список свободных дат и записаться'.format(
                                           name),
                                       reply_markup=buttons)

async def add_date_handler(update, context) -> None:
    """Запрашивает у пользователя ввод даты и времени."""
    chat = update.effective_chat
    chat_id = update.message.chat.id
    user_states[chat_id] = 'adding_date'  # Устанавливаем состояние пользователя
    await context.bot.send_message(chat_id=chat.id,
                                   text='Пожалуйста, введите дату и время в формате DD.MM HH:MM.')

async def cancel_handler(update, context) -> None:
    """Обрабатывает команду отмены."""
    chat = update.effective_chat
    chat_id = update.message.chat.id

    # Проверяем, есть ли состояние для данного пользователя
    if user_states.get(chat_id) is not None:
        user_states[chat_id] = None  # Сбрасываем состояние
        await context.bot.send_message(chat_id=chat.id,
                                       text='Хорошо, операция отменена.')
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Нет активной операции для отмены.')

async def handle_date_input(update, context) -> None:
    """Обрабатывает ввод даты и времени от пользователя."""
    chat = update.effective_chat
    chat_id = update.message.chat.id

    if user_states.get(chat_id) == 'adding_date':
        date_time = update.message.text
        name = "Неизвестно"  # Имя по умолчанию

        try:
            date_str, time_str = date_time.split()  # Разделяем ввод на дату и время
            result_message = add_date(date_str, time_str, name)  # Используем функцию для добавления даты

            if "Ошибка" in result_message:
                await context.bot.send_message(chat_id=chat.id,
                                               text=result_message)
                return

            await context.bot.send_message(chat_id=chat.id, text=result_message)
            user_states[chat_id] = None  # Сбрасываем состояние только при успешном добавлении
        except ValueError:
            await context.bot.send_message(chat_id=chat.id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.')
            return
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Выбери команду из списка, или нажми на нужную кнопку.')
        return

async def view_records(update, context) -> None:
    """Отправляет пользователю список записей, отсортированный по дате и времени."""
    chat_id = update.message.chat.id

    # Проверяем, существует ли файл с записями
    if not os.path.exists(DATA_FILE):
        await context.bot.send_message(chat_id=chat_id, text='Записей нет.')
        return

    # Чтение записей из файла
    try:
        df = pd.read_csv(DATA_FILE)

        # Сортировка записей по дате и времени
        df['Дата'] = pd.to_datetime(df['Дата'] + ' ' + df['Время'], format='%d.%m.%Y %H:%M')
        sorted_records = df.sort_values(by='Дата')

        # Формирование сообщения
        if not sorted_records.empty:
            message = "Твои записи:\n"
            for index, row in sorted_records.iterrows():
                # Формируем строку для вывода
                record_message = f"{row['Дата'].strftime('%d.%m.%Y')} {row['Время']}"

                # Проверяем колонку 'Имя'
                if row['Имя'] != "Неизвестно":
                    record_message += f" {row['Имя']}"

                # Проверяем колонку 'Подтверждение'
                if row['Подтверждение'] == 1:
                    record_message += " (Подтверждено)"

                message += record_message + "\n"
        else:
            message = "Записей нет."

        await context.bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text='Ошибка при чтении записей: {}'.format(str(e)))

def setup_handlers(application) -> None:
    """Настраивает обработчики команд и сообщений для бота."""
    application.add_handler(CommandHandler('start', wake_up))  # Обработчик команды /start
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Добавить свободную дату"),
                       add_date_handler))  # Обработчик текстового сообщения для добавления даты
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Посмотреть записи"),
                       view_records)) # Обработчик команды /посмотреть_записи
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Отмена"),
                       cancel_handler))  # Обработчик команды /отмена
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND,
                       handle_date_input))  # Обработчик текстовых сообщений