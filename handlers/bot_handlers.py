from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from buttons.buttons import (
    comfirm_canceling_record_buttons,
    get_admin_buttons,
    get_asking_buttons,
    get_cancel_admin_records,
    get_cancel_keyboard,
    get_cancel_user_records,
    get_deleting_date_buttons,
    get_free_dates_buttons,
    get_type_buttons,
    get_user_buttons,
)
from data import (
    ADMIN_CANCEL_NOTIFICATION_MESSAGE,
    ADMIN_CANCEL_RECORD_MESSAGE,
    BOOKING_REQUEST_MESSAGE,
    CANCEL_OPERATION_MESSAGE,
    CANCEL_QUESTION_PROMPT_MESSAGE,
    CANCEL_RECORD_PROMPT_MESSAGE,
    COMMENT,
    CONFIRM_CANCELING,
    CONFIRMED_MESSAGE,
    CONFIRMED_MESSAGE_FOR_USER,
    DATE_REQUEST_MESSAGE,
    DATE_TIME_FORMAT_ERROR_MESSAGE,
    ERROR_DATE_MESSAGE,
    ERROR_DELETE_MESSAGE,
    FREE_RECORDS_HEADER_MESSAGE,
    GET_USERNAME_MESSAGE,
    LAST_BOT_MESSAGE_ID,
    NO_ACTIVE_OPERATION_MESSAGE,
    NO_AVAILABLE_DATES_MESSAGE,
    NO_BUTTON,
    NO_FREE_RECORDS_MESSAGE,
    NO_RECORDS_MESSAGE,
    NO_RECORDS_TO_CANCEL_MESSAGE,
    NO_UPCOMING_RECORDS_MESSAGE,
    RECORD_CANCELLED_MESSAGE,
    RECORDS_HEADER_MESSAGE,
    RECORDS_MESSAGE_TEMPLATE,
    REJECTION_MESSAGE,
    SELECT_ACTION_MESSAGE,
    SELECT_COMMAND_MESSAGE,
    SELECT_DATE_MESSAGE,
    SELECT_DELETING_DATE_MESSAGE,
    SELECT_DELETING_DATE_MESSAGE_ERROR,
    SELECTED_DATE,
    SELECTED_DATE_MESSAGE,
    SEND_REQUEST_MESSAGE,
    SERVICE_NAMES,
    SUCCESS_DELETE_MESSAGE,
    SUCCESS_MESSAGE,
    SUCCESS_REQUEST_MESSAGE,
    TEXT_INFO,
    UNKNOWN_SERVICE,
    URL_INFO,
    USER_CANCEL_NOTIFICATION_MESSAGE,
    USER_REJECTION_MESSAGE,
    USER_REQUEST_MESSAGE_WITH_COM,
    USER_REQUEST_MESSAGE_WITHOUT_COM,
    USER_STATE_ADDING_COMMENT,
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
    text,
)
from services.data_service_sql import (
    add_date,
    book_date_in_file,
    delete_date,
    get_available_dates,
    get_filtered_records,
    get_upcoming_records,
    get_user_records,
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
        reply_markup = get_admin_buttons()
        await context.bot.send_message(
            chat_id=chat.id,
            text=WELCOME_MESSAGE_ADMIN.format(name),
            reply_markup=reply_markup,
        )
    else:
        reply_markup = get_user_buttons()
        await context.bot.send_message(
            chat_id=chat.id,
            text=WELCOME_MESSAGE_USER.format(name),
            reply_markup=reply_markup,
        )


async def add_date_handler(update, context) -> None:
    """Запрашивает у пользователя ввод даты и времени."""
    chat_id = update.callback_query.message.chat.id
    await update.callback_query.message.delete()

    USER_STATES[chat_id] = USER_STATE_ADDING_DATE

    sent_message = await context.bot.send_message(
        chat_id=chat_id,
        text=DATE_REQUEST_MESSAGE,
        reply_markup=get_cancel_keyboard(),
    )

    context.user_data[LAST_BOT_MESSAGE_ID] = sent_message.message_id


async def cancel_handler(update, context) -> None:
    """Обрабатывает команду отмены."""
    global text
    text = ""

    chat_id = update.callback_query.message.chat.id
    query = update.callback_query
    await query.answer()
    await update.callback_query.message.delete()

    if USER_STATES.get(chat_id) is not None:
        USER_STATES[chat_id] = None
        await update.callback_query.answer(
            text=CANCEL_OPERATION_MESSAGE, show_alert=True
        )
    else:
        await update.callback_query.answer(NO_ACTIVE_OPERATION_MESSAGE)

    reply_markup = get_buttons_for_user(chat_id)

    await context.bot.send_message(
        chat_id=chat_id, text=SELECT_ACTION_MESSAGE, reply_markup=reply_markup
    )


async def handle_date_input(update, context) -> None:
    """Обрабатывает ввод даты и времени от пользователя."""
    chat_id = update.message.chat.id

    # Удаляем предыдущее сообщение бота, если оно есть
    if LAST_BOT_MESSAGE_ID in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=context.user_data["last_bot_message_id"],
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

    if USER_STATES.get(chat_id) == USER_STATE_ADDING_DATE:
        date_time = update.message.text

        try:
            date, time = date_time.split()
            result_message = add_date(date, time)

            if not isinstance(result_message, bool):
                # Отправляем новое сообщение и сохраняем его ID
                sent_message = await context.bot.send_message(
                    chat_id=chat_id,
                    text=result_message,
                    reply_markup=get_cancel_keyboard(),
                )
                context.user_data["last_bot_message_id"] = (
                    sent_message.message_id
                )
                return

            reply_markup = get_buttons_for_user(chat_id)

            sent_message = await context.bot.send_message(
                chat_id=chat_id,
                text=SUCCESS_MESSAGE,
                reply_markup=reply_markup,
            )
            context.user_data[LAST_BOT_MESSAGE_ID] = sent_message.message_id
            USER_STATES[chat_id] = None

        except ValueError:
            # Отправляем новое сообщение и сохраняем его ID
            sent_message = await context.bot.send_message(
                chat_id=chat_id,
                text=DATE_TIME_FORMAT_ERROR_MESSAGE,
                reply_markup=get_cancel_keyboard(),
            )
            context.user_data[LAST_BOT_MESSAGE_ID] = sent_message.message_id
            return

    elif USER_STATES.get(chat_id) == USER_STATE_ADDING_COMMENT:
        await handle_comment_input(update, context)
    else:
        reply_markup = get_buttons_for_user(chat_id)
        # Отправляем новое сообщение и сохраняем его ID
        sent_message = await context.bot.send_message(
            chat_id=chat_id,
            text=SELECT_COMMAND_MESSAGE,
            reply_markup=reply_markup,
        )
        context.user_data[LAST_BOT_MESSAGE_ID] = sent_message.message_id


async def view_records(update, context) -> None:
    """
    Отправляет пользователю список записей, отсортированный по дате и времени.
    """
    chat_id = update.callback_query.message.chat.id
    reply_markup = get_buttons_for_user(chat_id)
    await update.callback_query.message.delete()

    sorted_records = get_filtered_records()
    if sorted_records:
        message = RECORDS_HEADER_MESSAGE
        for items in sorted_records:
            record = f"📅  {items[0]}  📅    ⏰  {items[1]}  ⏰\n"
            if all(item is not None for item in items[3: len(items)]):
                record += (
                    f"👤  {items[3]: <22}"
                    f"🌟  {items[6]}\n"
                    f"  {CONFIRMED_MESSAGE: >30}\n"
                )
            message += f"{record}\n"
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

    sorted_records = get_available_dates()
    await update.callback_query.message.delete()

    if sorted_records:
        message = FREE_RECORDS_HEADER_MESSAGE
        for items in sorted_records:
            record = (
                f"📅  {items.split()[0]}  📅    "
                f"⏰  {items.split()[1]}  ⏰\n"
            )
            message += f"{record}\n"
    else:
        message = NO_FREE_RECORDS_MESSAGE

    await context.bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup
    )


