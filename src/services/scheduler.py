import datetime
import logging
import uuid
from typing import List

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.core.context import AppContext
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

    async def add_reminder_job(
        self, reminder, tg_user_id: int, trigger_type, trigger_args
    ) -> Job | None:
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
            logger.info(
                f"Added job for reminder {reminder.id}. Next run: {job.next_run_time}"
            )
            return job
        except Exception as e:
            logger.error(
                f"Error scheduling job for reminder {reminder.id}: {e}", exc_info=True
            )
            return None

    async def remove_job(self, job_id: str) -> bool:
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

    async def pause_all_user_jobs(self, job_ids: List[str]) -> bool:
        logger.info("Attempting to pause all jobs in the scheduler.")
        try:
            for job_id in job_ids:
                try:
                    await self.pause_job(job_id)
                except LookupError:
                    logger.warning(
                        f"Job {job_id} was not found during pause iteration (might have been removed concurrently)."
                    )
                    failed_count += 1
        except Exception as e:
            logger.error(
                f"No ids in the list of jobs to pause: {job_ids}. Error pausing jobs: {e}",
                exc_info=True,
            )

    async def resume_all_user_jobs(self, job_ids: List[str]) -> bool:
        logger.info("Attempting to pause all jobs in the scheduler.")
        try:
            for job_id in job_ids:
                try:
                    await self.resume_job(job_id)
                except LookupError:
                    logger.warning(
                        f"Job {job_id} was not found during pause iteration (might have been removed concurrently)."
                    )
                    failed_count += 1
        except Exception as e:
            logger.error(
                f"No ids in the list of jobs to pause: {job_ids}. Error pausing jobs: {e}",
                exc_info=True,
            )

    async def remove_all_user_jobs(self, job_ids: List[str]) -> bool:
        logger.info("Attempting to pause all jobs in the scheduler.")
        try:
            for job_id in job_ids:
                try:
                    await self.remove_job(job_id)
                except LookupError:
                    logger.warning(
                        f"Job {job_id} was not found during pause iteration (might have been removed concurrently)."
                    )
                    failed_count += 1
        except Exception as e:
            logger.error(
                f"No ids in the list of jobs to pause: {job_ids}. Error pausing jobs: {e}",
                exc_info=True,
            )

    async def get_job_by_id(self, job_id: str) -> Job:
        try:
            return self.scheduler.get_job(job_id)
        except Exception as e:
            logger.error(f"Error retrieving job {job_id}: {e}", exc_info=True)
            return None

    async def get_next_run_time(self, job_id: str) -> datetime:
        try:
            return self.scheduler.get_job(job_id).next_run_time
        except Exception as e:
            logger.error(
                f"Error retrieving next run time for job {job_id}: {e}", exc_info=True
            )
        return None

    async def remove_all_jobs(self):
        try:
            self.scheduler.remove_all_jobs()
        except Exception as e:
            logger.error(f"Error removing all jobs: {e}", exc_info=True)

    async def reset_job_start_time(
        self, job_id: str, trigger_type: str, trigger_args: dict
    ) -> bool:
        job = self.scheduler.get_job(job_id)
        if not job:
            logger.warning(f"Задача с ID '{job_id}' не найдена.")
            return False
        try:
            self.scheduler.reschedule_job(job_id, trigger=trigger_type, **trigger_args)
        except Exception as e:
            logger.error(f"Error rescheduling job {job_id}: {e}", exc_info=True)
            return False
        return True
