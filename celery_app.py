from celery import Celery

from src.config.settings import settings
from src.utils.logger import logger, setup_logging

setup_logging()

app = Celery(
    "payment_success_consumer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)

logger.info("Celery app initialized", broker=settings.redis_url)
