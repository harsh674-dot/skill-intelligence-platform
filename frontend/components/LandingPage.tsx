"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import {
  ArrowRight,
  BookOpen,
  Brain,
  Sparkles,
  Target,
  Compass,
  Award,
  BarChart3,
  Layers,
  Zap,
  CheckCircle2,
  ChevronRight,
  RotateCw,
} from "lucide-react";

const COMPETENCIES = [
  {
    name: "Data Science & AI",
    category: "Core Analytical",
    level: "Level 4 • Advanced",
    color: "#2563eb",
    threeColor: 0x2563eb,
    icon: Brain,
    desc: "Machine learning, predictive algorithms & deep neural pipelines",
  },
  {
    name: "Official Statistics",
    category: "Methodology",
    level: "Level 3 • Proficient",
    color: "#4f46e5",
    threeColor: 0x4f46e5,
    icon: BarChart3,
    desc: "National sample surveys, census models & index compilation",
  },
  {
    name: "Survey Sampling",
    category: "Field Research",
    level: "Level 4 • Mastery",
    color: "#059669",
    threeColor: 0x059669,
    icon: Target,
    desc: "Multi-stage stratified sampling, variance estimation & bias auditing",
  },
  {
    name: "Econometric Modeling",
    category: "Economic Policy",
    level: "Level 3 • Proficient",
    color: "#d97706",
    threeColor: 0xd97706,
    icon: Award,
    desc: "Time series forecasting, macro indicators & econometric analysis",
  },
  {
    name: "Policy Governance",
    category: "Public Admin",
    level: "Level 2 • Intermediate",
    color: "#7c3aed",
    threeColor: 0x7c3aed,
    icon: Compass,
    desc: "Evidence-based policymaking, monitoring frameworks & KPI delivery",
  },
  {
    name: "Cloud & Data Ops",
    category: "Infrastructure",
    level: "Level 3 • Proficient",
    color: "#0284c7",
    threeColor: 0x0284c7,
    icon: Layers,
    desc: "Scalable data lakes, SQL/NoSQL data pipelines & automated ETL",
  },
];

interface LandingPageProps {
  onEnter: (tab?: "employee" | "assessments" | "rag_studio" | "admin", personaIndex?: number) => void;
}

