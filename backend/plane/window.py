import numpy as np



class Window:
    """
    Generates a highly realistic 3D airplane window mesh with:
      - Elliptical/oval profile (not just rounded rectangle)
      - Extruded frame with bevel
      - Glass pane inset
      - Optional mounting screws (vertices only)
    Parameters:
        width: total width of the window (outer frame)
        height: total height of the window (outer frame)
        thickness: extrusion depth (meters)
        frame_width: width of the window frame/bezel (meters)
        glass_inset: how far the glass is inset from the outer frame (meters)
        frame_bevel: how much the frame is beveled (meters)
        segments: number of segments for the ellipse (smoothness)
        screws: number of mounting screws (optional, for realism)
    """
    def __init__(self, width=0.38, height=0.54, thickness=0.045, frame_width=0.055, glass_inset=0.01, frame_bevel=0.012, segments=40, screws=8):
        self.width = width 
        self.height = height
        self.thickness = thickness
        self.frame_width = frame_width
        self.glass_inset = glass_inset
        self.frame_bevel = frame_bevel
        self.segments = segments
        self.screws = screws
        self.vertices = []
        self.indices = []
        self.screw_positions = []
        self._generate_mesh()

    def _ellipse_points(self, w, h, z=0.0, seg=None):
        if seg is None:
            seg = self.segments
        return [
            [0.5*w*np.cos(theta), 0.5*h*np.sin(theta), z]
            for theta in np.linspace(0, 2*np.pi, seg, endpoint=False)
        ]

    def _generate_mesh(self):
        w, h, t, fw, gi, fb, seg = self.width, self.height, self.thickness, self.frame_width, self.glass_inset, self.frame_bevel, self.segments
        # Outer frame (front, back, and bevel)
        outer_front = self._ellipse_points(w, h, z=0.0)
        outer_bevel = self._ellipse_points(w-fb*2, h-fb*2, z=-fb)
        outer_back = self._ellipse_points(w, h, z=-t)
        # Inner frame (front, back, and bevel)
        inner_w = w - 2*fw
        inner_h = h - 2*fw
        inner_front = self._ellipse_points(inner_w, inner_h, z=0.0)
        inner_bevel = self._ellipse_points(inner_w+fb*2, inner_h+fb*2, z=-fb)
        inner_back = self._ellipse_points(inner_w, inner_h, z=-t)
        # Glass pane (inset, slightly smaller than inner frame)
        glass_w = inner_w - 0.01
        glass_h = inner_h - 0.01
        glass = self._ellipse_points(glass_w, glass_h, z=-gi)

        v = []
        v.extend(outer_front)   # 0 ... n-1
        v.extend(outer_bevel)   # n ... 2n-1
        v.extend(outer_back)    # 2n ... 3n-1
        v.extend(inner_front)   # 3n ... 4n-1
        v.extend(inner_bevel)   # 4n ... 5n-1
        v.extend(inner_back)    # 5n ... 6n-1
        v.extend(glass)         # 6n ... 7n-1
        n = len(outer_front)
        self.vertices = v
        idx = []
        # Frame front face (outer to inner)
        for i in range(n):
            idx.append([i, (i+1)%n, 3*n + (i+1)%n])
            idx.append([i, 3*n + (i+1)%n, 3*n + i])
        # Frame back face (outer to inner)
        for i in range(n):
            idx.append([2*n + i, 2*n + (i+1)%n, 5*n + (i+1)%n])
            idx.append([2*n + i, 5*n + (i+1)%n, 5*n + i])
        # Outer wall (front to back)
        for i in range(n):
            idx.append([i, (i+1)%n, 2*n + (i+1)%n])
            idx.append([i, 2*n + (i+1)%n, 2*n + i])
        # Inner wall (front to back)
        for i in range(n):
            idx.append([3*n + i, 3*n + (i+1)%n, 5*n + (i+1)%n])
            idx.append([3*n + i, 5*n + (i+1)%n, 5*n + i])
        # Bevels (outer and inner)
        for i in range(n):
            idx.append([i, n + i, n + (i+1)%n])
            idx.append([i, n + (i+1)%n, (i+1)%n])
            idx.append([3*n + i, 4*n + i, 4*n + (i+1)%n])
            idx.append([3*n + i, 4*n + (i+1)%n, 3*n + (i+1)%n])
        # Bevel to back (outer and inner)
        for i in range(n):
            idx.append([n + i, 2*n + i, 2*n + (i+1)%n])
            idx.append([n + i, 2*n + (i+1)%n, n + (i+1)%n])
            idx.append([4*n + i, 5*n + i, 5*n + (i+1)%n])
            idx.append([4*n + i, 5*n + (i+1)%n, 4*n + (i+1)%n])
        # Glass pane (fan from center)
        glass_center = [0.0, 0.0, -gi]
        self.vertices.append(glass_center)
        glass_center_idx = len(self.vertices) - 1
        for i in range(n):
            idx.append([glass_center_idx, 6*n + i, 6*n + (i+1)%n])
        # Mounting screws (vertices only, not faces)
        self.screw_positions = []
        for i in range(self.screws):
            theta = 2 * np.pi * i / self.screws
            x = 0.5 * (w + inner_w) * 0.5 * np.cos(theta)
            y = 0.5 * (h + inner_h) * 0.5 * np.sin(theta)
            z = 0.002
            self.screw_positions.append([x, y, z])
        self.indices = idx

    def to_dict(self):
        return {
            'mesh_vertices': self.vertices,
            'mesh_indices': self.indices,
            'screw_positions': self.screw_positions
        }
