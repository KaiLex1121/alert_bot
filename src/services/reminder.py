import logging
from datetime import datetime, timedelta
from typing import Optional, Sequence

import pytz
from dateutil.relativedelta import relativedelta  # Для сложных интервалов
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao import ReminderDAO, HolderDAO
from src.database.models import Reminder
from src.services.scheduler import SchedulerService  # Импортируем сервис планировщика

from ..utils.datetime_utils import parse_custom_interval  # Нужна функция парсинга

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(
        self,
        dao: HolderDAO,
        scheduler_service: SchedulerService,
    ):
        self.dao = dao
        self.scheduler_service = scheduler_service

    async def create_new_reminder(
        self,
        user_id: int,
        tg_user_id: int,
        text: str,
        start_datetime: datetime,
        interval_data: dict,
    ) -> Optional[Reminder]:
        """Создает напоминание, сохраняет в БД и добавляет в планировщик."""
        try:
            # 1. Создаем запись в БД
            reminder = await self.dao.create_reminder(
                user_id=user_id,
                text=text,
                start_datetime=start_datetime,
                frequency_type=interval_data["frequency_type"],
                custom_frequency=interval_data["custom_frequency"],
                apscheduler_job_id=None,
            )

            # 2. Добавляем задачу в APScheduler
            job_id = await self.scheduler_service.add_reminder_job(reminder, tg_user_id)

            if job_id:
                # 3. Сохраняем job_id в БД
                await self.dao.update(reminder, {"apscheduler_job_id": job_id})
                await self.session.commit()  # Коммитим все изменения
                logger.info(
                    f"Successfully created reminder {reminder.id} with job_id {job_id}"
                )
                return reminder
            else:
                logger.error(
                    f"Failed to schedule job for new reminder (user_id={user_id}). Rolling back."
                )
                await self.session.rollback()  # Откатываем создание напоминания в БД
                return None
        except Exception as e:
            logger.error(
                f"Error creating reminder for user {user_id}: {e}", exc_info=True
            )
            await self.session.rollback()
            return None

    async def get_user_reminders(self, user_id: int) -> Sequence[Reminder]:
        """Получает все напоминания пользователя."""
        return await self.repo.get_reminders_by_user_id(user_id)

    async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """Получает одно напоминание по ID."""
        return await self.repo.get_reminder_by_id(reminder_id)

    async def update_reminder_text(
        self, reminder_id: int, new_text: str
    ) -> Optional[Reminder]:
        """Обновляет текст напоминания и задачу в планировщике."""
        try:
            reminder = await self.repo.update_reminder(reminder_id, text=new_text)
            if not reminder:
                return None

            # Обновляем задачу в планировщике (текст передается в kwargs)
            job_id = await self.scheduler_service.update_reminder_job(reminder)
            if job_id:
                # Обновляем job_id на всякий случай (хотя он должен быть тем же)
                await self.repo.update_job_id(reminder.id, job_id)
                await self.session.commit()
                logger.info(f"Updated text for reminder {reminder_id}")
                return reminder
            else:
                logger.error(
                    f"Failed to update scheduler job for reminder {reminder_id} after text change. Rolling back text update."
                )
                await self.session.rollback()
                return None
        except Exception as e:
            logger.error(
                f"Error updating reminder text for {reminder_id}: {e}", exc_info=True
            )
            await self.session.rollback()
            return None

    async def update_reminder_interval(
        self, reminder_id: int, new_interval_data: dict
    ) -> Optional[Reminder]:
        """Обновляет интервал напоминания и задачу в планировщике."""
        try:
            update_data = {
                "interval_years": new_interval_data.get("years"),
                "interval_months": new_interval_data.get("months"),
                "interval_weeks": new_interval_data.get("weeks"),
                "interval_days": new_interval_data.get("days"),
                "interval_hours": new_interval_data.get("hours"),
                "interval_minutes": new_interval_data.get("minutes"),
                "interval_description": new_interval_data.get("description"),
            }
            reminder = await self.repo.update_reminder(reminder_id, **update_data)
            if not reminder:
                return None

            # Обновляем задачу в планировщике (интервал влияет на триггер)
            job_id = await self.scheduler_service.update_reminder_job(reminder)
            if job_id:
                await self.repo.update_job_id(reminder.id, job_id)
                await self.session.commit()
                logger.info(f"Updated interval for reminder {reminder_id}")
                return reminder
            else:
                logger.error(
                    f"Failed to update scheduler job for reminder {reminder_id} after interval change. Rolling back interval update."
                )
                await self.session.rollback()
                return None
        except Exception as e:
            logger.error(
                f"Error updating reminder interval for {reminder_id}: {e}",
                exc_info=True,
            )
            await self.session.rollback()
            return None

    async def update_reminder_start_time(
        self, reminder_id: int, new_start_dt_utc: datetime, user_tz: str
    ) -> Optional[Reminder]:
        """Обновляет время начала напоминания и задачу в планировщике."""
        try:
            reminder = await self.repo.update_reminder(
                reminder_id, start_datetime_utc=new_start_dt_utc, user_timezone=user_tz
            )
            if not reminder:
                return None

            # Обновляем задачу в планировщике (start_date влияет на триггер)
            job_id = await self.scheduler_service.update_reminder_job(reminder)
            if job_id:
                await self.repo.update_job_id(reminder.id, job_id)
                await self.session.commit()
                logger.info(f"Updated start time for reminder {reminder_id}")
                return reminder
            else:
                logger.error(
                    f"Failed to update scheduler job for reminder {reminder_id} after start time change. Rolling back start time update."
                )
                await self.session.rollback()
                return None
        except Exception as e:
            logger.error(
                f"Error updating reminder start time for {reminder_id}: {e}",
                exc_info=True,
            )
            await self.session.rollback()
            return None

    async def set_reminder_active_status(
        self, reminder_id: int, is_active: bool
    ) -> bool:
        """Включает/выключает напоминание в БД и планировщике."""
        try:
            reminder = await self.repo.get_reminder_by_id(reminder_id)
            if not reminder or reminder.is_active == is_active:
                # Если не найдено или статус уже такой, ничего не делаем
                await self.session.rollback()  # Откатываем, т.к. сессия была начата
                return False

            # Обновляем статус в БД
            updated_reminder = await self.repo.set_active_status(reminder_id, is_active)
            if not updated_reminder:
                await self.session.rollback()
                return False

            # Обновляем статус в планировщике
            success = False
            if reminder.job_id:
                if is_active:
                    success = await self.scheduler_service.resume_job(reminder.job_id)
                else:
                    success = await self.scheduler_service.pause_job(reminder.job_id)
            else:
                # Если job_id нет (странно), но мы активируем, попробуем создать задачу
                if is_active:
                    job_id = await self.scheduler_service.add_reminder_job(
                        updated_reminder
                    )
                    if job_id:
                        await self.repo.update_job_id(reminder_id, job_id)
                        success = True
                else:
                    success = True  # Если деактивируем и job_id нет, то все ок

            if success:
                await self.session.commit()
                logger.info(f"Set reminder {reminder_id} active status to {is_active}")
                return True
            else:
                logger.error(
                    f"Failed to update scheduler job status for reminder {reminder_id}. Rolling back DB change."
                )
                await self.session.rollback()
                return False
        except Exception as e:
            logger.error(
                f"Error setting active status for reminder {reminder_id}: {e}",
                exc_info=True,
            )
            await self.session.rollback()
            return False

    async def delete_reminder_permanently(self, reminder_id: int) -> bool:
        """Полностью удаляет напоминание из БД и планировщика."""
        try:
            reminder = await self.repo.get_reminder_by_id(reminder_id)
            if not reminder:
                await self.session.rollback()
                return False  # Уже удалено или не существует

            # Удаляем задачу из планировщика
            if reminder.job_id:
                await self.scheduler_service.remove_job(reminder.job_id)

            # Удаляем запись из БД
            deleted = await self.repo.delete_reminder(reminder_id)

            if deleted:
                await self.session.commit()
                logger.info(f"Permanently deleted reminder {reminder_id}")
                return True
            else:
                # Этого не должно произойти, если reminder был найден
                logger.warning(
                    f"Reminder {reminder_id} found but failed to delete from DB. Rolling back."
                )
                await self.session.rollback()
                # Попытаться восстановить задачу в планировщике? Сложно.
                return False
        except Exception as e:
            logger.error(f"Error deleting reminder {reminder_id}: {e}", exc_info=True)
            await self.session.rollback()
            return False
