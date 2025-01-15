from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from services.date_service import (
    add_date,
    get_filtered_records,
    book_date_in_file,
    get_available_dates,
    get_user_records,
    update_record,
)
from user_type import is_admin, get_buttons_for_user, ADMIN_IDS
from buttons.buttons import (
    get_admin_buttons,
    get_user_buttons,
    get_cancel_keyboard,
)
import pandas as pd

DATA_FILE = "dates.csv"
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
        await context.bot.send_message(
            chat_id=chat.id,
            text="Привет, {}, есть новые даты? Можешь посмотреть имеющиеся записи.".format(
                name
            ),
            reply_markup=reply_markup,
        )
    else:
        reply_markup = get_user_buttons()  # Получаем пользовательские кнопки
        await context.bot.send_message(
            chat_id=chat.id,
            text="Привет, {}! Я бот для записи.\nМожешь посмотреть список свободных дат и записаться".format(
                name
            ),
            reply_markup=reply_markup,
        )


async def add_date_handler(update, context) -> None:
    """Запрашивает у пользователя ввод даты и времени."""
    chat_id = update.callback_query.message.chat.id  # Используем callback_query
    user_states[chat_id] = "adding_date"  # Устанавливаем состояние пользователя
    await context.bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, введите дату и время в формате DD.MM HH:MM.",
        reply_markup=get_cancel_keyboard(),
    )


async def cancel_handler(update, context) -> None:
    """Обрабатывает команду отмены."""
    chat_id = update.callback_query.message.chat.id

    # Проверяем, есть ли состояние для данного пользователя
    if user_states.get(chat_id) is not None:
        user_states[chat_id] = None  # Сбрасываем состояние
        await context.bot.send_message(
            chat_id=chat_id, text="Хорошо, операция отменена."
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, text="Нет активной операции для отмены."
        )

    reply_markup = get_buttons_for_user(chat_id)

    # Отправляем сообщение с кнопками
    await context.bot.send_message(
        chat_id=chat_id, text="Выберите действие:", reply_markup=reply_markup
    )


async def handle_date_input(update, context) -> None:
    """Обрабатывает ввод даты и времени от пользователя."""
    chat_id = update.message.chat.id

    if user_states.get(chat_id) == "adding_date":
        date_time = update.message.text

        try:
            date_str, time_str = date_time.split()  # Разделяем ввод на дату и время
            result_message = add_date(date_str, time_str)  # Используем функцию для добавления даты

            if "Ошибка" in result_message:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=result_message,
                    reply_markup=get_cancel_keyboard(),
                )
                return

            await context.bot.send_message(
                chat_id=chat_id,
                text=result_message,
                reply_markup=get_cancel_keyboard(),
            )
            user_states[chat_id] = None  # Сбрасываем состояние только при успешном добавлении
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.",
                reply_markup=get_cancel_keyboard(),
            )
            return
    else:
        reply_markup = get_buttons_for_user(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Выбери команду из списка.",
            reply_markup=reply_markup,
        )
        return


async def view_records(update, context) -> None:
    """Отправляет пользователю список записей, отсортированный по дате и времени."""
    chat_id = update.callback_query.message.chat.id
    reply_markup = get_buttons_for_user(chat_id)

    # Получаем отфильтрованные записи
    sorted_records = get_filtered_records()

    # Формирование сообщения
    if not sorted_records.empty:
        message = "Твои ближайшие записи на месяц (ограничены 30):\n"
        for index, row in sorted_records.iterrows():
            record_message = f"📅  {row['Дата'].strftime('%d.%m.%Y')}  📅     ⏰ {row['Время']}  ⏰\n"

            # Добавляем имя, если оно не "Неизвестно"
            if row["Имя"] is not None and not pd.isna(row["Имя"]):
                record_message += f"  👤  {row['Имя']}"

            # Добавляем подтверждение, если оно равно 1
            if row["Подтверждение"] == 1:
                record_message += "  ✅ Подтверждено\n"

            message += f"{record_message}\n"
    else:
        message = "😢 Записей нет "

    await context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup
    )


