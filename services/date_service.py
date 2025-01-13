import pandas as pd
import os
from datetime import datetime, timedelta


DATA_FILE = 'dates.csv'

def add_date(date_str, time_str, name="Неизвестно"):
    # Проверяем, существует ли файл, и создаем его, если нет
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['Дата', 'Время', 'Имя', 'id', 'Подтверждение'])
        df.to_csv(DATA_FILE, index=False)

    # Загружаем существующие данные
    df = pd.read_csv(DATA_FILE)

    # Получаем текущий год
    current_year = datetime.now().year

    # Формируем полную дату с текущим годом
    date_with_year = f"{date_str}.{current_year}"
    input_datetime = datetime.strptime(f"{date_with_year} {time_str}", "%d.%m.%Y %H:%M")

    # Проверка на актуальность даты и времени
    current_datetime = datetime.now()

    if input_datetime < current_datetime:
        return "Ошибка: нельзя добавить дату и время, которые уже прошли."

    # Проверка на дубликаты
    if ((df['Дата'] == date_with_year) & (df['Время'] == time_str)).any():
        return "Ошибка: такая дата и время уже существуют, добавьте другую."

    # Добавляем новую запись
    new_entry = pd.DataFrame(
        {'Дата': [date_with_year], 'Время': [time_str], 'Имя': [name],
         'Подтверждение': [0]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return "Дата успешно добавлена!"

def get_filtered_records():
    """Возвращает отфильтрованные записи по дате и времени."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()  # Возвращаем пустой DataFrame, если файл не существует

    df = pd.read_csv(DATA_FILE)
    df['Дата'] = pd.to_datetime(df['Дата'] + ' ' + df['Время'], format='%d.%m.%Y %H:%M')

    # Фильтрация записей: только записи от сегодняшнего дня до 30 дней вперед
    today = datetime.now()
    end_date = today + timedelta(days=30)
    filtered_records = df[(df['Дата'] >= today) & (df['Дата'] <= end_date)]

    # Ограничиваем количество записей до 30
    return filtered_records.sort_values(by='Дата').head(30)

def get_available_dates():
    """Возвращает список доступных дат для бронирования."""
    if not os.path.exists(DATA_FILE):
        return []  # Если файл не существует, возвращаем пустой список

    df = pd.read_csv(DATA_FILE)

    # Фильтруем записи, где подтверждение равно 0 (не подтверждено)
    available_dates = df[df['Подтверждение'] == 0]

    # Формируем список доступных дат в формате "Дата Время"
    return [f"{row['Дата']} {row['Время']}" for index, row in available_dates.iterrows()]

def book_date_in_file(selected_date, user_id, name):
    """Записывает информацию о бронировании в файл."""
    if not os.path.exists(DATA_FILE):
        return "Ошибка: файл с датами не найден."

    df = pd.read_csv(DATA_FILE)

    # Разделяем дату и время
    date_str, time_str = selected_date.split()

    # Находим строку с выбранной датой и временем
    index = df[(df['Дата'] == date_str) & (df['Время'] == time_str)].index

    if index.empty:
        return "Ошибка: выбранная дата и время не найдены."

    # Обновляем информацию о бронировании
    df.at[index[0], 'Имя'] = '@' + name
    df.at[index[0], 'id'] = user_id

    # Сохраняем изменения в файл
    df.to_csv(DATA_FILE, index=False)
    return "Бронирование успешно выполнено!"