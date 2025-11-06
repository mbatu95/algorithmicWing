// wing_api_client.js
// Fetches wing geometry from FastAPI backend and visualizes with Three.js

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';


async function fetchWingData(params) {
    const response = await fetch('http://127.0.0.1:8000/generate-wing');
    return await response.json();
}



function createWingSurfaceMesh(meshVertices, meshIndices) {
    // meshVertices: Array of [x, y, z] points
    // meshIndices: Array of [i0, i1, i2] triangle indices
    const geometry = new THREE.BufferGeometry();
    const vertices = new Float32Array(meshVertices.flat());
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    // Flatten indices for Three.js
    const flatIndices = new Uint32Array(meshIndices.flat());
    geometry.setIndex(new THREE.BufferAttribute(flatIndices, 1));
    geometry.computeVertexNormals();
    const material = new THREE.MeshStandardMaterial({
        color: 0xb0c4de,
        metalness: 0.9,
        roughness: 0.25,
        envMapIntensity: 1.0,
        clearcoat: 0.6,
        clearcoatRoughness: 0.1,
        side: THREE.DoubleSide,
    });
    return new THREE.Mesh(geometry, material);
}


// Main visualization function
async function visualizeWing() {
    // Parameters are now set in Python backend, not here
    const data = await fetchWingData();
    // Three.js setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x203040);
    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.001, 100);
    camera.position.set(0.5, 0.2, 30);
    camera.lookAt(0, 0, 0);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.style.margin = '0';
    document.body.appendChild(renderer.domElement);

    // HDR environment lighting
    const loader = new RGBELoader();
    loader.load('assets/plains_sunset_4k.hdr', (texture) => {
        texture.mapping = THREE.EquirectangularReflectionMapping;
        scene.environment = texture;
        scene.background = texture;
    });

    // controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 0, 0);

    // lights
    const hemi = new THREE.HemisphereLight(0xbbd6ff, 0x202025, 1.4);
    scene.add(hemi);
    const dir = new THREE.DirectionalLight(0xffffff, 3);
    dir.position.set(2, 2, 1);
    scene.add(dir);

    // Add all geometries from backend
    function previewGeometry(geometry) {
        const meshVertices = geometry.mesh_vertices;
        const meshIndices = geometry.mesh_indices;
        const color = geometry.color || 0xb0c4de;
        const position = geometry.position || [0, 0, 0];
        const material = new THREE.MeshStandardMaterial({
            color: color,
            metalness: 0.9,
            roughness: 0.25,
            envMapIntensity: 1.0,
            clearcoat: 0.6,
            clearcoatRoughness: 0.1,
            side: THREE.DoubleSide,
        });
        const mesh = createWingSurfaceMesh(meshVertices, meshIndices);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.position.set(position[0], position[1], position[2]);
        scene.add(mesh);
    }

    if (data.geometries && Array.isArray(data.geometries)) {
        for (const geometry of data.geometries) {
            previewGeometry(geometry);
        }
    }

    // Axes helper
    const axes = new THREE.AxesHelper(2);

    function makeAxisLabel(text, color) {
        const size = 128;
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = size;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, size, size);
        ctx.font = 'bold 96px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        // outline for contrast
        ctx.lineWidth = 8;
        ctx.strokeStyle = 'rgba(0,0,0,0.7)';
        ctx.strokeText(text, size / 2, size / 2 + 6);
        ctx.fillStyle = color || '#ffffff';
        ctx.fillText(text, size / 2, size / 2 + 6);
        const tex = new THREE.CanvasTexture(canvas);
        tex.needsUpdate = true;
        const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(0.6, 0.6, 1);
        return sprite;
    }

    const labelX = makeAxisLabel('X', '#ff0000');
    labelX.position.set(2.2, 0, 0);
    const labelY = makeAxisLabel('Y', '#00ff00');
    labelY.position.set(0, 2.2, 0);
    const labelZ = makeAxisLabel('Z', '#0000ff');
    labelZ.position.set(0, 0, 2.2);

    scene.add(labelX, labelY, labelZ);
    scene.add(axes);
    // ...existing code for labeled axes...

    // // Grid helper
    // const grid = new THREE.GridHelper(10, 20, 0x222222, 0x111111);
    // grid.rotation.x = Math.PI / 2;
    // scene.add(grid);

    // Responsive resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });


    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}

// Run visualization on page load
window.addEventListener('DOMContentLoaded', visualizeWing);
