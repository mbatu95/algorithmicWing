# geometry.py
# Generic geometry object for wings, fuselage, etc.

class Geometry:
    def __init__(self, type_, mesh_vertices, mesh_indices, position=None, color=None, material=None):
        self.type = type_  # e.g. 'wing', 'fuselage', etc.
        self.mesh_vertices = mesh_vertices  # List of [x, y, z]
        self.mesh_indices = mesh_indices    # List of [i0, i1, i2]
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
        return self.mesh_vertices, self.mesh_indices

    def __repr__(self):
        return f"Geometry(type={self.type}, position={self.position}, color={self.color}, material={self.material})"
