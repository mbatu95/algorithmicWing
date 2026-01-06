"""
AeroDesign: Applies aerodynamic transformations to Wing objects based on lift coefficient.
Takes an existing Wing instance and morphs it according to flight conditions.
"""

import numpy as np
from typing import Dict, Tuple
from backend.plane.wing import Wing


class AeroDesign:
    """
    Applies aerodynamic design transformations to Wing objects.
    Separates wing creation from aerodynamic configuration.
    """
    
    # Standard atmospheric conditions at sea level
    SEA_LEVEL_DENSITY = 1.225  # kg/m³
    
    def __init__(self, lift: float):
        """
        Initialize AeroDesign with a target lift coefficient.
        
        Args:
            lift: Lift coefficient from 0.0 (minimum) to 1.0 (maximum)
        """
        if not 0.0 <= lift <= 1.0:
            raise ValueError(f"Lift must be between 0.0 and 1.0, got {lift}")
        
        self.lift = lift
        self._params = self._calculate_parameters()
    
    def _calculate_parameters(self) -> Dict[str, float]:
        """
        Calculate aerodynamic parameters based on lift coefficient.
        
        Returns:
            dict: Morphing parameters for wing transformation
        """
        return {
            'thickness_factor': 0.2 + (self.lift * 0.3),      # 0.2 to 0.5
            'dihedral_angle_deg': 25 - (self.lift * 15),      # 25° to 10° (corrected)
            'shift_amount': 0.8 + (self.lift * 1.0),          # 0.8 to 1.8
            'taper_ratio': 0.6 - (self.lift * 0.3),           # 0.6 to 0.3
            'morph_start': 0.5 + (self.lift * 0.2),           # 0.5 to 0.7
        }
    
    def calculate_lift_force(self, 
                            airspeed: float, 
                            wing_area: float,
                            air_density: float = SEA_LEVEL_DENSITY,
                            angle_of_attack_deg: float = 5.0) -> Dict[str, float]:
        """
        Calculate actual lift force in Newtons.
        
        Args:
            airspeed: Aircraft speed in m/s
            wing_area: Total wing area in m²
            air_density: Air density in kg/m³ (default: sea level)
            angle_of_attack_deg: Angle of attack in degrees
        
        Returns:
            dict: Lift calculations including:
                - lift_force_N: Lift force in Newtons
                - lift_force_kgf: Lift force in kilogram-force
                - dynamic_pressure: Dynamic pressure q
                - effective_CL: Effective lift coefficient with AoA
        
        Formula: L = 0.5 × ρ × V² × S × C_L
        """
        # Adjust lift coefficient based on angle of attack
        # Typical: C_L increases by ~0.1 per degree AoA (up to stall)
        aoa_adjustment = angle_of_attack_deg * 0.1
        effective_CL = self.lift + aoa_adjustment
        
        # Limit to realistic values (stall around C_L = 1.5-2.0)
        effective_CL = min(effective_CL, 2.0)
        
        # Dynamic pressure: q = 0.5 × ρ × V²
        dynamic_pressure = 0.5 * air_density * (airspeed ** 2)
        
        # Lift force: L = q × S × C_L
        lift_force_N = dynamic_pressure * wing_area * effective_CL
        
        # Convert to kilogram-force for intuition (1 kgf = 9.81 N)
        lift_force_kgf = lift_force_N / 9.81
        
        return {
            'lift_force_N': lift_force_N,
            'lift_force_kgf': lift_force_kgf,
            'lift_force_lbf': lift_force_N * 0.224809,  # pounds-force
            'dynamic_pressure_Pa': dynamic_pressure,
            'effective_CL': effective_CL,
            'base_CL': self.lift,
            'aoa_contribution': aoa_adjustment
        }
    
    def calculate_required_speed(self,
                                 aircraft_weight_kg: float,
                                 wing_area: float,
                                 air_density: float = SEA_LEVEL_DENSITY,
                                 angle_of_attack_deg: float = 5.0) -> Dict[str, float]:
        """
        Calculate required airspeed to generate enough lift for aircraft weight.
        
        Args:
            aircraft_weight_kg: Total aircraft weight in kg
            wing_area: Total wing area in m²
            air_density: Air density in kg/m³
            angle_of_attack_deg: Angle of attack in degrees
        
        Returns:
            dict: Speed calculations
        
        Formula: V = sqrt((2 × Weight) / (ρ × S × C_L))
        """
        # Weight force in Newtons
        weight_N = aircraft_weight_kg * 9.81
        
        # Adjust CL for angle of attack
        aoa_adjustment = angle_of_attack_deg * 0.1
        effective_CL = min(self.lift + aoa_adjustment, 2.0)
        
        # Required speed: V = sqrt((2 × W) / (ρ × S × C_L))
        if effective_CL <= 0:
            raise ValueError("Effective C_L must be positive")
        
        required_speed_ms = np.sqrt(
            (2 * weight_N) / (air_density * wing_area * effective_CL)
        )
        
        # Stall speed (minimum speed at max C_L ≈ 1.5)
        max_CL = 1.5
        stall_speed_ms = np.sqrt(
            (2 * weight_N) / (air_density * wing_area * max_CL)
        )
        
        return {
            'required_speed_ms': required_speed_ms,
            'required_speed_kmh': required_speed_ms * 3.6,
            'required_speed_knots': required_speed_ms * 1.944,
            'stall_speed_ms': stall_speed_ms,
            'stall_speed_kmh': stall_speed_ms * 3.6,
            'stall_speed_knots': stall_speed_ms * 1.944,
            'safety_margin': (required_speed_ms / stall_speed_ms - 1) * 100  # % above stall
        }
    
    def apply_to_wing(self, wing: Wing) -> Wing:
        """
        Apply aerodynamic design to a Wing object.
        The wing's mirror_mode determines the correct transformations.
        
        Args:
            wing: Wing instance to be transformed
        
        Returns:
            Wing: The same wing instance (modified in place)
        """
        # Update wing's taper ratio
        wing.taper_ratio = self._params['taper_ratio']
        
        # Determine shift direction based on mirror_mode
        shift_direction = -1 if wing.mirror_mode else 1
        
        # Determine dihedral direction based on mirror_mode
        dihedral_direction = 1 if wing.mirror_mode else -1
        
        # Apply morphing
        wing.set_morph(
            start_percent=self._params['morph_start'],
            thickness_factor=self._params['thickness_factor'],
            shift_amount=self._params['shift_amount'] * shift_direction,
            dihedral_angle=np.radians(self._params['dihedral_angle_deg'] * dihedral_direction)
        )
        
        return wing
    
    def get_parameters(self) -> Dict[str, float]:
        """Get the calculated aerodynamic parameters."""
        return {
            'lift_coefficient': self.lift,
            **self._params
        }
    
    def calculate_induced_drag(self, aspect_ratio: float = 8.0) -> float:
        """
        Calculate induced drag coefficient.
        
        Args:
            aspect_ratio: Wing aspect ratio (span²/area)
        
        Returns:
            float: Induced drag coefficient
        """
        e = 0.85  # Oswald efficiency factor
        return (self.lift ** 2) / (np.pi * aspect_ratio * e)
    
    @staticmethod
    def get_preset_lift(mode: str) -> float:
        """
        Get lift coefficient for common flight modes.
        
        Args:
            mode: 'takeoff', 'cruise', 'landing', 'max', 'min'
        
        Returns:
            float: Corresponding lift coefficient
        """
        presets = {
            'takeoff': 0.75,
            'cruise': 0.5,
            'landing': 0.85,
            'max': 1.0,
            'min': 0.0,
        }
        mode_lower = mode.lower()
        if mode_lower not in presets:
            raise ValueError(f"Unknown mode: {mode}. Available: {list(presets.keys())}")
        return presets[mode_lower]
    
    @staticmethod
    def from_flight_conditions(aircraft_weight_kg: float,
                               wing_area: float,
                               airspeed_ms: float,
                               air_density: float = SEA_LEVEL_DENSITY) -> 'AeroDesign':
        """
        Create AeroDesign from flight conditions (reverse calculation).
        
        Args:
            aircraft_weight_kg: Aircraft weight in kg
            wing_area: Wing area in m²
            airspeed_ms: Airspeed in m/s
            air_density: Air density in kg/m³
        
        Returns:
            AeroDesign: Instance configured for required lift
        
        Example:
            # Create wing for 1000kg aircraft at 50 m/s
            aero = AeroDesign.from_flight_conditions(
                aircraft_weight_kg=1000,
                wing_area=20.0,
                airspeed_ms=50.0
            )
        """
        # Weight force
        weight_N = aircraft_weight_kg * 9.81
        
        # Dynamic pressure
        q = 0.5 * air_density * (airspeed_ms ** 2)
        
        # Required C_L: C_L = Weight / (q × S)
        required_CL = weight_N / (q * wing_area)
        
        # Normalize to 0-1 range (assuming max C_L ≈ 2.0)
        normalized_lift = min(required_CL / 2.0, 1.0)
        
        return AeroDesign(lift=normalized_lift)