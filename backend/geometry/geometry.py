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


