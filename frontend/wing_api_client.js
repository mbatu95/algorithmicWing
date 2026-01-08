// wing_api_client.js
// Fetches wing geometry from FastAPI backend and visualizes with Three.js

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

let scene, camera, renderer, controls;
let currentWingspan = 12.0;
let currentRootChord = 3.0;
let currentNaca = '4656';
let currentDihedral = 5.0;
let currentTaperRatio = 0.5;

async function fetchWingData(wingspan = 12.0, rootChord = 3.0, naca = '4656', dihedral = 5.0, taperRatio = 0.5) {
    console.log('Fetching wing data with:', { wingspan, rootChord, naca, dihedral, taperRatio });
    const response = await fetch(`http://127.0.0.1:8000/generate-wing?wingspan=${wingspan}&root_chord=${rootChord}&naca=${naca}&dihedral=${dihedral}&taper_ratio=${taperRatio}`);
    const data = await response.json();
    console.log('Received wing data:', data);
    return data;
}

function createInfoPanel() {
    const panel = document.createElement('div');
    panel.id = 'info-panel';
    panel.style.cssText = `
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.85);
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        min-width: 300px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 1000;
    `;

    panel.innerHTML = `
        <h3 style="margin: 0 0 15px 0; color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">
            ✈️ UÇAK PARAMETRELERİ
        </h3>
        <div id="info-content">Yükleniyor...</div>
    `;

    document.body.appendChild(panel);
}

function updateInfoPanel(data) {
    const wp = data.wing_parameters;
    const aero = data.aerodynamics;

    const content = document.getElementById('info-content');
    content.innerHTML = `
        <div style="margin-bottom: 15px;">
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">🔧 KANAT GEOMETRİSİ</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>NACA Profili: <span style="color: #4CAF50">${wp.naca_profile}</span></div>
                <div>Kök Veter: <span style="color: #4CAF50">${wp.chord_root.toFixed(2)} m</span></div>
                <div>Açıklık: <span style="color: #4CAF50">${wp.span.toFixed(2)} m</span></div>
                ${wp.effective_span ? `<div>Efektif Açıklık: <span style="color: #2196F3">${wp.effective_span.toFixed(2)} m</span></div>` : ''}
                <div>Kanat Alanı: <span style="color: #4CAF50">${wp.wing_area_m2} m²</span></div>
                ${wp.effective_wing_area_m2 ? `<div>Efektif Alan: <span style="color: #2196F3">${wp.effective_wing_area_m2.toFixed(2)} m²</span></div>` : ''}
                <div>En-Boy Oranı: <span style="color: #4CAF50">${wp.aspect_ratio}</span></div>
                <div>Daraltma Oranı: <span style="color: #4CAF50">${wp.taper_ratio.toFixed(3)}</span></div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">📐 MORFOLOJ PARAMETRELERİ</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>Kalınlık Faktörü: <span style="color: #4CAF50">${wp.thickness_factor.toFixed(3)}</span></div>
                <div>Dihedral Açısı: <span style="color: #4CAF50">${wp.dihedral_angle_deg.toFixed(1)}°</span></div>
                <div>Kayma Miktarı: <span style="color: #4CAF50">${wp.shift_amount.toFixed(2)}</span></div>
                <div>Morfoloj Başlangıcı: <span style="color: #4CAF50">${(wp.morph_start * 100).toFixed(0)}%</span></div>
            </div>
        </div>
        
        <div>
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">🌬️ AERODİNAMİK</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>C<sub>L</sub> (Temel): <span style="color: #4CAF50">${aero.lift_coefficient.toFixed(3)}</span></div>
                ${aero.effective_lift_coefficient ? `<div>C<sub>L</sub> (Efektif): <span style="color: #2196F3; font-weight: bold;">${aero.effective_lift_coefficient.toFixed(3)}</span></div>` : ''}
                <div>C<sub>Di</sub> (Sürükleme): <span style="color: #FF6B6B">${aero.induced_drag_coefficient}</span></div>
                ${aero.dihedral_effect_factor ? `<div style="font-size: 11px; color: #888;">Dihedral faktörü: ${aero.dihedral_effect_factor}</div>` : ''}
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="color: #888; font-size: 11px; margin-bottom: 4px;">@ ${aero.example_speed_ms} m/s, Hücum Açısı ${aero.example_aoa_deg || 5}°:</div>
                    <div>Kaldırma Kuvveti: <span style="color: #4CAF50">${aero.example_lift_force_kgf} kgf</span></div>
                    <div style="font-size: 11px; color: #888;">(${aero.example_lift_force_N} N)</div>
                </div>
            </div>
        </div>
    `;
}

