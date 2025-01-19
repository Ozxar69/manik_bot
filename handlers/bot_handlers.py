import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from buttons.buttons import (
    get_admin_buttons,
    get_cancel_keyboard,
    get_type_buttons,
    get_user_buttons,
)
from data import (
    ADMIN_CANCEL_NOTIFICATION_MESSAGE,
    ADMIN_CANCEL_RECORD_MESSAGE,
    BOOKING_REQUEST_MESSAGE,
    CANCEL_OPERATION_MESSAGE,
    CANCEL_QUESTION_PROMPT_MESSAGE,
    CANCEL_RECORD_BUTTON_TEXT,
    CANCEL_RECORD_PROMPT_MESSAGE,
    CONFIRM_CANCELING,
    CONFIRMATION_DATA,
    CONFIRMATION_RECEIVED,
    CONFIRMED_MESSAGE,
    DATE_DATA,
    DATE_FORMAT,
    DATE_REQUEST_MESSAGE,
    DATE_TIME_FORMAT_ERROR_MESSAGE,
    ERROR_DATE_MESSAGE,
    ERROR_MESSAGE,
    FREE_RECORDS_HEADER_MESSAGE,
    GET_USERNAME_MESSAGE,
    NO_ACTIVE_OPERATION_MESSAGE,
    NO_AVAILABLE_DATES_MESSAGE,
    NO_BUTTON,
    NO_FREE_RECORDS_MESSAGE,
    NO_RECORDS_MESSAGE,
    NO_RECORDS_TO_CANCEL_MESSAGE,
    NO_UPCOMING_RECORDS_MESSAGE,
    RECORD_CANCELLED_MESSAGE,
    RECORD_TYPE,
    RECORDS_HEADER_MESSAGE,
    RECORDS_MESSAGE_TEMPLATE,
    REJECTION_MESSAGE,
    SELECT_ACTION_MESSAGE,
    SELECT_COMMAND_MESSAGE,
    SELECT_DATE_MESSAGE,
    SELECTED_DATE,
    SELECTED_DATE_MESSAGE,
    SERVICE_NAMES,
    SUCCESS_REQUEST_MESSAGE,
    TEXT_INFO,
    TIME_DATA,
    UNKNOWN_SERVICE,
    URL_INFO,
    USER_CANCEL_NOTIFICATION_MESSAGE,
    USER_NAME,
    USER_REJECTION_MESSAGE,
    USER_REQUEST_MESSAGE,
    USER_STATE_ADDING_DATE,
    USER_STATE_CANCELING_RECORD,
    USER_STATES,
    USER_TEXT,
    USER_TEXT2,
    USER_TEXT3,
    USER_TEXT4,
    WELCOME_MESSAGE_ADMIN,
    WELCOME_MESSAGE_USER,
    YES_BUTTON,
)
from services.date_service import (
    add_date,
    book_date_in_file,
    get_available_dates,
    get_filtered_records,
    get_upcoming_records,
    get_user_records,
    update_record,
)
from user_type import ADMIN_IDS, get_buttons_for_user, is_admin


async def wake_up(update, context) -> None:
    """Отправляет сообщение о том, что бот активирован, с кнопками."""
    chat = update.effective_chat
    chat_id = update.message.chat.id
    name = update.message.chat.first_name
    username = update.message.chat.username

    if username is None:
        await context.bot.send_message(
            chat_id=chat_id, text=GET_USERNAME_MESSAGE
        )
        return

    if is_admin(chat_id):
        reply_markup = get_admin_buttons()  # Получаем администраторские кнопки
        await context.bot.send_message(
            chat_id=chat.id,
            text=WELCOME_MESSAGE_ADMIN.format(name),
            reply_markup=reply_markup,
        )
    else:
        reply_markup = get_user_buttons()  # Получаем пользовательские кнопки
        await context.bot.send_message(
            chat_id=chat.id,
            text=WELCOME_MESSAGE_USER.format(name),
            reply_markup=reply_markup,
        )


async def add_date_handler(update, context) -> None:
    """Запрашивает у пользователя ввод даты и времени."""
    chat_id = update.callback_query.message.chat.id  # Используем callback_query
    USER_STATES[chat_id] = (
        USER_STATE_ADDING_DATE  # Устанавливаем состояние пользователя
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=DATE_REQUEST_MESSAGE,
        reply_markup=get_cancel_keyboard(),
    )


