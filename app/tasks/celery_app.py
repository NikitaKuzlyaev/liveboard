# celery_app.py
# app/services/tasks/celery_app.py

from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# celery_app = Celery(
#     'app',
#     broker=os.getenv("REDIS_BROKER", "redis://localhost:6379/0"),
#     backend=os.getenv("REDIS_BACKEND", "redis://localhost:6379/0")
# )

celery_app = Celery(
    'app',
    broker="redis://localhost:6379/0",
)

celery_app.autodiscover_tasks()

"""
Для просмотра задач Celery можно использовать flower

1. Импортировать pip install flower

2. celery -A app.tasks.celery_app flower --port=5555

3. http://localhost:5555

"""

# celery -A app.tasks.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
# celery -A app.tasks.celery_app:celery_app worker --loglevel=debug --pool=solo
