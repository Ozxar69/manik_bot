import pandas as pd
import os
from datetime import datetime

DATA_FILE = 'dates.csv'

def add_date(date_str, time_str, name="Неизвестно"):
    # Проверяем, существует ли файл, и создаем его, если нет
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['Дата', 'Время', 'Имя', 'Подтверждение'])
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
    return "Дата успешно добавлена!"  # Успешно добавлено