from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    buttons = [
        [
            InlineKeyboardButton(
                "💅 Маникюр", callback_data="service_manicure"
            ),
            InlineKeyboardButton(
                "🦶 Педикюр", callback_data="service_pedicure"
            ),
            InlineKeyboardButton("🌟 Брови", callback_data="service_brows"),
        ]
    ]
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
