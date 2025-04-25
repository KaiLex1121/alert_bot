from __future__ import annotations

import datetime
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Interval,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base
from src.enums.reminder import FrequencyType


class Reminder(Base):
    __tablename__ = "reminders"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="reminders", lazy="joined")
    text: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(
        default=True, index=True
    )  # Активно ли напоминание
    job_id: Mapped[Optional[str]] = mapped_column(index=True)  # ID задачи в APScheduler
    frequency_type: Mapped[FrequencyType] = mapped_column(
        Enum(FrequencyType, name="frequency_type_enum")
    )
    custom_interval: Mapped[Dict[str, Any] | None] = mapped_column(JSON)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    apscheduler_job_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )  # Связь с задачей APScheduler

    def __repr__(self):
        rez = f"<User " f"ID={self.tg_id} " f"name={self.first_name} {self.last_name} "
        if self.username:
            rez += f"username=@{self.username}"
        return rez + ">"