async def book_date(update, context) -> None:
    """Запрашивает у пользователя выбор свободной даты."""
    chat_id = update.callback_query.message.chat.id
    available_dates = get_available_dates()
    await update.callback_query.message.delete()

    if not available_dates:
        reply_markup = get_buttons_for_user(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=NO_AVAILABLE_DATES_MESSAGE,
            reply_markup=reply_markup,
        )
        return
    reply_markup = get_free_dates_buttons(available_dates)

    await context.bot.send_message(
        chat_id=chat_id,
        text=SELECT_DATE_MESSAGE,
        reply_markup=reply_markup,
    )


async def handle_booking(update, context) -> None:
    """Обрабатывает выбор даты от пользователя."""
    query = update.callback_query
    await query.answer()
    await update.callback_query.message.delete()
    chat_id = update.callback_query.message.chat.id
    selected_date = update.callback_query.data.split("_")[1]

    await context.bot.send_message(
        chat_id=chat_id,
        text=SELECTED_DATE_MESSAGE.format(selected_date),
        reply_markup=get_type_buttons(),
    )

    context.user_data[SELECTED_DATE] = selected_date


async def handle_service_choice(update, context):
    """Обработчик выбора типа услуги."""
    query = update.callback_query
    await update.callback_query.message.delete()
    await query.answer()

    chosen_service = query.data.split("_")[1]

    selected_date = context.user_data.get(SELECTED_DATE)
    if not selected_date:
        await query.message.reply_text(ERROR_DATE_MESSAGE)
        return

    user_id = query.from_user.id
    username = query.from_user.username

    service_name = SERVICE_NAMES.get(chosen_service, UNKNOWN_SERVICE)

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

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=BOOKING_REQUEST_MESSAGE,
        reply_markup=get_user_buttons(),
    )


