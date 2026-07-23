from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import os
from dataset import LISSIVDataset

app = FastAPI()

class JobPayload(BaseModel):
    job_id: str
    task_type: str
    input_url: str

@app.post("/process")
async def process_job(payload: JobPayload):
    return {
        "job_id": payload.job_id,
        "status": "received",
        "message": f"Would process {payload.task_type} on {payload.input_url}"
    }


class PreprocessRequest(BaseModel):
    job_id: str
    scene_base_path: str  # local path for now; becomes a B2 URL later


@app.post("/preprocess")
async def preprocess_scene(req: PreprocessRequest):
    # Same coordinate lists we hand-picked in 1.7 — in a real pipeline these
    # would come from scanning the full scene for clear vs cloudy regions
    clear_coords = [(4000, 7000), (4200, 7200), (4400, 7400), (4600, 7600)]
    cloud_coords = [(2000, 2000), (2200, 2200)]

    dataset = LISSIVDataset(
        req.scene_base_path, clear_coords, cloud_coords, patch_size=256, augment=True
    )

    os.makedirs(f"processed/{req.job_id}", exist_ok=True)

    saved_files = []
    for i in range(len(dataset)):
        input_patch, target_patch = dataset[i]

        # Save as .npy — in the real pipeline, this is where we'd upload
        # to Backblaze B2 instead of local disk (uploadFile equivalent in Python)
        input_path = f"processed/{req.job_id}/input_{i}.npy"
        target_path = f"processed/{req.job_id}/target_{i}.npy"
        np.save(input_path, input_patch)
        np.save(target_path, target_patch)
        saved_files.append({"input": input_path, "target": target_path})

    # In the real pipeline: make an HTTP POST back to Express here,
    # updating the Job's status to "preprocessed" in NeonDB via Prisma.
    # e.g. requests.post(f"{EXPRESS_URL}/jobs/{req.job_id}/status", json={"status": "preprocessed"})

    return {
        "job_id": req.job_id,
        "status": "preprocessed",
        "num_patches": len(saved_files),
        "files": saved_files,
    }