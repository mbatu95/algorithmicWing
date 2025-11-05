import numpy as np

def mesh_to_stl(mesh, filename, ascii=True):
    """
    Export a Mesh object to an STL file (ASCII or binary).
    mesh: Mesh object with .vertices and .indices
    filename: output STL file path
    ascii: if True, writes ASCII STL; if False, writes binary STL
    """
    vertices = np.array(mesh.vertices)
    indices = np.array(mesh.indices)
    if ascii:
        with open(filename, 'w') as f:
            f.write('solid mesh\n')
            for tri in indices:
                v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
                # Calculate normal
                normal = np.cross(v1 - v0, v2 - v0)
                norm = np.linalg.norm(normal)
                if norm != 0:
                    normal = normal / norm
                else:
                    normal = np.array([0.0, 0.0, 0.0])
                f.write(f'  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n')
                f.write('    outer loop\n')
                f.write(f'      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n')
                f.write(f'      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n')
                f.write(f'      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n')
                f.write('    endloop\n')
                f.write('  endfacet\n')
            f.write('endsolid mesh\n')
    else:
        import struct
        with open(filename, 'wb') as f:
            f.write(b' ' * 80)  # header
            f.write(struct.pack('<I', len(indices)))
            for tri in indices:
                v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
                normal = np.cross(v1 - v0, v2 - v0)
                norm = np.linalg.norm(normal)
                if norm != 0:
                    normal = normal / norm
                else:
                    normal = np.array([0.0, 0.0, 0.0])
                f.write(struct.pack('<3f', *normal))
                f.write(struct.pack('<3f', *v0))
                f.write(struct.pack('<3f', *v1))
                f.write(struct.pack('<3f', *v2))
                f.write(struct.pack('<H', 0))  # attribute byte count
