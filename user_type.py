from buttons.buttons import get_admin_buttons, get_user_buttons

ADMIN_IDS = [792230644]  # Список ID администраторов


def is_admin(user_id):
    """Проверяет, является ли пользователь администратором."""
    return user_id in ADMIN_IDS


def get_buttons_for_user(user_id):
    """Возвращает соответствующую клавиатуру в зависимости от типа пользователя."""
    if user_id in ADMIN_IDS:
        return get_admin_buttons()  # Возвращаем администраторские кнопки
    else:
        return get_user_buttons()  # Возвращаем пользовательские кнопки
