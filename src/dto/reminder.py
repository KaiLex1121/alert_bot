from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Enum

from src.database.models.reminder import Reminder
from src.enums.reminder import FrequencyType


@dataclass(frozen=True)
class CreateReminderDTO:
    db_user_id: int
    tg_user_id: int
    text: str
    frequency_type: str
    start_datetime: str
    is_active: bool = True
    custom_frequency: Dict[str, int] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            db_user_id=data.get("user_id"),
            tg_user_id=data.get("tg_user_id"),
            text=data.get("text"),
            frequency_type=data.get("frequency_type"),
            start_datetime=data["start_datetime"],
            custom_frequency=data.get("custom_frequency"),
        )


@dataclass(frozen=True)
class GetReminderToShowDTO:
    text: str
    frequency_type: Enum[FrequencyType]
    start_datetime: datetime
    next_run_time: datetime
    is_active: bool = True
    custom_frequency: Dict[str, int] | None = None

    @classmethod
    def from_dao(cls, reminder: Reminder):
        return cls(
            text=reminder.text,
            frequency_type=reminder.frequency_type,
            custom_frequency=reminder.custom_frequency,
            start_datetime=reminder.start_datetime,
            is_active=reminder.is_active,
            next_run_time=reminder.next_run_time,
        )
