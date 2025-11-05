# Mesh class to hold mesh data
class Mesh:
    def __init__(self, vertices, indices):
        self.vertices = vertices  # List of [x, y, z]
        self.indices = indices    # List of [i0, i1, i2]

    def to_dict(self):
        return {
            'mesh_vertices': self.vertices,
            'mesh_indices': self.indices
        }

# Mesh class to hold mesh data
# Generic geometry object for wings, fuselage, etc.
class Geometry:
    def __init__(self, type_, mesh, position=None, color=None, material=None):
        self.type = type_  # e.g. 'wing', 'fuselage', etc.
        self.mesh = mesh   # Mesh object
        self.position = position if position is not None else [0, 0, 0]
        self.color = color  # e.g. '#ff0000' or [1,0,0]
        self.material = material  # e.g. 'metal', 'plastic', etc.

    def set_position(self, pos):
        self.position = pos

    def set_color(self, color):
        self.color = color

    def set_material(self, material):
        self.material = material

    def get_mesh(self):
        return self.mesh

    def to_dict(self):
        mesh_dict = self.mesh.to_dict() if self.mesh else {}
        return {
            'type': self.type,
            **mesh_dict,
            'position': self.position,
            'color': self.color,
            'material': self.material
        }

    def __repr__(self):
        return f"Geometry(type={self.type}, position={self.position}, color={self.color}, material={self.material}, mesh={self.mesh})"
