from sqlalchemy import desc, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.dao.base import BaseDAO
from src.database.models.reminder import Reminder


class ReminderDAO(BaseDAO[Reminder]):
    def __init__(self, session: AsyncSession):
        super().__init__(Reminder, session)

    async def create_reminder(
        self, user_id, apscheduler_job_id, FSM_dict: dict
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            text=FSM_dict["text"],
            frequency_type=FSM_dict["frequency_type"],
            custom_frequency=FSM_dict["custom_frequency"],
            start_datetime=FSM_dict["start_datetime"],
            apscheduler_job_id=apscheduler_job_id,
        )

        object = self.create(reminder)
        return object
