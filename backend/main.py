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

def calculate_lift_from_naca(naca: str, angle_of_attack_deg: float = 5.0) -> float:
    """
    Estimate lift coefficient from NACA 4-digit airfoil at a given angle of attack.
    
    NACA 4-digit format: MPXX
    - M: Maximum camber in percentage of chord (÷100)
    - P: Position of maximum camber in tenths of chord (÷10)
    - XX: Maximum thickness in percentage of chord (÷100)
    
    Args:
        naca: 4-digit NACA code
        angle_of_attack_deg: Angle of attack in degrees (default 5°)
    
    Returns:
        float: Estimated lift coefficient (CL)
    """
    if len(naca) != 4 or not naca.isdigit():
        naca = '4656'
    
    # Extract NACA parameters
    max_camber = int(naca[0]) / 100.0  # M: 0.00 to 0.09
    camber_position = int(naca[1]) / 10.0  # P: 0.0 to 0.9
    thickness = int(naca[2:4]) / 100.0  # XX: 0.00 to 0.25
    
    # Theoretical lift curve slope for 2D airfoil ≈ 2π per radian
    # In practice, it's around 0.1 per degree for thin airfoils
    lift_curve_slope = 0.105  # per degree (slightly higher for thicker airfoils)
    
    # Zero-lift angle of attack depends on camber
    # More camber = more negative zero-lift angle (generates lift at 0° AoA)
    # Approximate: α₀ ≈ -max_camber * 10 degrees
    zero_lift_aoa = -max_camber * 10.0
    
    # Effective angle of attack
    effective_aoa = angle_of_attack_deg - zero_lift_aoa
    
    # Base lift coefficient: CL = lift_curve_slope × (α - α₀)
    cl_base = lift_curve_slope * effective_aoa
    
    # Thickness correction: thicker airfoils have slightly different characteristics
    # but let's keep it simple
    thickness_factor = 1.0 + (thickness - 0.12) * 0.1  # slight adjustment around 12% thickness
    
    cl = cl_base * thickness_factor
    
    # Clamp to realistic range (stall limits)
    cl = max(0.0, min(1.8, cl))
    
    return cl

