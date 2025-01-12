ADMIN_IDS = [792230644]  # Список ID администраторов

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором."""
    return user_id in ADMIN_IDS