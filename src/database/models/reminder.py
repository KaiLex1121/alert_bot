from __future__ import annotations

import datetime
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base
from src.enums.reminder import FrequencyType


class Reminder(Base):
    __tablename__ = "reminders"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="reminders", lazy="joined")
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )
    frequency_type: Mapped[FrequencyType] = mapped_column(
        Enum(FrequencyType, name="frequency_type_enum"), nullable=False, index=True
    )
    custom_frequency: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    apscheduler_job_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )

    def __repr__(self):
        return (
            f"Reminder(id={self.id}, user_id={self.user_id}, text={self.text}, "
            f"is_active={self.is_active}, frequency_type={self.frequency_type}, "
            f"custom_frequency={self.custom_frequency}, start_datetime={self.start_datetime}, "
            f"apscheduler_job_id={self.apscheduler_job_id})"
        )
