# Algorithmic Wing - Local Development Guide

## Overview
This project generates 3D aircraft geometry (wings, fuselage, tail, windows) using Python FastAPI backend and Three.js frontend visualization.

## Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, etc.)

## Project Structure
```
algorithmicWing/
├── main.py              # FastAPI backend server
├── wing.py              # Wing geometry class
├── fuselage.py          # Fuselage geometry class
├── tail.py              # Tail geometry class
├── window.py            # Window geometry class
├── geometry.py          # Base geometry classes
├── geometry_utils.py    # Transformation utilities
└── frontend/
    ├── index.html       # Main HTML page
    └── wing_api_client.js  # Three.js visualization
```

## Running the Application

### Step 1: Start the Backend Server

Open a terminal and navigate to the project root:

```bash
cd /Users/muratbatuhangunaydin/projects/youtube/algorithmicWing
uvicorn main:app --reload
```

The FastAPI backend will start on: **http://127.0.0.1:8000**

- `main:app` refers to the `app` object in `main.py`
- `--reload` enables auto-reload on code changes (useful for development)

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
```

### Step 2: Start the Frontend Server

Open a **second terminal** and navigate to the frontend directory:

```bash
cd /Users/muratbatuhangunaydin/projects/youtube/algorithmicWing/frontend
python3 -m http.server 8080
```

The frontend HTTP server will start on: **http://localhost:8080**

You should see output like:
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### Step 3: Open in Browser

Open your web browser and navigate to:

```
http://localhost:8080
```

You should see the 3D visualization of the aircraft geometry with:
- Wings (left and right)
- Fuselage
- Tail (horizontal stabilizer)
- Windows

## API Endpoints

### GET /generate-wing
Returns JSON with all geometry data (vertices, indices, positions, colors, materials)

Example:
```
http://127.0.0.1:8000/generate-wing
```

Response format:
```json
{
  "geometries": [
    {
      "type": "wing",
      "mesh_vertices": [[x, y, z], ...],
      "mesh_indices": [[i0, i1, i2], ...],
      "position": [x, y, z],
      "color": "#b0c4de",
      "material": "metal"
    },
    ...
  ]
}
```

## Troubleshooting

### Port Already in Use
If you see `Address already in use` error:

**For backend (port 8000):**
```bash
lsof -ti:8000 | xargs kill -9
```

**For frontend (port 8080):**
```bash
lsof -ti:8080 | xargs kill -9
```

Then restart the servers.

### CORS Errors
If you see CORS errors in the browser console, make sure:
1. Backend is running on port 8000
2. Frontend is running on port 8080
3. CORS middleware is configured in `main.py` (already set to allow all origins with `"*"`)

### No Visualization Appears
1. Check browser console for errors (F12 or Cmd+Option+I)
2. Verify both servers are running (check terminals)
3. Make sure you're accessing `http://localhost:8080` (not `http://127.0.0.1:8080`)
4. Try hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows/Linux)

## Development Workflow

1. Make changes to Python backend files
2. Backend auto-reloads (if using `--reload` flag)
3. Refresh browser to see changes
4. Frontend changes (HTML/JS) only require browser refresh

## Stopping the Servers

To stop the servers, press `Ctrl+C` in each terminal window.

## Next Steps

- Modify wing parameters in `main.py`
- Adjust morphing parameters (taper, dihedral, sweep, thickness)
- Add more geometries or customize existing ones
- Export to STL for 3D printing (if STL export is implemented)

## Support

For issues or questions, check:
- Browser console (F12) for frontend errors
- Terminal output for backend errors
- Network tab (F12 > Network) to verify API requests
