import datetime

from sqlalchemy import select
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
        custom_frequency: dict[str, int],
    ) -> Reminder:
        reminder = Reminder(
            user_id=db_user_id,
            text=text,
            start_datetime=start_datetime,
            frequency_type=frequency_type,
            custom_frequency=custom_frequency,
            apscheduler_job_id=apscheduler_job_id,
        )
        reminder = await self.create(reminder)
        await self.flush()
        await self.refresh(reminder)
        return reminder

    async def delete_all_reminders(self):
        all_reminders = await self.get_all()
        return all_reminders

    async def get_active_user_reminders(self, user_id: int):
        stmt = (
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.is_active == True)
            .order_by(Reminder.start_datetime.asc())
        )
        result = await self.session.execute(stmt)
        reminders = result.scalars().all()
        return reminders

    async def get_disabled_user_reminders(self, user_id: int):
        stmt = (
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.is_active == False)
            .order_by(Reminder.start_datetime.asc())  #
        )
        result = await self.session.execute(stmt)
        reminders = result.scalars().all()
        return reminders

    async def get_all_user_reminders(self, user_id: int):
        stmt = (
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.start_datetime.asc())
        )
        result = await self.session.execute(stmt)
        reminders = result.scalars().all()
        return reminders
