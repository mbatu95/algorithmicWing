from fastapi import FastAPI
from pydantic import BaseModel
from wing import Wing
import numpy as np
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # veya ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WingParams(BaseModel):
    naca: str
    chord: float
    span: float
    points: int
    depth: float
    translateX: float = 0.0
    translateY: float = 0.0
    translateZ: float = 0.0

@app.post('/generate-wing')
async def generate_wing(params: WingParams):
    # Birinci kanat
    wing1 = Wing(
        naca=params.naca,
        chord=params.chord,
        span=params.span,
        points=params.points,
        depth=params.depth
    )
    mesh_vertices1, mesh_indices1 = wing1.extrude_mesh_with_indices()

    # İkinci kanat (aynı parametrelerle, X ekseninde +offset ile)
    offset_x = params.chord + 1.0  # Yan yana koymak için X ekseninde kaydırma
    wing2 = Wing(
        naca=params.naca,
        chord=params.chord,
        span=params.span,
        points=params.points,
        depth=params.depth
    )
    mesh_vertices2, mesh_indices2 = wing2.extrude_mesh_with_indices()
    mesh_vertices2 = np.array(mesh_vertices2)
    mesh_vertices2[:,0] += offset_x  # X ekseninde kaydır
    mesh_vertices2 = mesh_vertices2.tolist()

    # Meshleri birleştir
    mesh_vertices = mesh_vertices1 + mesh_vertices2
    # İkinci meshin indexlerini offsetle
    offset = len(mesh_vertices1)
    mesh_indices2_offset = [[i0+offset, i1+offset, i2+offset] for [i0,i1,i2] in mesh_indices2]
    mesh_indices = mesh_indices1 + mesh_indices2_offset

    # İsteğe bağlı mesh translate (her iki kanada uygula)
    if any([params.translateX, params.translateY, params.translateZ]):
        mesh_vertices = np.array(mesh_vertices)
        mesh_vertices += np.array([params.translateX, params.translateY, params.translateZ])
        mesh_vertices = mesh_vertices.tolist()

    return {
        'mesh_vertices': mesh_vertices,
        'mesh_indices': mesh_indices
    }
