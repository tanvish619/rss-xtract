import os

from celery import Celery


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)


celery_app = Celery(
    "rss_xtract",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.services.feed_worker"
    ],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=False,
    task_track_started=True,
    task_time_limit=120,
    task_soft_time_limit=100,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
