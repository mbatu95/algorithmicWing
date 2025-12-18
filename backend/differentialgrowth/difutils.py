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
    Only does ONE pass per call to prevent computational explosion.
    
    Args:
        particles: List of particles
        max_distance: Maximum allowed distance between neighbors
        max_particles: Maximum number of particles (prevents infinite growth)
    """
    if len(particles) >= max_particles:
        return
    
    # Single pass - only insert once per call
    i = 0
    n = len(particles)
    while i < n and len(particles) < max_particles:
        p1 = particles[i]
        p2 = particles[(i + 1) % len(particles)]
        vec = p2.position - p1.position
        distance = np.linalg.norm(vec)
        
        if distance > max_distance:
            mid_position = p1.position + vec / 2
            particles.insert(i + 1, Particle(position=mid_position))
            i += 2  # skip the newly inserted particle
            n += 1
        else:
            i += 1

 
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


def update_velocity(particles: list[Particle], repulsion_distance: float = 1.0, damping: float = 0.85) -> None:
    """
    Update velocity based on:
    1. Repulsion from nearby particles
    2. Attraction to neighbors (spring force)
    3. Velocity damping (prevents explosion)
    
    Args:
        particles: List of Particle objects
        repulsion_distance: Distance below which particles repel
        damping: Velocity damping factor (0-1, closer to 1 = less damping)
    """
    n = len(particles)
    
    for i, p in enumerate(particles):
        force = np.zeros(2)
        
        # Get neighbors (only adjacent particles for O(n) instead of O(n²))
        prev_particle = particles[(i - 1) % n]
        next_particle = particles[(i + 1) % n]
        neighbors = [prev_particle, next_particle]
        
        # Spring force to neighbors (keeps structure connected)
        for neighbor in neighbors:
            diff = neighbor.position - p.position
            distance = np.linalg.norm(diff)
            if distance > 0:
                direction = diff / distance
                # Spring force: pulls together if too far
                spring_force = (distance - repulsion_distance * 0.5) * 0.1
                force += direction * spring_force
        
        # Repulsion from ALL nearby particles (still needed for organic shape)
        for other in particles:
            if other is p:
                continue
            
            diff = p.position - other.position  # REVERSED: push AWAY
            distance = np.linalg.norm(diff)
            
            if distance < repulsion_distance and distance > 0:
                direction = diff / distance
                # Stronger repulsion when closer
                magnitude = (repulsion_distance - distance) / repulsion_distance
                force += direction * magnitude * 0.5
        
        # Update velocity with damping
        p.velocity = p.velocity * damping + force
        

def update_position(particles: list[Particle], dt: float = 0.5) -> None:
    """
    Update the position of each particle by adding its velocity.

    Args:
        particles: list of Particle objects
        dt: time step multiplier (smaller = more stable)
    """
    for p in particles:
        p.position += p.velocity * dt
        
        # Optional: Cap velocity to prevent explosions
        speed = np.linalg.norm(p.velocity)
        max_speed = 10.0
        if speed > max_speed:
            p.velocity = (p.velocity / speed) * max_speed