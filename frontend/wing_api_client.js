// wing_api_client.js
// Fetches wing geometry from FastAPI backend and visualizes with Three.js

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

let scene, camera, renderer, controls;
let currentLift = 0.5;
let currentWingspan = 12.0;
let currentMission = null;

async function fetchWingData(lift = 0.5, wingspan = 12.0) {
    const response = await fetch(`http://127.0.0.1:8000/generate-wing?lift=${lift}&wingspan=${wingspan}`);
    return await response.json();
}

async function fetchMissions() {
    const response = await fetch('http://127.0.0.1:8000/missions');
    return await response.json();
}

async function fetchMissionWing(missionName) {
    const response = await fetch(`http://127.0.0.1:8000/mission/${missionName}`);
    return await response.json();
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
            ✈️ AIRCRAFT PARAMETERS
        </h3>
        <div id="info-content">Loading...</div>
    `;

    document.body.appendChild(panel);
}

function updateInfoPanel(data) {
    const wp = data.wing_parameters;
    const aero = data.aerodynamics;

    const content = document.getElementById('info-content');
    content.innerHTML = `
        <div style="margin-bottom: 15px;">
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">🔧 WING GEOMETRY</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>NACA Profile: <span style="color: #4CAF50">${wp.naca_profile}</span></div>
                <div>Root Chord: <span style="color: #4CAF50">${wp.chord_root.toFixed(2)} m</span></div>
                <div>Span: <span style="color: #4CAF50">${wp.span.toFixed(2)} m</span></div>
                <div>Wing Area: <span style="color: #4CAF50">${wp.wing_area_m2} m²</span></div>
                <div>Aspect Ratio: <span style="color: #4CAF50">${wp.aspect_ratio}</span></div>
                <div>Taper Ratio: <span style="color: #4CAF50">${wp.taper_ratio.toFixed(3)}</span></div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">📐 MORPHING PARAMETERS</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>Thickness Factor: <span style="color: #4CAF50">${wp.thickness_factor.toFixed(3)}</span></div>
                <div>Dihedral Angle: <span style="color: #4CAF50">${wp.dihedral_angle_deg.toFixed(1)}°</span></div>
                <div>Shift Amount: <span style="color: #4CAF50">${wp.shift_amount.toFixed(2)}</span></div>
                <div>Morph Start: <span style="color: #4CAF50">${(wp.morph_start * 100).toFixed(0)}%</span></div>
            </div>
        </div>
        
        <div>
            <div style="color: #FFD700; font-weight: bold; margin-bottom: 8px;">🌬️ AERODYNAMICS</div>
            <div style="line-height: 1.8; padding-left: 10px;">
                <div>C<sub>L</sub> (Lift): <span style="color: #4CAF50; font-weight: bold;">${aero.lift_coefficient.toFixed(3)}</span></div>
                <div>C<sub>Di</sub> (Drag): <span style="color: #FF6B6B">${aero.induced_drag_coefficient}</span></div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="color: #888; font-size: 11px; margin-bottom: 4px;">@ ${aero.example_speed_ms} m/s:</div>
                    <div>Lift Force: <span style="color: #4CAF50">${aero.example_lift_force_kgf} kgf</span></div>
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
    title.textContent = '🎮 FLIGHT CONTROLS';
    title.style.cssText = `
        margin: 0 0 15px 0;
        color: #4CAF50;
        font-family: 'Courier New', monospace;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 5px;
    `;

    // Lift slider section
    const liftLabel = document.createElement('label');
    liftLabel.textContent = 'Lift Coefficient (CL)';
    liftLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
    `;

    const liftSlider = document.createElement('input');
    liftSlider.type = 'range';
    liftSlider.min = '0';
    liftSlider.max = '1';
    liftSlider.step = '0.01';
    liftSlider.value = '0.5';
    liftSlider.style.cssText = `
        width: 100%;
        margin: 10px 0;
        accent-color: #4CAF50;
    `;

    const liftValueDisplay = document.createElement('div');
    liftValueDisplay.textContent = '0.500';
    liftValueDisplay.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 20px;
        color: #4CAF50;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
    `;

    const modeLabel = document.createElement('div');
    modeLabel.textContent = 'Mode: Cruise';
    modeLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 20px;
    `;

    // Wingspan slider section
    const wingspanLabel = document.createElement('label');
    wingspanLabel.textContent = 'Wingspan (m)';
    wingspanLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: white;
        display: block;
        margin-bottom: 10px;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
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
    wingspanTypeLabel.textContent = 'Type: Medium Transport';
    wingspanTypeLabel.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        text-align: center;
        margin-top: 5px;
    `;

    // Event listeners
    liftSlider.addEventListener('input', async (e) => {
        currentLift = parseFloat(e.target.value);
        liftValueDisplay.textContent = currentLift.toFixed(3);

        // Update mode label
        if (currentLift < 0.25) modeLabel.textContent = 'Mode: High Speed';
        else if (currentLift < 0.6) modeLabel.textContent = 'Mode: Cruise';
        else if (currentLift < 0.8) modeLabel.textContent = 'Mode: Takeoff';
        else modeLabel.textContent = 'Mode: Landing';

        // Fetch and update
        const data = await fetchWingData(currentLift, currentWingspan);
        await updateScene(data);
    });

    wingspanSlider.addEventListener('input', async (e) => {
        currentWingspan = parseFloat(e.target.value);
        wingspanValueDisplay.textContent = `${currentWingspan.toFixed(1)} m`;

        // Update type label
        if (currentWingspan < 8) wingspanTypeLabel.textContent = 'Type: Light Aircraft';
        else if (currentWingspan < 12) wingspanTypeLabel.textContent = 'Type: General Aviation';
        else if (currentWingspan < 15) wingspanTypeLabel.textContent = 'Type: Medium Transport';
        else if (currentWingspan < 18) wingspanTypeLabel.textContent = 'Type: Regional Airliner';
        else wingspanTypeLabel.textContent = 'Type: Wide-body Airliner';

        // Fetch and update
        const data = await fetchWingData(currentLift, currentWingspan);
        await updateScene(data);
    });

    container.appendChild(title);
    container.appendChild(liftLabel);
    container.appendChild(liftSlider);
    container.appendChild(liftValueDisplay);
    container.appendChild(modeLabel);
    container.appendChild(wingspanLabel);
    container.appendChild(wingspanSlider);
    container.appendChild(wingspanValueDisplay);
    container.appendChild(wingspanTypeLabel);
    document.body.appendChild(container);

    return { liftSlider, wingspanSlider };
}

