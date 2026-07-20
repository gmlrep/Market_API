from celery import Celery

from app.core.config import settings

celery = Celery(
    "task",
    broker=settings.redis_settings.broker_url,
    include=["app.processes.processes"],
    broker_connection_retry_on_startup=True,
)
