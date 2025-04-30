import logging
import uuid
from datetime import datetime
from typing import List

from aiogram import Bot
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.context import AppContext
from src.database.dao.holder import HolderDAO
from src.database.models.reminder import Reminder

logger = logging.getLogger(__name__)


# --- Функция задачи ---
async def send_reminder_job(tg_user_id: int, reminder_id: int, text: str):
    bot = AppContext.get_bot()
    try:
        logger.info(
            f"Sending reminder job for reminder_id={reminder_id} for user_id={tg_user_id}"
        )
        await bot.send_message(chat_id=tg_user_id, text=f"Напоминание:\n\n{text}")
        logger.info(
            f"Reminder sent successfully for user_id={tg_user_id} reminder_id={reminder_id}"
        )
    except Exception as e:
        logger.error(
            f"Error sending reminder job for reminder_id={reminder_id}: {e}",
            exc_info=True,
        )


class SchedulerService:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def add_reminder_job(self, reminder, tg_user_id: int, trigger_type, trigger_args) -> str | None:

        job_id = uuid.uuid4().hex

        try:
            # await self.remove_job(job_id)
            job = self.scheduler.add_job(
                send_reminder_job,
                trigger=trigger_type,
                timezone="Europe/Moscow",
                id=job_id,
                name=f"Reminder {reminder.id}",
                replace_existing=True,
                kwargs={
                    "tg_user_id": tg_user_id,
                    "reminder_id": reminder.id,
                    "text": reminder.text,
                },
                misfire_grace_time=60 * 5,
                **trigger_args,
            )
            logger.info(f"Added job for reminder {reminder.id}. Next run: {job.next_run_time}")
            return job_id
        except Exception as e:
            logger.error(
                f"Error scheduling job for reminder {reminder.id}: {e}", exc_info=True
            )
            return None

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

    async def remove_all_jobs(self) -> bool:
        logger.info("Attempting to remove all jobs from the scheduler.")
        try:
            self.scheduler.remove_all_jobs()
            logger.info("Successfully removed all jobs from the scheduler.")
            return True
        except Exception as e:
            logger.error(
                f"Error removing all jobs from the scheduler: {e}", exc_info=True
            )
            return False

    # ------------------

    # Дополнительно: Метод для получения всех задач (может быть полезен для отладки)
    async def get_all_jobs(self) -> list[Job]:
        """Возвращает список всех задач в планировщике."""
        try:
            return self.scheduler.get_jobs()
        except Exception as e:
            logger.error(f"Error retrieving jobs: {e}", exc_info=True)
            return []

    async def pause_all_jobs(self) -> bool:
        """Приостанавливает все существующие задачи в планировщике."""
        logger.info("Attempting to pause all jobs in the scheduler.")
        paused_count = 0
        failed_count = 0
        try:
            jobs: List[Job] = self.scheduler.get_jobs()
            if not jobs:
                logger.info("No jobs found in the scheduler to pause.")
                return True  # Успех, т.к. нечего было делать

            for job in jobs:
                try:
                    # Проверяем, не приостановлена ли уже задача
                    if job.next_run_time is not None:
                        self.scheduler.pause_job(job.id)
                        logger.debug(f"Paused job {job.id}.")
                        paused_count += 1
                    else:
                        logger.debug(f"Job {job.id} is already paused.")
                        # Считаем уже приостановленные как "успех" в данном контексте
                        paused_count += 1
                except Exception as e:
                    logger.error(f"Error pausing job {job.id}: {e}", exc_info=True)
                    failed_count += 1

            logger.info(
                f"Finished pausing jobs. Paused: {paused_count}, Failed/Not Found: {failed_count}."
            )
            # Считаем операцию успешной, если хотя бы что-то удалось приостановить или не было ошибок
            return failed_count == 0
        except Exception as e:
            logger.error(f"Error retrieving or pausing jobs: {e}", exc_info=True)
            return False

    async def resume_all_jobs(self) -> bool:
        """Возобновляет все приостановленные задачи в планировщике."""
        logger.info("Attempting to resume all paused jobs in the scheduler.")
        resumed_count = 0
        failed_count = 0
        try:
            jobs: List[Job] = self.scheduler.get_jobs()
            if not jobs:
                logger.info("No jobs found in the scheduler to resume.")
                return True

            for job in jobs:
                try:
                    # Проверяем, приостановлена ли задача (у приостановленной next_run_time is None)
                    if job.next_run_time is None:
                        self.scheduler.resume_job(job.id)
                        logger.debug(f"Resumed job {job.id}.")
                        resumed_count += 1
                    else:
                        logger.debug(f"Job {job.id} is already running (not paused).")
                        # Не считаем ошибкой, просто пропускаем
                except LookupError:
                    logger.warning(
                        f"Job {job.id} was not found during resume iteration (might have been removed concurrently)."
                    )
                    failed_count += 1
                except Exception as e:
                    logger.error(f"Error resuming job {job.id}: {e}", exc_info=True)
                    failed_count += 1

            logger.info(
                f"Finished resuming jobs. Resumed: {resumed_count}, Failed/Not Found: {failed_count}."
            )
            return failed_count == 0
        except Exception as e:
            logger.error(f"Error retrieving or resuming jobs: {e}", exc_info=True)
            return False
