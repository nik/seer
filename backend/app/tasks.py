import os
from datetime import datetime
from celery.app import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery(__name__, broker=redis_url, backend=redis_url)


@celery_app.task
def dummy_task():
    folder = "workspace"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")
