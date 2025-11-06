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
NACA = '4656'
CHORD = 3
SPAN = 7.0
POINTS = 300
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
        chord=CHORD,
        span=SPAN,
        points=POINTS,
        depth=DEPTH
    )
    mesh2 = wing2.get_mesh()


    # First geometry
    geo_wing1 = Geometry(
        type_='wing',
        mesh=mesh1,
        position=[9, 0, 6],
        color='#b0c4de',
        material='metal'
    )
    # Second geometry
    geo_wing2 = Geometry(
        type_='wing',
        mesh=mesh2,
        position=[offset_x+13,0 ,6],
        color='#ff4444',
        material='plastic'
    )


    meshfuselage = Fuselage()
    geo_fuselage = Geometry(
        type_='fuselage',
        mesh=meshfuselage,
        position=[10, 0, 0],
        color='#0000ff',
        material='plastic'
    )
    
    meshwindow = Window()
    geo_window = Geometry(
        type_='window',
        mesh=meshwindow,
        position=[11.2, 0, 4],
        color='#ffff00',
        material='plastic'
    )
    
    scale_geometry(geo_window, scale=2.0)
    rotate_geometry(geo_wing1, angles=(0, np.radians(-90), 0))
    rotate_geometry(geo_wing2, angles=(0, np.radians(-90), 0))
    rotate_geometry(geo_window, angles=(0, np.radians(-90), 0))

    geometries = [geo_wing1, geo_wing2, geo_fuselage, geo_window]

    return {
        'geometries': [g.to_dict() for g in geometries]
    }