"""
Bezier curve implementation for generating smooth paths.
"""

import numpy as np
from typing import List


def bezier_curve(control_points: np.ndarray, num_points: int = 100) -> np.ndarray:
    """
    Generate points along a Bezier curve from control points.
    
    Args:
        control_points: Nx3 array of control points (can be 2D or 3D)
        num_points: Number of points to generate along the curve
        
    Returns:
        num_points x 3 array of points along the Bezier curve
    """
    n = len(control_points) - 1  # Degree of curve
    t_values = np.linspace(0, 1, num_points)
    
    curve_points = []
    
    for t in t_values:
        # De Casteljau's algorithm for stability
        # Need to work with a copy that we modify in place
        temp_points = control_points.copy().astype(float)
        
        for r in range(1, n + 1):
            for i in range(n + 1 - r):
                temp_points[i] = (1 - t) * temp_points[i] + t * temp_points[i + 1]
        
        curve_points.append(temp_points[0])
    
    return np.array(curve_points)


def cubic_bezier(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, num_points: int = 100) -> np.ndarray:
    """
    Generate cubic Bezier curve (4 control points).
    
    Args:
        p0, p1, p2, p3: Control points
        num_points: Number of points to generate
        
    Returns:
        Array of points along the curve
    """
    control_points = np.array([p0, p1, p2, p3])
    return bezier_curve(control_points, num_points)


def quadratic_bezier(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, num_points: int = 100) -> np.ndarray:
    """
    Generate quadratic Bezier curve (3 control points).
    
    Args:
        p0, p1, p2: Control points
        num_points: Number of points to generate
        
    Returns:
        Array of points along the curve
    """
    control_points = np.array([p0, p1, p2])
    return bezier_curve(control_points, num_points)
