from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao.base import BaseDAO
from src.database.models.reminder import Reminder


class ReminderDAO(BaseDAO[Reminder]):
    def __init__(self, session: AsyncSession):
        super().__init__(Reminder, session)

    async def create_reminder(
        self,
        tg_user_id,
        apscheduler_job_id,
        text,
        start_datetime,
        frequency_type,
        custom_frequency,
    ) -> Reminder:
        reminder = Reminder(
            user_id=tg_user_id,
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
