import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao.base import BaseDAO
from src.database.models.reminder import Reminder
from src.enums.reminder import FrequencyType


class ReminderDAO(BaseDAO[Reminder]):
    def __init__(self, session: AsyncSession):
        super().__init__(Reminder, session)

    async def create_reminder(
        self,
        db_user_id: int,
        apscheduler_job_id: str,
        text: str,
        start_datetime: datetime,
        frequency_type: FrequencyType,
        custom_frequency: dict[str, int]
    ) -> Reminder:
        reminder = Reminder(
            user_id=db_user_id,
            text=text,
            start_datetime=start_datetime,
            frequency_type=frequency_type,
            custom_frequency=custom_frequency,
            apscheduler_job_id=apscheduler_job_id,
        )
        await self.create(reminder)
        return reminder

    async def delete_all_reminders(self):
        all_reminders = await self.get_all()
        return all_reminders