async def cancel_handler(update, context) -> None:
    """Обрабатывает команду отмены."""
    chat_id = update.callback_query.message.chat.id
    query = update.callback_query
    await query.answer()
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )

    # Проверяем, есть ли состояние для данного пользователя
    if USER_STATES.get(chat_id) is not None:
        USER_STATES[chat_id] = None  # Сбрасываем состояние
        await context.bot.send_message(
            chat_id=chat_id, text=CANCEL_OPERATION_MESSAGE
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, text=NO_ACTIVE_OPERATION_MESSAGE
        )

    reply_markup = get_buttons_for_user(chat_id)

    # Отправляем сообщение с кнопками
    await context.bot.send_message(
        chat_id=chat_id, text=SELECT_ACTION_MESSAGE, reply_markup=reply_markup
    )


async def handle_date_input(update, context) -> None:
    """Обрабатывает ввод даты и времени от пользователя."""
    chat_id = update.message.chat.id

    if USER_STATES.get(chat_id) == USER_STATE_ADDING_DATE:
        date_time = update.message.text

        try:
            date_str, time_str = (
                date_time.split()
            )  # Разделяем ввод на дату и время
            result_message = add_date(
                date_str, time_str
            )  # Используем функцию для добавления даты

            if ERROR_MESSAGE in result_message:
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
            USER_STATES[chat_id] = (
                None  # Сбрасываем состояние только при успешном добавлении
            )
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text=DATE_TIME_FORMAT_ERROR_MESSAGE,
                reply_markup=get_cancel_keyboard(),
            )
            return
    else:
        reply_markup = get_buttons_for_user(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=SELECT_COMMAND_MESSAGE,
            reply_markup=reply_markup,
        )


async def view_records(update, context) -> None:
    """
    Отправляет пользователю список записей, отсортированный по дате и времени.
    """
    chat_id = update.callback_query.message.chat.id
    reply_markup = get_buttons_for_user(chat_id)

    # Получаем отфильтрованные записи
    sorted_records = get_filtered_records()

    # Формирование сообщения
    if not sorted_records.empty:
        message = RECORDS_HEADER_MESSAGE
        for index, row in sorted_records.iterrows():
            record_message = (
                f"📅  {row[DATE_DATA].strftime(DATE_FORMAT)}  📅    "
                f"⏰  {row[TIME_DATA]}  ⏰\n"
            )

            # Добавляем имя, если оно не "Неизвестно"
            if row[USER_NAME] is not None and not pd.isna(row[USER_NAME]):
                record_message += f"👤  {row[USER_NAME]: <22}"
            if row[RECORD_TYPE] is not None and not pd.isna(row[RECORD_TYPE]):
                record_message += f"🌟  {row[RECORD_TYPE]}\n"

            # Добавляем подтверждение, если оно равно 1
            if row[CONFIRMATION_DATA] == CONFIRMATION_RECEIVED:
                record_message += f"{CONFIRMED_MESSAGE: >30}\n"

            message += f"{record_message}\n"
    else:
        message = NO_RECORDS_MESSAGE

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

    # Фильтруем записи, где нет подтверждения
    free_records = sorted_records[sorted_records[CONFIRMATION_DATA].isnull()]

    # Формирование сообщения
    if not free_records.empty:
        message = FREE_RECORDS_HEADER_MESSAGE
        for index, row in free_records.iterrows():
            record_message = (
                f"📅  {row[DATE_DATA].strftime(DATE_FORMAT)}  "
                f"📅     ⏰  {row[TIME_DATA]}  ⏰\n"
            )
            message += f"{record_message}\n"
    else:
        message = NO_FREE_RECORDS_MESSAGE

    await context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup
    )


async def book_date(update, context) -> None:
    """Запрашивает у пользователя выбор свободной даты."""
    chat_id = update.callback_query.message.chat.id
    available_dates = get_available_dates()

    if not available_dates:
        reply_markup = get_buttons_for_user(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=NO_AVAILABLE_DATES_MESSAGE,
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
        text=SELECT_DATE_MESSAGE,
        reply_markup=reply_markup,
    )