@app.get('/generate-wing')
async def shaper(
    wingspan: float = Query(default=12.0, ge=6.0, le=20.0, description="Wingspan in meters"),
    root_chord: float = Query(default=None, ge=1.0, le=10.0, description="Root chord length in meters (optional)"),
    naca: str = Query(default='4656', min_length=4, max_length=4, description="NACA 4-digit airfoil code"),
    dihedral: float = Query(default=5.0, ge=0.0, le=15.0, description="Dihedral angle in degrees"),
    lift: float = Query(default=0.5, ge=0.0, le=1.0, description="Lift coefficient (0-1) - optional")
):
    """
    Generate wing geometry based on wingspan, root chord, NACA, dihedral, and other parameters.
    
    Args:
        wingspan: Total wingspan in meters (6-20m) - affects aspect ratio and area
        root_chord: Root chord length in meters (1-10m) - if None, auto-calculated
        naca: NACA 4-digit airfoil code (e.g., '4656')
        dihedral: Dihedral angle in degrees (0-15°)
        lift: Lift coefficient (0-1) - affects camber, thickness, taper (optional)
    """
    # Validate NACA is 4 digits
    if not naca.isdigit() or len(naca) != 4:
        naca = '4656'  # fallback to default
    
    # Calculate lift coefficient from NACA profile (at typical cruise AoA)
    calculated_lift = calculate_lift_from_naca(naca, angle_of_attack_deg=5.0)
    
    print(f"Generating wing with NACA: {naca}, wingspan: {wingspan}, root_chord: {root_chord}, dihedral: {dihedral}")
    print(f"Calculated lift coefficient from NACA {naca}: {calculated_lift:.3f}")
    
    # Create AeroDesign with lift parameter
    aero = AeroDesign(lift=lift)
    aero_params = aero.get_parameters()
    
    # Calculate root chord based on wingspan and taper ratio
    taper_ratio = aero_params['taper_ratio']
    
    # Use provided root_chord or auto-calculate
    if root_chord is None:
        # Scale target area with wingspan to maintain reasonable proportions
        scaled_area = TARGET_WING_AREA * (wingspan / DEFAULT_SPAN)
        calculated_root_chord = calculate_root_chord(wingspan, scaled_area, taper_ratio)
    else:
        calculated_root_chord = root_chord
    
    # Convert dihedral angle from degrees to radians
    dihedral_radians = np.radians(dihedral)
    
    # Right wing (wing1) - will be rotated 180°, so use mirror_mode=True
    wing1 = Wing(
        naca=naca,
        chord=calculated_root_chord,
        span=wingspan,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=True,  # Mirrors the shift during mesh generation
        taper_ratio=taper_ratio
    )
    
    # Store the original NACA before applying aero design
    original_naca = naca
    aero.apply_to_wing(wing1)
    # Restore the user-specified NACA (override AeroDesign's NACA)
    wing1.set_naca(original_naca)
    # Apply dihedral angle
    wing1.dihedral_angle = dihedral_radians

    mesh1 = wing1.get_mesh()

    # Left wing (wing2) - stays in original orientation, so mirror_mode=False
    wing2 = Wing(
        naca=naca,
        chord=calculated_root_chord,
        span=wingspan,
        points=POINTS,
        depth=DEPTH,
        mirror_mode=False,  # Normal shift direction
        taper_ratio=taper_ratio
    )
    
    aero.apply_to_wing(wing2)
    # Restore the user-specified NACA (override AeroDesign's NACA)
    wing2.set_naca(original_naca)
    # Apply dihedral angle
    wing2.dihedral_angle = dihedral_radians
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
    
    # Calculate wing area (planform area, not affected by dihedral)
    actual_wing_area = wingspan * calculated_root_chord * (1 + taper_ratio) / 2
    tip_chord = calculated_root_chord * taper_ratio
    
    # Dihedral affects effective wingspan and aspect ratio
    # cos(dihedral) accounts for the projected span reduction
    dihedral_rad = np.radians(dihedral)
    effective_wingspan = wingspan * np.cos(dihedral_rad)
    effective_aspect_ratio = (effective_wingspan ** 2) / actual_wing_area
    
    # Dihedral also reduces effective wing area for lift generation
    # The vertical component doesn't contribute to vertical lift
    effective_wing_area = actual_wing_area * np.cos(dihedral_rad)
    
    # Calculate lift force using the NACA-derived lift coefficient
    # But account for reduced effective area due to dihedral
    example_speed = 50.0  # m/s
    example_aoa = 5.0  # degrees
    
    # Adjust lift coefficient for dihedral effects
    # Higher dihedral slightly reduces effective lift
    dihedral_lift_factor = np.cos(dihedral_rad)
    effective_lift_coefficient = calculated_lift * dihedral_lift_factor
    
    # Create a temporary AeroDesign with the effective lift to calculate forces
    aero_for_calc = AeroDesign(lift=min(1.0, effective_lift_coefficient))
    lift_force_data = aero_for_calc.calculate_lift_force(
        airspeed=example_speed,
        wing_area=effective_wing_area,
        angle_of_attack_deg=example_aoa
    )
    
    # Calculate induced drag with effective aspect ratio
    induced_drag_coeff = aero_for_calc.calculate_induced_drag(effective_aspect_ratio)

    return {
        'geometries': [g.to_dict() for g in geometries],
        'wing_parameters': {
            'naca_profile': naca,  # Use the provided NACA code
            'chord_root': round(calculated_root_chord, 2),
            'chord_tip': round(tip_chord, 2),
            'span': wingspan,
            'effective_span': round(effective_wingspan, 2),
            'wing_area_m2': round(actual_wing_area, 2),
            'effective_wing_area_m2': round(effective_wing_area, 2),
            'aspect_ratio': round(effective_aspect_ratio, 2),
            'dihedral_angle_deg': dihedral,
            **{k: v for k, v in aero_params.items() if k != 'naca_profile'}
        },
        'aerodynamics': {
            'lift_coefficient': round(calculated_lift, 3),
            'effective_lift_coefficient': round(effective_lift_coefficient, 3),
            'induced_drag_coefficient': round(induced_drag_coeff, 4),
            'example_lift_force_N': round(lift_force_data['lift_force_N'], 1),
            'example_lift_force_kgf': round(lift_force_data['lift_force_kgf'], 1),
            'example_speed_ms': example_speed,
            'example_aoa_deg': example_aoa,
            'dihedral_effect_factor': round(dihedral_lift_factor, 3)
        }
    }
    
    #buraya en son gelecez