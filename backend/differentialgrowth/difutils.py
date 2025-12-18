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

 
def update(particles: list[Particle], dt: float=1.0):
    
    changed = True
    while changed:
        changed = False
        n = len(particles)
        for i in range(n):
            p1 = particles[i]
            p2 = particles[(i + 1) % n]  # wrap-around
            vec = p2.position - p1.position
            distance = np.linalg.norm(vec)
            if distance > 10.0:  # Example threshold
                mid_position = p1.position + vec / 2
                particles.insert(i + 1, Particle(position=mid_position))
                changed = True
                break  # restart the loop because list changed


def update_velocity(particles: list[Particle], repulsion_distance: float = 1.0) -> None:
    """
    Update the velocity of each particle based on repulsion from other particles.

    Args:
        particles: List of Particle objects
        repulsion_distance: distance below which particles repel each other
    """
    for p in particles:
        force = np.zeros(2)  # total force on this particle

        for other in particles:
            if other is p:
                continue  # skip self

            diff = other.position - p.position  # vector from p to other
            distance = np.linalg.norm(diff)

            if distance < repulsion_distance and distance > 0:  # avoid division by zero
                direction = diff / distance  # normalize
                magnitude = -1 / (distance ** 2)  # repulsion inversely proportional to distance^2
                force += direction * magnitude  # add repulsive force

        # Update velocity (v = v + a), here acceleration = total force
        p.velocity += force
        print(p.velocity)
        

def update_position(particles: list[Particle], dt: float = 1.0) -> None:
    """
    Update the position of each particle by adding its velocity.

    Args:
        particles: list of Particle objects
        dt: time step multiplier (default 1.0)
    """
    for p in particles:
        p.position += p.velocity * dt