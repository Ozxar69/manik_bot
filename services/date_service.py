import os
from datetime import datetime, timedelta

import pandas as pd

from data import (
    CONFIRMATION_DATA,
    CONFIRMATION_RECEIVED,
    DATA_FILE,
    DATE_DATA,
    DATE_FORMAT,
    DATE_TIME_DATA,
    DATE_TIME_FORMAT,
    ERROR_DATE_TIME_NOT_FOUND,
    ERROR_DUPLICATE_MESSAGE,
    ERROR_FILE_NOT_FOUND,
    ERROR_PAST_DATE_MESSAGE,
    ID_DATA,
    RECORD_TYPE,
    SUCCESS_MESSAGE,
    TIME_DATA,
    TIME_FORMAT,
    USER_NAME,
)
from utils.utils import CURRENT_DATETIME


def add_date(date_str, time_str, name="", confirmation=None, type=""):
    """Добавляет запись с указанной датой и временем."""

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(
            columns=[
                DATE_DATA,
                TIME_DATA,
                USER_NAME,
                ID_DATA,
                CONFIRMATION_DATA,
                RECORD_TYPE,
            ]
        )
        df.to_csv(DATA_FILE, index=False)

    df = pd.read_csv(DATA_FILE)
    df[USER_NAME] = df[USER_NAME].astype(str)
    df[USER_NAME] = df[USER_NAME].astype(str)

    current_year = CURRENT_DATETIME.year

    date_with_year = f"{date_str}.{current_year}"
    input_datetime = datetime.strptime(
        f"{date_with_year} {time_str}", DATE_TIME_FORMAT
    )

    if input_datetime < CURRENT_DATETIME:
        return ERROR_PAST_DATE_MESSAGE

    if ((df[DATE_DATA] == date_with_year) & (df[TIME_DATA] == time_str)).any():
        return ERROR_DUPLICATE_MESSAGE

    new_entry = pd.DataFrame(
        {
            DATE_DATA: [date_with_year],
            TIME_DATA: [time_str],
            USER_NAME: [name],
            CONFIRMATION_DATA: [confirmation],
            RECORD_TYPE: [type],
        }
    )
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return SUCCESS_MESSAGE


def get_filtered_records():
    """Возвращает отфильтрованные записи по дате и времени."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)
    df[DATE_DATA] = pd.to_datetime(
        df[DATE_DATA] + " " + df[TIME_DATA], format=DATE_TIME_FORMAT
    )

    end_date = CURRENT_DATETIME + timedelta(days=30)
    filtered_records = df[
        (df[DATE_DATA] >= CURRENT_DATETIME) & (df[DATE_DATA] <= end_date)
    ]

    return filtered_records.sort_values(by=DATE_DATA).head(30)


def get_available_dates():
    """Возвращает список доступных дат для бронирования."""
    if not os.path.exists(DATA_FILE):
        return []

    df = pd.read_csv(DATA_FILE)

    available_dates = df[df[CONFIRMATION_DATA].isnull()]

    available_dates = available_dates[
        available_dates[DATE_DATA] + " " + available_dates[TIME_DATA]
        > CURRENT_DATETIME.strftime(DATE_TIME_FORMAT)
    ]

    available_dates[DATE_TIME_DATA] = pd.to_datetime(
        available_dates[DATE_DATA] + " " + available_dates[TIME_DATA],
        format=DATE_TIME_FORMAT,
    )

    available_dates = available_dates.sort_values(by=DATE_TIME_DATA)

    return [
        f"{row[DATE_DATA]} {row[TIME_DATA]}"
        for index, row in available_dates.iterrows()
    ]


def book_date_in_file(selected_date, user_id, name, service_type):
    """Записывает информацию о бронировании в файл."""
    if not os.path.exists(DATA_FILE):
        return ERROR_FILE_NOT_FOUND

    df = pd.read_csv(DATA_FILE)

    date_str, time_str = selected_date.split()

    index = df[(df[DATE_DATA] == date_str) & (df[TIME_DATA] == time_str)].index

    if index.empty:
        return ERROR_DATE_TIME_NOT_FOUND

    df.at[index[0], USER_NAME] = "@" + name
    df.at[index[0], ID_DATA] = int(user_id)
    df.at[index[0], CONFIRMATION_DATA] = CONFIRMATION_RECEIVED
    df.at[index[0], RECORD_TYPE] = service_type

    df.to_csv(DATA_FILE, index=False)


def get_user_records(user_id):
    """Получает записи пользователя по его ID, исключая прошедшие записи."""
    df = pd.read_csv(DATA_FILE)
    user_records = df[df[ID_DATA] == user_id]

    if user_records.empty:
        return None
    user_records = user_records[
        (
            pd.to_datetime(
                user_records[DATE_DATA] + " " + user_records[TIME_DATA],
                dayfirst=True,
            )
        )
        > CURRENT_DATETIME
    ]

    if user_records.empty:
        return None

    return list(
        zip(
            user_records[DATE_DATA],
            user_records[TIME_DATA],
            user_records[RECORD_TYPE],
        )
    )


def update_record(user_id, date, time):
    """Обновляет запись пользователя в CSV файле."""
    df = pd.read_csv(DATA_FILE)

    record_exists = df[
        (df[ID_DATA] == user_id)
        & (df[DATE_DATA] == date)
        & (df[TIME_DATA] == time)
    ]
    if record_exists.empty:
        return False

    df.loc[
        (df[ID_DATA] == user_id)
        & (df[DATE_DATA] == date)
        & (df[TIME_DATA] == time),
        [ID_DATA, USER_NAME, CONFIRMATION_DATA, RECORD_TYPE],
    ] = [None, "", None, ""]

    df.to_csv(DATA_FILE, index=False)
    return True


def get_upcoming_records():
    """Возвращает список предстоящих записей."""
    df = pd.read_csv(DATA_FILE)

    df[DATE_DATA] = pd.to_datetime(
        df[DATE_DATA], format=DATE_FORMAT, dayfirst=True
    )
    df[TIME_DATA] = pd.to_datetime(df[TIME_DATA], format=TIME_FORMAT).dt.time
    upcoming_records = []

    for index, row in df.iterrows():
        record_date = row[DATE_DATA]
        record_time = row[TIME_DATA]
        name = row[USER_NAME]
        service_type = row[RECORD_TYPE]
        id = row[ID_DATA]
        record_datetime = datetime.combine(
            row[DATE_DATA].date(), row[TIME_DATA]
        )

        if (
            record_datetime >= CURRENT_DATETIME
            and row[CONFIRMATION_DATA] == CONFIRMATION_RECEIVED
        ):
            formatted_date = record_date.strftime(DATE_FORMAT)
            formatted_time = record_time.strftime(TIME_FORMAT)

            upcoming_records.append(
                (formatted_date, formatted_time, name, service_type, int(id))
            )

    upcoming_records.sort(key=lambda x: datetime.strptime(x[0], DATE_FORMAT))
    return upcoming_records


def delete_date(record):
    """Удаляет выбранную дату."""
    date = record.split(" ")

    df = pd.read_csv(DATA_FILE)
    record_exists = df[
        (df[DATE_DATA] == date[0])
        & (df[TIME_DATA] == date[1])
        & (df[CONFIRMATION_DATA] != CONFIRMATION_RECEIVED)
    ]
    if record_exists is None:
        return False
    else:

        df = df.drop(record_exists.index)

        df.to_csv(DATA_FILE, index=False)

        return True
