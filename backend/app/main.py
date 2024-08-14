from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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
    return {"message": "Query received successfully", "task_id": task.id}


@app.get("/job_status/{task_id}")
async def get_job_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {"status": task_result.status}
