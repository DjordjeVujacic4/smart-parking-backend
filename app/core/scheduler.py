import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services import reservation_service

logger = logging.getLogger(__name__)

_EXPIRE_JOB_ID = "expire_reservations"

scheduler = BackgroundScheduler(timezone="UTC")


def _expire_reservations_job() -> None:
    with SessionLocal() as db:
        expired = reservation_service.expire_overdue_reservations(db)
    logger.info("Reservation expiration job ran, expired %d reservation(s)", expired)


def start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        _expire_reservations_job,
        trigger="interval",
        seconds=60,
        id=_EXPIRE_JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
