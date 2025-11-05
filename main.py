from fastapi import FastAPI
from wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded parameters
NACA = '2412'
CHORD = 1.4
SPAN = 5.0
POINTS = 100
DEPTH = 10
TRANSLATE_X = 0.0
TRANSLATE_Y = 0.0
TRANSLATE_Z = 0.0

@app.get('/generate-wing')
async def generate_wing():
    # First wing
    wing1 = Wing(
        naca=NACA,
        chord=CHORD,
        span=SPAN,
        points=POINTS,
        depth=DEPTH
    )
    mesh_vertices1, mesh_indices1 = wing1.extrude_mesh_with_indices()

    # Second wing, shifted in X
    offset_x = CHORD + 1.0
    wing2 = Wing(
        naca=NACA,
        chord=4,
        span=SPAN,
        points=POINTS,
        depth=DEPTH
    )
    mesh_vertices2, mesh_indices2 = wing2.extrude_mesh_with_indices()
    mesh_vertices2 = np.array(mesh_vertices2)
    mesh_vertices2[:,0] += offset_x
    mesh_vertices2 = mesh_vertices2.tolist()

    mesh_vertices = mesh_vertices1 + mesh_vertices2
    offset = len(mesh_vertices1)
    mesh_indices2_offset = [[i0+offset, i1+offset, i2+offset] for [i0,i1,i2] in mesh_indices2]
    mesh_indices = mesh_indices1 + mesh_indices2_offset

    # Optional translation
    if any([TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z]):
        mesh_vertices = np.array(mesh_vertices)
        mesh_vertices += np.array([TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z])
        mesh_vertices = mesh_vertices.tolist()

    return {
        'mesh_vertices': mesh_vertices,
        'mesh_indices': mesh_indices
    }