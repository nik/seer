import os
from scripts.dump import dump_code
from celery.app import Celery
from ai.tarsier import TarsierAgent
import asyncio
from celery.utils.log import get_task_logger
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatMessage
from ai.prompt import PROMPT
from pydantic import BaseModel

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery(__name__, broker=redis_url, backend=redis_url)
logger = get_task_logger(__name__)


class GenerateStepsOutput(BaseModel):
    """Output of the generate steps task"""

    steps: str


@celery_app.task
def combine_code(repo_name, ignored_extensions=None):
    import os

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    repo_dir = os.path.join(parent_dir, "backend", "workspace", repo_name)
    output_file = os.path.join(
        parent_dir, "backend", "workspace", "combined_code_dump.txt"
    )
    dump_code(
        repo_dir=repo_dir,
        ignore_dirs=["node_modules", "dev-dist"],
        output_file=output_file,
        file_extensions=ignored_extensions,
    )


@celery_app.task(bind=True)
def run_tarsier_query(self, query: str):
    self.update_state(state="PROGRESS", meta={"progress": "Starting Tarsier query"})
    agent = TarsierAgent()
    agent.initialize()
    logger.info(f"Running Tarsier query: {query}")

    with open("../workspace/combined_code_dump.txt", "r") as f:
        codebase = f.read()

    # llm = Anthropic(
    #     model="claude-3-5-sonnet-20240620",
    #     api_key="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",
    #     temperature=0.1,
    #     max_tokens=4096,
    # )

    llm = OpenAI(
        model="gpt-4o-mini",
        api_key="sk-proj-29d4DSvaHkCwNPAHMAEnT3BlbkFJ8YrVeQ0glkDOxKe2gQaS",
        temperature=0.1,
        max_tokens=4096,
    )

    prompt_tmpl = PromptTemplate(PROMPT)
    formatted_prompt = prompt_tmpl.format(user_query=query, codebase=codebase)

    messages = [
        ChatMessage(role="user", content=formatted_prompt),
    ]
    response = llm.chat(messages)

    agent_instructions = (
        response.message.content.split("<agent_todo>")[1]
        .split("</agent_todo>")[0]
        .strip()
    )

    logger.info(f"Agent instructions: {agent_instructions}")
    asyncio.run(agent.run(agent_instructions))
    self.update_state(state="SUCCESS", meta={"status": "Query completed"})
    return "Done"
