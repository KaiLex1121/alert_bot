import logging
from datetime import datetime
from typing import Optional
import uuid

from src.database.dao.holder import HolderDAO
from src.database.dto.reminder import CreateReminderDTO
from src.database.models.reminder import Reminder
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
    ) -> Reminder | None:

        try:
            reminder = await dao.reminder.create_reminder(
                db_user_id=dto.db_user_id,
                text=dto.text,
                start_datetime=datetime.fromisoformat(dto.start_datetime),
                frequency_type=dto.frequency_type.upper(),
                custom_frequency=dto.custom_frequency,
                apscheduler_job_id=None,
            )

            job_trigger_type, job_trigger_args = create_trigger_args(
                dto.frequency_type,
                dto.start_datetime,
                dto.custom_frequency,
            )

            job_id = await scheduler_service.add_reminder_job(reminder, dto.tg_user_id, job_trigger_type, job_trigger_args)

            if job_id:
                await dao.base.update(reminder, {"apscheduler_job_id": job_id})
                await dao.base.commit()
                logger.info(
                    f"Successfully created reminder {reminder.id} with job_id {job_id}"
                )
                return reminder
            else:
                logger.error(
                    f"Failed to schedule job for new reminder (user_id={dto.db_user_id}). Rolling back."
                )
                await dao.base.rollback()
                return None
        except Exception as e:
            logger.error(
                f"Error creating reminder for user {dto.db_user_id}: {e}", exc_info=True
            )
            await dao.base.rollback()
            return None

    async def disable_reminder(self, dao: HolderDAO, reminder_id: int):
        pass

    async def enable_reminder(self, dao: HolderDAO, reminder_id: int):
        pass

    async def delete_reminder(self, dao: HolderDAO, reminder_id: int):
        pass

    async def get_all_user_reminders(self, dao: HolderDAO, user_id: int):
        all_reminders = await dao.reminder.get_all()
        return all_reminders

    async def disable_all_reminders(
        self, scheduler_service: SchedulerService, dao: HolderDAO
    ):
        await scheduler_service.pause_all_jobs()
        reminders = await dao.reminder.get_all()
        for reminder in reminders:
            await dao.reminder.update(reminder, {"is_active": False})
        await dao.base.commit()

    async def enable_all_reminders(
        self, scheduler_service: SchedulerService, dao: HolderDAO
    ):
        await scheduler_service.resume_all_jobs()
        reminders = await dao.reminder.get_all()
        for reminder in reminders:
            await dao.reminder.update(reminder, {"is_active": True})
        await dao.base.commit()

    # async def get_user_reminders(self, user_id: int) -> Sequence[Reminder]:
    #     """Получает все напоминания пользователя."""
    #     return await self.repo.get_reminders_by_user_id(user_id)

    # async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
    #     """Получает одно напоминание по ID."""
    #     return await self.repo.get_reminder_by_id(reminder_id)

    # async def update_reminder_text(
    #     self, reminder_id: int, new_text: str
    # ) -> Optional[Reminder]:
    #     """Обновляет текст напоминания и задачу в планировщике."""
    #     try:
    #         reminder = await self.repo.update_reminder(reminder_id, text=new_text)
    #         if not reminder:
    #             return None

    #         # Обновляем задачу в планировщике (текст передается в kwargs)
    #         job_id = await self.scheduler_service.update_reminder_job(reminder)
    #         if job_id:
    #             # Обновляем job_id на всякий случай (хотя он должен быть тем же)
    #             await self.repo.update_job_id(reminder.id, job_id)
    #             await self.session.commit()
    #             logger.info(f"Updated text for reminder {reminder_id}")
    #             return reminder
    #         else:
    #             logger.error(
    #                 f"Failed to update scheduler job for reminder {reminder_id} after text change. Rolling back text update."
    #             )
    #             await self.session.rollback()
    #             return None
    #     except Exception as e:
    #         logger.error(
    #             f"Error updating reminder text for {reminder_id}: {e}", exc_info=True
    #         )
    #         await self.session.rollback()
    #         return None

    # async def update_reminder_interval(
    #     self, reminder_id: int, new_interval_data: dict
    # ) -> Optional[Reminder]:
    #     """Обновляет интервал напоминания и задачу в планировщике."""
    #     try:
    #         update_data = {
    #             "interval_years": new_interval_data.get("years"),
    #             "interval_months": new_interval_data.get("months"),
    #             "interval_weeks": new_interval_data.get("weeks"),
    #             "interval_days": new_interval_data.get("days"),
    #             "interval_hours": new_interval_data.get("hours"),
    #             "interval_minutes": new_interval_data.get("minutes"),
    #             "interval_description": new_interval_data.get("description"),
    #         }
    #         reminder = await self.repo.update_reminder(reminder_id, **update_data)
    #         if not reminder:
    #             return None

    #         # Обновляем задачу в планировщике (интервал влияет на триггер)
    #         job_id = await self.scheduler_service.update_reminder_job(reminder)
    #         if job_id:
    #             await self.repo.update_job_id(reminder.id, job_id)
    #             await self.session.commit()
    #             logger.info(f"Updated interval for reminder {reminder_id}")
    #             return reminder
    #         else:
    #             logger.error(
    #                 f"Failed to update scheduler job for reminder {reminder_id} after interval change. Rolling back interval update."
    #             )
    #             await self.session.rollback()
    #             return None
    #     except Exception as e:
    #         logger.error(
    #             f"Error updating reminder interval for {reminder_id}: {e}",
    #             exc_info=True,
    #         )
    #         await self.session.rollback()
    #         return None

    # async def update_reminder_start_time(
    #     self, reminder_id: int, new_start_dt_utc: datetime, user_tz: str
    # ) -> Optional[Reminder]:
    #     """Обновляет время начала напоминания и задачу в планировщике."""
    #     try:
    #         reminder = await self.repo.update_reminder(
    #             reminder_id, start_datetime_utc=new_start_dt_utc, user_timezone=user_tz
    #         )
    #         if not reminder:
    #             return None

    #         # Обновляем задачу в планировщике (start_date влияет на триггер)
    #         job_id = await self.scheduler_service.update_reminder_job(reminder)
    #         if job_id:
    #             await self.repo.update_job_id(reminder.id, job_id)
    #             await self.session.commit()
    #             logger.info(f"Updated start time for reminder {reminder_id}")
    #             return reminder
    #         else:
    #             logger.error(
    #                 f"Failed to update scheduler job for reminder {reminder_id} after start time change. Rolling back start time update."
    #             )
    #             await self.session.rollback()
    #             return None
    #     except Exception as e:
    #         logger.error(
    #             f"Error updating reminder start time for {reminder_id}: {e}",
    #             exc_info=True,
    #         )
    #         await self.session.rollback()
    #         return None

    # async def set_reminder_active_status(
    #     self, reminder_id: int, is_active: bool
    # ) -> bool:
    #     """Включает/выключает напоминание в БД и планировщике."""
    #     try:
    #         reminder = await self.repo.get_reminder_by_id(reminder_id)
    #         if not reminder or reminder.is_active == is_active:
    #             # Если не найдено или статус уже такой, ничего не делаем
    #             await self.session.rollback()  # Откатываем, т.к. сессия была начата
    #             return False

    #         # Обновляем статус в БД
    #         updated_reminder = await self.repo.set_active_status(reminder_id, is_active)
    #         if not updated_reminder:
    #             await self.session.rollback()
    #             return False

    #         # Обновляем статус в планировщике
    #         success = False
    #         if reminder.job_id:
    #             if is_active:
    #                 success = await self.scheduler_service.resume_job(reminder.job_id)
    #             else:
    #                 success = await self.scheduler_service.pause_job(reminder.job_id)
    #         else:
    #             # Если job_id нет (странно), но мы активируем, попробуем создать задачу
    #             if is_active:
    #                 job_id = await self.scheduler_service.add_reminder_job(
    #                     updated_reminder
    #                 )
    #                 if job_id:
    #                     await self.repo.update_job_id(reminder_id, job_id)
    #                     success = True
    #             else:
    #                 success = True  # Если деактивируем и job_id нет, то все ок

    #         if success:
    #             await self.session.commit()
    #             logger.info(f"Set reminder {reminder_id} active status to {is_active}")
    #             return True
    #         else:
    #             logger.error(
    #                 f"Failed to update scheduler job status for reminder {reminder_id}. Rolling back DB change."
    #             )
    #             await self.session.rollback()
    #             return False
    #     except Exception as e:
    #         logger.error(
    #             f"Error setting active status for reminder {reminder_id}: {e}",
    #             exc_info=True,
    #         )
    #         await self.session.rollback()
    #         return False

    # async def delete_reminder_permanently(self, reminder_id: int) -> bool:
    #     """Полностью удаляет напоминание из БД и планировщика."""
    #     try:
    #         reminder = await self.repo.get_reminder_by_id(reminder_id)
    #         if not reminder:
    #             await self.session.rollback()
    #             return False  # Уже удалено или не существует

    #         # Удаляем задачу из планировщика
    #         if reminder.job_id:
    #             await self.scheduler_service.remove_job(reminder.job_id)

    #         # Удаляем запись из БД
    #         deleted = await self.repo.delete_reminder(reminder_id)

    #         if deleted:
    #             await self.session.commit()
    #             logger.info(f"Permanently deleted reminder {reminder_id}")
    #             return True
    #         else:
    #             # Этого не должно произойти, если reminder был найден
    #             logger.warning(
    #                 f"Reminder {reminder_id} found but failed to delete from DB. Rolling back."
    #             )
    #             await self.session.rollback()
    #             # Попытаться восстановить задачу в планировщике? Сложно.
    #             return False
    #     except Exception as e:
    #         logger.error(f"Error deleting reminder {reminder_id}: {e}", exc_info=True)
    #         await self.session.rollback()
    #         return False
