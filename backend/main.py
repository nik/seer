from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        with open(f"uploaded_{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File uploaded: {file.filename}")
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return {"error": str(e), "status": "failed"}
