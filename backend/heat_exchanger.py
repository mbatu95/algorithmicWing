"""
Heat Exchanger Generator
Creates multiple tubes with different cross-sections and paths for heat exchanger visualization.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sweep.sweep import sweep
from spline.bezier import bezier_curve
from differentialgrowth.differentialgrowth import generate_differential_growth_profile


def generate_circular_profile(radius: float = 0.3, num_points: int = 30) -> np.ndarray:
    """Generate a simple circular cross-section."""
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x = np.cos(angles) * radius
    y = np.sin(angles) * radius
    return np.column_stack([x, y])


def generate_tube_path(tube_index: int, total_tubes: int, length: float = 20.0, num_points: int = 50, is_differential_growth: bool = False) -> np.ndarray:
    """
    Generate a U-shaped path for a single tube in the heat exchanger.
    Tubes are arranged in a circular pattern (filling a cylinder cross-section).
    Each tube goes forward, makes a U-turn, and comes back.
    
    Args:
        tube_index: Index of the current tube (0-based)
        total_tubes: Total number of tubes
        length: Length of the straight section
        num_points: Number of points along the path
        is_differential_growth: If True, increases spacing between tubes
        
    Returns:
        Nx3 array of path points
    """
    # Adjust spacing based on cross-section type
    base_ring_radius = 2.0 if is_differential_growth else 1.2  # More space for DG
    
    # Arrange tubes in circular pattern (like filling a cylinder)
    if total_tubes == 1:
        # Single tube in center
        x_pos = 0
        y_pos = 0
    else:
        # Distribute tubes in concentric circles
        # Determine which ring this tube belongs to
        tubes_in_rings = []
        ring = 0
        total_placed = 0
        
        # First ring: 1 tube in center (if total_tubes > 1, skip center for better distribution)
        if total_tubes <= 7:
            tubes_in_rings.append(total_tubes)
        else:
            # Multiple rings: 6 tubes per ring, increasing by 6 each ring
            ring_capacity = 6
            while total_placed < total_tubes:
                tubes_this_ring = min(ring_capacity * (ring + 1) if ring > 0 else 1, total_tubes - total_placed)
                tubes_in_rings.append(tubes_this_ring)
                total_placed += tubes_this_ring
                ring += 1
        
        # Find which ring this tube is in
        current_ring = 0
        tube_in_ring = tube_index
        for tubes_count in tubes_in_rings:
            if tube_in_ring < tubes_count:
                break
            tube_in_ring -= tubes_count
            current_ring += 1
        
        # Calculate position in circular pattern
        if current_ring == 0 and tubes_in_rings[0] == 1:
            # Center tube
            x_pos = 0
            y_pos = 0
        else:
            # Tubes in outer rings
            ring_radius = (current_ring + 1) * base_ring_radius
            angle = (tube_in_ring / tubes_in_rings[current_ring]) * 2 * np.pi
            x_pos = np.cos(angle) * ring_radius
            y_pos = np.sin(angle) * ring_radius
    
    # U-shaped path parameters
    u_radius = 2.5  # Radius of U-turn (slightly larger)
    straight_length = length
    
    # Control points for U-shaped Bezier curve
    control_points = [
        # Forward path (going in +Z direction)
        [x_pos, y_pos, 0],
        [x_pos, y_pos, straight_length / 3],
        [x_pos, y_pos, 2 * straight_length / 3],
        [x_pos, y_pos, straight_length],
        
        # U-turn (180 degree turn, moving outward in radial direction)
        [x_pos + u_radius * 0.5, y_pos, straight_length + u_radius * 0.5],
        [x_pos + u_radius, y_pos, straight_length + u_radius],
        [x_pos + u_radius * 1.5, y_pos, straight_length + u_radius * 0.5],
        [x_pos + 2 * u_radius, y_pos, straight_length],
        
        # Return path (going back in -Z direction)
        [x_pos + 2 * u_radius, y_pos, 2 * straight_length / 3],
        [x_pos + 2 * u_radius, y_pos, straight_length / 3],
        [x_pos + 2 * u_radius, y_pos, 0]
    ]
    
    return bezier_curve(np.array(control_points), num_points)


class HeatExchangerHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {'message': 'Heat Exchanger API running'}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            try:
                num_tubes = data.get('num_tubes', 3)
                tube_length = data.get('tube_length', 20.0)  # Longer tubes
                path_points = data.get('path_points', 50)
                
                # Get tube configurations
                tubes_config = data.get('tubes', [])
                
                # Check if using differential growth to adjust spacing
                is_dg = tubes_config[0].get('type') == 'differential_growth' if tubes_config else False
                
                all_tubes = []
                
                for i in range(num_tubes):
                    # Get configuration for this tube
                    if i < len(tubes_config):
                        tube_config = tubes_config[i]
                    else:
                        # Default configuration
                        tube_config = {
                            'type': 'circle',
                            'radius': 0.15  # Thinner default
                        }
                    
                    # Generate cross-section
                    if tube_config.get('type') == 'differential_growth':
                        dg_radius = tube_config.get('radius', 0.2)  # Smaller default for DG
                        dg_iterations = tube_config.get('iterations', 50)
                        dg_initial_points = tube_config.get('initial_points', 12)
                        
                        cross_section = generate_differential_growth_profile(
                            initial_radius=dg_radius,
                            num_initial_points=dg_initial_points,
                            iterations=dg_iterations
                        )
                    else:  # circle
                        radius = tube_config.get('radius', 0.15)  # Thinner
                        cross_section = generate_circular_profile(radius)
                    
                    # Generate path for this tube with spacing adjustment
                    path = generate_tube_path(i, num_tubes, tube_length, path_points, is_dg)
                    
                    # Create the tube geometry
                    vertices, faces = sweep(cross_section, path)
                    
                    all_tubes.append({
                        'vertices': vertices.tolist(),
                        'faces': faces.tolist(),
                        'type': tube_config.get('type', 'circle')
                    })
                
                response = {
                    'tubes': all_tubes,
                    'num_tubes': num_tubes
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                import traceback
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                self.wfile.write(json.dumps(error_response).encode())


if __name__ == '__main__':
    httpd = HTTPServer(('', 8002), HeatExchangerHandler)
    print('🔥 Heat Exchanger server: http://localhost:8002')
    print('📊 POST to /generate with tube configurations')
    httpd.serve_forever()
