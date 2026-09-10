"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { useLanguage } from "@/context/LanguageContext";
import { Play, Pause, RotateCcw, Sparkles, Compass, Eye } from "lucide-react";

interface SkillNodeData {
  name: string;
  domain: string;
  color: number;
  radius: number;
  phi: number;
  theta: number;
  level: number;
  required: number;
}

const SKILLS_DATA: SkillNodeData[] = [
  { name: "Survey Design", domain: "Statistical", color: 0x0284c7, radius: 7.2, phi: 0.6, theta: 0.3, level: 3, required: 4 },
  { name: "Sampling", domain: "Statistical", color: 0x0284c7, radius: 6.6, phi: 1.3, theta: 0.9, level: 2, required: 4 },
  { name: "Statistical Analysis", domain: "Statistical", color: 0x0369a1, radius: 7.5, phi: 1.9, theta: 1.5, level: 4, required: 4 },
  { name: "Python", domain: "Technical", color: 0x4f46e5, radius: 6.9, phi: 2.3, theta: 2.7, level: 2, required: 3 },
  { name: "SQL", domain: "Technical", color: 0x6366f1, radius: 6.3, phi: 0.9, theta: 3.6, level: 3, required: 4 },
  { name: "AI/ML", domain: "Technical", color: 0x7c3aed, radius: 7.6, phi: 2.6, theta: 4.3, level: 1, required: 3 },
  { name: "Data Quality", domain: "Domain", color: 0xd97706, radius: 6.5, phi: 1.6, theta: 5.0, level: 3, required: 4 },
  { name: "National Accounts", domain: "Domain", color: 0xd97706, radius: 7.1, phi: 2.9, theta: 5.6, level: 2, required: 3 },
  { name: "Metadata Standards", domain: "Domain", color: 0xb45309, radius: 6.7, phi: 0.5, theta: 5.3, level: 2, required: 3 },
  { name: "Communication", domain: "Soft Skills", color: 0x059669, radius: 6.1, phi: 2.0, theta: 6.2, level: 4, required: 4 },
  { name: "Ethics", domain: "Soft Skills", color: 0x059669, radius: 6.9, phi: 2.8, theta: 0.8, level: 3, required: 3 },
];

interface ThreeSkillGalaxyProps {
  activeSkill?: string;
  onSelectSkill?: (skillName: string) => void;
}

