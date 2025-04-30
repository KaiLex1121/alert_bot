from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

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
