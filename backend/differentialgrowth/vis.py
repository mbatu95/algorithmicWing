import matplotlib.pyplot as plt
from difutils import create_particle_ring
from particle import Particle
import numpy as np

def plot_vectors(particles):
    """
    Plot a list of particles.
    
    Args:
        particles: List of Particle objects with position attributes
    """
    if not particles:
        print("No particles to plot")
        return
    
    for p in particles:
        print(p.position)
    
    x_coords = [p.position[0] for p in particles]
    y_coords = [p.position[1] for p in particles]
    
    plt.figure(figsize=(8, 6))
    plt.scatter(x_coords, y_coords, c='red', s=50, zorder=5)
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Particle Plot')
    plt.show()



if __name__ == "__main__":
    # Example usage

    particles = create_particle_ring(center_particle={'x': 0, 'y': 0}, num_particles=500, radius=5.0)
    print(f"Created {len(particles)} particles in a ring.")
    plot_vectors(particles)