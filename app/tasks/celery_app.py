from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the Celery app
celery_app = Celery(
    'tasks',
    broker=os.getenv("REDIS_BROKER", "redis://redis:6379/0"),  # Use default if not in .env
    backend=os.getenv("REDIS_BACKEND", "redis://redis:6379/0")  # Use default if not in .env
)

celery_app.autodiscover_tasks()

# Optionally define custom task routes if needed
celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

# Celery app is now ready for use
