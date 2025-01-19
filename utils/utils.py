import re
from user_type import ADMIN_IDS


async def request_phone_number(update, context):
    """Запрашивает номер телефона у пользователя."""
    user_id = update.callback_query.from_user.id
    context.user_data['waiting_for_phone'] = True  # Устанавливаем флаг ожидания номера телефона

    # Отправляем сообщение с просьбой ввести номер телефона
    await update.callback_query.message.reply_text(
        "Пожалуйста, введите ваш номер телефона в формате +7хххххххххх."
    )


async def handle_phone_number(update, context):
    """Обрабатывает ввод номера телефона от пользователя."""
    phone_number = update.message.text
    admin_id = ADMIN_IDS[0]

    # Проверяем валидность номера телефона
    if validate_phone_number(phone_number):
        context.user_data[
            'phone_number'] = phone_number  # Сохраняем номер телефона
        username = phone_number  # Присваиваем номер телефона переменной username
        await update.message.reply_text("Спасибо! Ваш номер телефона сохранен.")

        await context.bot.send_message(
            chat_id=admin_id,
            text=username,
            reply_markup=None,
        )
        return username  # Возвращаем номер телефона

    else:
        await update.message.reply_text(
            "Неверный формат номера телефона. Пожалуйста, попробуйте снова."
        )


def validate_phone_number(phone_number):
    """Проверяет, является ли номер телефона валидным."""
    pattern = re.compile(r'^\+7\d{10}$')  # Формат: +7 и 10 цифр
    return bool(pattern.match(phone_number))

