def scale_geometry(geometry, scale):
    """
    Scales the mesh vertices of a Geometry object by the given scale factor or vector.
    Only affects the input geometry, not other geometries sharing the same mesh.
    scale: float or tuple/list of (sx, sy, sz)
    """
    from copy import deepcopy
    import numpy as np
    mesh_copy = deepcopy(geometry.mesh)
    verts = np.array(mesh_copy.vertices)
    if isinstance(scale, (int, float)):
        scale_vec = np.array([scale, scale, scale])
    else:
        scale_vec = np.array(scale)
    verts_scaled = verts * scale_vec
    mesh_copy.vertices = verts_scaled.tolist()
    geometry.mesh = mesh_copy
def translate_geometry(geometry, translation):
    """
    Translates the mesh vertices of a Geometry object by the given (x, y, z) vector.
    Only affects the input geometry, not other geometries sharing the same mesh.
    translation: tuple or list of (x, y, z)
    """
    from copy import deepcopy
    import numpy as np
    mesh_copy = deepcopy(geometry.mesh)
    verts = np.array(mesh_copy.vertices)
    translation_vec = np.array(translation)
    verts_translated = verts + translation_vec
    mesh_copy.vertices = verts_translated.tolist()
    geometry.mesh = mesh_copy
import numpy as np

def rotate_geometry(geometry, angles):
    """
    Rotates the mesh vertices of a Geometry object around the x, y, and z axes.
    angles: tuple of (x, y, z) rotation angles in radians
    Only affects the input geometry, not other geometries sharing the same mesh.
    """
    from copy import deepcopy
    x_angle, y_angle, z_angle = angles
    verts = np.array(geometry.mesh.vertices)
    # Rotation matrices
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(x_angle), -np.sin(x_angle)],
        [0, np.sin(x_angle), np.cos(x_angle)]
    ])
    Ry = np.array([
        [np.cos(y_angle), 0, np.sin(y_angle)],
        [0, 1, 0],
        [-np.sin(y_angle), 0, np.cos(y_angle)]
    ])
    Rz = np.array([
        [np.cos(z_angle), -np.sin(z_angle), 0],
        [np.sin(z_angle), np.cos(z_angle), 0],
        [0, 0, 1]
    ])
    # Combined rotation: Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    verts_rotated = verts @ R.T
    # Clone mesh so only this geometry is affected
    mesh_copy = deepcopy(geometry.mesh)
    mesh_copy.vertices = verts_rotated.tolist()
    geometry.mesh = mesh_copy
