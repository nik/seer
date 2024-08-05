from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import zipfile
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workspace_dir = Path("workplace")
workspace_dir.mkdir(exist_ok=True)


@app.post("/upload")
async def upload_code(file: UploadFile = File(...)):
    try:
        file_path = workspace_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(workspace_dir)

        print(f"File uploaded and unzipped: {file.filename}")
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return {"error": str(e), "status": "failed"}