function createLiftSlider() {
    const container = document.createElement('div');
    container.style.cssText = `
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(0, 0, 0, 0.85);
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        min-width: 280px;
    `;

    const title = document.createElement('h3');
    title.textContent = '🎮 UÇUŞ KONTROL PANELİ';
    title.style.cssText = `
        margin: 0 0 15px 0;
        color: #4CAF50;
        font-family: 'Courier New', monospace;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 5px;
    `;

    // Wingspan slider section
    const wingspanLabel = document.createElement('label');
    wingspanLabel.textContent = 'Kanat Açıklığı (m)';
    wingspanLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
    `;

    const wingspanSlider = document.createElement('input');
    wingspanSlider.type = 'range';
    wingspanSlider.min = '6';
    wingspanSlider.max = '20';
    wingspanSlider.step = '0.5';
    wingspanSlider.value = '12';
    wingspanSlider.style.cssText = `
        width: 100%;
        margin: 10px 0;
        accent-color: #2196F3;
    `;

    const wingspanValueDisplay = document.createElement('div');
    wingspanValueDisplay.textContent = '12.0 m';
    wingspanValueDisplay.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 20px;
        color: #2196F3;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
    `;

    const wingspanTypeLabel = document.createElement('div');
    wingspanTypeLabel.textContent = 'Tip: Orta Ölçekli Taşıma';
    wingspanTypeLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        text-align: center;
        margin-top: 5px;
    `;

    // Root Chord input section
    const rootChordLabel = document.createElement('label');
    rootChordLabel.textContent = 'Kök Veter (m)';
    rootChordLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
    `;

    const rootChordInput = document.createElement('input');
    rootChordInput.type = 'number';
    rootChordInput.min = '1.0';
    rootChordInput.max = '10.0';
    rootChordInput.step = '0.1';
    rootChordInput.value = '3.0';
    rootChordInput.style.cssText = `
        width: 100%;
        padding: 8px;
        margin: 10px 0;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 5px;
        color: #FF9800;
        font-family: 'Courier New', monospace;
        font-size: 16px;
        font-weight: bold;
    `;

    // NACA input section
    const nacaLabel = document.createElement('label');
    nacaLabel.textContent = 'NACA Kanat Profili';
    nacaLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
    `;

    const nacaInput = document.createElement('input');
    nacaInput.type = 'text';
    nacaInput.maxLength = '4';
    nacaInput.value = '4656';
    nacaInput.placeholder = 'e.g., 4656';
    nacaInput.style.cssText = `
        width: 100%;
        padding: 8px;
        margin: 10px 0;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 5px;
        color: #9C27B0;
        font-family: 'Courier New', monospace;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
    `;

    // Dihedral Angle slider section
    const dihedralLabel = document.createElement('label');
    dihedralLabel.textContent = 'Dihedral Açısı (°)';
    dihedralLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
    `;

    const dihedralSlider = document.createElement('input');
    dihedralSlider.type = 'range';
    dihedralSlider.min = '0';
    dihedralSlider.max = '15';
    dihedralSlider.step = '0.5';
    dihedralSlider.value = '5';
    dihedralSlider.style.cssText = `
        width: 100%;
        margin: 10px 0;
        accent-color: #FF5722;
    `;

    const dihedralValueDisplay = document.createElement('div');
    dihedralValueDisplay.textContent = '5.0°';
    dihedralValueDisplay.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 20px;
        color: #FF5722;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
    `;

    // Taper Ratio slider section
    const taperRatioLabel = document.createElement('label');
    taperRatioLabel.textContent = 'Daraltma Oranı';
    taperRatioLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
    `;

    const taperRatioSlider = document.createElement('input');
    taperRatioSlider.type = 'range';
    taperRatioSlider.min = '0.3';
    taperRatioSlider.max = '1.0';
    taperRatioSlider.step = '0.05';
    taperRatioSlider.value = '0.5';
    taperRatioSlider.style.cssText = `
        width: 100%;
        margin: 10px 0;
        accent-color: #00BCD4;
    `;

    const taperRatioValueDisplay = document.createElement('div');
    taperRatioValueDisplay.textContent = '0.50';
    taperRatioValueDisplay.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 20px;
        color: #00BCD4;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
    `;

    const taperRatioInfo = document.createElement('div');
    taperRatioInfo.textContent = 'Uç veter / Kök veter';
    taperRatioInfo.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        text-align: center;
        margin-top: 5px;
    `;

    // Event listeners
    wingspanSlider.addEventListener('input', async (e) => {
        currentWingspan = parseFloat(e.target.value);
        wingspanValueDisplay.textContent = `${currentWingspan.toFixed(1)} m`;

        // Update type label
        if (currentWingspan < 8) wingspanTypeLabel.textContent = 'Tip: Hafif Uçak';
        else if (currentWingspan < 12) wingspanTypeLabel.textContent = 'Tip: Genel Havacılık';
        else if (currentWingspan < 15) wingspanTypeLabel.textContent = 'Tip: Orta Ölçekli Taşıma';
        else if (currentWingspan < 18) wingspanTypeLabel.textContent = 'Tip: Bölgesel Hat Uçağı';
        else wingspanTypeLabel.textContent = 'Tip: Geniş Gövdeli Uçak';

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);
        await updateScene(data);
    });

    rootChordInput.addEventListener('change', async (e) => {
        currentRootChord = parseFloat(e.target.value);
        if (currentRootChord < 1.0) currentRootChord = 1.0;
        if (currentRootChord > 10.0) currentRootChord = 10.0;
        rootChordInput.value = currentRootChord.toFixed(1);

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);
        await updateScene(data);
    });

    nacaInput.addEventListener('change', async (e) => {
        currentNaca = e.target.value;
        console.log('NACA input changed to:', currentNaca);
        // Validate NACA format (should be 4 digits)
        if (!/^\d{4}$/.test(currentNaca)) {
            alert('NACA kanat profili 4 rakamdan oluşmalıdır (örn: 4656)');
            nacaInput.value = currentNaca = '4656';
            return;
        }

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);
        await updateScene(data);
    });

    dihedralSlider.addEventListener('input', async (e) => {
        currentDihedral = parseFloat(e.target.value);
        dihedralValueDisplay.textContent = `${currentDihedral.toFixed(1)}°`;

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);
        await updateScene(data);
    });

    taperRatioSlider.addEventListener('input', async (e) => {
        currentTaperRatio = parseFloat(e.target.value);
        taperRatioValueDisplay.textContent = currentTaperRatio.toFixed(2);

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);
        await updateScene(data);
    });

    container.appendChild(title);
    container.appendChild(wingspanLabel);
    container.appendChild(wingspanSlider);
    container.appendChild(wingspanValueDisplay);
    container.appendChild(wingspanTypeLabel);
    container.appendChild(rootChordLabel);
    container.appendChild(rootChordInput);
    container.appendChild(nacaLabel);
    container.appendChild(nacaInput);
    container.appendChild(dihedralLabel);
    container.appendChild(dihedralSlider);
    container.appendChild(dihedralValueDisplay);
    container.appendChild(taperRatioLabel);
    container.appendChild(taperRatioSlider);
    container.appendChild(taperRatioValueDisplay);
    container.appendChild(taperRatioInfo);
    document.body.appendChild(container);
}