async function createMissionSelector() {
    const container = document.createElement('div');
    container.style.cssText = `
        position: absolute;
        bottom: 20px;
        left: 20px;
        background: rgba(0, 0, 0, 0.9);
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        min-width: 280px;
        max-width: 350px;
    `;

    const title = document.createElement('h3');
    title.textContent = '🎯 MISSION PROFILES';
    title.style.cssText = `
        margin: 0 0 15px 0;
        color: #FF9800;
        font-family: 'Courier New', monospace;
        border-bottom: 2px solid #FF9800;
        padding-bottom: 5px;
    `;

    const description = document.createElement('div');
    description.style.cssText = `
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        margin-bottom: 15px;
        line-height: 1.5;
    `;
    description.textContent = 'Select a mission profile to automatically optimize wing design';

    container.appendChild(title);
    container.appendChild(description);

    // Fetch missions
    const missionsData = await fetchMissions();
    const missions = missionsData.missions;

    // Create mission buttons
    missions.forEach(mission => {
        const button = document.createElement('button');
        button.textContent = `${getMissionIcon(mission.name)} ${mission.display_name}`;
        button.style.cssText = `
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            background: rgba(255, 152, 0, 0.1);
            border: 1px solid #FF9800;
            border-radius: 5px;
            color: white;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        `;

        button.addEventListener('mouseenter', () => {
            button.style.background = 'rgba(255, 152, 0, 0.3)';
            button.style.transform = 'translateX(5px)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.background = 'rgba(255, 152, 0, 0.1)';
            button.style.transform = 'translateX(0)';
        });

        button.addEventListener('click', async () => {
            currentMission = mission.name;

            // Highlight selected button
            container.querySelectorAll('button').forEach(btn => {
                btn.style.background = 'rgba(255, 152, 0, 0.1)';
                btn.style.borderWidth = '1px';
            });
            button.style.background = 'rgba(255, 152, 0, 0.5)';
            button.style.borderWidth = '2px';

            // Fetch and apply mission wing
            const data = await fetchMissionWing(mission.name);

            // Update sliders to match mission parameters
            currentLift = data.aerodynamics.lift_coefficient;
            currentWingspan = data.wing_parameters.span;

            // Update scene
            await updateScene(data);

            // Show mission info
            showMissionInfo(data.mission);
        });

        container.appendChild(button);
    });

    document.body.appendChild(container);
}

function getMissionIcon(missionName) {
    const icons = {
        'endurance': '🛫',
        'speed': '⚡',
        'heavy_lift': '📦',
        'agile': '🎪',
        'cruise': '✈️',
        'stol': '🛬'
    };
    return icons[missionName] || '🔧';
}

function showMissionInfo(mission) {
    // Remove existing mission info if any
    const existing = document.getElementById('mission-info');
    if (existing) existing.remove();

    const info = document.createElement('div');
    info.id = 'mission-info';
    info.style.cssText = `
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: rgba(255, 152, 0, 0.95);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #FF9800;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        max-width: 300px;
        font-family: 'Courier New', monospace;
        color: white;
        animation: slideIn 0.3s ease;
    `;

    info.innerHTML = `
        <div style="font-size: 14px; font-weight: bold; margin-bottom: 10px;">
            ${getMissionIcon(mission.name)} ${mission.display_name.toUpperCase()}
        </div>
        <div style="font-size: 11px; line-height: 1.6; margin-bottom: 10px;">
            ${mission.description}
        </div>
        <div style="font-size: 10px; color: rgba(255,255,255,0.8); padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.3);">
            <strong>Examples:</strong><br>${mission.example_aircraft}
        </div>
        <div style="margin-top: 10px; font-size: 10px; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 5px;">
            <div>🎯 Lift Priority: ${(mission.weights.lift * 100).toFixed(0)}%</div>
            <div>💨 Drag Priority: ${(mission.weights.drag * 100).toFixed(0)}%</div>
            <div>⚖️ Stability: ${(mission.weights.stability * 100).toFixed(0)}%</div>
            <div>🎮 Maneuver: ${(mission.weights.maneuver * 100).toFixed(0)}%</div>
        </div>
        <button onclick="this.parentElement.remove()" style="
            margin-top: 10px;
            padding: 5px 10px;
            background: rgba(0,0,0,0.5);
            border: 1px solid white;
            border-radius: 3px;
            color: white;
            cursor: pointer;
            font-size: 10px;
        ">Close</button>
    `;

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(info);

    // Auto-close after 10 seconds
    setTimeout(() => {
        if (info.parentElement) info.remove();
    }, 10000);
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
    const data = await fetchWingData(currentLift, currentWingspan);

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
    await createMissionSelector();

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
