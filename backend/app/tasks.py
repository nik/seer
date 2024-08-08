import os
from scripts.dump import dump_code
from celery.app import Celery
from ai.tarsier import TarsierAgent
import asyncio
from celery.utils.log import get_task_logger

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery(__name__, broker=redis_url, backend=redis_url)
logger = get_task_logger(__name__)

@celery_app.task
def combine_code(ignored_extensions=None):
    main_dir = "workspace"
    dump_code(
        repo_dir=main_dir,
        ignore_dirs=["node_modules", "dev-dist"],
        output_file=f"{main_dir}/combined_code_dump.txt",
        file_extensions=ignored_extensions,
    )


@celery_app.task
def run_tarsier_query(query: str):
    agent = TarsierAgent()
    agent.initialize()
    logger.info(f"Running Tarsier query: {query}")
    asyncio.run(agent.run(query))
    return "Done"