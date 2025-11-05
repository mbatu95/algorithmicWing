class Mesh:
    def __init__(self, vertices, indices):
        self.vertices = vertices  # List of [x, y, z]
        self.indices = indices    # List of [i0, i1, i2]

    def to_dict(self):
        return {
            'mesh_vertices': self.vertices,
            'mesh_indices': self.indices
        }

# geometry.py
