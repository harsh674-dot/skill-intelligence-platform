"use client";

import React, { useState } from "react";
import {
  BrainCircuit,
  BarChart3,
  ChevronDown,
  Sparkles,
  GraduationCap,
  ShieldAlert,
  Languages,
  Key,
  Mail,
  Lock,
  LogIn,
  X,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { UserResponse, login, getMe, register, getRoles } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

export interface DemoPersona {
  email: string;
  name: string;
  role: string;
  department: string;
  access_role: "employee" | "admin";
}

export const DEMO_PERSONAS: DemoPersona[] = [
  {
    email: "ananya.sharma@demo.gov.in",
    name: "Ananya Sharma",
    role: "Statistical Officer",
    department: "National Statistical Office",
    access_role: "employee",
  },
  {
    email: "rahul.verma@demo.gov.in",
    name: "Rahul Verma",
    role: "Data Analyst",
    department: "National Statistical Office",
    access_role: "employee",
  },
  {
    email: "priya.nair@demo.gov.in",
    name: "Priya Nair",
    role: "Senior Statistical Officer",
    department: "National Sample Survey Office",
    access_role: "employee",
  },
  {
    email: "rohit.kumar@demo.gov.in",
    name: "Rohit Kumar",
    role: "System Admin",
    department: "State Directorate of Economics",
    access_role: "admin",
  },
];

interface NavbarProps {
  currentUser: UserResponse | null;
  currentTab: "employee" | "assessments" | "rag_studio" | "admin";
  onSelectTab: (tab: "employee" | "assessments" | "rag_studio" | "admin") => void;
  onSwitchPersona: (persona: DemoPersona) => void;
  isBackendOnline: boolean;
  onReturnTo3D?: () => void;
}

export default function Navbar({
  currentUser,
  currentTab,
  onSelectTab,
  onSwitchPersona,
  isBackendOnline,
  onReturnTo3D,
}: NavbarProps) {
  const [isPersonaMenuOpen, setIsPersonaMenuOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();

  const getTranslatedRole = (roleName?: string) => {
    if (!roleName) return "";
    if (roleName.toLowerCase().includes("senior")) return t.roleSeniorStatisticalOfficer;
    if (roleName.toLowerCase().includes("statistical")) return t.roleStatisticalOfficer;
    if (roleName.toLowerCase().includes("analyst")) return t.roleDataAnalyst;
    if (roleName.toLowerCase().includes("admin")) return t.roleSystemAdmin;
    return roleName;
  };

  const getTranslatedDept = (deptName?: string) => {
    if (!deptName) return "";
    if (deptName.includes("Sample")) return t.deptNSSO;
    if (deptName.includes("Statistical")) return t.deptNSO;
    if (deptName.includes("Directorate")) return t.deptStateDirectorate;
    return deptName;
  };

  const [isCustomLoginOpen, setIsCustomLoginOpen] = useState(false);
  const [customEmail, setCustomEmail] = useState("ananya.sharma@demo.gov.in");
  const [customPassword, setCustomPassword] = useState("Demo@12345");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regFullName, setRegFullName] = useState("");
  const [regRoleId, setRegRoleId] = useState<string>("");
  const [regDepartment, setRegDepartment] = useState("");
  const [regDesignation, setRegDesignation] = useState("");
  const [registerError, setRegisterError] = useState<string | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [availableRoles, setAvailableRoles] = useState<Array<{ id: string; name: string }>>([]);

  const handleCustomLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);
    setIsLoggingIn(true);
    try {
      const authRes = await login(customEmail.trim(), customPassword);
      if (typeof window !== "undefined") {
        sessionStorage.setItem("token_" + customEmail.trim(), authRes.access_token);
      }
      const userMe = await getMe(authRes.access_token);
      const persona: DemoPersona = {
        email: userMe.email,
        name: userMe.full_name,
        role: userMe.access_role === "admin" ? "System Admin" : "Statistical Officer",
        department: "National Statistical Office",
        access_role: userMe.access_role as "employee" | "admin",
      };
      onSwitchPersona(persona);
      setIsCustomLoginOpen(false);
      setIsPersonaMenuOpen(false);
    } catch (err: unknown) {
      setLoginError(err instanceof Error ? err.message : "Authentication failed. Check email/password.");
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError(null);
    setIsRegistering(true);
    try {
      const userRes = await register(
        regEmail.trim(),
        regPassword,
        regFullName.trim(),
        regRoleId || undefined,
        regDepartment || undefined,
        regDesignation || undefined
      );
      const authRes = await login(regEmail.trim(), regPassword);
      if (typeof window !== "undefined") {
        sessionStorage.setItem("token_" + regEmail.trim(), authRes.access_token);
      }
      const persona: DemoPersona = {
        email: userRes.email,
        name: userRes.full_name,
        role: availableRoles.find((r) => r.id === regRoleId)?.name || "Employee",
        department: regDepartment || "National Statistical Office",
        access_role: userRes.access_role as "employee" | "admin",
      };
      onSwitchPersona(persona);
      setIsRegisterOpen(false);
      setIsPersonaMenuOpen(false);
    } catch (err: unknown) {
      setRegisterError(err instanceof Error ? err.message : "Registration failed. Please try again.");
    } finally {
      setIsRegistering(false);
    }
  };

  const openRegister = async () => {
    setIsCustomLoginOpen(false);
    setIsPersonaMenuOpen(false);
    setIsRegisterOpen(true);
    setRegisterError(null);
    if (availableRoles.length === 0) {
      try {
        const roles = await getRoles();
        setAvailableRoles(roles.map((r) => ({ id: r.id, name: r.name })));
      } catch {
        // ignore roles fetch error
      }
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/80 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.03)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Brand & Emblem */}
            <div
              onClick={onReturnTo3D}
              className="flex items-center gap-2 sm:gap-3 cursor-pointer group select-none"
              role="button"
              tabIndex={0}
              title="Return to 3D Space"
            >
              <div className="flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-600 text-white shadow-md shadow-indigo-500/25 shrink-0 transition-transform group-hover:scale-105">
                <BrainCircuit className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <span className="text-sm sm:text-base font-extrabold tracking-tight text-slate-900 group-hover:text-indigo-600 transition-colors">
                    {t.brandTitle}
                  </span>
                  <span className="hidden xs:inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-200/80 text-indigo-700 tracking-wide shadow-2xs">
                    {t.sihBadge}
                  </span>
                </div>
                <p className="hidden sm:block text-xs text-slate-500 font-medium">
                  {t.brandSubtitle}
                </p>
              </div>
            </div>

            {/* Center Tabs */}
            <nav className="hidden md:flex items-center gap-1 bg-slate-100/90 p-1 rounded-2xl border border-slate-200/70 shadow-2xs">
              <button
                onClick={() => onSelectTab("employee")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 ${
                  currentTab === "employee"
                    ? "bg-white text-indigo-700 shadow-xs border border-slate-200/80 font-bold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
                }`}
              >
                <BarChart3 className={`w-4 h-4 ${currentTab === "employee" ? "text-indigo-600" : "text-slate-400"}`} />
                {t.tabEmployee}
              </button>

              <button
                onClick={() => onSelectTab("assessments")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 ${
                  currentTab === "assessments"
                    ? "bg-white text-indigo-700 shadow-xs border border-slate-200/80 font-bold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
                }`}
              >
                <GraduationCap className={`w-4 h-4 ${currentTab === "assessments" ? "text-indigo-600" : "text-slate-400"}`} />
                {t.tabAssessments}
              </button>

              <button
                onClick={() => onSelectTab("rag_studio")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 ${
                  currentTab === "rag_studio"
                    ? "bg-white text-indigo-700 shadow-xs border border-slate-200/80 font-bold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
                }`}
              >
                <Sparkles className={`w-4 h-4 ${currentTab === "rag_studio" ? "text-indigo-600" : "text-slate-400"}`} />
                {t.tabRagStudio}
              </button>

              <button
                onClick={() => onSelectTab("admin")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 ${
                  currentTab === "admin"
                    ? "bg-white text-indigo-700 shadow-xs border border-slate-200/80 font-bold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-white/70"
                }`}
              >
                <ShieldAlert className={`w-4 h-4 ${currentTab === "admin" ? "text-indigo-600" : "text-slate-400"}`} />
                {t.tabAdmin}
              </button>
            </nav>

            {/* Right Action: Language Toggle + Demo Persona Switcher & Live Status */}
            <div className="flex items-center gap-2.5">
              {/* Language Selector (English / हिंदी) */}
              <div className="flex items-center bg-slate-100 p-0.5 rounded-xl border border-slate-200">
                <button
                  onClick={() => setLanguage("en")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                    language === "en"
                      ? "bg-white text-indigo-700 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                  title="Switch to English"
                >
                  <Languages className="w-3 h-3" />
                  EN
                </button>
                <button
                  onClick={() => setLanguage("hi")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                    language === "hi"
                      ? "bg-white text-indigo-700 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                  title="हिंदी में बदलें"
                >
                  हिन्दी
                </button>
              </div>

              {/* Backend Status Ping */}
              <div
                className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                  isBackendOnline
                    ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                    : "bg-rose-50 border-rose-200 text-rose-700"
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    isBackendOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
                  }`}
                />
                {isBackendOnline ? t.apiOnline : t.apiOffline}
              </div>

              {/* Persona Switcher Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setIsPersonaMenuOpen(!isPersonaMenuOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:border-slate-300 text-xs font-medium text-slate-700 shadow-xs transition-all"
                >
                  <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold">
                    {currentUser ? currentUser.full_name.charAt(0) : "U"}
                  </div>
                  <div className="text-left hidden sm:block">
                    <div className="text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                      {currentUser?.full_name || t.selectPersona}
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-medium uppercase ${
                          currentUser?.access_role === "admin"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-indigo-100 text-indigo-800"
                        }`}
                      >
                        {currentUser?.access_role || "Demo"}
                      </span>
                    </div>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {isPersonaMenuOpen && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white border border-slate-200 shadow-2xl p-2.5 z-50 animate-in fade-in zoom-in-95 duration-150">
                    <div className="px-3 py-2 border-b border-slate-100 mb-2 flex items-center justify-between">
                      <div>
                        <p className="text-xs font-bold text-slate-900">
                          {t.judgeSwitcherTitle}
                        </p>
                        <p className="text-[11px] text-slate-500">
                          {t.judgeSwitcherSub}
                        </p>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                        PostgreSQL Live
                      </span>
                    </div>

                    <div className="space-y-1.5 max-h-[380px] overflow-y-auto pr-1">
                      {DEMO_PERSONAS.map((p) => {
                        const isSelected = currentUser?.email === p.email;
                        return (
                          <div
                            key={p.email}
                            onClick={() => {
                              onSwitchPersona(p);
                              setIsPersonaMenuOpen(false);
                            }}
                            className={`w-full text-left p-2.5 rounded-xl text-xs transition-all flex items-start gap-2.5 cursor-pointer border ${
                              isSelected
                                ? "bg-indigo-50/80 border-indigo-200 text-indigo-900"
                                : "hover:bg-slate-50 border-slate-100 text-slate-700"
                            }`}
                          >
                            <div className="w-8 h-8 rounded-lg bg-indigo-100/70 border border-indigo-200 flex items-center justify-center font-bold text-xs text-indigo-700 shrink-0 mt-0.5">
                              {p.name.charAt(0)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-bold truncate text-slate-900 flex items-center gap-1.5">
                                <span>{p.name}</span>
                                <span
                                  className={`text-[9px] px-1.5 py-0.2 rounded font-semibold uppercase ${
                                    p.access_role === "admin"
                                      ? "bg-amber-100 text-amber-800"
                                      : "bg-indigo-100 text-indigo-800"
                                  }`}
                                >
                                  {p.access_role}
                                </span>
                              </div>
                              <div className="text-[11px] text-slate-500 truncate mt-0.5">
                                {getTranslatedRole(p.role)} • {getTranslatedDept(p.department)}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                     {/* Custom Credentials Login Button */}
                     <div className="mt-2.5 pt-2.5 border-t border-slate-100 space-y-2">
                       <button
                         onClick={() => {
                           setIsCustomLoginOpen(true);
                           setIsPersonaMenuOpen(false);
                         }}
                         className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
                       >
                         <LogIn className="w-3.5 h-3.5 text-indigo-400" />
                         <span>Sign In with Custom Credentials</span>
                       </button>
                       <button
                         onClick={openRegister}
                         className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
                       >
                         <span>Register New Employee</span>
                       </button>
                     </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ── CUSTOM LOGIN MODAL ──────────────────────────────────────────────── */}
      {isCustomLoginOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="w-full max-w-md rounded-2xl bg-white border border-slate-200 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Direct Account Authentication
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Real JWT Login against PostgreSQL database
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsCustomLoginOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleCustomLogin} className="p-6 space-y-4">
              {loginError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{loginError}</span>
                </div>
              )}

              {/* Quick Fill Preset Pills */}
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Quick Select Account
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  {DEMO_PERSONAS.map((p) => (
                    <button
                      key={p.email}
                      type="button"
                      onClick={() => {
                        setCustomEmail(p.email);
                        setCustomPassword("Demo@12345");
                      }}
                      className={`text-left p-2 rounded-lg border text-xs transition-all ${
                        customEmail === p.email
                          ? "border-indigo-600 bg-indigo-50/50 text-indigo-900 font-bold"
                          : "border-slate-200 hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <div className="truncate font-semibold">{p.name}</div>
                      <div className="text-[10px] text-slate-400 truncate">{p.access_role}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Email Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Login Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={customEmail}
                    onChange={(e) => setCustomEmail(e.target.value)}
                    placeholder="name@demo.gov.in"
                    className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-600 focus:border-transparent text-xs text-slate-900 font-mono"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Key className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={customPassword}
                    onChange={(e) => setCustomPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-600 focus:border-transparent text-xs text-slate-900 font-mono"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoggingIn}
                  className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md shadow-indigo-600/25 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isLoggingIn ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Authenticate & Sign In</span>
                    </>
                  )}
                </button>
              </div>

              <div className="text-center text-[11px] text-slate-400 pt-1">
                Connected to local PostgreSQL • Table: <code className="text-slate-600">users</code>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── REGISTRATION MODAL ─────────────────────────────────────────────── */}
      {isRegisterOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="w-full max-w-md rounded-2xl bg-white border border-slate-200 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Register New Employee</h3>
                  <p className="text-[11px] text-slate-500">Create account and assign role</p>
                </div>
              </div>
              <button
                onClick={() => setIsRegisterOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRegister} className="p-6 space-y-4">
              {registerError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{registerError}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  placeholder="e.g. Ananya Sharma"
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="name@demo.gov.in"
                    className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <div className="relative">
                  <Key className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Min 8 characters"
                    className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Role</label>
                <select
                  required
                  value={regRoleId}
                  onChange={(e) => setRegRoleId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900"
                >
                  <option value="">Select a role...</option>
                  {availableRoles.map((r) => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Department</label>
                  <input
                    type="text"
                    value={regDepartment}
                    onChange={(e) => setRegDepartment(e.target.value)}
                    placeholder="e.g. NSO"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Designation</label>
                  <input
                    type="text"
                    value={regDesignation}
                    onChange={(e) => setRegDesignation(e.target.value)}
                    placeholder="e.g. Statistical Officer"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-600 focus:border-transparent text-xs text-slate-900"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isRegistering}
                  className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/25 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isRegistering ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Register & Sign In</span>
                    </>
                  )}
                </button>
              </div>

              <div className="text-center text-[11px] text-slate-400 pt-1">
                Account will be created with selected role and initial competencies
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Sleek Mobile Bottom Navigation Bar */}
      <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden bg-white/90 backdrop-blur-xl border-t border-slate-200/80 shadow-[0_-4px_24px_rgba(0,0,0,0.04)] px-2 py-2 flex items-center justify-around">

        <button
          onClick={() => onSelectTab("employee")}
          className={`flex flex-col items-center gap-1 py-1 px-2.5 rounded-2xl transition-all duration-200 ${currentTab === "employee"
              ? "text-indigo-600 font-bold bg-indigo-50/80 shadow-2xs"
              : "text-slate-500 hover:text-slate-800"
            }`}
        >
          <BarChart3 className="w-5 h-5" />
          <span className="text-[10px] tracking-tight">{t.tabEmployee}</span>
        </button>

        <button
          onClick={() => onSelectTab("assessments")}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-2xl transition-all duration-200 ${currentTab === "assessments"
              ? "text-indigo-600 font-bold bg-indigo-50/80 shadow-2xs"
              : "text-slate-500 hover:text-slate-800"
            }`}
        >
          <GraduationCap className="w-5 h-5" />
          <span className="text-[10px] tracking-tight">{t.tabAssessments}</span>
        </button>

        <button
          onClick={() => onSelectTab("rag_studio")}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-2xl transition-all duration-200 ${currentTab === "rag_studio"
              ? "text-purple-600 font-bold bg-purple-50/80 shadow-2xs"
              : "text-slate-500 hover:text-slate-800"
            }`}
        >
          <Sparkles className="w-5 h-5" />
          <span className="text-[10px] tracking-tight">{t.tabRagStudio}</span>
        </button>

        <button
          onClick={() => onSelectTab("admin")}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-2xl transition-all duration-200 ${currentTab === "admin"
              ? "text-amber-600 font-bold bg-amber-50/80 shadow-2xs"
              : "text-slate-500 hover:text-slate-800"
            }`}
        >
          <ShieldAlert className="w-5 h-5" />
          <span className="text-[10px] tracking-tight">{t.tabAdmin}</span>
        </button>
      </div>
    </>
  );
}
