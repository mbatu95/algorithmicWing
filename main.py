# Utility function to rotate geometry mesh vertices around x, y, z axes (in radians)
from geometry_utils import rotate_geometry, translate_geometry, scale_geometry
from fastapi import FastAPI
from wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from geometry import Geometry
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
CHORD = 4
SPAN = 12.0
POINTS = 300
DEPTH = 10

@app.get('/generate-wing')
async def shaper():
    # Right wing (wing1) - will be rotated 180°, so use mirror_mode=True
    wing1 = Wing(
        naca=NACA,
        chord=CHORD,
        span=SPAN,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=True,  # Mirrors the shift during mesh generation
        taper_ratio=0.4
    )
    
    wing1.set_morph(
        start_percent=0.6,
        thickness_factor=0.3,
        shift_amount=-1.3,              # Same value for both wings
        dihedral_angle=np.radians(25)
        
    )
    mesh1 = wing1.get_mesh()

    # Left wing (wing2) - stays in original orientation, so mirror_mode=False
    wing2 = Wing(
        naca=NACA,
        chord=CHORD,
        span=SPAN,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=False,  # Normal shift direction
        taper_ratio=0.4
    )
    
    wing2.set_morph(
        start_percent=0.6,
        thickness_factor=0.3,
        shift_amount=1.3,              # Same value for both wings
        dihedral_angle=np.radians(-25)
    )
    mesh2 = wing2.get_mesh()


    # Right wing geometry
    geo_wing1 = Geometry(
        type_='wing',
        mesh=mesh1,
        position=[11, 0, 6],
        color='#b0c4de',
        material='metal'
    )
    # Left wing geometry
    geo_wing2 = Geometry(
        type_='wing',
        mesh=mesh2,
        position=[8.8, 0, 6], # this asyymetric position is related to hardcoded positoning.
        color='#ff4444',
        material='plastic'
    )


    meshfuselage = Fuselage()
    geo_fuselage = Geometry(
        type_='fuselage',
        mesh=meshfuselage,
        position=[10, 0, 0], ## hardkodla pozisyon atamak yerine node assign eder assemble etme ozelligi getirecegiz ilerde.
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
    rotate_geometry(geo_wing1, angles=(0, np.radians(180), 0))
    rotate_geometry(geo_wing1, angles=(np.radians(180), 0, 0))

    rotate_geometry(geo_wing2, angles=(0, np.radians(-90), 0))
    # rotate_geometry(geo_wing2, angles=(0, 0, np.radians(180)))
    # rotate_geometry(geo_wing2, angles=( np.radians(180), 0,0))

    rotate_geometry(geo_window, angles=(0, np.radians(-90), 0))
    
    

    geometries = [geo_wing1, geo_wing2, geo_fuselage, geo_window]

    return {
        'geometries': [g.to_dict() for g in geometries]
    }
    
    #buraya en son gelecez