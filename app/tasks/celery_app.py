# celery_app.py
# app/tasks/celery_app.py

from celery import Celery
import os
from dotenv import load_dotenv
#from app.tasks import tasks

load_dotenv()

# celery_app = Celery(
#     'app',
#     broker=os.getenv("REDIS_BROKER", "redis://localhost:6379/0"),
#     backend=os.getenv("REDIS_BACKEND", "redis://localhost:6379/0")
# )

# celery_app = Celery(
#     'app',
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0"
# )

celery_app = Celery(
    'app',
    broker="redis://localhost:6379/0",
)

# Автоматический поиск задач в указанной папке
#celery_app.autodiscover_tasks('app.tasks', force=True)

#celery_app.autodiscover_tasks(['app', 'app.tasks', 'app.handlers', 'app.handlers.rooms'])
celery_app.autodiscover_tasks()

# celery_app.conf.task_routes = {
#     "app.tasks.*": {"queue": "default"},
#     "*": {"queue": "default"},
# }

"""
Для просмотра задач Celery можно использовать flower

1. Импортировать pip install flower

2. celery -A app.tasks.celery_app flower --port=5555

3. http://localhost:5555

"""

# celery -A app.tasks.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
# celery -A app.tasks.celery_app:celery_app worker --loglevel=debug --pool=solo