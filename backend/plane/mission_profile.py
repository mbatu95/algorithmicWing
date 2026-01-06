"""
Mission Profile: Defines aircraft mission requirements and optimizes wing design accordingly.
Each mission has different priorities for lift, drag, stability, and maneuverability.
"""

from typing import Dict, Tuple, Any
from dataclasses import dataclass


@dataclass
class MissionWeights:
    """Weights for different performance criteria (0.0 to 1.0)"""
    lift: float      # Higher = more lift capability
    drag: float      # Higher = lower drag (efficiency)
    stability: float # Higher = more stable flight
    maneuver: float  # Higher = more maneuverable


class MissionProfile:
    """
    Mission profiles with optimized wing parameters for specific tasks.
    """
    
    # Define mission profiles with their priority weights
    PROFILES = {
        'endurance': MissionWeights(
            lift=1.0,      # Maximum lift for long flight
            drag=1.0,      # Minimum drag for efficiency
            stability=0.7, # Good stability
            maneuver=0.2   # Low maneuverability needed
        ),
        'speed': MissionWeights(
            lift=0.3,      # Low lift (high speed)
            drag=0.2,      # Some drag acceptable at high speed
            stability=0.4, # Moderate stability
            maneuver=1.0   # High maneuverability
        ),
        'heavy_lift': MissionWeights(
            lift=1.0,      # Maximum lift
            drag=0.6,      # Drag less important
            stability=1.0, # Maximum stability for heavy loads
            maneuver=0.3   # Low maneuverability
        ),
        'agile': MissionWeights(
            lift=0.5,      # Moderate lift
            drag=0.5,      # Moderate efficiency
            stability=0.3, # Low stability for agility
            maneuver=1.0   # Maximum maneuverability
        ),
        'cruise': MissionWeights(
            lift=0.5,      # Balanced
            drag=0.8,      # Good efficiency
            stability=0.6, # Good stability
            maneuver=0.5   # Moderate maneuverability
        ),
        'stol': MissionWeights(
            lift=1.0,      # Maximum lift
            drag=0.4,      # Drag not critical
            stability=0.8, # High stability
            maneuver=0.4   # Moderate maneuverability
        )
    }
    
    @staticmethod
    def get_mission_names():
        """Get list of available mission names"""
        return list(MissionProfile.PROFILES.keys())
    
    @staticmethod
    def get_mission_weights(mission: str) -> MissionWeights:
        """Get weights for a specific mission"""
        if mission not in MissionProfile.PROFILES:
            raise ValueError(f"Unknown mission: {mission}. Available: {MissionProfile.get_mission_names()}")
        return MissionProfile.PROFILES[mission]
    
    @staticmethod
    def calculate_optimal_parameters(mission: str) -> Dict[str, Any]:
        """
        Calculate optimal wing parameters for a mission profile.
        
        Returns:
            dict: Optimal lift coefficient and wingspan for the mission
        """
        weights = MissionProfile.get_mission_weights(mission)
        
        # Calculate optimal lift coefficient (0.0-1.0)
        # High lift weight → High CL
        # High drag weight → Lower CL (elliptical, efficient)
        # High maneuver weight → Lower CL (thinner, faster)
        lift_coefficient = (
            weights.lift * 0.6 +           # Lift priority
            weights.drag * 0.2 +           # Efficiency needs some lift
            weights.stability * 0.1 -      # Stability needs moderate lift
            weights.maneuver * 0.3         # Maneuver needs low lift
        )
        # Clamp to valid range
        lift_coefficient = max(0.2, min(1.0, lift_coefficient))
        
        # Calculate optimal wingspan (6-20m)
        # High drag weight → Long wingspan (high AR, low induced drag)
        # High lift weight → Long wingspan (more area)
        # High maneuver weight → Short wingspan (roll rate)
        # High stability weight → Moderate wingspan
        wingspan = (
            weights.drag * 8.0 +           # Efficiency needs long wings
            weights.lift * 4.0 +           # Lift needs area
            weights.stability * 2.0 -      # Stability moderate
            weights.maneuver * 6.0         # Maneuver needs short wings
        ) + 8.0  # Base wingspan
        
        # Clamp to valid range
        wingspan = max(6.0, min(20.0, wingspan))
        
        return {
            'lift_coefficient': lift_coefficient,
            'wingspan': wingspan,
            'mission_weights': {
                'lift': weights.lift,
                'drag': weights.drag,
                'stability': weights.stability,
                'maneuver': weights.maneuver
            }
        }
    
    @staticmethod
    def get_mission_description(mission: str) -> str:
        """Get human-readable description of mission"""
        descriptions = {
            'endurance': 'Long-range, fuel-efficient flight. Maximizes flight time and range.',
            'speed': 'High-speed intercept or racing. Prioritizes speed and maneuverability.',
            'heavy_lift': 'Cargo transport, heavy loads. Maximum lift and stability.',
            'agile': 'Aerobatic, dogfighting. Maximum maneuverability and responsiveness.',
            'cruise': 'Balanced general aviation. Good all-around performance.',
            'stol': 'Short takeoff/landing. Maximum lift at low speeds.'
        }
        return descriptions.get(mission, 'Unknown mission')
    
    @staticmethod
    def get_mission_example_aircraft(mission: str) -> str:
        """Get example aircraft for mission type"""
        examples = {
            'endurance': 'Global Hawk UAV, U-2 Spy Plane, Solar Impulse',
            'speed': 'F-16 Fighter, SR-71 Blackbird, Racing Aircraft',
            'heavy_lift': 'C-130 Hercules, C-17 Globemaster, An-225 Mriya',
            'agile': 'Su-27 Flanker, F-22 Raptor, Extra 300 Aerobatic',
            'cruise': 'Cessna 172, Boeing 737, Airbus A320',
            'stol': 'DHC-6 Twin Otter, Pilatus PC-6, Bush Planes'
        }
        return examples.get(mission, 'N/A')