async def view_free_records(update, context) -> None:
    """Отправляет пользователю список свободных записей,
    отсортированный по дате и времени."""
    chat_id = update.callback_query.message.chat.id
    reply_markup = get_buttons_for_user(chat_id)

    # Получаем отфильтрованные записи
    sorted_records = get_filtered_records()

    # Фильтруем записи, где нет подтвержденя
    free_records = sorted_records[sorted_records["Подтверждение"].isnull()]

    # Формирование сообщения
    if not free_records.empty:
        message = "Свободные записи:\n"
        for index, row in free_records.iterrows():
            record_message = f"📅  {row['Дата'].strftime('%d.%m.%Y')}  📅     ⏰  {row['Время']}  ⏰\n"

            message += f"{record_message}\n"
    else:
        message = "😢  Свободных записей нет"

    await context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup
    )


async def book_date(update, context) -> None:
    """Запрашивает у пользователя выбор свободной даты."""
    chat_id = update.callback_query.message.chat.id
    available_dates = get_available_dates()
    reply_markup = get_buttons_for_user(
        chat_id
    )

    if not available_dates:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Нет доступных дат для бронирования.",
            reply_markup=reply_markup,
        )
        return

    # Создаем клавиатуру с доступными датами
    keyboard = [
        [InlineKeyboardButton(date, callback_data=f"book_{date}")]
        for date in available_dates
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, выберите доступную дату:",
        reply_markup=reply_markup,
    )


async def handle_booking(update, context) -> None:
    """Обрабатывает выбор даты от пользователя."""
    chat_id = update.callback_query.message.chat.id
    selected_date = update.callback_query.data.split("_")[
        1
    ]  # Извлекаем дату из callback_data
    user_id = chat_id  # ID пользователя
    name = update.callback_query.from_user.username  # Получаем имя пользователя

    # Отправляем сообщение администратору
    admin_id = ADMIN_IDS[0]  # Берем первого администратора из списка
    keyboard = [
        [
            InlineKeyboardButton(
                "Да", callback_data=f"confirm|{selected_date}|{user_id}|{name}"
            ),
            InlineKeyboardButton("Нет", callback_data=f"deny|{user_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=admin_id,
        text=f"Пользователь @{name} хочет записаться на дату {selected_date}. Подтвердите запись?",
        reply_markup=reply_markup,
    )

    # Убираем кнопки выбора даты у пользователя
    await context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=None,  # Убираем клавиатуру
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text="Ваш запрос на бронирование отправлен администратору.",
    )


async def confirm_booking(update, context) -> None:
    """Обрабатывает подтверждение бронирования пользователем."""
    query = update.callback_query
    await query.answer()  # Это важно для подтверждения нажатия кнопки

    # Извлекаем данные из callback_data
    data = query.data.split("|")
    selected_date = data[1]
    user_id = data[2]
    name = data[3]
    reply_markup = get_buttons_for_user(user_id)

    # Обновляем информацию о бронировании
    book_date_in_file(
        selected_date, user_id, name
    )  # Функция для записи в файл

    # Уведомляем пользователя
    await context.bot.send_message(
        chat_id=user_id, text="Запись подтверждена.", reply_markup=reply_markup
    )
    await query.message.edit_text(
        text="Запись подтверждена.", reply_markup=reply_markup
    )



async def deny_booking(update, context) -> None:
    """Обрабатывает отклонение бронирования пользователем."""
    query = update.callback_query
    chat_id = update.callback_query.message.chat.id
    await query.answer()  # Это важно для подтверждения нажатия кнопки
    reply_markup = get_buttons_for_user(chat_id)
    user_id = query.data.split("|")[1]  # Извлекаем ID пользователя

    # Обновляем сообщение с отключенными кнопками
    await query.message.edit_text(
        text="Подтверждение отклонено.", reply_markup=reply_markup
    )

    reply_markup = get_buttons_for_user(user_id)
    await context.bot.send_message(
        chat_id=user_id,
        text="К сожалению, не удалось подтвердить дату, выберите другую или свяжитесь с администратором.",
        reply_markup=reply_markup,
    )


async def view_personal_records(update, context) -> None:
    """Обрабатывает запрос пользователя на просмотр своих записей."""
    user_id = update.callback_query.from_user.id  # Получаем ID пользователя
    records = get_user_records(user_id)  # Получаем записи пользователя
    reply_markup = get_buttons_for_user(user_id)

    if records is None:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text="У вас нет записей."
        )
        return

    # Формируем сообщения на основе полученных записей
    messages = [f"Вы записаны на прием {date} в {time}." for date, time in records]

    # Отправляем сообщения пользователю
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text="\n".join(messages),
        reply_markup=reply_markup  # Здесь можно оставить кнопку для отмены записи
    )