async def handle_booking(update, context) -> None:
    """Обрабатывает выбор даты от пользователя."""
    query = update.callback_query
    await query.answer()
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    chat_id = update.callback_query.message.chat.id
    selected_date = update.callback_query.data.split("_")[1]

    # Отправляем пользователю кнопки для выбора услуги
    await context.bot.send_message(
        chat_id=chat_id,
        text=SELECTED_DATE_MESSAGE.format(selected_date),
        reply_markup=get_type_buttons(),  # Отправляем кнопки выбора услуг
    )

    context.user_data[SELECTED_DATE] = selected_date


async def handle_service_choice(update, context):
    """Обработчик выбора типа услуги."""
    query = update.callback_query
    await query.answer()

    # Получаем выбранную услугу из callback_data
    chosen_service = query.data.split("_")[1]

    # Извлекаем дату из user_data
    selected_date = context.user_data.get(SELECTED_DATE)
    if not selected_date:
        await query.message.reply_text(ERROR_DATE_MESSAGE)
        return

    user_id = query.from_user.id
    username = query.from_user.username

    # Получаем читаемое название услуги
    service_name = SERVICE_NAMES.get(chosen_service, UNKNOWN_SERVICE)

    # Отправляем сообщение администратору
    admin_id = ADMIN_IDS[0]
    keyboard = [
        [
            InlineKeyboardButton(
                YES_BUTTON,
                callback_data=f"confirm|{selected_date}|{user_id}"
                f"|{username}|{service_name}",
            ),
            InlineKeyboardButton(NO_BUTTON, callback_data=f"deny|{user_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=admin_id,
        text=f"{USER_TEXT}{username}"
        f"{USER_TEXT2}{service_name}{USER_TEXT3}"
        f"{selected_date}{USER_TEXT4}",
        reply_markup=reply_markup,
    )

    # Убираем кнопки выбора услуги у пользователя
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=BOOKING_REQUEST_MESSAGE,
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
    service_type = data[4]  # Извлекаем тип услуги

    reply_markup = get_buttons_for_user(user_id)

    # Обновляем информацию о бронировании
    book_date_in_file(
        selected_date, user_id, name, service_type  # Передаем тип услуги
    )  # Функция для записи в файл

    # Уведомляем пользователя
    await context.bot.send_message(
        chat_id=user_id, text=CONFIRMED_MESSAGE, reply_markup=reply_markup
    )
    await query.message.edit_text(text=CONFIRMED_MESSAGE, reply_markup=None)


async def deny_booking(update, context) -> None:
    """Обрабатывает отклонение бронирования пользователем."""
    query = update.callback_query
    chat_id = update.callback_query.message.chat.id
    await query.answer()  # Это важно для подтверждения нажатия кнопки
    reply_markup = get_buttons_for_user(chat_id)
    user_id = query.data.split("|")[1]  # Извлекаем ID пользователя

    # Обновляем сообщение с отключенными кнопками
    await query.message.edit_text(
        text=REJECTION_MESSAGE, reply_markup=reply_markup
    )

    reply_markup = get_buttons_for_user(user_id)
    await context.bot.send_message(
        chat_id=user_id,
        text=USER_REJECTION_MESSAGE,
        reply_markup=reply_markup,
    )


async def view_personal_records(update, context) -> None:
    """Обрабатывает запрос пользователя на просмотр своих записей."""
    user_id = update.callback_query.from_user.id  # Получаем ID пользователя
    records = get_user_records(user_id)  # Получаем записи пользователя
    reply_markup = get_buttons_for_user(user_id)

    # Проверяем, есть ли записи
    if records is None or len(records) == 0:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=NO_RECORDS_MESSAGE,
        )
        return

    # Формируем сообщения на основе полученных записей
    messages = [
        RECORDS_MESSAGE_TEMPLATE.format(type=type, date=date, time=time)
        for date, time, type in records
    ]

    # Отправляем сообщения пользователю
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text="\n".join(messages),
        reply_markup=reply_markup,  # Здесь оставить кнопку для отмены записи
    )


