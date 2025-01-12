from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from services.date_service import add_date

# Словарь для хранения состояний пользователей
user_states = {}



async def wake_up(update, context) -> None:
    """Отправляет сообщение о том, что бот активирован, с кнопками."""
    chat = update.effective_chat
    chat_id = update.message.chat.id
    name = update.message.chat.first_name
    if chat_id == 792230644:  # Проверка на конкретного пользователя
        buttons = ReplyKeyboardMarkup(
            [['Посмотреть записи'], ['Добавить свободную дату']])
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, {}, есть новые даты? Можешь посмотреть имеющиеся записи.'.format(name),
                                       reply_markup=buttons)
    else:
        buttons = ReplyKeyboardMarkup(
            [['Посмотреть свободные записи'], ['Записаться на свободную дату']])
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
                # Не сбрасываем состояние, чтобы пользователь мог попробовать снова
                return

            await context.bot.send_message(chat_id=chat.id, text=result_message)
            user_states[chat_id] = None  # Сбрасываем состояние только при успешном добавлении
        except ValueError:
            await context.bot.send_message(chat_id=chat.id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.')
            # Не сбрасываем состояние, чтобы пользователь мог попробовать снова

    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Сначала нажмите "Добавить дату".')

def setup_handlers(application) -> None:
    """Настраивает обработчики команд и сообщений для бота."""
    application.add_handler(CommandHandler('start', wake_up))  # Обработчик команды /start
    #application.add_handler(CommandHandler('add_date', add_date_handler))  # Обработчик команды /add_date
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Добавить свободную дату"),
                       add_date_handler))  # Обработчик текстового сообщения для добавления даты
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input))  # Обработчик текстовых сообщений