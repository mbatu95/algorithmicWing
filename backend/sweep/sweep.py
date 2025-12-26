"""
Simple sweep algorithm: Extrude a 2D cross-section along a 3D path.
"""

import numpy as np
from typing import Tuple


def compute_parallel_transport_frames(path: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute stable frames along path using parallel transport (Rotation Minimizing Frames).
    Returns arrays of tangents, normals, and binormals for each path point.
    """
    n = len(path)
    tangents = np.zeros((n, 3))
    normals = np.zeros((n, 3))
    binormals = np.zeros((n, 3))
    
    # Compute tangents
    for i in range(n):
        if i == 0:
            tangents[i] = path[1] - path[0]
        elif i == n - 1:
            tangents[i] = path[-1] - path[-2]
        else:
            tangents[i] = path[i + 1] - path[i - 1]
        tangents[i] = tangents[i] / (np.linalg.norm(tangents[i]) + 1e-12)
    
    # Initialize first frame with a stable normal
    t0 = tangents[0]
    # Choose initial normal perpendicular to tangent
    if abs(t0[1]) < 0.9:
        n0 = np.array([0.0, 1.0, 0.0])
    else:
        n0 = np.array([0.0, 0.0, 1.0])
    n0 = n0 - np.dot(n0, t0) * t0
    n0 = n0 / (np.linalg.norm(n0) + 1e-12)
    
    normals[0] = n0
    binormals[0] = np.cross(t0, n0)
    binormals[0] = binormals[0] / (np.linalg.norm(binormals[0]) + 1e-12)
    
    # Parallel transport: propagate frame along path with minimal rotation
    for i in range(1, n):
        t_prev = tangents[i - 1]
        t_curr = tangents[i]
        
        # Rotation axis: perpendicular to both tangents
        v = np.cross(t_prev, t_curr)
        c = np.dot(t_prev, t_curr)
        
        # If tangents are nearly parallel, just use previous frame
        if np.linalg.norm(v) < 1e-9:
            normals[i] = normals[i - 1]
            binormals[i] = binormals[i - 1]
        else:
            # Rodrigues' rotation formula to rotate previous normal
            v = v / np.linalg.norm(v)
            s = np.sqrt(1 - c * c)
            
            # Rotate previous normal around v
            n_prev = normals[i - 1]
            normals[i] = n_prev * c + np.cross(v, n_prev) * s + v * np.dot(v, n_prev) * (1 - c)
            normals[i] = normals[i] / (np.linalg.norm(normals[i]) + 1e-12)
            
            # Recompute binormal
            binormals[i] = np.cross(t_curr, normals[i])
            binormals[i] = binormals[i] / (np.linalg.norm(binormals[i]) + 1e-12)
    
    return tangents, normals, binormals


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
    
    # Compute all frames at once using parallel transport
    tangents, normals, binormals = compute_parallel_transport_frames(path)
    
    # Create vertices by placing and orienting cross-section at each path point
    vertices = []
    
    for i, path_point in enumerate(path):
        # Get precomputed frame at this point
        normal = normals[i]
        binormal = binormals[i]
        
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
