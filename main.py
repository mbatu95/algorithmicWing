# Utility function to rotate geometry mesh vertices around x, y, z axes (in radians)
from geometry_utils import rotate_geometry, translate_geometry, scale_geometry
from fastapi import FastAPI
from wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from geometry import Geometry
from cube_mesh import CubeMesh
from fuselage import Fuselage
from window import Window

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
        
    rotate_geometry(geometry2, angles=(0, 0, np.radians(30)))
    translate_geometry(geometry2,(0, -10, 1 ))

    meshcube = CubeMesh(size=3.0)
    geometry4 = Geometry(
        type_='cube',
        mesh=meshcube,
        position=[-5, 0, 0],
        color='#00ff00',
        material='plastic'
    )

    meshfuselage = Fuselage()
    geometry5 = Geometry(
        type_='fuselage',
        mesh=meshfuselage,
        position=[10, 0, 0],
        color='#0000ff',
        material='plastic'
    )
    
    meshwindow = Window()
    geometry6 = Geometry(
        type_='window',
        mesh=meshwindow,
        position=[12, 0, 0],
        color='#ffff00',
        material='plastic'
    )
    
    scale_geometry(geometry6, scale=4.0)

    geometries = [geometry1, geometry2, geometry3, geometry4, geometry5, geometry6]

    return {
        'geometries': [g.to_dict() for g in geometries]
    }