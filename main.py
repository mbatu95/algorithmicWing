from fastapi import FastAPI
from wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from geometry import Geometry, Mesh

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
async def shaper():
    # First wing
    wing1 = Wing(
        naca=NACA,
        chord=CHORD,
        span=SPAN,
        points=POINTS,
        depth=DEPTH
    )
    mesh1 = wing1.get_mesh()

    # Second wing, shifted in X
    offset_x = CHORD + 1.0
    wing2 = Wing(
        naca=NACA,
        chord=4,
        span=SPAN,
        points=POINTS,
        depth=DEPTH
    )
    mesh2 = wing2.get_mesh()


    # First geometry
    geometry1 = Geometry(
        type_='wing',
        mesh=mesh1,
        position=[0, 0, 0],
        color='#b0c4de',
        material='metal'
    )
    # Second geometry
    geometry2 = Geometry(
        type_='wing',
        mesh=mesh2,
        position=[offset_x, 5, 5],
        color='#ff4444',
        material='plastic'
    )
    # Third geometry (example, same mesh as geometry2, different position)
    geometry3 = Geometry(
        type_='wing',
        mesh=mesh2,
        position=[offset_x, -5, -5],
        color='#ff4444',
        material='plastic'
    )


    geometries = [geometry1, geometry2, geometry3]

    return {
        'geometries': [g.to_dict() for g in geometries]
    }