export default function ThreeSkillGalaxy({
  activeSkill = "Statistical Analysis",
  onSelectSkill,
}: ThreeSkillGalaxyProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { t } = useLanguage();
  const [isRotating, setIsRotating] = useState<boolean>(true);
  const [selectedDomain, setSelectedDomain] = useState<string>("all");
  const [hoveredNode, setHoveredNode] = useState<{
    name: string;
    domain: string;
    level: number;
    required: number;
    x: number;
    y: number;
  } | null>(null);

  const resetCameraRef = useRef<() => void>(() => {});
  const isRotatingRef = useRef<boolean>(true);
  isRotatingRef.current = isRotating;

  const selectedDomainRef = useRef<string>("all");
  selectedDomainRef.current = selectedDomain;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Scene setup
    const scene = new THREE.Scene();
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 420;

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    camera.position.set(0, 1.5, 18);

    const defaultCamPos = new THREE.Vector3(0, 1.5, 18);
    const targetCamPos = defaultCamPos.clone();
    const defaultLookAt = new THREE.Vector3(0, 0, 0);
    const currentLookAt = defaultLookAt.clone();
    const targetLookAt = defaultLookAt.clone();

    resetCameraRef.current = () => {
      targetCamPos.copy(defaultCamPos);
      targetLookAt.copy(defaultLookAt);
    };

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.appendChild(renderer.domElement);

    // Dynamic Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
    dirLight.position.set(12, 18, 14);
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0x6366f1, 2.5, 20);
    pointLight.position.set(0, 0, 0);
    scene.add(pointLight);

    const group = new THREE.Group();
    scene.add(group);

    // Central Core Mesh (Outer Wireframe Icosahedron)
    const coreGeo = new THREE.IcosahedronGeometry(2.2, 1);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x4f46e5,
      wireframe: true,
      transparent: true,
      opacity: 0.28,
      roughness: 0.3,
      metalness: 0.7,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    group.add(coreMesh);

    // Inner Luminous Core
    const innerGeo = new THREE.SphereGeometry(1.2, 24, 24);
    const innerMat = new THREE.MeshStandardMaterial({
      color: 0x818cf8,
      emissive: 0x4338ca,
      emissiveIntensity: 0.6,
      roughness: 0.2,
      metalness: 0.5,
      transparent: true,
      opacity: 0.85,
    });
    const innerSphere = new THREE.Mesh(innerGeo, innerMat);
    group.add(innerSphere);

    // Core Gyro Ring
    const gyroRingGeo = new THREE.TorusGeometry(2.6, 0.04, 16, 64);
    const gyroRingMat = new THREE.MeshBasicMaterial({
      color: 0xa5b4fc,
      transparent: true,
      opacity: 0.35,
    });
    const gyroRing = new THREE.Mesh(gyroRingGeo, gyroRingMat);
    group.add(gyroRing);

    // Create Nodes & Lines
    const nodeMeshes: THREE.Mesh[] = [];
    const ringMeshes: THREE.Mesh[] = [];
    const nodePositions: THREE.Vector3[] = [];
    let activeAuraMesh: THREE.Mesh | null = null;

    SKILLS_DATA.forEach((skill) => {
      const x = skill.radius * Math.sin(skill.phi) * Math.cos(skill.theta);
      const y = skill.radius * Math.cos(skill.phi);
      const z = skill.radius * Math.sin(skill.phi) * Math.sin(skill.theta);
      const pos = new THREE.Vector3(x, y, z);
      nodePositions.push(pos);

      const isCurrent = skill.name.toLowerCase() === activeSkill.toLowerCase();

      // Physical Spherical Node
      const nodeGeo = new THREE.SphereGeometry(isCurrent ? 0.68 : 0.48, 32, 32);
      const nodeMat = new THREE.MeshStandardMaterial({
        color: skill.color,
        emissive: isCurrent ? skill.color : 0x000000,
        emissiveIntensity: isCurrent ? 0.45 : 0.0,
        roughness: 0.25,
        metalness: 0.35,
        transparent: true,
        opacity: 0.95,
      });
      const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
      nodeMesh.position.copy(pos);
      nodeMesh.userData = { ...skill };
      group.add(nodeMesh);
      nodeMeshes.push(nodeMesh);

      // Orbital Halo Ring
      const ringGeo = new THREE.RingGeometry(0.55, 0.72, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: skill.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: isCurrent ? 0.75 : 0.28,
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.copy(pos);
      ringMesh.lookAt(0, 0, 0);
      group.add(ringMesh);
      ringMeshes.push(ringMesh);

      if (isCurrent) {
        // Pulsing Aura Ring around active node
        const auraGeo = new THREE.RingGeometry(0.8, 1.05, 32);
        const auraMat = new THREE.MeshBasicMaterial({
          color: 0x4f46e5,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.5,
        });
        activeAuraMesh = new THREE.Mesh(auraGeo, auraMat);
        activeAuraMesh.position.copy(pos);
        activeAuraMesh.lookAt(0, 0, 0);
        group.add(activeAuraMesh);
      }
    });

    // Inter-node Constellation Connecting Lines (Domain based)
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0xc7d2fe,
      transparent: true,
      opacity: 0.35,
    });

    for (let i = 0; i < nodePositions.length; i++) {
      for (let j = i + 1; j < nodePositions.length; j++) {
        const dist = nodePositions[i].distanceTo(nodePositions[j]);
        const sameDomain = SKILLS_DATA[i].domain === SKILLS_DATA[j].domain;
        if (dist < 6.8 || (sameDomain && dist < 8.5)) {
          const lineGeo = new THREE.BufferGeometry().setFromPoints([
            nodePositions[i],
            nodePositions[j],
          ]);
          const lineMat = sameDomain
            ? new THREE.LineBasicMaterial({
                color: SKILLS_DATA[i].color,
                transparent: true,
                opacity: 0.38,
              })
            : lineMaterial;
          const line = new THREE.Line(lineGeo, lineMat);
          group.add(line);
        }
      }
    }

    // Radial spokes connecting core to outer nodes
    nodePositions.forEach((pos, idx) => {
      const spokeGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        pos,
      ]);
      const spokeMat = new THREE.LineBasicMaterial({
        color: SKILLS_DATA[idx].color,
        transparent: true,
        opacity: 0.18,
      });
      group.add(new THREE.Line(spokeGeo, spokeMat));
    });

    // Ambient Stardust Particle Field (200 particles)
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      const radius = 8 + Math.random() * 12;
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      positions[i] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i + 1] = radius * Math.cos(phi);
      positions[i + 2] = radius * Math.sin(phi) * Math.sin(theta);
    }
    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x818cf8,
      size: 0.12,
      transparent: true,
      opacity: 0.45,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // Raycasting & Mouse Drag Controls
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let dragVelocityX = 0;
    let dragVelocityY = 0;

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
      container.style.cursor = "grabbing";
    };

    const onMouseUp = () => {
      isDragging = false;
      container.style.cursor = "grab";
    };

    const onMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const clientX = event.clientX - rect.left;
      const clientY = event.clientY - rect.top;

      mouse.x = (clientX / rect.width) * 2 - 1;
      mouse.y = -(clientY / rect.height) * 2 + 1;

      if (isDragging) {
        const deltaX = event.clientX - previousMousePosition.x;
        const deltaY = event.clientY - previousMousePosition.y;
        dragVelocityX = deltaX * 0.005;
        dragVelocityY = deltaY * 0.005;
        group.rotation.y += dragVelocityX;
        group.rotation.x += dragVelocityY;
        previousMousePosition = { x: event.clientX, y: event.clientY };
        return;
      }

      // Raycast against node meshes
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      if (intersects.length > 0) {
        const hit = intersects[0].object as THREE.Mesh;
        const skillData = hit.userData as SkillNodeData;
        container.style.cursor = "pointer";
        setHoveredNode({
          name: skillData.name,
          domain: skillData.domain,
          level: skillData.level,
          required: skillData.required,
          x: clientX,
          y: clientY,
        });
      } else {
        container.style.cursor = isDragging ? "grabbing" : "grab";
        setHoveredNode(null);
      }
    };

    const onClick = (event: MouseEvent) => {
      if (Math.abs(dragVelocityX) > 0.01 || Math.abs(dragVelocityY) > 0.01) return;

      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      if (intersects.length > 0) {
        const hit = intersects[0].object as THREE.Mesh;
        const skillData = hit.userData as SkillNodeData;

        // Smooth camera lerp towards clicked node
        const worldPos = new THREE.Vector3();
        hit.getWorldPosition(worldPos);
        targetLookAt.copy(worldPos);
        targetCamPos.set(worldPos.x * 1.5, worldPos.y * 1.5 + 1.2, worldPos.z * 1.5 + 8);

        if (onSelectSkill) {
          onSelectSkill(skillData.name);
        }
      }
    };

    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        isDragging = true;
        previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      }
    };

    const onTouchEnd = () => {
      isDragging = false;
    };

    const onTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 1 && isDragging) {
        const touch = e.touches[0];
        const deltaX = touch.clientX - previousMousePosition.x;
        const deltaY = touch.clientY - previousMousePosition.y;
        dragVelocityX = deltaX * 0.006;
        dragVelocityY = deltaY * 0.006;
        group.rotation.y += dragVelocityX;
        group.rotation.x += dragVelocityY;
        previousMousePosition = { x: touch.clientX, y: touch.clientY };

        const rect = container.getBoundingClientRect();
        mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(nodeMeshes);
        if (intersects.length > 0) {
          const hit = intersects[0].object as THREE.Mesh;
          const skillData = hit.userData as SkillNodeData;
          setHoveredNode({
            name: skillData.name,
            domain: skillData.domain,
            level: skillData.level,
            required: skillData.required,
            x: touch.clientX - rect.left,
            y: touch.clientY - rect.top,
          });
        }
      }
    };

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mouseup", onMouseUp);
    container.addEventListener("mousemove", onMouseMove);
    container.addEventListener("click", onClick);
    container.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchend", onTouchEnd);
    container.addEventListener("touchmove", onTouchMove, { passive: true });

    // Resize Handler
    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", onResize);

    // Animation Loop with precise performance timing
    let animationFrameId: number;
    let lastTime = performance.now();
    let totalElapsedTime = 0;

    const animate = (now: number) => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;
      totalElapsedTime += delta;

      // Inertial damping when dragging stops
      if (!isDragging) {
        dragVelocityX *= 0.92;
        dragVelocityY *= 0.92;
        group.rotation.y += dragVelocityX;
        group.rotation.x += dragVelocityY;

        if (isRotatingRef.current) {
          group.rotation.y += delta * 0.12;
        }
      }

      // Smooth camera interpolation (lerp)
      camera.position.lerp(targetCamPos, 0.05);
      currentLookAt.lerp(targetLookAt, 0.05);
      camera.lookAt(currentLookAt);

      // Domain Dimming / Highlighting
      const activeDom = selectedDomainRef.current;
      nodeMeshes.forEach((mesh) => {
        const d = mesh.userData.domain;
        const mat = mesh.material as THREE.MeshStandardMaterial;
        if (activeDom === "all" || d.toLowerCase() === activeDom.toLowerCase()) {
          mat.opacity = 0.95;
          mesh.scale.set(1, 1, 1);
        } else {
          mat.opacity = 0.22;
          mesh.scale.set(0.65, 0.65, 0.65);
        }
      });

      // Animated Pulsing Aura Ring
      if (activeAuraMesh) {
        const pulse = Math.sin(totalElapsedTime * 3.5) * 0.15 + 1.0;
        activeAuraMesh.scale.set(pulse, pulse, 1);
      }

      // Core Rotation & Gyro Ring
      coreMesh.rotation.y = -totalElapsedTime * 0.25;
      coreMesh.rotation.z = totalElapsedTime * 0.15;
      gyroRing.rotation.x = totalElapsedTime * 0.4;
      gyroRing.rotation.y = totalElapsedTime * 0.2;

      // Particle gentle drift
      particleSystem.rotation.y = totalElapsedTime * 0.03;

      renderer.render(scene, camera);
    };

    animate(performance.now());

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      container.removeEventListener("mousemove", onMouseMove);
      container.removeEventListener("click", onClick);
      container.removeEventListener("touchstart", onTouchStart);
      window.removeEventListener("touchend", onTouchEnd);
      container.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("resize", onResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [activeSkill, onSelectSkill]);

  return (
    <div className="relative w-full h-[320px] sm:h-[430px] rounded-3xl overflow-hidden bg-gradient-to-b from-[#060814] via-[#090e24] to-[#060814] border border-slate-800/90 shadow-xl flex items-center justify-center group select-none touch-none">
      {/* 3D WebGL Canvas */}
      <div
        ref={containerRef}
        className="absolute inset-0 z-0 cursor-grab active:cursor-grabbing"
      />

      {/* Floating Interactive Tooltip */}
      {hoveredNode && (
        <div
          className="absolute z-30 pointer-events-none transition-all duration-75 ease-out animate-in fade-in zoom-in-95"
          style={{
            left: Math.min(hoveredNode.x + 16, 420),
            top: Math.max(hoveredNode.y - 45, 16),
          }}
        >
          <div className="p-3.5 rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 shadow-2xl text-xs space-y-2 min-w-48 text-white">
            <div className="flex items-center justify-between gap-2">
              <span className="font-bold text-white text-sm">{hoveredNode.name}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 font-semibold border border-indigo-500/40">
                {hoveredNode.domain}
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-[11px] text-slate-300">
                <span>Proficiency Level</span>
                <strong className="text-white">L{hoveredNode.level} / L{hoveredNode.required}</strong>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    hoveredNode.level >= hoveredNode.required ? "bg-emerald-400" : "bg-amber-400"
                  }`}
                  style={{ width: `${(hoveredNode.level / hoveredNode.required) * 100}%` }}
                />
              </div>
            </div>
            <div className="flex items-center justify-between text-[10px] text-indigo-300 font-medium pt-1 border-t border-slate-800">
              <span className="flex items-center gap-1">
                <Eye className="w-3 h-3" /> Focus Node
              </span>
              <span>Click to inspect</span>
            </div>
          </div>
        </div>
      )}

      {/* Top Left Title & Telemetry Badge */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/85 border border-slate-700/80 shadow-md backdrop-blur-xl">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span className="text-xs font-bold text-white tracking-wide">
            {t.topographyTitle}
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>
        <p className="text-[11px] text-slate-400 mt-1.5 pl-1 hidden sm:block">
          Drag to orbit • Click node to zoom & inspect
        </p>
      </div>

      {/* Top Right 3D Controls */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
        <button
          onClick={() => setIsRotating(!isRotating)}
          className="p-2 rounded-xl bg-slate-900/85 hover:bg-slate-800 border border-slate-700/80 text-slate-200 shadow-md hover:shadow-lg transition-all"
          title={isRotating ? "Pause Rotation" : "Play Rotation"}
        >
          {isRotating ? <Pause className="w-3.5 h-3.5 text-indigo-400" /> : <Play className="w-3.5 h-3.5 text-slate-300" />}
        </button>
        <button
          onClick={() => resetCameraRef.current()}
          className="p-2 rounded-xl bg-slate-900/85 hover:bg-slate-800 border border-slate-700/80 text-slate-200 shadow-md hover:shadow-lg transition-all flex items-center gap-1 text-xs"
          title="Reset Camera View"
        >
          <RotateCcw className="w-3.5 h-3.5 text-slate-300" />
        </button>
      </div>

      {/* Bottom Interactive Domain Filter Pills */}
      <div className="absolute bottom-3 sm:bottom-4 left-3 sm:left-4 right-3 sm:right-4 z-10 flex items-center justify-between gap-2 pointer-events-auto">
        <div className="flex items-center gap-1.5 flex-nowrap overflow-x-auto no-scrollbar py-0.5 max-w-full">
          <button
            onClick={() => setSelectedDomain("all")}
            className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all ${
              selectedDomain === "all"
                ? "bg-white text-slate-900 font-bold shadow-md"
                : "bg-slate-900/80 text-slate-300 hover:bg-slate-800 border border-slate-700/60"
            }`}
          >
            {t.allDomains}
          </button>
          <button
            onClick={() => setSelectedDomain("statistical")}
            className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              selectedDomain === "statistical"
                ? "bg-sky-500 text-white font-bold shadow-md shadow-sky-500/30"
                : "bg-slate-900/80 text-slate-300 hover:bg-slate-800 border border-slate-700/60"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-sky-400" /> {t.statDomain}
          </button>
          <button
            onClick={() => setSelectedDomain("technical")}
            className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              selectedDomain === "technical"
                ? "bg-indigo-600 text-white font-bold shadow-md shadow-indigo-500/30"
                : "bg-slate-900/80 text-slate-300 hover:bg-slate-800 border border-slate-700/60"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-indigo-400" /> {t.techDomain}
          </button>
          <button
            onClick={() => setSelectedDomain("domain")}
            className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              selectedDomain === "domain"
                ? "bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/30"
                : "bg-slate-900/80 text-slate-300 hover:bg-slate-800 border border-slate-700/60"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-amber-400" /> {t.domainDomain}
          </button>
          <button
            onClick={() => setSelectedDomain("soft skills")}
            className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
              selectedDomain === "soft skills"
                ? "bg-emerald-500 text-white font-bold shadow-md shadow-emerald-500/30"
                : "bg-slate-900/80 text-slate-300 hover:bg-slate-800 border border-slate-700/60"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400" /> {t.softDomain}
          </button>
        </div>

        <div className="text-[11px] text-slate-300 bg-slate-900/85 px-3 py-1 rounded-xl border border-slate-700/80 backdrop-blur-xl hidden sm:flex items-center gap-1.5 shadow-md">
          <Compass className="w-3.5 h-3.5 text-indigo-400" />
          <span>Selected: <strong className="text-indigo-300">{activeSkill}</strong></span>
        </div>
      </div>
    </div>
  );
}
