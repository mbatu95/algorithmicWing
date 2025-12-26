"""
Test the sweep algorithm with your input.
"""

import math
import numpy as np
from sweep import sweep


# Your cross-section
cross_section = np.array([
    [0.0, 0.0],
    [0.2, 0.05],
    [0.5, 0.08],
    [0.8, 0.03],
    [1.0, 0.0]
])

# Generate path using Bézier curve with more steps
def bezier_curve(points, num_samples=15):
    """
    Generate a Bézier curve through the given points.
    Uses De Casteljau's algorithm for arbitrary number of control points.
    """
    n = len(points) - 1
    t_values = np.linspace(0, 1, num_samples)
    curve = []
    
    for t in t_values:
        # Binomial coefficients for Bézier curve
        point = np.zeros(3)
        for i in range(n + 1):
            binomial = math.comb(n, i)
            point += binomial * ((1 - t) ** (n - i)) * (t ** i) * points[i]
        curve.append(point)
    
    return np.array(curve)

# Control points for the path
control_points = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.2, 0.1],
    [2.0, 0.4, 0.3],
    [3.0, 0.6, 0.6],
])

# Generate smooth path with Bézier curve
path = bezier_curve(control_points, num_samples=100)

# Perform sweep
vertices, faces = sweep(cross_section, path)

print(f"Vertices: {len(vertices)}")
print(f"Faces: {len(faces)}")
print(f"\nFirst 5 vertices:\n{vertices[:5]}")
print(f"\nFirst 5 faces:\n{faces[:5]}")
