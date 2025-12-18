import numpy as np
from particle import Particle

def create_particle_ring(center_particle:dict[str, float], num_particles:int=20, radius:float=1.0) -> list[Particle]:
    """1
    Create a ring of particles around a center particle.
    
    Args:
        center_particle: Particle with x, y coordinates (assumed to have .x and .y attributes)
        num_particles: Number of particles in the ring
        radius: Radius of the ring
    
    Returns:
        List of Particle objects
    """
    angles = np.linspace(0, 2 * np.pi, num_particles, endpoint=False)
    
    x_coords = center_particle['x'] + radius * np.cos(angles)
    y_coords = center_particle['y'] + radius * np.sin(angles)
    
    particles = [Particle(position=np.array([x, y])) for x, y in zip(x_coords, y_coords)]
    
    return particles



def insert_particle(particles: list[Particle], max_distance: float):
    """
    Insert particles between all consecutive pairs including the last-to-first segment
    until all gaps are below max_distance.
    """
    changed = True
    while changed:
        changed = False
        n = len(particles)
        for i in range(n):
            p1 = particles[i]
            p2 = particles[(i + 1) % n]  # wrap-around
            vec = p2.position - p1.position
            distance = np.linalg.norm(vec)
            if distance > max_distance:
                mid_position = p1.position + vec / 2
                particles.insert(i + 1, Particle(position=mid_position))
                changed = True
                break  # restart the loop because list changed
