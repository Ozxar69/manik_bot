import sqlite3
from datetime import datetime, timedelta

from data import (
    CREATE_TABLE,
    DATE_TIME_FORMAT,
    DB_PATH,
    ERROR_DUPLICATE_MESSAGE,
    ERROR_PAST_DATE_MESSAGE,
    FIND_TABLE,
    SORTED_RECORDS,
)
from utils.utils import get_current_time


def create_table() -> bool:
    """Проверяет, существует ли таблица 'clients', и создает ее, если нет."""
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(FIND_TABLE)
        table_exists = cur.fetchone()

        if not table_exists:
            cur.execute(CREATE_TABLE)
    return True


def check_datetime(date: str = "", time: str = "") -> list:
    """Проверяет дату, возвращает отфильтрованные записи по дате и времени."""
    current_datetime = get_current_time()
    current_year = current_datetime.year
    date_with_year = f"{date}.{current_year}"
    input_datetime = datetime.strptime(
        f"{date_with_year} {time}", DATE_TIME_FORMAT
    )
    if input_datetime < current_datetime:
        return ERROR_PAST_DATE_MESSAGE
    input_datetime_str = input_datetime.strftime(DATE_TIME_FORMAT)
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT date, time FROM clients WHERE date = ? AND time = ?",
            (input_datetime_str.split()[0], input_datetime_str.split()[1]),
        )
        if cur.fetchone():
            return ERROR_DUPLICATE_MESSAGE
    return input_datetime_str.split()


def add_date(date: str = "", time: str = ""):
    """Добавляет запись с указанной датой и временем."""
    if create_table():
        valid_data_time = check_datetime(date, time)
        if isinstance(valid_data_time, list):
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO "
                    "clients (date, time, datetime) "
                    "VALUES(?, ?, ?);",
                    (valid_data_time[0], time, f"{valid_data_time[0]} {time}"),
                )
                con.commit()
            return True
        else:
            return valid_data_time


def get_filtered_records() -> list:
    """Возвращает для админа все записи на месяц."""
    current_datetime = get_current_time()
    end_date = current_datetime + timedelta(days=30)
    result = []

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(SORTED_RECORDS)
        for item in cur:
            if (
                current_datetime
                < datetime.strptime(item[2], DATE_TIME_FORMAT)
                < end_date
            ):
                result.append(item)
    return result


def get_available_dates() -> list:
    """Возвращает список доступных дат для бронирования."""
    all_records = get_filtered_records()
    result = []
    for item in all_records:
        if item[5] is None:
            result.append(item[2])
    return result


def book_date_in_file(
    selected_date: str = None,
    user_id: str = None,
    username: str = None,
    service_type: str = None,
):
    """Записывает информацию о бронировании в файл."""
    if user_id is None:
        confirmation = None
    else:
        confirmation = 1

    if username:
        username = "@" + username
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE clients"
            " SET username = ?,"
            " confirmation = ?,"
            " type = ?,"
            " user_id = ?"
            " WHERE datetime = ?;",
            (username, confirmation, service_type, user_id, selected_date),
        )
        con.commit()
        return True


def get_user_records(user_id: int = None) -> list:
    all_records = get_filtered_records()
    result = []
    for item in all_records:
        if item[4] == user_id:
            result.append([item[0], item[1], item[-1]])

    return result


def get_upcoming_records() -> list:
    """Возвращает список предстоящих записей."""
    all_records = get_filtered_records()
    result = []
    for item in all_records:
        if item[5] is not None:
            result.append((item[0], item[1], item[3], item[-1], item[4]))
    return result


def delete_date(record: str) -> bool:
    """Удаляет выбранную дату."""
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM clients WHERE datetime = ?", (record,))
        con.commit()

        return cur.rowcount > 0
