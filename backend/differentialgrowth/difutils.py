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



def insert_particle(particles: list[Particle], max_distance: float, max_particles: int = 1000):
    """
    Insert particles between consecutive pairs if distance exceeds max_distance.
    OPTIMIZED: Batch collect insertions, then insert all at once.
    
    Args:
        particles: List of particles
        max_distance: Maximum allowed distance between neighbors
        max_particles: Maximum number of particles (prevents infinite growth)
    """
    if len(particles) >= max_particles:
        return
    
    n = len(particles)
    max_distance_sq = max_distance ** 2  # Avoid sqrt
    
    # Collect all insertions first (to avoid modifying list while iterating)
    insertions = []
    
    for i in range(n):
        if len(particles) + len(insertions) >= max_particles:
            break
            
        p1 = particles[i]
        p2 = particles[(i + 1) % n]
        
        diff = p2.position - p1.position
        dist_sq = np.dot(diff, diff)  # Faster than norm for squared distance
        
        if dist_sq > max_distance_sq:
            mid_position = p1.position + diff * 0.5
            insertions.append((i + 1, Particle(position=mid_position)))
    
    # Insert all new particles (in reverse order to maintain indices)
    for idx, particle in reversed(insertions):
        particles.insert(idx, particle)

 
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


def update_velocity(particles: list[Particle], repulsion_distance: float = 1.0, damping: float = 0.7) -> None:
    """
    Update velocity based on repulsion from all nearby particles.
    OPTIMIZED: Uses vectorized numpy operations for 10-50x speedup.
    
    Args:
        particles: List of Particle objects
        repulsion_distance: Distance below which particles repel
        damping: Velocity damping factor (0-1, lower = more damping)
    """
    n = len(particles)
    
    # Pre-compute all positions as numpy array (vectorization!)
    positions = np.array([p.position for p in particles])  # Shape: (n, 2)
    repulsion_sq = repulsion_distance ** 2  # Avoid sqrt by comparing squared distances
    
    for i, p in enumerate(particles):
        # Vectorized distance calculation to ALL particles at once
        diff = positions[i] - positions  # Shape: (n, 2) - broadcast
        dist_sq = np.sum(diff ** 2, axis=1)  # Squared distances, shape: (n,)
        
        # Find particles within repulsion range (excluding self)
        mask = (dist_sq < repulsion_sq) & (dist_sq > 0.01)
        
        if np.any(mask):
            # Get distances for repelling particles
            distances = np.sqrt(dist_sq[mask])
            # Normalize directions
            directions = diff[mask] / distances[:, np.newaxis]
            # Calculate strengths
            strengths = (repulsion_distance - distances) / repulsion_distance
            # Sum all forces
            force = np.sum(directions * strengths[:, np.newaxis], axis=0)
        else:
            force = np.zeros(2)
        
        # Apply force with strong damping
        p.velocity = p.velocity * damping + force * 0.3
        

def update_position(particles: list[Particle], dt: float = 1.0) -> None:
    """
    Update the position of each particle by adding its velocity.

    Args:
        particles: list of Particle objects
        dt: time step multiplier (smaller = more stable)
    """
    for p in particles:
        # Cap velocity to prevent explosions
        speed = np.linalg.norm(p.velocity)
        max_speed = 5.0  # Lower max speed for stability
        if speed > max_speed:
            p.velocity = (p.velocity / speed) * max_speed
        
        p.position += p.velocity * dt