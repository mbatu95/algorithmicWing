# Utility function to rotate geometry mesh vertices around x, y, z axes (in radians)
from backend.utils.geometry_utils import rotate_geometry, translate_geometry, scale_geometry
from fastapi import FastAPI, Query
from backend.plane.wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from backend.geometry.geometry import Geometry
from backend.plane.fuselage import Fuselage
from backend.plane.window import Window
from backend.plane.aero_design import AeroDesign

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
TARGET_WING_AREA = 36.0  # m² - target wing area (can be adjusted with span)
DEFAULT_SPAN = 12.0
POINTS = 300
DEPTH = 10

def calculate_root_chord(span: float, target_area: float, taper_ratio: float) -> float:
    """
    Calculate root chord to maintain target wing area.
    
    Area = span × root_chord × (1 + taper_ratio) / 2
    root_chord = 2 × Area / (span × (1 + taper_ratio))
    """
    return (2 * target_area) / (span * (1 + taper_ratio))

@app.get('/generate-wing')
async def shaper(
    lift: float = Query(default=0.5, ge=0.0, le=1.0, description="Lift coefficient (0-1)"),
    wingspan: float = Query(default=12.0, ge=6.0, le=20.0, description="Wingspan in meters")
):
    """
    Generate wing geometry based on lift and wingspan parameters.
    
    Args:
        lift: Lift coefficient (0-1) - affects camber, thickness, taper
        wingspan: Total wingspan in meters (6-20m) - affects aspect ratio and area
    """
    # Create AeroDesign with lift parameter
    aero = AeroDesign(lift=lift)
    aero_params = aero.get_parameters()
    
    # Calculate root chord based on wingspan and taper ratio
    taper_ratio = aero_params['taper_ratio']
    # Scale target area with wingspan to maintain reasonable proportions
    scaled_area = TARGET_WING_AREA * (wingspan / DEFAULT_SPAN)
    root_chord = calculate_root_chord(wingspan, scaled_area, taper_ratio)
    
    # Right wing (wing1) - will be rotated 180°, so use mirror_mode=True
    wing1 = Wing(
        naca=NACA,
        chord=root_chord,
        span=wingspan,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=True,  # Mirrors the shift during mesh generation
        taper_ratio=taper_ratio
    )
    
    aero.apply_to_wing(wing1)

    mesh1 = wing1.get_mesh()

    # Left wing (wing2) - stays in original orientation, so mirror_mode=False
    wing2 = Wing(
        naca=NACA,
        chord=root_chord,
        span=wingspan,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=False,  # Normal shift direction
        taper_ratio=taper_ratio
    )
    
    aero.apply_to_wing(wing2)
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
    
    # Get aero parameters
    aero_params = aero.get_parameters()
    
    # Calculate wing area
    actual_wing_area = wingspan * root_chord * (1 + taper_ratio) / 2
    tip_chord = root_chord * taper_ratio
    aspect_ratio = (wingspan ** 2) / actual_wing_area
    
    # Calculate some example flight data
    example_speed = 50.0  # m/s
    lift_force_data = aero.calculate_lift_force(
        airspeed=example_speed,
        wing_area=actual_wing_area,
        angle_of_attack_deg=5.0
    )

    return {
        'geometries': [g.to_dict() for g in geometries],
        'wing_parameters': {
            'naca_profile': aero_params['naca_profile'],  # Dynamic NACA based on lift
            'chord_root': round(root_chord, 2),
            'chord_tip': round(tip_chord, 2),
            'span': wingspan,
            'wing_area_m2': round(actual_wing_area, 2),
            'aspect_ratio': round(aspect_ratio, 2),
            **{k: v for k, v in aero_params.items() if k != 'naca_profile'}
        },
        'aerodynamics': {
            'lift_coefficient': lift,
            'induced_drag_coefficient': round(aero.calculate_induced_drag(aspect_ratio), 4),
            'example_lift_force_N': round(lift_force_data['lift_force_N'], 1),
            'example_lift_force_kgf': round(lift_force_data['lift_force_kgf'], 1),
            'example_speed_ms': example_speed
        }
    }
    
    #buraya en son gelecez