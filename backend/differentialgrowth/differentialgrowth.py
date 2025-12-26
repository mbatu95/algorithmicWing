"""
Differential Growth Algorithm for generating organic shapes.
"""

import numpy as np
from typing import List, Tuple


class DifferentialGrowth:
    def __init__(self, initial_radius: float = 1.0, num_points: int = 20):
        """
        Initialize differential growth with a circle.
        
        Args:
            initial_radius: Starting circle radius
            num_points: Number of initial points
        """
        self.points = []
        self.max_edge_length = 0.12
        self.min_edge_length = 0.02
        self.repulsion_radius = 0.35
        self.repulsion_force = 0.2
        self.attraction_force = 0.1
        self.damping = 0.7
        self.max_points = 200  # Limit total points for performance
        
        # Create initial circle with strong random perturbations
        np.random.seed(None)  # Random seed for unique shapes each time
        for i in range(num_points):
            angle = (i / num_points) * 2 * np.pi
            # Add strong random noise to break symmetry
            noise_radius = initial_radius * (1.0 + np.random.uniform(-0.35, 0.35))
            noise_angle = angle + np.random.uniform(-0.3, 0.3)
            x = np.cos(noise_angle) * noise_radius
            y = np.sin(noise_angle) * noise_radius
            self.points.append(np.array([x, y]))
    
    def step(self, iterations: int = 1):
        """
        Run differential growth simulation steps.
        
        Args:
            iterations: Number of iterations to run
        """
        for _ in range(iterations):
            self._apply_forces()
            self._split_edges()
            self._remove_short_edges()
    
    def _apply_forces(self):
        """Apply attraction, repulsion, and smoothing forces."""
        n = len(self.points)
        forces = [np.array([0.0, 0.0]) for _ in range(n)]
        
        # Attraction to neighbors (spring force)
        for i in range(n):
            prev_i = (i - 1) % n
            next_i = (i + 1) % n
            
            # Spring to previous
            to_prev = self.points[prev_i] - self.points[i]
            dist_prev = np.linalg.norm(to_prev)
            if dist_prev > 0:
                spring_force = (dist_prev - self.min_edge_length) * self.attraction_force
                forces[i] += (to_prev / dist_prev) * spring_force
            
            # Spring to next
            to_next = self.points[next_i] - self.points[i]
            dist_next = np.linalg.norm(to_next)
            if dist_next > 0:
                spring_force = (dist_next - self.min_edge_length) * self.attraction_force
                forces[i] += (to_next / dist_next) * spring_force
        
        # Repulsion from all other points
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # Skip immediate neighbors
                if j == (i - 1) % n or j == (i + 1) % n:
                    continue
                
                diff = self.points[i] - self.points[j]
                dist = np.linalg.norm(diff)
                
                if dist < self.repulsion_radius and dist > 0:
                    # Much stronger repulsion force with cubic falloff for organic shapes
                    force_mag = self.repulsion_force * ((self.repulsion_radius - dist) / self.repulsion_radius) ** 1.5
                    forces[i] += (diff / dist) * force_mag
        
        # Apply forces with damping
        for i in range(n):
            self.points[i] += forces[i] * self.damping
    
    def _split_edges(self):
        """Split edges that are too long."""
        if len(self.points) >= self.max_points:
            return  # Stop splitting if we have too many points
            
        i = 0
        while i < len(self.points):
            if len(self.points) >= self.max_points:
                break
                
            next_i = (i + 1) % len(self.points)
            
            edge = self.points[next_i] - self.points[i]
            edge_length = np.linalg.norm(edge)
            
            if edge_length > self.max_edge_length:
                # Insert new point at midpoint
                midpoint = (self.points[i] + self.points[next_i]) / 2.0
                self.points.insert(next_i, midpoint)
                i += 1  # Skip the new point
            
            i += 1
    
    def _remove_short_edges(self):
        """Remove points where edges are too short."""
        i = 0
        while i < len(self.points) and len(self.points) > 3:
            next_i = (i + 1) % len(self.points)
            
            edge = self.points[next_i] - self.points[i]
            edge_length = np.linalg.norm(edge)
            
            if edge_length < self.min_edge_length * 0.5:
                # Remove one of the points
                self.points.pop(next_i if next_i < len(self.points) else i)
            else:
                i += 1
    
    def get_points(self) -> np.ndarray:
        """Get current points as numpy array."""
        return np.array(self.points)
    
    def get_2d_profile(self) -> np.ndarray:
        """Get points as 2D profile (for sweep cross-section)."""
        return self.get_points()


def generate_differential_growth_profile(
    initial_radius: float = 1.0,
    num_initial_points: int = 12,
    iterations: int = 50,
    max_edge_length: float = 0.12,
    repulsion_radius: float = 0.35
) -> np.ndarray:
    """
    Generate an organic profile using differential growth.
    
    Args:
        initial_radius: Starting circle radius
        num_initial_points: Number of points in initial circle
        iterations: Number of growth iterations
        max_edge_length: Maximum edge length before splitting
        repulsion_radius: Radius for repulsion forces
        
    Returns:
        Nx2 array of profile points
    """
    dg = DifferentialGrowth(initial_radius, num_initial_points)
    dg.max_edge_length = max_edge_length
    dg.repulsion_radius = repulsion_radius
    
    dg.step(iterations)
    
    return dg.get_2d_profile()
