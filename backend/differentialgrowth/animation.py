import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from difutils import create_particle_ring, insert_particle, update_velocity, update_position
from particle import Particle
import numpy as np

def animate_particles(particles, steps=100, repulsion_distance=25, max_distance=12):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-300, 300)
    ax.set_ylim(-300, 300)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Differential Growth Simulation')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    # Initial scatter plot
    x_coords = [p.position[0] for p in particles]
    y_coords = [p.position[1] for p in particles]
    scat = ax.scatter(x_coords, y_coords, c='red', s=30, zorder=5)
    
    # Line segments connecting neighbors
    lines = []
    for i in range(len(particles)):
        p1 = particles[i]
        p2 = particles[(i + 1) % len(particles)]
        line, = ax.plot([p1.position[0], p2.position[0]], 
                        [p1.position[1], p2.position[1]], 
                        'b-', alpha=0.5, linewidth=1.5)
        lines.append(line)

    def update(frame):
        # Update particles each frame
        insert_particle(particles, max_distance=max_distance, max_particles=1000)
        update_velocity(particles, repulsion_distance=repulsion_distance)
        update_position(particles)

        # Update scatter plot positions
        x_coords = [p.position[0] for p in particles]
        y_coords = [p.position[1] for p in particles]
        # scat.set_offsets(np.c_[x_coords, y_coords])
        
        # Remove old lines and create new ones
        for line in lines:
            line.remove()
        lines.clear()
        
        # Draw new line segments
        for i in range(len(particles)):
            p1 = particles[i]
            p2 = particles[(i + 1) % len(particles)]
            line, = ax.plot([p1.position[0], p2.position[0]], 
                            [p1.position[1], p2.position[1]], 
                            'b-', alpha=0.5, linewidth=1.5)
            lines.append(line)
        
        # Update title with particle count
        ax.set_title(f'Differential Growth - Frame {frame} - Particles: {len(particles)}')
        
        return [scat] + lines

    anim = FuncAnimation(fig, update, frames=steps, interval=50, blit=False)  # blit=False for dynamic lines
    plt.show()


if __name__ == "__main__":
    # Tuned parameters for stable differential growth
    particles = create_particle_ring(
        center_particle={'x': 0, 'y': 0}, 
        num_particles=4,           # Start with enough particles
        radius=30                   # Good starting size
    )
    animate_particles(
        particles, 
        steps=300,                  
        repulsion_distance=25,      # Moderate repulsion
        max_distance=12             # Allow some spacing before split
    )