async def cancel_record(update, context) -> None:
    """Отменяет запись пользователя."""
    user_id = update.callback_query.from_user.id
    records = get_user_records(user_id)  # Получаем записи пользователя

    if records is None:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text="У вас нет записей для отмены."
        )
        return

    # Создаем кнопки для каждой записи
    buttons = [
        InlineKeyboardButton(f"❌ Отменить {date} в {time}",
                             callback_data=f"confirm_cancel_{date}_{time}")
        for date, time in records
    ]
    reply_markup = InlineKeyboardMarkup([[button] for button in buttons])

    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text="Выберите запись для отмены:",
        reply_markup=reply_markup
    )

async def confirm_cancel_record(update, context) -> None:
    """Подтверждает отмену записи."""
    user_id = update.callback_query.from_user.id
    name = update.callback_query.from_user.name
    data = update.callback_query.data.split("_")
    date = data[2]
    time = data[3]

    # Обновляем запись в CSV
    update_record(user_id, date, time)

    await update.callback_query.answer()
    reply_markup = get_user_buttons()
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=f"Запись на {date} в {time} отменена.",
        reply_markup=reply_markup
    )
    await context.bot.send_message(
        chat_id=ADMIN_IDS[0],
        text=f'Клиент {name}, отменил запись на {date} в {time}.')

def setup_handlers(application) -> None:
    """Настраивает обработчики команд и сообщений для бота."""
    application.add_handler(
        CommandHandler("start", wake_up)
    )  # Обработчик команды /start

    # Обработчик для добавления свободной даты
    application.add_handler(
        CallbackQueryHandler(add_date_handler, pattern="^add_date$")
    )

    # Обработчик для просмотра записей
    application.add_handler(
        CallbackQueryHandler(view_records, pattern="^view_records$")
    )

    # Обработчик для отмены кнопки отмены
    application.add_handler(
        CallbackQueryHandler(cancel_handler, pattern="^cancel$")
    )

    # Обработчик для просмотра свободных записей
    application.add_handler(
        CallbackQueryHandler(view_free_records, pattern="^view_free_records$")
    )

    # Обработчик для записи на свободную дату
    application.add_handler(
        CallbackQueryHandler(book_date, pattern="^book_date$")
    )
    application.add_handler(
        CallbackQueryHandler(handle_booking, pattern="^book_")
    )

    # Регистрация обработчиков
    application.add_handler(
        CallbackQueryHandler(confirm_booking, pattern="^confirm\\|")
    )
    application.add_handler(
        CallbackQueryHandler(deny_booking, pattern="^deny\\|")
    )
    # Обработчик для просмотра своих записей
    application.add_handler(
        CallbackQueryHandler(view_personal_records, pattern="my_records")
    )

    application.add_handler(
        CallbackQueryHandler(cancel_record, pattern="^cancel_record$")
    )
    # Добавление обработчика для подтверждения отмены записи
    application.add_handler(
        CallbackQueryHandler(confirm_cancel_record, pattern=r"^confirm_cancel_")
    )

    # Обработчик текстовых сообщений для ввода даты
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)
    )

