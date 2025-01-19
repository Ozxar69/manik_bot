# bot_handlers.py
DATA_FILE = "dates.csv"
USER_STATES = {}
SERVICE_NAMES = {"manicure": "Маникюр", "pedicure": "Педикюр", "brows": "Брови"}
WELCOME_MESSAGE_ADMIN = (
    "Привет, {}, есть новые даты? Можешь посмотреть имеющиеся записи."
)
WELCOME_MESSAGE_USER = "Привет, {}! Я бот для записи.\nМожешь посмотреть список свободных дат и записаться."

DATE_REQUEST_MESSAGE = "Пожалуйста, введите дату и время в формате DD.MM HH:MM."
USER_STATE_ADDING_DATE = "adding_date"

CANCEL_OPERATION_MESSAGE = "Хорошо, операция отменена."
NO_ACTIVE_OPERATION_MESSAGE = "Нет активной операции для отмены."
SELECT_ACTION_MESSAGE = "Выберите действие:"

DATE_INPUT_ERROR_MESSAGE = (
    "Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM."
)
COMMAND_SELECTION_MESSAGE = "Выбери команду из списка."
DATE_TIME_FORMAT_ERROR_MESSAGE = (
    "Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM."
)
SELECT_COMMAND_MESSAGE = "Выбери команду из списка."
ERROR_MESSAGE = "Ошибка"

NO_RECORDS_MESSAGE = "😢 Записей нет "
RECORDS_HEADER_MESSAGE = "Твои ближайшие записи на месяц (ограничены 30):\n"
CONFIRMED_MESSAGE = "✅ Подтверждено"
DATE_DATA = "Дата"
TIME_DATA = "Время"
USER_NAME = "Имя"
CONFIRMATION_DATA = "Подтверждение"
RECORD_TYPE = "Тип"
ID_DATA = "id"
DATE_FORMAT = "%d.%m.%Y"
DATE_TIME_FORMAT = "%d.%m.%Y %H:%M"
TIME_FORMAT = "%H:%M"
CONFIRMATION_RECEIVED = 1
DATE_TIME_DATA = "Дата Время"

FREE_RECORDS_HEADER_MESSAGE = "Свободные записи:\n"
NO_FREE_RECORDS_MESSAGE = "😢  Свободных записей нет"

NO_AVAILABLE_DATES_MESSAGE = "Нет доступных дат для бронирования."
SELECT_DATE_MESSAGE = "Пожалуйста, выберите доступную дату:"

SELECTED_DATE_MESSAGE = "Вы выбрали дату: {}. Пожалуйста, выберите услугу:"
SELECTED_DATE = "selected_date"

ERROR_DATE_MESSAGE = "Ошибка: не удалось получить информацию о дате."
BOOKING_REQUEST_MESSAGE = "Ваш запрос на бронирование отправлен администратору."
YES_BUTTON = "Да"
NO_BUTTON = "Нет"
UNKNOWN_SERVICE = "Неизвестная услуга"
USER_TEXT = "Пользователь @"
USER_TEXT2 = " хочет записаться на "
USER_TEXT3 = " на дату "
USER_TEXT4 = ". Подтвердите запись?"

REJECTION_MESSAGE = "Подтверждение отклонено."
USER_REJECTION_MESSAGE = "К сожалению, не удалось подтвердить дату, выберите другую или свяжитесь с администратором."

RECORDS_MESSAGE_TEMPLATE = "Вы записаны на {type} - {date} в {time}."

NO_RECORDS_TO_CANCEL_MESSAGE = "У вас нет записей для отмены."
CANCEL_RECORD_PROMPT_MESSAGE = "Выберите запись для отмены:"
CANCEL_RECORD_BUTTON_TEXT = "❌ {type} {date} в {time}"

RECORD_CANCELLED_MESSAGE = "Запись на {date} в {time} отменена."
ADMIN_CANCEL_NOTIFICATION_MESSAGE = (
    "Клиент {name} отменил запись на {date} в {time}."
)

CANCEL_QUESTION_PROMPT_MESSAGE = "Какую запись вы хотите отменить?"
NO_UPCOMING_RECORDS_MESSAGE = "У вас нет предстоящих записей для отмены."

ADMIN_CANCEL_RECORD_MESSAGE = "Запись на {date} в {time} отменена."
USER_CANCEL_NOTIFICATION_MESSAGE = "К сожалению, ваша запись была отменена администратором. Попробуйте записаться на другую дату или свяжитесь с администратором."

# date_service.py

ERROR_PAST_DATE_MESSAGE = (
    "Ошибка: нельзя добавить дату и время, которые уже прошли."
)
ERROR_DUPLICATE_MESSAGE = (
    "Ошибка: такая дата и время уже существуют, добавьте другую."
)
SUCCESS_MESSAGE = "Дата успешно добавлена!"

TEXT_INFO = (
    "Список моих услуг:\n\n"
    "👣 SMART-Педикюр                   2000₽\n"
    "------------------------------------------\n"
    "💅 SMART-Педикюр и \n"
    "покрытие гель-лак                      2500₽\n"
    "------------------------------------------\n"
    "💅 Маникюр                                 1000₽\n"
    "------------------------------------------\n"
    "💅 Маникюр и \n"
    "покрытие гель-лак                       2000₽\n"
    "------------------------------------------\n"
    "💅 Маникюр и \n"
    "покрытие лаком                            1600₽\n"
    "------------------------------------------\n"
    "🛠️ Система восстановления \n"
    "ногтей IBX (если решили\n"
    " ходить без гель-лака)                   300₽\n"
    "------------------------------------------\n"
    "❌ Только снятие покрытия\n"
    " или снятие другого мастера       300₽\n"
    "------------------------------------------\n"
    "🇫🇷 Французский маникюр\n"
    " (все ногти)                                        300₽\n"
    "------------------------------------------\n"
    "🌈 Градиент/омбре/растяжка\n"
    " цвета (1 ноготь)                               100₽\n"
    "------------------------------------------\n"
    "🖌️ Стемпинг (1 ноготь)                   50₽\n"
    "------------------------------------------\n"
    "🌟 Ламинирование бровей        600₽\n"
    "------------------------------------------\n"
    "🎨 Окрашивание бровей            600₽\n"
)

URL_INFO = (
    "\nСсылочки на мои работы:\n"
    "Instagram (https://tinyurl.com/2t9zk75d)\n"
    "Avito (https://tinyurl.com/53eeerpx)"
)

ERROR_FILE_NOT_FOUND = "Ошибка: файл с датами не найден."
ERROR_DATE_TIME_NOT_FOUND = "Ошибка: выбранная дата и время не найдены."

GET_USERNAME_MESSAGE = "У вас не указан username в профиле.\n" \
                       "Пожалуйста выберите username, он необходим для моей обратной связи с вами.\n" \
                       "Для этого перейдите Мой профиль - Редактировать - Имя пользователя.\n" \
                       "После чего вы можете перезапустить бота нажав в меню старт или нажать сюда -\n /start"

USER_REQUEST_MESSAGE = "Польльзователь @{username} просит вас добавить свободную дату для записи"
SUCCESS_REQUEST_MESSAGE = "Ваш запрос отправлен админинстратору 👌\n" \
                          "Следите за обновлениями 👀"