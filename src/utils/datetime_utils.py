import re
from datetime import date, datetime, time, timedelta
from typing import Dict, Union, Tuple, Optional, Any
from dateutil.relativedelta import relativedelta


def parse_frequency(frequency: str | None) -> Dict[str, int]:

    if frequency:

        result = {}

        # Все возможные единицы измерения и их нормализация
        units_mapping = {
            'минут': 'minutes', 'минуты': 'minutes', 'мин': 'minutes', 'м': 'minutes',
            'часов': 'hours', 'часа': 'hours', 'час': 'hours', 'ч': 'hours',
            'дней': 'days', 'дня': 'days', 'день': 'days', 'д': 'days',
            'недель': 'weeks', 'неделя': 'weeks', 'недели': 'weeks', 'н': 'weeks',
            'месяцев': 'months', 'месяца': 'months', 'месяц': 'months', 'мес': 'months',
            'лет': 'years', 'года': 'years', 'год': 'years', 'г': 'years'
        }

        # Регулярное выражение для поиска числа и единицы измерения
        pattern = r'(\d+)\s+(минут|минуты|мин|м|часов|часа|час|ч|дней|дня|день|д|недель|неделя|недели|н|месяцев|месяца|месяц|мес|лет|года|год|г)'

        matches = re.findall(pattern, frequency, re.IGNORECASE)

        for value, unit in matches:
            value = int(value)
            normalized_unit = units_mapping.get(unit.lower())
            if normalized_unit:
                result[normalized_unit] = value

        return result


def parse_start_time(start_time: str) -> str:

    if start_time == "start_now":
        start_time = datetime.now()
        to_return = datetime.isoformat(datetime.now())
        print(to_return)
        print(start_time)
        return to_return

    # Define month mapping
    month_map = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }

    # Pattern for format: DD month YYYY года/г HH:MM
    pattern = r'(\d{1,2})\s*([а-яА-Я]+)\s*(\d{4})\s*(?:года|г)?\s*(\d{1,2}):(\d{2})'

    match = re.match(pattern, start_time.lower().strip())
    if not match:
        raise ValueError(f"Invalid datetime format: {start_time}")

    day, month_str, year, hour, minute = match.groups()

    # Convert month name to number
    month = None
    for m_name, m_num in month_map.items():
        if month_str.startswith(m_name[:3]):  # Match first 3 letters
            month = m_num
            break

    if not month:
        raise ValueError(f"Invalid month name: {month_str}")

    # Create datetime object
    dt = datetime(
        year=int(year),
        month=month,
        day=int(day),
        hour=int(hour),
        minute=int(minute)
    )

    return dt.isoformat()


def create_trigger_args(
    frequency_type: str,
    start_datetime: str,
    custom_frequency: str | None = None
) -> Tuple[str, Dict[str, Any]]:

    # Определяем тип триггера и его параметры в зависимости от частоты
    if frequency_type == "daily":
        return 'cron', {
            'start_date': start_datetime,
            'hour': datetime.fromisoformat(start_datetime).hour,
            'minute': datetime.fromisoformat(start_datetime).minute,
        }
    elif frequency_type == "weekly":
        return 'cron', {
            'start_date': start_datetime,
            'day_of_week': datetime.fromisoformat(start_datetime).weekday(),
            'hour': datetime.fromisoformat(start_datetime).hour,
            'minute': datetime.fromisoformat(start_datetime).minute,
        }
    elif frequency_type == "monthly":
        return 'cron', {
            'start_date': start_datetime,
            'day': datetime.fromisoformat(start_datetime).day,
            'hour': datetime.fromisoformat(start_datetime).hour,
            'minute': datetime.fromisoformat(start_datetime).minute,
        }
    elif frequency_type == "yearly":
        dt = datetime.fromisoformat(start_datetime)
        return 'cron', {
            'start_date': start_datetime,
            'month': dt.month,
            'day': dt.day,
            'hour': dt.hour,
            'minute': dt.minute,
        }
    elif frequency_type == "other":
        custom_frequency
        if not custom_frequency:
            raise ValueError(f"Не удалось распознать частоту: {custom_frequency}")

        return 'interval', {
            'start_date': start_datetime,
            **custom_frequency
        }
    else:
        raise ValueError(f"Неподдерживаемый тип частоты: {frequency_type}")


# Tests
# frequency_type = "other"
# custom_frequency = "15 минут"
# start_time = "30 мая 2025 года 23:45"
# start_time_now = "start_now"
# result = create_trigger_args(frequency_type=frequency_type, start_datetime=start_time, custom_frequency=custom_frequency)
# print(result)