async function updateScene(data) {
    // Clear existing meshes except lights
    const objectsToRemove = scene.children.filter(child =>
        child instanceof THREE.Mesh ||
        child instanceof THREE.AxesHelper ||
        child instanceof THREE.Sprite
    );
    objectsToRemove.forEach(obj => scene.remove(obj));

    // Add geometries
    data.geometries.forEach(geomData => {
        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(geomData.mesh_vertices.flat());
        const indices = new Uint32Array(geomData.mesh_indices.flat());

        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        geometry.computeVertexNormals();

        const material = new THREE.MeshStandardMaterial({
            color: geomData.color,
            metalness: geomData.material === 'metal' ? 0.7 : 0.2,
            roughness: 0.3,
            side: THREE.DoubleSide
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(...geomData.position);
        scene.add(mesh);
    });

    // Re-add axes
    const axes = new THREE.AxesHelper(2);
    scene.add(axes);

    // Update info panel
    updateInfoPanel(data);
}

// Main visualization function
async function init() {
    // Fetch initial data
    const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio);

    // Three.js setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x203040);

    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.001, 100);
    camera.position.set(0.5, 0.2, 30);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true });
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
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 0, 0);

    // lights
    const hemi = new THREE.HemisphereLight(0xbbd6ff, 0x202025, 1.4);
    scene.add(hemi);
    const dir = new THREE.DirectionalLight(0xffffff, 3);
    dir.position.set(2, 2, 1);
    scene.add(dir);

    // Create UI panels
    createInfoPanel();
    createLiftSlider();

    // Add initial geometries
    await updateScene(data);

    // Responsive resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}

// Run visualization on page load
window.addEventListener('DOMContentLoaded', init);
