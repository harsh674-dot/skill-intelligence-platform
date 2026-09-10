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
} from "lucide-react";
import { UserResponse } from "@/lib/api";
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
}

export default function Navbar({
  currentUser,
  currentTab,
  onSelectTab,
  onSwitchPersona,
  isBackendOnline,
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

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Emblem */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-600 text-white shadow-xs">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-slate-900">
                  {t.brandTitle}
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 tracking-wide">
                  {t.sihBadge}
                </span>
              </div>
              <p className="text-xs text-slate-500">
                {t.brandSubtitle}
              </p>
            </div>
          </div>

          {/* Center Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200/80">
            <button
              onClick={() => onSelectTab("employee")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                currentTab === "employee"
                  ? "bg-white text-indigo-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <BarChart3 className="w-4 h-4 text-indigo-600" />
              {t.tabEmployee}
            </button>

            <button
              onClick={() => onSelectTab("assessments")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                currentTab === "assessments"
                  ? "bg-white text-indigo-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <GraduationCap className="w-4 h-4 text-indigo-600" />
              {t.tabAssessments}
            </button>

            <button
              onClick={() => onSelectTab("rag_studio")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                currentTab === "rag_studio"
                  ? "bg-white text-purple-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <Sparkles className="w-4 h-4 text-purple-600" />
              {t.tabRagStudio}
            </button>

            <button
              onClick={() => onSelectTab("admin")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                currentTab === "admin"
                  ? "bg-white text-amber-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <ShieldAlert className="w-4 h-4 text-amber-600" />
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
                <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-white border border-slate-200 shadow-lg p-2 z-50">
                  <div className="px-3 py-2 border-b border-slate-100 mb-1">
                    <p className="text-xs font-semibold text-slate-900">
                      {t.judgeSwitcherTitle}
                    </p>
                    <p className="text-[11px] text-slate-500">
                      {t.judgeSwitcherSub}
                    </p>
                  </div>

                  <div className="space-y-1">
                    {DEMO_PERSONAS.map((p) => {
                      const isSelected = currentUser?.email === p.email;
                      return (
                        <button
                          key={p.email}
                          onClick={() => {
                            onSwitchPersona(p);
                            setIsPersonaMenuOpen(false);
                          }}
                          className={`w-full text-left p-2.5 rounded-xl text-xs transition-all flex items-center gap-2.5 ${
                            isSelected
                              ? "bg-indigo-50 border border-indigo-200 text-indigo-900"
                              : "hover:bg-slate-50 text-slate-700"
                          }`}
                        >
                          <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-xs text-indigo-600">
                            {p.name.charAt(0)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate text-slate-900 flex items-center gap-1.5">
                              {p.name}
                              <span
                                className={`text-[9px] px-1.5 py-0.5 rounded font-medium uppercase ${
                                  p.access_role === "admin"
                                    ? "bg-amber-100 text-amber-800"
                                    : "bg-indigo-100 text-indigo-800"
                                }`}
                              >
                                {p.access_role}
                              </span>
                            </div>
                            <div className="text-[11px] text-slate-500 truncate">
                              {getTranslatedRole(p.role)} • {getTranslatedDept(p.department)}
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
