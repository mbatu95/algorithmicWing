# AlgorithmicWing

A Python tool for designing aircraft with code. Generate 3D aircraft models (wings, fuselage, windows) programmatically and export them for 3D printing or analysis.

## What It Does

- **Generate aircraft components** using mathematical parameters
- **Create wings** with NACA airfoil profiles
- **Design fuselages** with customizable shapes
- **Add windows** with realistic frames
- **Export to STL** for 3D printing or CFD analysis

## Quick Start

### Installation

```bash
git clone <repository-url>
cd algorithmicWing

# Create virtual environment 
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn numpy
```

### Run the Application

**1. Start the Backend (Python/FastAPI):**
```bash
# Make sure virtual environment is activated first
uvicorn main:app --reload
```

**2. Open the Frontend (Web Interface):**
- local server: `python -m http.server 8001` then visit `http://localhost:8001/frontend/`

The 3D visualization will load and display the aircraft model with:
- Interactive 3D view (rotate, zoom, pan)
- Real-time aircraft generation
- Wing, fuselage, and window components

### View the API

You can also access the API directly:
- `http://localhost:8000/generate-wing` - Returns aircraft geometry as JSON
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)


## Dependencies

- FastAPI - Web server
- NumPy - Math operations
- Uvicorn - ASGI server

## License

Open source. Check repository for details.