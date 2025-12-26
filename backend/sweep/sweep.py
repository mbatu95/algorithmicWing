"""
Simple sweep algorithm: Extrude a 2D cross-section along a 3D path.
"""

import numpy as np
from typing import Tuple


def compute_frame(path: np.ndarray, i: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute local coordinate frame (tangent, normal, binormal) at path point i.
    """
    n = len(path)
    
    # Compute tangent (path direction)
    if i == 0:
        tangent = path[1] - path[0]
    elif i == n - 1:
        tangent = path[-1] - path[-2]
    else:
        tangent = path[i + 1] - path[i - 1]
    
    tangent = tangent / (np.linalg.norm(tangent) + 1e-10)
    
    # Choose an up vector that's not parallel to tangent
    if abs(tangent[1]) < 0.9:
        up = np.array([0, 1, 0])
    else:
        up = np.array([0, 0, 1])
    
    # Binormal (perpendicular to tangent and up)
    binormal = np.cross(tangent, up)
    binormal = binormal / (np.linalg.norm(binormal) + 1e-10)
    
    # Normal (perpendicular to both)
    normal = np.cross(binormal, tangent)
    normal = normal / (np.linalg.norm(normal) + 1e-10)
    
    return tangent, normal, binormal


def sweep(cross_section: np.ndarray, path: np.ndarray, closed: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sweep a 2D cross-section along a 3D path to create a 3D mesh.
    
    Args:
        cross_section: Mx2 array of 2D points (x, y)
        path: Nx3 array of 3D points (x, y, z)
        closed: If True, connect last point to first (for circles, tubes)
        
    Returns:
        Tuple of (vertices, faces):
            - vertices: (N*M)x3 array of 3D vertex positions
            - faces: Fx3 array of triangle indices
    """
    n_path = len(path)
    n_profile = len(cross_section)
    
    # Create vertices by placing and orienting cross-section at each path point
    vertices = []
    
    for i, path_point in enumerate(path):
        # Get local coordinate frame at this point
        tangent, normal, binormal = compute_frame(path, i)
        
        for cs_x, cs_y in cross_section:
            # Transform cross-section point to 3D using local frame
            # cs_x maps to binormal direction, cs_y maps to normal direction
            vertex = path_point + cs_x * binormal + cs_y * normal
            vertices.append(vertex)
    
    vertices = np.array(vertices)
    
    # Create faces by connecting adjacent cross-sections
    faces = []
    
    for i in range(n_path - 1):
        for j in range(n_profile - 1 if not closed else n_profile):
            # Indices of quad corners
            v0 = i * n_profile + j
            v1 = i * n_profile + ((j + 1) % n_profile if closed else (j + 1))
            v2 = (i + 1) * n_profile + j
            v3 = (i + 1) * n_profile + ((j + 1) % n_profile if closed else (j + 1))
            
            # Split quad into two triangles
            faces.append([v0, v2, v1])
            faces.append([v1, v2, v3])
    
    faces = np.array(faces)
    
    return vertices, faces