async def confirm_booking(update, context) -> None:
    """Обрабатывает подтверждение бронирования пользователем."""
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    selected_date = data[1]
    user_id = data[2]
    username = data[3]
    service_type = data[4]

    book_date_in_file(
        selected_date=selected_date,
        user_id=user_id,
        username=username,
        service_type=service_type,
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=CONFIRMED_MESSAGE_FOR_USER.format(
            type=service_type, date=selected_date
        ),
        # reply_markup=reply_markup
    )
    await query.message.edit_text(text=CONFIRMED_MESSAGE)


async def deny_booking(update, context) -> None:
    """Обрабатывает отклонение бронирования пользователем."""
    query = update.callback_query
    await query.answer()
    user_id = query.data.split("|")[1]

    await query.message.edit_text(text=REJECTION_MESSAGE)

    reply_markup = get_buttons_for_user(user_id)
    await context.bot.send_message(
        chat_id=user_id,
        text=USER_REJECTION_MESSAGE,
        reply_markup=reply_markup,
    )


async def view_personal_records(update, context) -> None:
    """Обрабатывает запрос пользователя на просмотр своих записей."""
    user_id = update.callback_query.from_user.id
    records = get_user_records(user_id=user_id)
    reply_markup = get_buttons_for_user(user_id)
    await update.callback_query.message.delete()

    if records is None or len(records) == 0:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=NO_RECORDS_MESSAGE,
            reply_markup=reply_markup,
        )
        return

    messages = [
        RECORDS_MESSAGE_TEMPLATE.format(type=type, date=date, time=time)
        for date, time, type in records
    ]

    await context.bot.send_message(
        chat_id=update.callback_query.message.chat.id,
        text="\n".join(messages),
        reply_markup=reply_markup,
    )


async def cancel_record(update, context) -> None:
    """Отменяет запись пользователя."""
    user_id = update.callback_query.from_user.id
    records = get_user_records(user_id)
    await update.callback_query.message.delete()
    reply_markup = get_buttons_for_user(user_id)
    if records is None or len(records) == 0:
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text=NO_RECORDS_TO_CANCEL_MESSAGE,
            reply_markup=reply_markup,
        )
        return

    reply_markup = get_cancel_user_records(records)

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
    await update.callback_query.message.delete()
    book_date_in_file(selected_date=(date + " " + time))
    await update.callback_query.answer()
    reply_markup = get_user_buttons()

    await context.bot.send_message(
        chat_id=user_id,
        text=RECORD_CANCELLED_MESSAGE.format(date=date, time=time),
        reply_markup=reply_markup,
    )

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
    await update.callback_query.message.delete()

    upcoming_records = get_upcoming_records()

    reply_markup = get_admin_buttons()
    if not upcoming_records:
        await query.message.reply_text(
            NO_UPCOMING_RECORDS_MESSAGE, reply_markup=reply_markup
        )
        return

    reply_markup = get_cancel_admin_records(upcoming_records)
    await query.message.reply_text(
        CANCEL_QUESTION_PROMPT_MESSAGE, reply_markup=reply_markup
    )


async def request_confirm_admin_cancel_record(update, context):
    """Запрашивает согласие на отмену записи."""
    query = update.callback_query
    await query.answer()
    data = update.callback_query.data.split("|")
    await update.callback_query.message.delete()
    USER_STATES[ADMIN_IDS[0]] = USER_STATE_CANCELING_RECORD
    reply_markup = comfirm_canceling_record_buttons(data)
    await query.message.reply_text(CONFIRM_CANCELING, reply_markup=reply_markup)


