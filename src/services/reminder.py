import logging
from datetime import datetime

from src.database.dao.holder import HolderDAO
from src.database.models.reminder import Reminder
from src.dto.reminder import CreateReminderDTO, GetReminderToShowDTO
from src.services.scheduler import SchedulerService
from src.utils.datetime_utils import create_trigger_args

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(
        self,
        scheduler_service: SchedulerService,
    ):
        self.scheduler_service = scheduler_service

    async def create_reminder(
        self,
        scheduler_service: SchedulerService,
        dao: HolderDAO,
        dto: CreateReminderDTO,
    ) -> datetime | None:

        try:
            reminder = await dao.reminder.create_reminder(
                db_user_id=dto.db_user_id,
                text=dto.text,
                start_datetime=datetime.fromisoformat(dto.start_datetime),
                frequency_type=dto.frequency_type.upper(),
                custom_frequency=dto.custom_frequency,
                apscheduler_job_id=None,
            )
            await dao.base.flush(reminder)
        except Exception as e:
            logger.error(
                f"Error creating reminder for user {dto.db_user_id}: {e}", exc_info=True
            )
            await dao.base.rollback()
            return None

        try:
            job_trigger_type, job_trigger_args = create_trigger_args(
                dto.frequency_type,
                dto.start_datetime,
                dto.custom_frequency,
            )
            job = await scheduler_service.add_reminder_job(
                reminder, dto.tg_user_id, job_trigger_type, job_trigger_args
            )
            job_id = job.id
            job_next_run_time = job.next_run_time
            await dao.base.update(
                reminder,
                {"apscheduler_job_id": job_id},
            )
            await dao.base.commit()
            logger.info(
                f"Successfully created reminder {reminder.id} with job_id {job_id}"
            )
            return job_next_run_time
        except Exception:
            logger.error(
                f"Failed to schedule job for new reminder (user_id={dto.db_user_id}). Rolling back."
            )
            await dao.base.rollback()
            return None

    async def delete_reminder(
        self, dao: HolderDAO, reminder_id: int, scheduler_service: SchedulerService
    ):
        reminder = await dao.reminder.get_by_id(reminder_id)
        await dao.reminder.delete(reminder)
        await dao.base.commit()
        await scheduler_service.remove_job(reminder.apscheduler_job_id)

    async def get_user_reminder(self, dao: HolderDAO, reminder_id: int):
        return await dao.reminder.get_by_id(reminder_id)

    async def get_user_reminder_to_show(self, dao: HolderDAO, reminder_id: int):
        reminder = await dao.reminder.get_by_id(reminder_id)
        return GetReminderToShowDTO.from_dao(reminder)

    async def update_reminder_next_run_time(
        self, dao: HolderDAO, reminder_id: int, scheduler_service: SchedulerService
    ):
        reminder = await dao.reminder.get_by_id(reminder_id)
        next_run_time = await scheduler_service.get_next_run_time(
            reminder.apscheduler_job_id
        )
        updated_reminder = await dao.reminder.update(
            reminder, {"next_run_time": next_run_time}
        )
        await dao.base.commit()
        return GetReminderToShowDTO.from_dao(updated_reminder)

    async def disable_reminder(
        self, dao: HolderDAO, reminder_id: int, scheduler_service: SchedulerService
    ) -> bool:
        reminder = await dao.reminder.get_by_id(reminder_id)
        await dao.reminder.update(reminder, {"is_active": False})
        await dao.base.commit()
        await scheduler_service.pause_job(reminder.apscheduler_job_id)
        return reminder.is_active

    async def enable_reminder(
        self, dao: HolderDAO, reminder_id: int, scheduler_service: SchedulerService
    ) -> bool:
        reminder = await dao.reminder.get_by_id(reminder_id)
        await dao.reminder.update(reminder, {"is_active": True})
        await dao.base.commit()
        await scheduler_service.resume_job(reminder.apscheduler_job_id)
        return reminder.is_active

    async def get_all_user_reminders(self, dao: HolderDAO, user_id: int):
        try:
            all_reminders = await dao.reminder.get_all_user_reminders(user_id)
            return all_reminders
        except Exception as e:
            logger.error(f"Error getting all reminders: {e}", exc_info=True)
            return None

    async def get_active_user_reminders(
        self, dao: HolderDAO, user_id: int
    ) -> list[Reminder] | None:
        try:
            all_active_reminders = await dao.reminder.get_active_user_reminders(user_id)
            return all_active_reminders
        except Exception as e:
            logger.error(f"Error getting active reminders: {e}", exc_info=True)
            return None

    async def get_disabled_user_reminders(self, dao: HolderDAO, user_id: int):
        try:
            all_disabled_reminders = await dao.reminder.get_disabled_user_reminders(
                user_id
            )
            return all_disabled_reminders
        except Exception as e:
            logger.error(f"Error getting disabled reminders: {e}", exc_info=True)
            return None

    async def disable_all_user_reminders(
        self, scheduler_service: SchedulerService, dao: HolderDAO, user_id: int
    ):
        reminders = await dao.reminder.get_all_user_reminders(user_id)
        await scheduler_service.pause_all_user_jobs(
            [reminder.apscheduler_job_id for reminder in reminders]
        )
        for reminder in reminders:
            await dao.reminder.update(reminder, {"is_active": False})
        await dao.base.commit()

    async def enable_all_user_reminders(
        self, scheduler_service: SchedulerService, dao: HolderDAO, user_id: int
    ):
        reminders = await dao.reminder.get_all_user_reminders(user_id)
        await scheduler_service.resume_all_user_jobs(
            [reminder.apscheduler_job_id for reminder in reminders]
        )
        for reminder in reminders:
            await dao.reminder.update(reminder, {"is_active": True})
        await dao.base.commit()

    async def delete_all_user_reminders(
        self, dao: HolderDAO, scheduler_service: SchedulerService, user_id: int
    ):
        reminders = await dao.reminder.get_all_user_reminders(user_id)
        await scheduler_service.remove_all_user_jobs(
            [reminder.apscheduler_job_id for reminder in reminders]
        )
        for reminder in reminders:
            await dao.reminder.delete(reminder)
        await dao.base.commit()

    async def delete_all_active_user_reminders(
        self, dao: HolderDAO, scheduler_service: SchedulerService, user_id: int
    ):
        reminders = await dao.reminder.get_active_user_reminders(user_id)
        await scheduler_service.remove_all_user_jobs(
            [reminder.apscheduler_job_id for reminder in reminders]
        )
        for reminder in reminders:
            await dao.reminder.delete(reminder)
        await dao.base.commit()

    async def delete_all_disabled_user_reminders(
        self, dao: HolderDAO, scheduler_service: SchedulerService, user_id: int
    ):
        reminders = await dao.reminder.get_disabled_user_reminders(user_id)\

        await scheduler_service.remove_all_user_jobs(
            [reminder.apscheduler_job_id for reminder in reminders]
        )
        for reminder in reminders:
            await dao.reminder.delete(reminder)
        await dao.base.commit()