from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data import CANCEL_RECORD_BUTTON_TEXT, YES_BUTTON, NO_BUTTON

cancel = [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]


def get_admin_buttons():
    """Создает администраторские кнопки."""
    buttons = [
        [
            InlineKeyboardButton(
                "🗓️ Добавить свободную дату", callback_data="add_date"
            ),
            InlineKeyboardButton(
                "🚷  Отменить запись", callback_data="admin_cancel_date"
            ),
        ],
        [
            InlineKeyboardButton(
                "🚫 Удалить дату", callback_data="get_dates_for_deleting"
            ),
        ],
        [
            InlineKeyboardButton(
                "👀 Посмотреть записи", callback_data="view_records"
            ),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def get_user_buttons():
    """Создает пользовательские кнопки."""
    buttons = [
        [
            InlineKeyboardButton(
                "ℹ️Вся информация об услугах",
                callback_data="full_info",
            ),
        ],
        [
            InlineKeyboardButton(
                "👀 Посмотреть свободные даты",
                callback_data="view_free_records",
            ),
        ],
        [
            InlineKeyboardButton("📜Мои записи", callback_data="my_records"),
            InlineKeyboardButton(
                "❌ Отменить запись", callback_data="cancel_record"
            ),
        ],
        [
            InlineKeyboardButton(
                "📅 Попросить добавить даты", callback_data="ask_date"
            ),
        ],
        [
            InlineKeyboardButton("✍️ Записаться", callback_data="book_date"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def get_cancel_keyboard():
    """Создает клавиатуру с кнопкой отмены."""
    buttons = [cancel]
    return InlineKeyboardMarkup(buttons)


def get_type_buttons():
    """Создает кнопки для выбора типа услуг."""
    buttons = [[
        InlineKeyboardButton(
            "💅 Маникюр", callback_data="service_manicure"
        ),
        InlineKeyboardButton(
            "🦶 Педикюр", callback_data="service_pedicure"
        ),
        InlineKeyboardButton("🌟 Брови", callback_data="service_brows"),
    ], cancel]
    return InlineKeyboardMarkup(buttons)


def get_asking_buttons():
    buttons = [[InlineKeyboardButton("Отправить запрос", callback_data="send_handler")],
               cancel]
    return InlineKeyboardMarkup(buttons)


def get_free_dates_buttons(available_dates):
    keyboard = [
        [InlineKeyboardButton(date, callback_data=f"book_{date}")]
        for date in available_dates
    ]
    keyboard.append(cancel)
    return InlineKeyboardMarkup(keyboard)


def get_cancel_user_records(records):
    buttons = [[
        InlineKeyboardButton(
            CANCEL_RECORD_BUTTON_TEXT.format(type=type, date=date, time=time),
            callback_data=f"confirm_cancel_{date}_{time}",
        )
        for date, time, type in records
    ], cancel]
    reply_markup = InlineKeyboardMarkup([button for button in buttons])

    return reply_markup


def get_cancel_admin_records(upcoming_records):
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
    buttons.append(cancel)
    return InlineKeyboardMarkup(buttons)


def comfirm_canceling_record_buttons(data):
    buttons = [
        [
            InlineKeyboardButton(
                YES_BUTTON,
                callback_data=f"handle_admin_cancel_record|{data[1]}"
                              f"|{data[2]}|{data[3]}",
            ),
            InlineKeyboardButton(
                NO_BUTTON,
                callback_data="cancel",
            ),
        ], cancel
    ]
    return InlineKeyboardMarkup(buttons)
