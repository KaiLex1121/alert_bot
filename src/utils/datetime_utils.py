import re
from datetime import date, datetime, time, timedelta
from typing import Dict, Optional, Tuple

import pytz
from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

    # Регулярное выражение для парсинга кастомного интервала
    # Пример: "3 года 10 месяцев 24 дня 15 часов 15 минут"
    INTERVAL_REGEX = re.compile(
        r"\s*(?:(?P<years>\d+)\s*(?:г|год|года|лет))?"
        r"\s*(?:(?P<months>\d+)\s*(?:мес|месяц|месяца|месяцев))?"
        r"\s*(?:(?P<weeks>\d+)\s*(?:н|нед|неделя|недели|недель))?"
        r"\s*(?:(?P<days>\d+)\s*(?:д|дн|день|дня|дней))?"
        r"\s*(?:(?P<hours>\d+)\s*(?:ч|час|часа|часов))?"
        r"\s*(?:(?P<minutes>\d+)\s*(?:м|мин|минута|минуты|минут))?\s*",
        re.IGNORECASE | re.UNICODE
    )

    def parse_custom_interval(text: str) -> Optional[Dict[str, int]]:
        """Парсит строку кастомного интервала и возвращает словарь компонентов."""
        match = INTERVAL_REGEX.fullmatch(text.strip())
        if not match:
            return None

        data = {k: int(v) for k, v in match.groupdict().items() if v is not None}
        if not data: # Если ничего не найдено
            return None

        # Добавляем 'description' для хранения исходной строки или форматированного описания
        # data['description'] = text.strip() # Или можно сформировать красивое описание
        return data

    def get_interval_description(interval_data: dict) -> str:
        """Создает читаемое описание интервала."""
        parts = []
        if interval_data.get('years'): parts.append(f"{interval_data['years']} г.")
        if interval_data.get('months'): parts.append(f"{interval_data['months']} мес.")
        if interval_data.get('weeks'): parts.append(f"{interval_data['weeks']} нед.")
        if interval_data.get('days'): parts.append(f"{interval_data['days']} дн.")
        if interval_data.get('hours'): parts.append(f"{interval_data['hours']} ч.")
        if interval_data.get('minutes'): parts.append(f"{interval_data['minutes']} мин.")
        return "Каждые " + ", ".join(parts) if parts else "Однократно" # Или другая логика

    def validate_future_date(selected_date: date) -> bool:
        """Проверяет, что выбранная дата не в прошлом."""
        today = datetime.now(pytz.utc).date() # Сравниваем с UTC датой
        return selected_date >= today

    def validate_future_time(selected_date: date, selected_time: time) -> bool:
        """Проверяет, что выбранное время не в прошлом для СЕГОДНЯШНЕЙ даты."""
        now = datetime.now(pytz.utc) # Работаем в UTC
        today_utc = now.date()

        if selected_date > today_utc:
            return True # Если дата в будущем, любое время подходит
        if selected_date < today_utc:
            return False # Дата в прошлом

        # Если дата сегодня, сравниваем время
        selected_dt = datetime.combine(selected_date, selected_time, tzinfo=pytz.utc)
        # Добавляем небольшой буфер (например, 1 минута), чтобы избежать гонки условий
        return selected_dt > (now + timedelta(minutes=1))

    def combine_date_time_to_utc(selected_date: date, selected_time: time, user_tz_str: str = 'UTC') -> datetime:
        """Объединяет дату и время и конвертирует в UTC."""
        try:
            user_tz = pytz.timezone(user_tz_str)
        except pytz.UnknownTimeZoneError:
            user_tz = pytz.utc # Fallback to UTC

        naive_dt = datetime.combine(selected_date, selected_time)
        local_dt = user_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

    def format_datetime_user(dt_utc: datetime, user_tz_str: str = 'UTC') -> str:
         """Форматирует datetime UTC в строку для пользователя с учетом его таймзоны."""
         try:
             user_tz = pytz.timezone(user_tz_str)
         except pytz.UnknownTimeZoneError:
             user_tz = pytz.utc
         local_dt = dt_utc.astimezone(user_tz)
         return local_dt.strftime("%d.%m.%Y %H:%M (%Z)") # Пример формата