export default function LandingPage({ onEnter }: LandingPageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(true);
  const [activeCompetency, setActiveCompetency] = useState<number>(0);

  const handleEnterPlatform = (tab?: "employee" | "assessments" | "rag_studio" | "admin", personaIndex?: number) => {
    setVisible(false);
    setTimeout(() => onEnter(tab, personaIndex), 450);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // ── 1. WebGL Renderer with Crisp Light Canvas ───────────────────────────
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setClearColor(0x000000, 0); // Transparent to blend with rich CSS gradient
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // ── 2. Scene & Camera ───────────────────────────────────────────────────
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      45,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 1.2, 22);

    // ── 3. High-Key Educational Studio Lighting ──────────────────────────────
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0xe0e7ff, 2.0);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
    dirLight.position.set(16, 24, 18);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const blueLight = new THREE.PointLight(0x38bdf8, 3.0, 60);
    blueLight.position.set(-14, 12, 12);
    scene.add(blueLight);

    const indigoLight = new THREE.PointLight(0x818cf8, 2.5, 60);
    indigoLight.position.set(14, -10, 10);
    scene.add(indigoLight);

    const emeraldLight = new THREE.PointLight(0x34d399, 2.0, 45);
    emeraldLight.position.set(0, 16, -8);
    scene.add(emeraldLight);

    // ── 4. Main 3D Knowledge Structure (Astrolabe / Armillary Core) ──────────
    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // Center Pearlescent Knowledge Core
    const coreGeometry = new THREE.IcosahedronGeometry(2.6, 3);
    const coreMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.12,
      metalness: 0.15,
    });
    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    mainGroup.add(coreMesh);

    // Dynamic Iridescent Inner Core
    const innerGeo = new THREE.SphereGeometry(2.0, 32, 32);
    const innerMat = new THREE.MeshStandardMaterial({
      color: 0x4f46e5,
      roughness: 0.3,
      metalness: 0.7,
      transparent: true,
      opacity: 0.25,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    mainGroup.add(innerMesh);

    // Geodesic Curriculum Wireframe Cage
    const cageGeometry = new THREE.IcosahedronGeometry(3.3, 1);
    const cageMaterial = new THREE.MeshBasicMaterial({
      color: 0x4f46e5,
      wireframe: true,
      transparent: true,
      opacity: 0.28,
    });
    const cageMesh = new THREE.Mesh(cageGeometry, cageMaterial);
    mainGroup.add(cageMesh);

    // 3 Gyroscopic Orbital Learning Rings
    const ring1Geo = new THREE.TorusGeometry(4.8, 0.045, 16, 140);
    const ring1Mat = new THREE.MeshStandardMaterial({
      color: 0x2563eb,
      metalness: 0.6,
      roughness: 0.2,
      transparent: true,
      opacity: 0.7,
    });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 3;
    ring1.rotation.y = Math.PI / 6;
    mainGroup.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(5.8, 0.04, 16, 140);
    const ring2Mat = new THREE.MeshStandardMaterial({
      color: 0x059669,
      metalness: 0.6,
      roughness: 0.2,
      transparent: true,
      opacity: 0.65,
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = -Math.PI / 4;
    ring2.rotation.z = Math.PI / 5;
    mainGroup.add(ring2);

    const ring3Geo = new THREE.TorusGeometry(6.8, 0.035, 16, 140);
    const ring3Mat = new THREE.MeshStandardMaterial({
      color: 0x7c3aed,
      metalness: 0.6,
      roughness: 0.2,
      transparent: true,
      opacity: 0.6,
    });
    const ring3 = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3.rotation.y = Math.PI / 2;
    ring3.rotation.x = Math.PI / 8;
    mainGroup.add(ring3);

    // ── 5. Orbiting Competency Satellites ─────────────────────────────────────
    const satelliteCount = COMPETENCIES.length;
    const satellites: THREE.Mesh[] = [];
    const satelliteConnectors: THREE.Line[] = [];
    const satelliteAngles: number[] = [];
    const satelliteDistances: number[] = [6.2, 7.0, 7.8, 6.6, 7.4, 8.2];
    const satelliteHeights: number[] = [1.8, -1.6, 2.2, -2.4, 0.8, -0.6];

    for (let i = 0; i < satelliteCount; i++) {
      const comp = COMPETENCIES[i];
      const geo = i % 2 === 0
        ? new THREE.DodecahedronGeometry(0.55)
        : new THREE.OctahedronGeometry(0.65);

      const mat = new THREE.MeshStandardMaterial({
        color: comp.threeColor,
        roughness: 0.15,
        metalness: 0.4,
      });
      const mesh = new THREE.Mesh(geo, mat);

      const angle = (i / satelliteCount) * Math.PI * 2;
      satelliteAngles.push(angle);

      const dist = satelliteDistances[i];
      const y = satelliteHeights[i];
      mesh.position.set(Math.cos(angle) * dist, y, Math.sin(angle) * dist);
      mainGroup.add(mesh);
      satellites.push(mesh);

      // Pulsing energy line connecting satellite to knowledge hub
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(mesh.position.x, mesh.position.y, mesh.position.z),
      ]);
      const lineMat = new THREE.LineBasicMaterial({
        color: comp.threeColor,
        transparent: true,
        opacity: 0.35,
      });
      const line = new THREE.Line(lineGeo, lineMat);
      mainGroup.add(line);
      satelliteConnectors.push(line);
    }

    // ── 6. Luminous Knowledge Atmosphere (Soft Airy Floating Particles) ─────
    const moteCount = 140;
    const moteGeo = new THREE.BufferGeometry();
    const motePositions = new Float32Array(moteCount * 3);
    for (let i = 0; i < moteCount; i++) {
      motePositions[i * 3] = (Math.random() - 0.5) * 45;
      motePositions[i * 3 + 1] = (Math.random() - 0.5) * 30;
      motePositions[i * 3 + 2] = (Math.random() - 0.5) * 30;
    }
    moteGeo.setAttribute("position", new THREE.BufferAttribute(motePositions, 3));
    const moteMat = new THREE.PointsMaterial({
      color: 0x6366f1,
      size: 0.18,
      transparent: true,
      opacity: 0.35,
      sizeAttenuation: true,
    });
    const motes = new THREE.Points(moteGeo, moteMat);
    scene.add(motes);

    // ── 7. Interactive Controls & Mouse Tracking ─────────────────────────────
    let mouseX = 0;
    let mouseY = 0;
    let targetRotX = 0;
    let targetRotY = 0;
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const deltaX = e.clientX - prevMouseX;
        const deltaY = e.clientY - prevMouseY;
        mainGroup.rotation.y += deltaX * 0.006;
        mainGroup.rotation.x += deltaY * 0.006;
        prevMouseX = e.clientX;
        prevMouseY = e.clientY;
      } else {
        const rect = canvas.getBoundingClientRect();
        mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
        mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
      }
    };

    const handleMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);

    // ── 8. Responsive Canvas Resizer ─────────────────────────────────────────
    const handleResize = () => {
      if (!canvas) return;
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener("resize", handleResize);

    // ── 9. Render Loop ───────────────────────────────────────────────────────
    let animId: number;
    let clock = 0;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      clock += 0.012;

      // Smooth inertia on mouse movement
      if (!isDragging) {
        targetRotY = mouseX * 0.45;
        targetRotX = -mouseY * 0.35;
        mainGroup.rotation.y += (targetRotY - mainGroup.rotation.y) * 0.035;
        mainGroup.rotation.x += (targetRotX - mainGroup.rotation.x) * 0.035;
      }

      // Continuous Gyroscopic Rotations
      coreMesh.rotation.y = clock * 0.25;
      coreMesh.rotation.x = Math.sin(clock * 0.15) * 0.1;

      cageMesh.rotation.y = -clock * 0.3;
      cageMesh.rotation.z = Math.cos(clock * 0.2) * 0.15;

      ring1.rotation.z = clock * 0.22;
      ring2.rotation.z = -clock * 0.18;
      ring3.rotation.x = clock * 0.16;

      // Orbit each skill satellite smoothly
      for (let i = 0; i < satelliteCount; i++) {
        const sat = satellites[i];
        const currentAngle = satelliteAngles[i] + clock * 0.25;
        const dist = satelliteDistances[i];
        const y = satelliteHeights[i] + Math.sin(clock * 1.6 + i) * 0.25;
        const x = Math.cos(currentAngle) * dist;
        const z = Math.sin(currentAngle) * dist;

        sat.position.set(x, y, z);
        sat.rotation.x += 0.015;
        sat.rotation.y += 0.02;

        // Update dynamic connector lines
        const posAttr = satelliteConnectors[i].geometry.attributes.position;
        const arr = posAttr.array as Float32Array;
        arr[3] = x;
        arr[4] = y;
        arr[5] = z;
        posAttr.needsUpdate = true;
      }

      // Subtle breath on knowledge core
      const pulse = 1 + Math.sin(clock * 2) * 0.03;
      innerMesh.scale.set(pulse, pulse, pulse);

      // Slow drift of background particles
      motes.rotation.y = clock * 0.03;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[9999] overflow-hidden select-none"
      style={{
        opacity: visible ? 1 : 0,
        transition: "opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1)",
        pointerEvents: visible ? "all" : "none",
        background: `
          radial-gradient(circle at 75% 25%, rgba(99, 102, 241, 0.09) 0%, rgba(14, 165, 233, 0.06) 30%, transparent 65%),
          radial-gradient(circle at 20% 80%, rgba(16, 185, 129, 0.07) 0%, rgba(99, 102, 241, 0.04) 35%, transparent 60%),
          #f8fafc
        `,
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
      }}
    >
      {/* ── TOP EDGE-TO-EDGE HEADER ────────────────────────────────────────── */}
      <header className="absolute top-0 left-0 right-0 h-20 px-6 sm:px-10 flex items-center justify-between z-30 pointer-events-auto border-b border-slate-200/60 bg-white/70 backdrop-blur-md">
        {/* Institutional Branding */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 ring-1 ring-white/50">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-extrabold tracking-tight text-slate-900">
                Skill Intelligence Platform
              </span>
              <span className="hidden sm:inline-flex text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200/70">
                MoSPI Architecture
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Ministry of Statistics & Programme Implementation • Govt. of India
            </p>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>40/60 Competency Engine Active</span>
          </div>

          <button
            onClick={() => handleEnterPlatform("employee")}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 hover:shadow-indigo-600/30 transition-all duration-200 hover:-translate-y-0.5 cursor-pointer"
          >
            <span>Launch Platform</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* ── FULL SCREEN 2-COLUMN HERO VIEWPORT ─────────────────────────────── */}
      <main className="w-full h-full pt-20 flex flex-col lg:flex-row relative">
        {/* LEFT COLUMN: Clean, Elegant Educational Narrative (54% width) */}
        <div className="w-full lg:w-[54%] h-full overflow-y-auto px-6 sm:px-12 lg:px-16 py-8 sm:py-12 flex flex-col justify-center relative z-20 pointer-events-auto">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/90 border border-indigo-100 shadow-xs text-indigo-700 text-xs font-bold w-fit mb-5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Official Statistical Workforce Intelligence</span>
          </div>

          {/* Primary Educational Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-[1.15] mb-5">
            Empower Every Learner with{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-600">
              Intelligent 3D Skill Mapping
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl mb-8 font-normal">
            A comprehensive competency architecture built for public service and data governance. Automatically audit skills, detect proficiency gaps with the 40/60 baseline rule, and generate personalized learning roadmaps.
          </p>

          {/* 3 Core Educational Pillars */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 max-w-2xl mb-8">
            <div className="p-4 rounded-2xl bg-white/80 border border-slate-200/80 shadow-xs hover:border-indigo-300 transition-colors">
              <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                <Target className="w-4 h-4" />
              </div>
              <h2 className="text-xs font-bold text-slate-900 mb-1">40/60 Gap Rule</h2>
              <p className="text-[11px] text-slate-500 leading-normal">
                40% foundational knowledge + 60% scenario assessments.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/80 border border-slate-200/80 shadow-xs hover:border-indigo-300 transition-colors">
              <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
                <Brain className="w-4 h-4" />
              </div>
              <h2 className="text-xs font-bold text-slate-900 mb-1">AI Adaptive Tests</h2>
              <p className="text-[11px] text-slate-500 leading-normal">
                15 domain-tailored questions dynamically calibrated to roles.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/80 border border-slate-200/80 shadow-xs hover:border-indigo-300 transition-colors">
              <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
                <Compass className="w-4 h-4" />
              </div>
              <h2 className="text-xs font-bold text-slate-900 mb-1">Tailored Curricula</h2>
              <p className="text-[11px] text-slate-500 leading-normal">
                Automated iGOT Karmayogi course recommendations.
              </p>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3.5 mb-8">
            <button
              onClick={() => handleEnterPlatform("employee")}
              className="flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/35 transition-all duration-200 hover:-translate-y-0.5 cursor-pointer"
            >
              <span>Enter Learning Hub</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => handleEnterPlatform("assessments")}
              className="flex items-center gap-2 px-5 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300/80 font-bold text-sm shadow-xs hover:border-slate-400 transition-all cursor-pointer"
            >
              <Zap className="w-4 h-4 text-amber-500 fill-amber-400" />
              <span>Take 15-Q Assessment</span>
            </button>
          </div>

        </div>

        {/* RIGHT COLUMN: Expansive 3D Knowledge Network Canvas (46% width) */}
        <div className="w-full lg:w-[46%] h-[50vh] lg:h-full relative flex items-center justify-center">
          {/* Full Screen 3D Canvas */}
          <canvas
            ref={canvasRef}
            className="w-full h-full block cursor-grab active:cursor-grabbing"
          />

          {/* Floating Top-Right Telemetry Card */}
          <div className="absolute top-6 right-6 hidden sm:block p-4 rounded-2xl bg-white/85 backdrop-blur-xl border border-slate-200/90 shadow-lg shadow-slate-200/50 max-w-xs pointer-events-auto">
            <div className="flex items-center justify-between gap-3 mb-2">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Live Competency Index
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                94.6% Match
              </span>
            </div>
            <p className="text-[11px] text-slate-500 leading-tight mb-2.5">
              120+ standard competencies benchmarked across 4 organizational tiers.
            </p>
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-emerald-500 h-full w-[78%] rounded-full" />
            </div>
          </div>

          {/* Floating Bottom Competency Inspector Widget */}
          <div className="absolute bottom-6 left-6 right-6 sm:left-auto sm:right-6 sm:max-w-sm p-4 rounded-2xl bg-white/90 backdrop-blur-xl border border-slate-200/90 shadow-xl shadow-slate-200/50 pointer-events-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-600" />
                Featured 3D Node: {COMPETENCIES[activeCompetency].name}
              </span>
              <button
                onClick={() => setActiveCompetency((prev) => (prev + 1) % COMPETENCIES.length)}
                className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
              >
                <span>Next</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal mb-2.5">
              {COMPETENCIES[activeCompetency].desc}
            </p>
            <div className="flex items-center justify-between text-[11px] text-slate-600 pt-2 border-t border-slate-100">
              <span className="font-semibold text-indigo-700">
                {COMPETENCIES[activeCompetency].category}
              </span>
              <span className="px-2 py-0.5 rounded bg-slate-100 font-medium text-slate-700">
                {COMPETENCIES[activeCompetency].level}
              </span>
            </div>
          </div>

          {/* 3D Interaction Prompt Badge */}
          <div className="absolute top-6 left-6 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-md border border-slate-200/80 text-[11px] font-medium text-slate-500 flex items-center gap-1.5 pointer-events-none shadow-2xs">
            <RotateCw className="w-3 h-3 text-indigo-500 animate-spin" style={{ animationDuration: "8s" }} />
            <span>Interactive 3D • Drag to spin knowledge core</span>
          </div>
        </div>
      </main>

      {/* ── BOTTOM SKILL RIBBON ────────────────────────────────────────────── */}
      <footer className="absolute bottom-0 left-0 right-0 h-10 px-6 hidden md:flex items-center justify-between border-t border-slate-200/60 bg-white/60 backdrop-blur-xs text-[11px] text-slate-500 z-30 pointer-events-none">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-slate-700">Competency Frameworks:</span>
          <span>Official Statistics</span>
          <span>•</span>
          <span>Sampling & Estimation</span>
          <span>•</span>
          <span>Generative AI & RAG</span>
          <span>•</span>
          <span>Microdata Governance</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Official MoSPI Platform • National Skill Architecture</span>
        </div>
      </footer>
    </div>
  );
}
