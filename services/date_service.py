import pandas as pd
import os
from datetime import datetime, timedelta


DATA_FILE = "dates.csv"


def add_date(date_str, time_str, name="", confirmation=None, ):  # Добавляем параметр confirmation
    # Проверяем, существует ли файл, и создаем его, если нет
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(
            columns=["Дата", "Время", "Имя", "id", "Подтверждение", "Тип"]
        )
        df.to_csv(DATA_FILE, index=False)

    # Загружаем существующие данные
    df = pd.read_csv(DATA_FILE)

    # Получаем текущий год
    current_year = datetime.now().year

    # Формируем полную дату с текущим годом
    date_with_year = f"{date_str}.{current_year}"
    input_datetime = datetime.strptime(
        f"{date_with_year} {time_str}", "%d.%m.%Y %H:%M"
    )

    # Проверка на актуальность даты и времени
    current_datetime = datetime.now()

    if input_datetime < current_datetime:
        return "Ошибка: нельзя добавить дату и время, которые уже прошли."

    # Проверка на дубликаты
    if ((df["Дата"] == date_with_year) & (df["Время"] == time_str)).any():
        return "Ошибка: такая дата и время уже существуют, добавьте другую."

    # Добавляем новую запись
    new_entry = pd.DataFrame(
        {
            "Дата": [date_with_year],
            "Время": [time_str],
            "Имя": [name],  # Имя может быть None
            "Подтверждение": [confirmation],  # Подтверждение может быть None
        }
    )
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return "Дата успешно добавлена!"


def get_filtered_records():
    """Возвращает отфильтрованные записи по дате и времени."""
    if not os.path.exists(DATA_FILE):
        return (
            pd.DataFrame()
        )  # Возвращаем пустой DataFrame, если файл не существует

    df = pd.read_csv(DATA_FILE)
    df["Дата"] = pd.to_datetime(
        df["Дата"] + " " + df["Время"], format="%d.%m.%Y %H:%M"
    )

    # Фильтрация записей: только записи от сегодняшнего дня до 30 дней вперед
    today = datetime.now()
    end_date = today + timedelta(days=30)
    filtered_records = df[(df["Дата"] >= today) & (df["Дата"] <= end_date)]

    # Ограничиваем количество записей до 30
    return filtered_records.sort_values(by="Дата").head(30)


def get_available_dates():
    """Возвращает список доступных дат для бронирования."""
    if not os.path.exists(DATA_FILE):
        return []  # Если файл не существует, возвращаем пустой список

    df = pd.read_csv(DATA_FILE)

    # Фильтруем записи, где подтверждение равно 0 (не подтверждено)
    available_dates = df[df["Подтверждение"].isnull()]

    # Получаем текущее время
    current_time = datetime.now()  # Используем текущее время

    # Создаем новый DataFrame с актуальными датами и временем
    available_dates = available_dates[available_dates['Дата'] + ' ' + available_dates['Время'] > current_time.strftime("%d.%m.%Y %H:%M")]

    # Преобразуем даты и время в формат datetime для сортировки
    available_dates['Дата Время'] = pd.to_datetime(available_dates['Дата'] + ' ' + available_dates['Время'], format="%d.%m.%Y %H:%M")

    # Сортируем по дате и времени
    available_dates = available_dates.sort_values(by='Дата Время')

    # Возвращаем список доступных дат в нужном формате
    return [
        f"{row['Дата']} {row['Время']}"
        for index, row in available_dates.iterrows()
    ]


def book_date_in_file(selected_date, user_id, name):
    """Записывает информацию о бронировании в файл."""
    if not os.path.exists(DATA_FILE):
        return "Ошибка: файл с датами не найден."

    df = pd.read_csv(DATA_FILE)

    # Разделяем дату и время
    date_str, time_str = selected_date.split()

    # Находим строку с выбранной датой и временем
    index = df[(df["Дата"] == date_str) & (df["Время"] == time_str)].index

    if index.empty:
        return "Ошибка: выбранная дата и время не найдены."

    # Обновляем информацию о бронировании
    df.at[index[0], "Имя"] = "@" + name
    df.at[index[0], "id"] = int(user_id)
    df.at[index[0], "Подтверждение"] = 1

    # Сохраняем изменения в файл
    df.to_csv(DATA_FILE, index=False)
    return


def get_user_records(user_id):
    """Получает записи пользователя по его ID, исключая прошедшие записи."""
    df = pd.read_csv(DATA_FILE)  # Загружаем данные из CSV файла
    user_records = df[df['id'] == user_id]  # Фильтруем записи по ID пользователя

    if user_records.empty:
        return None  # Если записей нет, возвращаем None

    # Получаем текущее время
    now = datetime.now()

    # Фильтруем записи, исключая те, которые уже прошли
    user_records = user_records[
        (pd.to_datetime(user_records['Дата'] + ' ' + user_records['Время'], dayfirst=True)) > now
    ]

    if user_records.empty:
        return None  # Если после фильтрации записей нет, возвращаем None

    # Возвращаем только даты и время в виде списка кортежей
    return list(zip(user_records['Дата'], user_records['Время']))


def update_record(user_id, date, time):
    """Обновляет запись пользователя в CSV файле."""
    df = pd.read_csv(DATA_FILE)

    # Обновляем записи, где ID пользователя совпадает
    df.loc[(df['id'] == user_id) & (df['Дата'] == date) & (df['Время'] == time), ['id', 'Имя', 'Подтверждение']] = [None, None, None]

    # Сохраняем изменения обратно в CSV
    df.to_csv(DATA_FILE, index=False)
