# celery_app.py
# app/email/celery_app.py

from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()



celery_app = Celery(
    'app',
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.autodiscover_tasks()

"""
Для просмотра задач Celery можно использовать flower

1. Импортировать pip install flower

2. celery -A app.email.celery_app flower --port=5556

3. http://localhost:5556

"""

# celery -A app.email.celery_app worker --loglevel=info
# celery -A app.email.celery_app worker --loglevel=info --pool=solo
# celery -A app.email.celery_app:celery_app worker --loglevel=debug --pool=solo
