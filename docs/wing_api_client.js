// wing_api_client.js
// Fetches wing geometry from FastAPI backend and visualizes with Three.js
// GitHub Pages compatible version with mock data fallback

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

let scene, camera, renderer, controls;
let currentWingspan = 12.0;
let currentRootChord = 3.0;
let currentNaca = '4656';
let currentDihedral = 5.0;
let currentTaperRatio = 0.5;
let currentShiftAmount = 1.0;
let useBackend = false; // GitHub Pages mode by default

// Check if backend is available
async function checkBackend() {
    try {
        const response = await fetch('http://127.0.0.1:8000/health', {
            method: 'GET',
            mode: 'cors',
            signal: AbortSignal.timeout(1000)
        });
        return response.ok;
    } catch {
        return false;
    }
}

// Generate mock wing data for GitHub Pages
function generateMockWingData(wingspan = 12.0, rootChord = 3.0, naca = '4656', dihedral = 5.0, taperRatio = 0.5, shiftAmount = 1.0) {
    const wingArea = wingspan * rootChord * (1 + taperRatio) / 2;
    const aspectRatio = (wingspan * wingspan) / wingArea;
    const dihedralRad = dihedral * Math.PI / 180;
    const effectiveSpan = wingspan * Math.cos(dihedralRad);
    const effectiveArea = wingArea * Math.cos(dihedralRad);

    // Generate simple wing mesh
    const segments = 20;
    const vertices = [];
    const indices = [];

    // Generate wing surface
    for (let i = 0; i <= segments; i++) {
        const t = i / segments;
        const y = wingspan / 2 * (t * 2 - 1);
        const chord = rootChord * (1 - (1 - taperRatio) * Math.abs(t * 2 - 1));
        const z = Math.abs(y) * Math.tan(dihedralRad);

        for (let j = 0; j <= segments; j++) {
            const s = j / segments;
            const x = (s - 0.5) * chord;
            const thickness = 0.12 * chord * (1 - Math.pow(2 * s - 1, 2)); // Approximate airfoil thickness

            vertices.push(x, y, z + thickness * shiftAmount);
        }
    }

    // Generate indices
    for (let i = 0; i < segments; i++) {
        for (let j = 0; j < segments; j++) {
            const a = i * (segments + 1) + j;
            const b = a + segments + 1;
            const c = a + 1;
            const d = b + 1;

            indices.push(a, b, c);
            indices.push(c, b, d);
        }
    }

    // Calculate aerodynamics
    const nacaDigits = naca.split('').map(Number);
    const maxCamber = nacaDigits[0] / 100;
    const baseCL = 0.3 + maxCamber * 10;
    const dihedralFactor = Math.cos(dihedralRad * 0.5);
    const effectiveCL = baseCL * dihedralFactor;
    const Cdi = (effectiveCL * effectiveCL) / (Math.PI * aspectRatio);

    const exampleSpeed = 50;
    const exampleAoA = 5;
    const density = 1.225;
    const liftForceN = 0.5 * density * exampleSpeed * exampleSpeed * effectiveArea * effectiveCL;
    const liftForceKgf = liftForceN / 9.81;

    return {
        wing_parameters: {
            naca_profile: naca,
            chord_root: rootChord,
            span: wingspan,
            effective_span: effectiveSpan,
            wing_area_m2: wingArea.toFixed(2),
            effective_wing_area_m2: effectiveArea,
            aspect_ratio: aspectRatio.toFixed(2),
            taper_ratio: taperRatio,
            thickness_factor: nacaDigits[2] * 0.01 + nacaDigits[3] * 0.001,
            dihedral_angle_deg: dihedral,
            shift_amount: shiftAmount,
            morph_start: 0.3
        },
        aerodynamics: {
            lift_coefficient: baseCL.toFixed(3),
            effective_lift_coefficient: effectiveCL,
            induced_drag_coefficient: Cdi.toFixed(4),
            dihedral_effect_factor: dihedralFactor.toFixed(3),
            example_speed_ms: exampleSpeed,
            example_aoa_deg: exampleAoA,
            example_lift_force_N: liftForceN.toFixed(1),
            example_lift_force_kgf: liftForceKgf.toFixed(1)
        },
        geometries: [
            {
                mesh_vertices: vertices,
                mesh_indices: indices,
                color: '#3A7BD5',
                material: 'plastic',
                position: [0, 0, 0]
            }
        ]
    };
}

