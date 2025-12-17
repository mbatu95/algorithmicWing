import numpy as np

class Particle:
    def __init__(self, position=None, velocity=None):
        """
        Initialize a particle with position and velocity vectors.
        
        Args:
            position: numpy array for position (default: zero vector)
            velocity: numpy array for velocity (default: zero vector)
        """
        self.position = position if position is not None else np.array([0.0, 0.0])
        self.velocity = velocity if velocity is not None else np.array([0.0, 0.0])
    
    def update(self, dt=1.0):
        """Update particle position based on velocity."""
        self.position += self.velocity * dt