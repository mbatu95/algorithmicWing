import numpy as np

class Fuselage:
    """
    Generates a fuselage mesh with nose, cylindrical body, and tail.
    Parameters:
        length: total length of fuselage
        diameter: max diameter (circular cross-section)
        nose_length: length of nose cone (fraction of length or absolute)
        tail_length: length of tail cone (fraction of length or absolute)
        sections: number of cross-section slices (smoothness)
        profile: optional list of diameter multipliers along length (for bulges, custom shapes)
        nose_type: 'cone' (default), 'ogive', 'parabolic' (future)
        tail_type: 'cone' (default), 'ogive', 'parabolic' (future)
    """
    def __init__(
        self,
        length=20.0,              # meters, typical for a small aircraft
        diameter=2.5,             # meters, max width
        nose_length=0.18,         # 18% of length, smooth ogive nose
        tail_length=0.22,         # 22% of length, longer tail for smooth taper
        sections=40,              # smoothness
        profile=None,             # can be set for bulges, defaults to smooth
        nose_type='ogive',        # ogive is more realistic than cone
        tail_type='cone',         # cone is simple and plausible
    ):
        self.length = length
        self.diameter = diameter
        self.nose_length = nose_length if nose_length < 1 else nose_length / length
        self.tail_length = tail_length if tail_length < 1 else tail_length / length
        self.sections = sections
        self.profile = profile
        self.nose_type = nose_type
        self.tail_type = tail_type
        self.vertices = []
        self.indices = []
        self._generate_mesh()

    def _generate_mesh(self):
        n_circle = 24  # points per cross-section
        L = self.length
        D = self.diameter
        nose_L = self.nose_length * L
        tail_L = self.tail_length * L
        body_L = L - nose_L - tail_L
        z_sections = np.linspace(0, L, self.sections)
        # Profile: 0 to 1 along length
        if self.profile is not None:
            profile = np.array(self.profile)
            if len(profile) != self.sections:
                profile = np.interp(np.linspace(0,1,self.sections), np.linspace(0,1,len(profile)), profile)
        else:
            profile = np.ones(self.sections)
        # Compute radius at each section
        radii = np.ones(self.sections) * (D/2)
        for i, z in enumerate(z_sections):
            if z < nose_L:
                # Nose shape
                if self.nose_type == 'ogive':
                    # Ogive nose: r = R * sqrt(1 - ((z - a)/a)^2), a = nose_L
                    a = nose_L
                    R = D/2
                    rel_z = z
                    if a > 0:
                        ogive_r = R * np.sqrt(1 - ((a - rel_z)/a)**2) if rel_z <= a else R
                        radii[i] = ogive_r
                else:
                    # Default: cone
                    radii[i] *= (z / nose_L)
            elif z > (L - tail_L):
                # Tail cone
                radii[i] *= ((L - z) / tail_L)
            # Apply profile
            radii[i] *= profile[i]
        # Generate vertices
        for i, (z, r) in enumerate(zip(z_sections, radii)):
            for j in range(n_circle):
                theta = 2 * np.pi * j / n_circle
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                self.vertices.append([x, y, z])
        # Generate indices (quads split into triangles)
        for i in range(self.sections - 1):
            for j in range(n_circle):
                next_j = (j + 1) % n_circle
                v0 = i * n_circle + j
                v1 = i * n_circle + next_j
                v2 = (i + 1) * n_circle + j
                v3 = (i + 1) * n_circle + next_j
                self.indices.append([v0, v2, v1])
                self.indices.append([v1, v2, v3])

    def to_dict(self):
        return {'mesh_vertices': self.vertices, 'mesh_indices': self.indices}