async function fetchWingData(wingspan = 12.0, rootChord = 3.0, naca = '4656', dihedral = 5.0, taperRatio = 0.5, shiftAmount = 1.0) {
    console.log('Fetching wing data with:', { wingspan, rootChord, naca, dihedral, taperRatio, shiftAmount });

    if (useBackend) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/generate-wing?wingspan=${wingspan}&root_chord=${rootChord}&naca=${naca}&dihedral=${dihedral}&taper_ratio=${taperRatio}&shift_amount=${shiftAmount}`);
            const data = await response.json();
            console.log('Received wing data from backend:', data);
            return data;
        } catch (error) {
            console.warn('Backend not available, using mock data');
            useBackend = false;
        }
    }

    // Use mock data for GitHub Pages
    const data = generateMockWingData(wingspan, rootChord, naca, dihedral, taperRatio, shiftAmount);
    console.log('Generated mock wing data:', data);
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
        <div id="backend-status" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 10px; color: #888; text-align: center;">
            Mod: GitHub Pages (Demo)
        </div>
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
                <div>C<sub>L</sub> (Temel): <span style="color: #4CAF50">${aero.lift_coefficient}</span></div>
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

    // Update backend status
    const statusDiv = document.getElementById('backend-status');
    if (statusDiv) {
        statusDiv.textContent = useBackend ? 'Mod: Backend API' : 'Mod: GitHub Pages (Demo)';
        statusDiv.style.color = useBackend ? '#4CAF50' : '#FF9800';
    }
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
        max-height: 85vh;
        overflow-y: auto;
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
    dihedralSlider.min = '-20';
    dihedralSlider.max = '20';
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

    // Shift Amount slider section
    const shiftAmountLabel = document.createElement('label');
    shiftAmountLabel.textContent = 'Kayma Miktarı';
    shiftAmountLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
    `;

    const shiftAmountSlider = document.createElement('input');
    shiftAmountSlider.type = 'range';
    shiftAmountSlider.min = '0.0';
    shiftAmountSlider.max = '2.0';
    shiftAmountSlider.step = '0.1';
    shiftAmountSlider.value = '1.0';
    shiftAmountSlider.style.cssText = `
        width: 100%;
        margin: 10px 0;
        accent-color: #E91E63;
    `;

    const shiftAmountValueDisplay = document.createElement('div');
    shiftAmountValueDisplay.textContent = '1.0';
    shiftAmountValueDisplay.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 20px;
        color: #E91E63;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
    `;

    const shiftAmountInfo = document.createElement('div');
    shiftAmountInfo.textContent = 'Kanat kamber ayarı';
    shiftAmountInfo.style.cssText = `
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
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
        await updateScene(data);
    });

    rootChordInput.addEventListener('change', async (e) => {
        currentRootChord = parseFloat(e.target.value);
        if (currentRootChord < 1.0) currentRootChord = 1.0;
        if (currentRootChord > 10.0) currentRootChord = 10.0;
        rootChordInput.value = currentRootChord.toFixed(1);

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
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
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
        await updateScene(data);
    });

    dihedralSlider.addEventListener('input', async (e) => {
        currentDihedral = parseFloat(e.target.value);
        dihedralValueDisplay.textContent = `${currentDihedral.toFixed(1)}°`;

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
        await updateScene(data);
    });

    taperRatioSlider.addEventListener('input', async (e) => {
        currentTaperRatio = parseFloat(e.target.value);
        taperRatioValueDisplay.textContent = currentTaperRatio.toFixed(2);

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
        await updateScene(data);
    });

    shiftAmountSlider.addEventListener('input', async (e) => {
        currentShiftAmount = parseFloat(e.target.value);
        shiftAmountValueDisplay.textContent = currentShiftAmount.toFixed(1);

        // Fetch and update
        const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);
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
    container.appendChild(shiftAmountLabel);
    container.appendChild(shiftAmountSlider);
    container.appendChild(shiftAmountValueDisplay);
    container.appendChild(shiftAmountInfo);
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
        const vertices = new Float32Array(geomData.mesh_vertices);
        const indices = new Uint32Array(geomData.mesh_indices);

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
    // Hide loading indicator
    const loadingDiv = document.getElementById('loading');

    // Check if backend is available
    console.log('Checking backend availability...');
    useBackend = await checkBackend();
    console.log('Backend available:', useBackend);

    if (loadingDiv) {
        loadingDiv.textContent = useBackend ? 'Backend bağlandı...' : 'GitHub Pages modunda başlatılıyor...';
    }

    // Fetch initial data
    const data = await fetchWingData(currentWingspan, currentRootChord, currentNaca, currentDihedral, currentTaperRatio, currentShiftAmount);

    // Three.js setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x203040);

    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.001, 100);
    camera.position.set(0.5, 0.2, 30);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.body.style.margin = '0';
    document.body.appendChild(renderer.domElement);

    // HDR environment lighting (optional for GitHub Pages)
    const loader = new RGBELoader();
    loader.load(
        'assets/plains_sunset_4k.hdr',
        (texture) => {
            texture.mapping = THREE.EquirectangularReflectionMapping;
            scene.environment = texture;
            scene.background = texture;
        },
        undefined,
        (error) => {
            console.warn('HDR texture not found, using solid background');
            scene.background = new THREE.Color(0x203040);
        }
    );

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

    // Hide loading indicator
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }

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
