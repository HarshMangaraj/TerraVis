from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import os
import torch
from dataset import LISSIVDataset
from models import Generator

app = FastAPI()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


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
    scene_base_path: str


@app.post("/preprocess")
async def preprocess_scene(req: PreprocessRequest):
    clear_coords = [(4000, 7000), (4200, 7200), (4400, 7400), (4600, 7600)]
    cloud_coords = [(4000, 7000), (4100, 7100), (4050, 7300)]

    dataset = LISSIVDataset(
        req.scene_base_path, clear_coords, cloud_coords, patch_size=256, augment=True
    )

    os.makedirs(f"processed/{req.job_id}", exist_ok=True)

    saved_files = []
    for i in range(len(dataset)):
        input_patch, target_patch = dataset[i]
        input_path = f"processed/{req.job_id}/input_{i}.npy"
        target_path = f"processed/{req.job_id}/target_{i}.npy"
        np.save(input_path, input_patch)
        np.save(target_path, target_patch)
        saved_files.append({"input": input_path, "target": target_path})

    return {
        "job_id": req.job_id,
        "status": "preprocessed",
        "num_patches": len(saved_files),
        "files": saved_files,
    }


_ps2_generator = None
def get_ps2_generator():
    global _ps2_generator
    if _ps2_generator is None:
        _ps2_generator = Generator().to(DEVICE)
        _ps2_generator.load_state_dict(torch.load("checkpoints/generator_epoch5.pth", map_location=DEVICE))
        _ps2_generator.eval()
    return _ps2_generator


class InferenceRequest(BaseModel):
    job_id: str
    patch_npy_path: str


@app.post("/infer")
async def run_inference(req: InferenceRequest):
    gen = get_ps2_generator()

    input_patch = np.load(req.patch_npy_path)  # (256, 256, 3), range [0,1]
    x = torch.from_numpy(input_patch).permute(2, 0, 1).unsqueeze(0).float().to(DEVICE)
    x = x * 2 - 1  # match training normalization

    with torch.no_grad():
        output = gen(x)

    output = (output.squeeze(0).permute(1, 2, 0).cpu().numpy() + 1) / 2
    output = np.clip(output, 0, 1)

    out_path = f"processed/{req.job_id}/inference_output.npy"
    os.makedirs(f"processed/{req.job_id}", exist_ok=True)
    np.save(out_path, output)

    mse = np.mean((output - input_patch) ** 2)
    psnr = 20 * np.log10(1.0 / np.sqrt(mse)) if mse > 0 else 100.0

    return {"job_id": req.job_id, "status": "complete", "output_path": out_path, "psnr": float(psnr)}