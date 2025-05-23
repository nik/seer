from fastapi import FastAPI, UploadFile, File, Request
from sse_starlette import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import shutil
import zipfile
from pathlib import Path
import tasks as tasks
from celery.result import AsyncResult
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_code(file: UploadFile = File(...)) -> dict[str, str | None]:
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(exist_ok=True)
    file_path = workspace_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(workspace_dir)

    repo_name = file.filename.rsplit(".", 1)[0]
    tasks.combine_code(repo_name, ignored_extensions=["py", "ts", "typed", "tsx"])
    return {"filename": file.filename, "status": "success"}

class Query(BaseModel):
    text: str

@app.post("/query")
async def query(query: Query):
    task = tasks.run_tarsier_query.delay(query.text)
    listener_task = tasks.listen_for_screenshots.delay()
    return {
        "message": "Query received successfully",
        "task_id": task.id,
        "listener_task_id": listener_task.id,
    }


@app.get("/generator_job/{task_id}")
async def generator_job(task_id: str, request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            task_result = AsyncResult(task_id)
            yield {"event": "job_status", "data": task_result.status}

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

@app.get("/listener_job/{task_id}")
async def listener_job(task_id: str, request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            task_result = AsyncResult(task_id)
            yield {"event": "job_status", "data": task_result.status}

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
