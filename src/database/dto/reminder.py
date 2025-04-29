from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from src.enums.reminder import FrequencyType


@dataclass(frozen=True)
class CreateReminderDTO:
    bd_user_id: int
    tg_user_id: int
    text: str
    frequency_type: FrequencyType
    start_datetime: datetime
    is_active: bool = True
    custom_frequency: Dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bd_user_id=data.get("user_id"),
            tg_user_id=data.get("tg_user_id"),
            text=data.get("text"),
            frequency_type=data.get("frequency_type"),
            start_datetime=data["start_datetime"],
            custom_frequency=data.get("custom_frequency"),
        )
