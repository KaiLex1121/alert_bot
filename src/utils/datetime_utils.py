import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta


def convert_dt_to_russian(dt: str | datetime) -> str:
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return f"{dt.day} {months[dt.month]} {dt.year} года в {dt.hour:02d}:{dt.minute:02d}"


def parse_frequency(frequency: str | None) -> Dict[str, int]:

    if frequency:

        result = {}

        # Все возможные единицы измерения и их нормализация
        units_mapping = {
            "минут": "minutes",
            "минуты": "minutes",
            "мин": "minutes",
            "м": "minutes",
            "часов": "hours",
            "часа": "hours",
            "час": "hours",
            "ч": "hours",
            "дней": "days",
            "дня": "days",
            "день": "days",
            "д": "days",
            "недель": "weeks",
            "неделя": "weeks",
            "недели": "weeks",
            "н": "weeks",
            "месяцев": "months",
            "месяца": "months",
            "месяц": "months",
            "мес": "months",
            "лет": "years",
            "года": "years",
            "год": "years",
            "г": "years",
        }

        # Регулярное выражение для поиска числа и единицы измерения
        pattern = r"(\d+)\s+(месяцев|месяца|месяц|мес|недель|неделя|недели|н|минут|минуты|мин|м|часов|часа|час|ч|дней|дня|день|д|лет|года|год|г)"

        matches = re.findall(pattern, frequency, re.IGNORECASE)

        for value, unit in matches:
            value = int(value)
            normalized_unit = units_mapping.get(unit.lower())
            if normalized_unit:
                result[normalized_unit] = value
        return result


def parse_start_time(start_time: str) -> str:
    if start_time.lower().strip() == "start_now":
        return datetime.now().isoformat()
    month_map = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }

    # Паттерн для формата "DD month YYYY года/г HH:MM"
    full_pattern = (
        r"(\d{1,2})\s*([а-яА-Я]+)\s*(\d{4})\s*(?:года|г)?\s*(\d{1,2}):(\d{2})"
    )
    # Паттерн для формата "HH:MM"
    time_pattern = r"(\d{1,2}):(\d{2})"

    # Проверяем формат "DD month YYYY года/г HH:MM"
    match_full = re.match(full_pattern, start_time.lower().strip())
    if match_full:
        day, month_str, year, hour, minute = match_full.groups()

        # Конвертируем название месяца в номер
        month = None
        for m_name, m_num in month_map.items():
            if month_str.startswith(m_name[:3]):  # Сравниваем первые 3 буквы
                month = m_num
                break

        if not month:
            raise ValueError(f"Неверное название месяца: {month_str}")

        # Создаем объект datetime
        dt = datetime(
            year=int(year),
            month=month,
            day=int(day),
            hour=int(hour),
            minute=int(minute),
        )
        return dt.isoformat()

    # Проверяем формат "HH:MM"
    match_time = re.match(time_pattern, start_time.strip())
    if match_time:
        hour, minute = match_time.groups()
        # Получаем текущую дату
        now = datetime.now()
        # Создаем объект datetime с текущей датой и указанным временем
        dt = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=int(hour),
            minute=int(minute),
        )
        return dt.isoformat()


def create_trigger_args(
    frequency_type: str,
    start_datetime: str | datetime,
    custom_frequency: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any]]:
    if isinstance(start_datetime, str):
        dt = datetime.fromisoformat(start_datetime)
    else:
        dt = start_datetime
    if frequency_type == "daily":
        return "cron", {
            "start_date": start_datetime,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
        }
    elif frequency_type == "weekly":
        return "cron", {
            "start_date": start_datetime,
            "day_of_week": dt.weekday(),
            "hour": dt.hour,
            "minute": dt.minute,
        }
    elif frequency_type == "monthly":
        return "cron", {
            "start_date": start_datetime,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
        }
    elif frequency_type == "yearly":
        return "cron", {
            "start_date": start_datetime,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
        }
    elif frequency_type == "other":
        if not custom_frequency:
            raise ValueError("Для типа 'other' необходимо указать custom_frequency.")

        # Создаем копию начальной даты
        delta_args = {}
        if "years" in custom_frequency:
            delta_args["years"] = int(custom_frequency["years"])
        if "months" in custom_frequency:
            delta_args["months"] = int(custom_frequency["months"])
        if "days" in custom_frequency:
            delta_args["days"] = int(custom_frequency["days"])
        if "hours" in custom_frequency:
            delta_args["hours"] = int(custom_frequency["hours"])
        if "minutes" in custom_frequency:
            delta_args["minutes"] = int(custom_frequency["minutes"])

        # Применяем все интервалы сразу
        next_dt = dt + relativedelta(**delta_args)

        # Вычисляем разницу в секундах между начальной и следующей датой
        total_seconds = int((next_dt - dt).total_seconds())

        return "interval", {"start_date": start_datetime, "seconds": total_seconds}
    else:
        raise ValueError(f"Неподдерживаемый тип частоты: {frequency_type}")
