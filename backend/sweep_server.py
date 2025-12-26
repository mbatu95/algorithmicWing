from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sweep.sweep import sweep
from spline.bezier import bezier_curve

class SweepHandler(BaseHTTPRequestHandler):
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
        response = {'message': 'Sweep API running'}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/sweep':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            try:
                cross_section = np.array(data['cross_section'])
                
                # Check if control_points are provided (use Bezier)
                if 'control_points' in data:
                    control_points = np.array(data['control_points'])
                    num_points = data.get('num_points', 100)
                    path = bezier_curve(control_points, num_points)
                else:
                    # Use direct path
                    path = np.array(data['path'])
                
                vertices, faces = sweep(cross_section, path)
                
                response = {'vertices': vertices.tolist(), 'faces': faces.tolist()}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode())

if __name__ == '__main__':
    httpd = HTTPServer(('', 8001), SweepHandler)
    print('🚀 Sweep server: http://localhost:8001')
    httpd.serve_forever()
