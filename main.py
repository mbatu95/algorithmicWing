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
async def shaper():
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

    from geometry import Geometry
    geometries = []
    # First geometry
    geometry1 = Geometry(
        type_='wing',
        mesh_vertices=mesh_vertices1,
        mesh_indices=mesh_indices1,
        position=[0, 0, 0],
        color='#b0c4de',
        material='metal'
    )
    # Second geometry
    geometry2 = Geometry(
        type_='wing',
        mesh_vertices=mesh_vertices2,
        mesh_indices=mesh_indices2,
        position=[offset_x, 5, 5],
        color='#ff4444',
        material='plastic'
    )
    # Third geometry (example, same mesh as geometry2, different position)
    geometry3 = Geometry(
        type_='wing',
        mesh_vertices=mesh_vertices2,
        mesh_indices=mesh_indices2,
        position=[offset_x, -5, -5],
        color='#ff4444',
        material='plastic'
    )
    # Optional translation for each geometry
    if any([TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z]):
        for geom in [geometry1, geometry2, geometry3]:
            verts = np.array(geom.mesh_vertices)
            verts += np.array([TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z])
            geom.mesh_vertices = verts.tolist()
            
    geometries = [geometry1, geometry2, geometry3]
    
    
    return {
        'geometries': [g.to_dict() for g in geometries]
    }