from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_buttons():
    """Создает администраторские кнопки."""
    buttons = [
        [
            InlineKeyboardButton(
                "👀 Посмотреть записи", callback_data="view_records"
            ),
            InlineKeyboardButton(
                "🗓️ Добавить свободную дату", callback_data="add_date"
            ),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_user_buttons():
    """Создает пользовательские кнопки."""
    buttons = [
        [
            InlineKeyboardButton(
                "👀 Посмотреть свободные даты",
                callback_data="view_free_records",
            ),
            InlineKeyboardButton("✍️ Записаться", callback_data="book_date"),
        ],
        [
            InlineKeyboardButton("📜Мои записи", callback_data="my_records"),
            InlineKeyboardButton("❌ Отменить запись", callback_data="cancel_record"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def get_cancel_keyboard():
    """Создает клавиатуру с кнопкой отмены."""
    buttons = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(buttons)
