import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.database.models.reminder import Reminder  # Импортируем модель

# Важно: Функция, которая будет выполняться по расписанию
# Она должна быть импортируема APScheduler'ом, поэтому лучше вынести ее
# в отдельный модуль или определить здесь на верхнем уровне.

logger = logging.getLogger(__name__)


# --- Функция задачи ---
async def send_reminder_job(bot: Bot, chat_id: int, reminder_id: int, text: str):
    """
    Функция, выполняемая APScheduler для отправки напоминания.
    """
    try:
        logger.info(
            f"Sending reminder job for reminder_id={reminder_id} to chat_id={chat_id}"
        )
        await bot.send_message(chat_id=chat_id, text=f"🔔 Напоминание:\n\n{text}")
        logger.info(f"Reminder sent successfully for reminder_id={reminder_id}")
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

    async def add_reminder_job(self, reminder: Reminder) -> str | None:
        """Добавляет задачу напоминания в планировщик."""
        trigger_args = reminder.get_apscheduler_trigger_args()
        if not trigger_args:
            logger.error(
                f"Cannot schedule reminder {reminder.id}: Invalid interval data."
            )
            return None

        job_id = f"reminder_{reminder.id}"
        try:
            # Удаляем старую задачу, если она существует (на случай обновления)
            await self.remove_job(job_id)

            job = self.scheduler.add_job(
                send_reminder_job,
                trigger=IntervalTrigger(**trigger_args),
                id=job_id,
                name=f"Reminder for user {reminder.user_id} (ID: {reminder.id})",
                replace_existing=True,  # Заменить существующую задачу с тем же ID
                # Передаем аргументы в функцию send_reminder_job
                kwargs={
                    "bot": self.bot,  # Передаем экземпляр бота
                    "chat_id": reminder.user_id,  # ID пользователя = chat_id
                    "reminder_id": reminder.id,
                    "text": reminder.text,
                },
                misfire_grace_time=60 * 5,  # 5 минут на выполнение пропущенной задачи
            )
            logger.info(
                f"Scheduled job {job.id} for reminder {reminder.id}. Next run: {job.next_run_time}"
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