async def cancel_record(update, context) -> None:
    """Отменяет запись пользователя."""
    user_id = update.callback_query.from_user.id
    records = get_user_records(user_id)  # Получаем записи пользователя

    if records is None or len(records) == 0:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=NO_RECORDS_TO_CANCEL_MESSAGE,
        )
        return

    # Создаем кнопки для каждой записи
    buttons = [
        InlineKeyboardButton(
            CANCEL_RECORD_BUTTON_TEXT.format(type=type, date=date, time=time),
            callback_data=f"confirm_cancel_{date}_{time}",
        )
        for date, time, type in records
    ]
    reply_markup = InlineKeyboardMarkup([[button] for button in buttons])

    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=CANCEL_RECORD_PROMPT_MESSAGE,
        reply_markup=reply_markup,
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
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    # Отправляем сообщение пользователю
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text=RECORD_CANCELLED_MESSAGE.format(date=date, time=time),
        reply_markup=reply_markup,
    )

    # Уведомляем администратора
    await context.bot.send_message(
        chat_id=ADMIN_IDS[0],
        text=ADMIN_CANCEL_NOTIFICATION_MESSAGE.format(
            name=name, date=date, time=time
        ),
    )


async def handle_admin_cancel_date(update, context):
    """Обработчик для кнопки отмены записи администратором."""
    query = update.callback_query
    await query.answer()

    # Получаем список предстоящих записей
    upcoming_records = get_upcoming_records()

    # Проверяем, есть ли записи для отмены
    if not upcoming_records:
        await query.message.reply_text(NO_UPCOMING_RECORDS_MESSAGE)
        return

    # Формируем кнопки для отмены записей
    buttons = []
    for record in upcoming_records:
        date, time, name, service_type, id = record
        button_text = f"{date} в {time} - {name} ({service_type})"
        buttons.append(
            [
                InlineKeyboardButton(
                    button_text, callback_data=f"cancel|{date}|{time}|{id}"
                )
            ]
        )

    # Отправляем сообщение с кнопками
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(
        CANCEL_QUESTION_PROMPT_MESSAGE, reply_markup=reply_markup
    )


async def request_confirm_admin_cancel_record(update, context):
    """Запрашивает согласие на отмену записи."""
    query = update.callback_query
    await query.answer()
    data = update.callback_query.data.split("|")
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    USER_STATES[ADMIN_IDS[0]] = (
        USER_STATE_CANCELING_RECORD  # Устанавливаем состояние пользователя
    )
    buttons = [
        [
            InlineKeyboardButton(
                YES_BUTTON,
                callback_data=f"handle_admin_cancel_record|{data[1]}|{data[2]}|{data[3]}",
            ),
            InlineKeyboardButton(
                NO_BUTTON,
                callback_data="cancel",
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(CONFIRM_CANCELING, reply_markup=reply_markup)


async def handle_admin_cancel_record(update, context):
    """Обработчик для отмены записи по выбранной дате администратором."""
    query = update.callback_query
    await query.answer()
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    data = update.callback_query.data.split("|")
    update_record(int(data[3]), data[1], data[2])
    USER_STATES[ADMIN_IDS[0]] = None
    # Уведомляем администратора
    await context.bot.send_message(
        chat_id=ADMIN_IDS[0],
        text=ADMIN_CANCEL_RECORD_MESSAGE.format(date=data[1], time=data[2]),
        reply_markup=get_admin_buttons(),
    )

    # Уведомляем пользователя
    await context.bot.send_message(
        chat_id=int(data[3]),
        text=USER_CANCEL_NOTIFICATION_MESSAGE,
        reply_markup=get_buttons_for_user(int(data[3])),
    )


async def view_info(update, context):
    """Отправляет сообщение с текстом об услугах и другой информации."""
    chat_id = update.callback_query.from_user.id
    chat_message = TEXT_INFO + URL_INFO
    await context.bot.send_message(
        chat_id=chat_id,
        text=chat_message,
        reply_markup=get_buttons_for_user(chat_id),
    )


async def ask_date(update, context):
    """Отправляет запрос администратору с просьбой добавить свободные даты."""
    admin_id = ADMIN_IDS[0]
    username = update.callback_query.from_user.username
    user_id = update.callback_query.from_user.id
    await context.bot.send_message(
        chat_id=admin_id,
        text=USER_REQUEST_MESSAGE.format(username=username),
        reply_markup=get_buttons_for_user(admin_id),
    )
    await context.bot.send_message(
        chat_id=user_id,
        text=SUCCESS_REQUEST_MESSAGE,
        reply_markup=get_buttons_for_user(user_id),
    )
