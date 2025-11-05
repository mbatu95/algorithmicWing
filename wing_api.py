from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple, Optional
from wing import Wing
import numpy as np


app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://[::]:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WingRequest(BaseModel):
    naca: str = '2412'
    chord: float = 1.0
    span: float = 3.0
    points: int = 200
    depth: float = 3.0
    start_percent: Optional[float] = 0.5
    thickness_factor: Optional[float] = 1.0
    shift_amount: Optional[float] = 0.0
    dihedral_angle: Optional[float] = 0.0  # radians

class MeshResponse(BaseModel):
    mesh_vertices: List[List[float]]
    mesh_indices: List[List[int]]
    profile: List[List[float]]

@app.post("/generate-wing", response_model=MeshResponse)
def generate_wing(data: WingRequest = Body(...)):
    wing = Wing(
        naca=data.naca,
        chord=data.chord,
        span=data.span,
        points=data.points,
        depth=data.depth
    )
    # Use defaults if any morph parameter is None
    start_percent = data.start_percent if data.start_percent is not None else 0.5
    thickness_factor = data.thickness_factor if data.thickness_factor is not None else 1.0
    shift_amount = data.shift_amount if data.shift_amount is not None else 0.0
    dihedral_angle = data.dihedral_angle if data.dihedral_angle is not None else 0.0
    wing.set_morph(
        start_percent=start_percent,
        thickness_factor=thickness_factor,
        shift_amount=shift_amount,
        dihedral_angle=dihedral_angle
    )
    profile = wing.generate_airfoil_profile()
    vertices, indices = wing.extrude_mesh_with_indices()
    return {"mesh_vertices": vertices, "mesh_indices": indices, "profile": profile}

# To run:
# uvicorn wing_api:app --reload
