from celery import Celery
from app.core.config import settings

celery = Celery('task',
                broker=f'redis://{settings.redis_settings.host}:{settings.redis_settings.port}',
                include=['app.processes.processes'],
                broker_connection_retry_on_startup=True,
                )
