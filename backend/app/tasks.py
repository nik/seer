import os
from scripts.dump import dump_code
from celery.app import Celery
from ai.tarsier import TarsierAgent
import asyncio
from celery.utils.log import get_task_logger
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.groq import Groq
from llama_index.core import PromptTemplate
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

    repo_dir = os.path.join(parent_dir, "workspace", repo_name)
    output_file = os.path.join(parent_dir, "workspace", "combined_code_dump.txt")
    print(repo_dir)
    print(output_file)
    dump_code(
        repo_dir=repo_dir,
        ignore_dirs=["node_modules", "dev-dist"],
        output_file=output_file,
        file_extensions=ignored_extensions,
    )


@celery_app.task
def run_tarsier_query(query: str):
    agent = TarsierAgent()
    agent.initialize()
    logger.info(f"Running Tarsier query: {query}")

    with open("../workspace/combined_code_dump.txt", "r") as f:
        codebase = f.read()

    llm = Groq(
        model="llama-3.1-70b-versatile",
        api_key="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",
    )
    prompt_tmpl = PromptTemplate(PROMPT)
    prompt_tmpl.format(user_query=query, codebase=codebase)

    logger.info(f"Prompt: {prompt_tmpl}")
    # program = LLMTextCompletionProgram.from_defaults(
    #    output_cls=GenerateStepsOutput, llm=llm, prompt=prompt_tmpl, verbose=True
    # )
    # response = program()

    # agent_instructions = (
    #    response.split("<agent_todo>")[1].split("</agent_todo>")[0].strip()
    # )

    # logger.info(f"Agent instructions: {agent_instructions}")
    # asyncio.run(agent.run(agent_instructions))
    return "Done"