async def handle_admin_cancel_record(update, context):
    """Обработчик для отмены записи по выбранной дате администратором."""
    query = update.callback_query
    await query.answer()
    await update.callback_query.message.delete()
    data = update.callback_query.data.split("|")
    if data[2].startswith("0"):
        data[2] = data[2][1:]
    book_date_in_file(selected_date=(data[1] + " " + data[2]))
    USER_STATES[ADMIN_IDS[0]] = None

    await context.bot.send_message(
        chat_id=ADMIN_IDS[0],
        text=ADMIN_CANCEL_RECORD_MESSAGE.format(date=data[1], time=data[2]),
        reply_markup=get_admin_buttons(),
    )

    await context.bot.send_message(
        chat_id=int(data[3]),
        text=USER_CANCEL_NOTIFICATION_MESSAGE,
        # reply_markup=get_buttons_for_user(int(data[3])),
    )


async def view_info(update, context):
    """Отправляет сообщение с текстом об услугах и другой информации."""
    chat_id = update.callback_query.from_user.id
    await update.callback_query.message.delete()
    chat_message = TEXT_INFO + URL_INFO
    await context.bot.send_message(
        chat_id=chat_id,
        text=chat_message,
        reply_markup=get_buttons_for_user(chat_id),
    )


async def ask_date(update, context):
    """Устанавливает состояние добавления комментария."""
    user_id = update.callback_query.from_user.id
    await update.callback_query.message.delete()

    sent_message = await context.bot.send_message(
        chat_id=user_id,
        text=SEND_REQUEST_MESSAGE,
        reply_markup=get_asking_buttons(),
    )
    context.user_data[LAST_BOT_MESSAGE_ID] = sent_message.message_id

    USER_STATES[user_id] = USER_STATE_ADDING_COMMENT


async def handle_comment_input(update, context) -> None:
    """Обрабатывает комментарий пользователя."""
    user_id = update.message.from_user.id
    if USER_STATES.get(user_id) == USER_STATE_ADDING_COMMENT:
        await context.bot.delete_message(
            chat_id=update.message.chat.id, message_id=update.message.message_id
        )
        bot_message_id = context.user_data.get(LAST_BOT_MESSAGE_ID)
        if bot_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.message.chat.id, message_id=bot_message_id
                )
            except Exception as e:
                print(f"Не удалось удалить сообщение бота: {e}")
        global text
        text += update.message.text + "\n"

        await context.bot.send_message(
            chat_id=user_id,
            text=COMMENT.format(text=text),
            reply_markup=get_asking_buttons(),
        )


async def send_handler(update, context) -> None:
    """Отправляет запрос администратору с просьбой добавить свободные даты."""
    global text
    admin_id = ADMIN_IDS[0]
    username = update.callback_query.from_user.username
    user_id = update.callback_query.from_user.id
    await update.callback_query.message.delete()

    USER_STATES[user_id] = None
    if text:
        await context.bot.send_message(
            chat_id=admin_id,
            text=USER_REQUEST_MESSAGE_WITH_COM.format(
                username=username, com=text
            ),
            # reply_markup=get_buttons_for_user(admin_id),
        )
        text = ""
    else:
        await context.bot.send_message(
            chat_id=admin_id,
            text=USER_REQUEST_MESSAGE_WITHOUT_COM.format(username=username),
            reply_markup=get_buttons_for_user(admin_id),
        )
    await context.bot.send_message(
        chat_id=user_id,
        text=SUCCESS_REQUEST_MESSAGE,
        reply_markup=get_buttons_for_user(user_id),
    )


async def get_dates_for_deleting(update, context):
    """Получаем кнопки для удаления даты."""
    chat_id = update.callback_query.from_user.id
    await update.callback_query.message.delete()
    available_dates = get_available_dates()
    if available_dates:
        reply_markup = get_deleting_date_buttons(available_dates)

        await context.bot.send_message(
            chat_id=chat_id,
            text=SELECT_DELETING_DATE_MESSAGE,
            reply_markup=reply_markup,
        )
    else:
        reply_markup = get_buttons_for_user(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=SELECT_DELETING_DATE_MESSAGE_ERROR,
            reply_markup=reply_markup,
        )


async def delete_dates(update, context):
    """Удаляет выбранную дату из файла."""
    chat_id = update.callback_query.from_user.id
    query = update.callback_query
    await query.answer()
    await update.callback_query.message.delete()
    data = update.callback_query.data.split("|")

    delete = delete_date(data[1])
    if delete is False:
        await context.bot.send_message(
            chat_id=chat_id,
            text=ERROR_DELETE_MESSAGE,
        )

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=SUCCESS_DELETE_MESSAGE.format(data=data[1]),
            reply_markup=get_buttons_for_user(chat_id),
        )
