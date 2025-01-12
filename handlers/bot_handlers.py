
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from services.date_service import add_date
from user_type import is_admin
from buttons.buttons import get_admin_buttons, get_user_buttons, get_cancel_keyboard

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

    # Проверяем, является ли пользователь администратором
    if is_admin(chat_id):  # Используем функцию для проверки
        reply_markup = get_admin_buttons()  # Получаем администраторские кнопки
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, {}, есть новые даты? Можешь посмотреть имеющиеся записи.'.format(name),
                                       reply_markup=reply_markup)
    else:
        reply_markup = get_user_buttons()  # Получаем пользовательские кнопки
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, {}! Я бот для записи.\nМожешь посмотреть список свободных дат и записаться'.format(name),
                                       reply_markup=reply_markup)

async def add_date_handler(update, context) -> None:
    """Запрашивает у пользователя ввод даты и времени."""
    chat_id = update.callback_query.message.chat.id  # Используем callback_query
    user_states[chat_id] = 'adding_date'  # Устанавливаем состояние пользователя
    await context.bot.send_message(chat_id=chat_id,
                                   text='Пожалуйста, введите дату и время в формате DD.MM HH:MM.',
                                   reply_markup=get_cancel_keyboard())

async def cancel_handler(update, context) -> None:
    """Обрабатывает команду отмены."""
    chat_id = update.callback_query.message.chat.id  # Используем callback_query

    # Проверяем, есть ли состояние для данного пользователя
    if user_states.get(chat_id) is not None:
        user_states[chat_id] = None  # Сбрасываем состояние
        await context.bot.send_message(chat_id=chat_id,
                                       text='Хорошо, операция отменена.')
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='Нет активной операции для отмены.')

    # Определяем, администратор ли пользователь и выводим соответствующий блок кнопок
    if is_admin(chat_id):  # Используем функцию для проверки
        reply_markup = get_admin_buttons()  # Получаем администраторские кнопки
    else:
        reply_markup = get_user_buttons()  # Получаем пользовательские кнопки

    # Отправляем сообщение с кнопками
    await context.bot.send_message(chat_id=chat_id,
                                   text='Выберите действие:',
                                   reply_markup=reply_markup)

async def handle_date_input(update, context) -> None:
    """Обрабатывает ввод даты и времени от пользователя."""
    chat_id = update.message.chat.id  # Здесь все еще используем message, так как это текстовый ввод

    if user_states.get(chat_id) == 'adding_date':
        date_time = update.message.text
        name = "Неизвестно"  # Имя по умолчанию

        try:
            date_str, time_str = date_time.split()  # Разделяем ввод на дату и время
            result_message = add_date(date_str, time_str, name)  # Используем функцию для добавления даты

            if "Ошибка" in result_message:
                await context.bot.send_message(chat_id=chat_id,
                                               text=result_message)
                return

            await context.bot.send_message(chat_id=chat_id, text=result_message)
            user_states[chat_id] = None  # Сбрасываем состояние только при успешном добавлении
        except ValueError:
            await context.bot.send_message(chat_id=chat_id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.',
                                   reply_markup=get_cancel_keyboard())
            return
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='Выбери команду из списка, или нажми на нужную кнопку.',
                                   reply_markup=get_cancel_keyboard())
        return

async def view_records(update, context) -> None:
    """Отправляет пользователю список записей, отсортированный по дате и времени."""
    chat_id = update.callback_query.message.chat.id  # Используем callback_query

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
            message = "Твои близжайшие записи:\n"
            for index, row in sorted_records.iterrows():
                record_message = f"📅 **Дата:**   {row['Дата'].strftime('%d.%m.%Y')}  ⏰ **Время:**   {row['Время']}"

                # Добавляем имя, если оно не "Неизвестно"
                if row['Имя'] != "Неизвестно":
                    record_message += f"  👤 **Имя:**   {row['Имя']}"

                # Добавляем подтверждение, если оно равно 1
                if row['Подтверждение'] == 1:
                    record_message += "  ✅   **Подтверждено**"

                message += f"{record_message}\n"
        else:
            message = "Записей нет."

        await context.bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text='Ошибка при чтении записей: {}'.format(str(e)),
                                       reply_markup=get_cancel_keyboard())
        return

    # Определяем, администратор ли пользователь и выводим соответствующий блок кнопок
    if is_admin(chat_id):  # Используем функцию для проверки
        reply_markup = get_admin_buttons()  # Получаем администраторские кнопки
    else:
        reply_markup = get_user_buttons()  # Получаем пользовательские кнопки

    # Отправляем сообщение с кнопками
    await context.bot.send_message(chat_id=chat_id,
                                   text='Выберите действие:',
                                   reply_markup=reply_markup)


def setup_handlers(application) -> None:
    """Настраивает обработчики команд и сообщений для бота."""
    application.add_handler(CommandHandler('start', wake_up))  # Обработчик команды /start

    # Обработчик для добавления свободной даты
    application.add_handler(
        CallbackQueryHandler(add_date_handler, pattern='^add_date$'))  # Обработчик для добавления даты

    # Обработчик для просмотра записей
    application.add_handler(
        CallbackQueryHandler(view_records, pattern='^view_records$'))  # Обработчик для просмотра записей

    # Обработчик для отмены
    application.add_handler(
        CallbackQueryHandler(cancel_handler, pattern='^cancel$'))  # Обработчик для отмены

    # Обработчик текстовых сообщений для ввода даты
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND,
                       handle_date_input))  # Обработчик текстовых сообщений