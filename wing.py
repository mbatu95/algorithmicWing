from mesh import Mesh
from typing import List, Tuple
import numpy as np

class Wing:
    """
    Object-oriented wing design class for future extensibility (e.g. fuselage, tail).
    Encapsulates airfoil profile, morph parameters, and geometry generation.
    """
    def __init__(self, naca: str = '2412', chord: float = 1.0, span: float = 3.0, points: int = 200, depth: float = 3.0):
        self.naca = naca.zfill(4)
        self.chord = chord
        self.span = span
        self.points = points
        self.depth = depth
        # Morph parameters
        self.start_percent = 0.5
        self.thickness_factor = 1.0
        self.shift_amount = 0.0
        self.dihedral_angle = 0.0  # radians
        # Geometry cache
        self.profile_coords = self.generate_airfoil_profile()
        self.mesh = None

    def set_naca(self, naca: str):
        self.naca = naca.zfill(4)
        self.profile_coords = self.generate_airfoil_profile()

    def set_morph(self, start_percent: float, thickness_factor: float, shift_amount: float, dihedral_angle: float):
        self.start_percent = start_percent
        self.thickness_factor = thickness_factor
        self.shift_amount = shift_amount
        self.dihedral_angle = dihedral_angle

    def generate_airfoil_profile(self) -> List[Tuple[float, float]]:
        """
        Generates NACA 4-digit airfoil coordinates as a list of (x, y) tuples.
        """
        M = int(self.naca[0]) / 100.0
        P = int(self.naca[1]) / 10.0
        TT = int(self.naca[2:]) / 100.0
        x = np.linspace(0, self.chord, self.points)
        yt = 5 * TT * (
            0.2969 * np.sqrt(x / self.chord) -
            0.1260 * (x / self.chord) -
            0.3516 * (x / self.chord) ** 2 +
            0.2843 * (x / self.chord) ** 3 -
            0.1015 * (x / self.chord) ** 4
        )
        yc = np.where(
            x < P * self.chord,
            M / (P ** 2) * (2 * P * (x / self.chord) - (x / self.chord) ** 2),
            M / ((1 - P) ** 2) * ((1 - 2 * P) + 2 * P * (x / self.chord) - (x / self.chord) ** 2)
        )
        dyc_dx = np.where(
            x < P * self.chord,
            2 * M / (P ** 2) * (P - x / self.chord),
            2 * M / ((1 - P) ** 2) * (P - x / self.chord)
        )
        theta = np.arctan(dyc_dx)
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        # Combine upper and lower surfaces
        coords = [(xu[i], yu[i]) for i in range(self.points)] + [(xl[i], yl[i]) for i in reversed(range(self.points))]
        return coords

    def get_mesh(self):
        """
        Extrudes the airfoil profile along the span to create a 3D mesh and returns a Mesh object.
        Returns:
            Mesh: Mesh object containing vertices and indices
        """
        coords = np.array(self.profile_coords)
        slices = int(self.depth)
        N = len(coords)
        vertices = []
        for s in range(slices):
            z = s * self.span / (slices - 1) if slices > 1 else 0
            for x, y in coords:
                vertices.append([x, y, z])
        # Triangulate between slices
        indices = []
        for s in range(slices - 1):
            base = s * N
            next_base = (s + 1) * N
            for j in range(N):
                j2 = (j + 1) % N
                indices.append([base + j, next_base + j, next_base + j2])
                indices.append([base + j, next_base + j2, base + j2])
        return Mesh(vertices, indices)

    def __repr__(self):
        return f"Wing(naca={self.naca}, chord={self.chord}, span={self.span}, points={self.points}, depth={self.depth})"

