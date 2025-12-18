import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from difutils import create_particle_ring, insert_particle, update_velocity, update_position
from particle import Particle
import numpy as np

def animate_particles(particles, steps=100, repulsion_distance=25, max_distance=12):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Differential Growth Simulation')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    # Initial scatter plot
    x_coords = [p.position[0] for p in particles]
    y_coords = [p.position[1] for p in particles]
    scat = ax.scatter(x_coords, y_coords, c='red', s=20, zorder=5)
    
    # Add line plot to show connectivity
    line, = ax.plot([], [], 'b-', alpha=0.3, linewidth=1)

    def update(frame):
        # Update particles each frame
        insert_particle(particles, max_distance=max_distance, max_particles=500)
        update_velocity(particles, repulsion_distance=repulsion_distance)
        update_position(particles)

        # Update scatter plot positions
        x_coords = [p.position[0] for p in particles]
        y_coords = [p.position[1] for p in particles]
        scat.set_offsets(np.c_[x_coords, y_coords])
        
        # Update line to show ring structure
        x_line = x_coords + [x_coords[0]]  # Close the loop
        y_line = y_coords + [y_coords[0]]
        line.set_data(x_line, y_line)
        
        # Update title with particle count
        ax.set_title(f'Differential Growth - Frame {frame} - Particles: {len(particles)}')
        
        return scat, line

    anim = FuncAnimation(fig, update, frames=steps, interval=50, blit=True)
    plt.show()


if __name__ == "__main__":
    # Better parameters for smooth, organic growth
    particles = create_particle_ring(
        center_particle={'x': 0, 'y': 0}, 
        num_particles=4,           # Start small
        radius=30                   # Smaller radius
    )
    animate_particles(
        particles, 
        steps=200,                  # More frames to see evolution
        repulsion_distance=15,      # Half the radius
        max_distance=8              # Tighter spacing
    )
