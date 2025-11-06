
class CubeMesh:
    """
    Generates a cube mesh of arbitrary size centered at the origin.
    """
    def __init__(self, size=1.0):
        self.size = size
        self.vertices = []
        self.indices = []
        self._generate_mesh()

    def _generate_mesh(self):
        s = self.size / 2.0
        # 8 vertices of the cube
        self.vertices = [
            [-s, -s, -s],
            [ s, -s, -s],
            [ s,  s, -s],
            [-s,  s, -s],
            [-s, -s,  s],
            [ s, -s,  s],
            [ s,  s,  s],
            [-s,  s,  s],
        ]
        # 12 triangles (2 per face)
        self.indices = [
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 5, 6], [4, 6, 7],  # top
            [0, 1, 5], [0, 5, 4],  # front
            [2, 3, 7], [2, 7, 6],  # back
            [1, 2, 6], [1, 6, 5],  # right
            [3, 0, 4], [3, 4, 7],  # left
        ]

    def to_dict(self):
        return {'mesh_vertices': self.vertices, 'mesh_indices': self.indices}
