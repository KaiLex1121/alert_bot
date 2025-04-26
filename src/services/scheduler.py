import logging
from datetime import datetime
import uuid

from aiogram import Bot
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.database.dao.holder import HolderDAO
from src.database.models import Reminder
from src.services.reminder import ReminderService  # Импортируем модель

logger = logging.getLogger(__name__)


# --- Функция задачи ---
async def send_reminder_job(bot: Bot, tg_user_id: int, reminder_id: int, text: str):
    try:
        logger.info(
            f"Sending reminder job for reminder_id={reminder_id} for user_id={user_id}"
        )
        await bot.send_message(user_id=tg_user_id, text=f"Напоминание:\n\n{text}")
        logger.info(
            f"Reminder sent successfully for user_id={user_id} reminder_id={reminder_id}"
        )
    except Exception as e:
        logger.error(
            f"Error sending reminder job for reminder_id={reminder_id}: {e}",
            exc_info=True,
        )


class SchedulerService:
    def __init__(self, bot: Bot, scheduler: AsyncIOScheduler):
        self.bot = bot
        self.scheduler = scheduler

    async def start(self):
        """Запускает планировщик."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")

    async def stop(self):
        """Останавливает планировщик."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")

    async def add_reminder_job(self, reminder, tg_user_id: int) -> str | None:
        # trigger_args = reminder_service.get_apscheduler_trigger_args()
        job_id = uuid.uuid4().hex

        try:
            await self.remove_job(job_id)
            job = self.scheduler.add_job(
                send_reminder_job,
                trigger=IntervalTrigger(seconds=15),
                id=job_id,
                name=f"Reminder {reminder.id}",
                replace_existing=True,
                kwargs={
                    "bot": self.bot,
                    "user_tg_id": tg_user_id,
                    "reminder_id": reminder.id,
                    "text": reminder.text,
                },
                misfire_grace_time=60 * 5,
            )
            return job.id
        except Exception as e:
            logger.error(
                f"Error scheduling job for reminder {reminder.id}: {e}", exc_info=True
            )
            return None

    async def remove_job(self, job_id: str) -> bool:
        """Удаляет задачу из планировщика."""
        try:
            existing_job = self.scheduler.get_job(job_id)
            if existing_job:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed job {job_id} from scheduler.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}", exc_info=True)
            return False

    async def pause_job(self, job_id: str) -> bool:
        """Приостанавливает задачу."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.pause_job(job_id)
                logger.info(f"Paused job {job_id}.")
                return True
            logger.warning(f"Job {job_id} not found for pausing.")
            return False
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}", exc_info=True)
            return False

    async def resume_job(self, job_id: str) -> bool:
        """Возобновляет задачу."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.resume_job(job_id)
                logger.info(f"Resumed job {job_id}.")
                return True
            logger.warning(f"Job {job_id} not found for resuming.")
            return False
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}", exc_info=True)
            return False

    async def update_reminder_job(self, reminder: Reminder) -> str | None:
        """Обновляет существующую задачу (удаляет старую и создает новую)."""
        logger.info(f"Attempting to update job for reminder {reminder.id}")
        # Просто пересоздаем задачу с новыми параметрами
        return await self.add_reminder_job(reminder)
