import os

from dotenv import load_dotenv

from buttons.buttons import get_admin_buttons, get_user_buttons

load_dotenv()
ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")
ADMIN_IDS = list(map(int, ADMIN_IDS))


def is_admin(user_id):
    """Проверяет, является ли пользователь администратором."""
    return user_id in ADMIN_IDS


def get_buttons_for_user(user_id):
    """Возвращает соответствующую клавиатуру в зависимости от типа пользователя."""
    if user_id in ADMIN_IDS:
        return get_admin_buttons()  # Возвращаем администраторские кнопки
    else:
        return get_user_buttons()  # Возвращаем пользовательские кнопки
