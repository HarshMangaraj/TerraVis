# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

app = FastAPI()

# Pydantic model = defines the expected shape of incoming JSON,
# FastAPI auto-validates the request body against this
class JobPayload(BaseModel):
    job_id: str
    task_type: str
    input_url: str

@app.post("/process")
async def process_job(payload: JobPayload):
    # dummy response for now — real ML inference comes in Phase 2
    return {
        "job_id": payload.job_id,
        "status": "received",
        "message": f"Would process {payload.task_type} on {payload.input_url}"
    }