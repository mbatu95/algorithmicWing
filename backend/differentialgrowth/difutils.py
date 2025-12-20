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


def update_velocity(particles: list[Particle], repulsion_distance: float = 1.0, damping: float = 0.7) -> None:
    """
    Update velocity based on repulsion from all nearby particles.
    Uses simple repulsion-only physics for stable growth.
    
    Args:
        particles: List of Particle objects
        repulsion_distance: Distance below which particles repel
        damping: Velocity damping factor (0-1, lower = more damping)
    """
    n = len(particles)
    
    for i, p in enumerate(particles):
        force = np.zeros(2)
        
        # Repulsion from ALL particles (creates organic spreading)
        for j, other in enumerate(particles):
            if i == j:
                continue
            
            diff = p.position - other.position  # Vector pointing away from other
            distance = np.linalg.norm(diff)
            
            if distance < repulsion_distance and distance > 0.01:  # Avoid division by zero
                direction = diff / distance
                # Linear repulsion: stronger when closer
                strength = (repulsion_distance - distance) / repulsion_distance
                force += direction * strength
        
        # Apply force with strong damping
        p.velocity = p.velocity * damping + force * 0.3  # 0.3 = force multiplier
        

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