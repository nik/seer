import os
from scripts.dump import dump_code
from celery.app import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery(__name__, broker=redis_url, backend=redis_url)


@celery_app.task
def combine_code(ignored_extensions=None):
    main_dir = "workspace"
    dump_code(
        repo_dir=main_dir,
        ignore_dirs=["node_modules", "dev-dist"],
        output_file=f"{main_dir}/combined_code_dump.txt",
        file_extensions=ignored_extensions,
    )
