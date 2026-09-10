"use client";

import React, { useState, useMemo } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  BookOpen,
  Zap,
  Target,
  Award,
  Layers,
  ChevronRight,
  Brain,
  Search,
  X,
  ExternalLink,
  SlidersHorizontal,
  ArrowUpRight,
  HelpCircle,
} from "lucide-react";
import { EmployeeDashboardData } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import dynamic from "next/dynamic";

const ThreeSkillGalaxy = dynamic(() => import("./ThreeSkillGalaxy"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-80 rounded-2xl bg-white border border-slate-200 flex flex-col items-center justify-center gap-2 text-xs text-slate-400">
      <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      <span>Loading 3D Skill Topography...</span>
    </div>
  ),
});

interface EmployeeDashboardProps {
  data: EmployeeDashboardData;
  onOpenAssessment: (courseId?: string) => void;
}

export default function EmployeeDashboard({
  data,
  onOpenAssessment,
}: EmployeeDashboardProps) {
  const { t } = useLanguage();
  const [selectedCompetency, setSelectedCompetency] = useState<string>(
    data.priority_gaps[0]?.competency_name || "Python"
  );
  const [filterDomain, setFilterDomain] = useState<string>("all");
  const [cardFilter, setCardFilter] = useState<"all" | "gaps" | "mastered" | "critical">("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [expandedCompId, setExpandedCompId] = useState<string | null>(null);
  const [providerFilter, setProviderFilter] = useState<string>("all");
  const [showFormulaHelp, setShowFormulaHelp] = useState<boolean>(false);

  const domains = [
    "all",
    ...Array.from(new Set(data.competencies.map((c) => c.domain).filter(Boolean))),
  ];

  // Filter competencies based on domain, card filter, and search query
  const filteredCompetencies = useMemo(() => {
    return data.competencies.filter((c) => {
      // Domain filter
      if (filterDomain !== "all" && c.domain.toLowerCase() !== filterDomain.toLowerCase()) {
        return false;
      }

      // Stat card filter
      if (cardFilter === "gaps" && c.gap === 0) return false;
      if (cardFilter === "mastered" && c.gap > 0) return false;
      if (cardFilter === "critical" && !c.is_critical) return false;

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = c.competency_name.toLowerCase().includes(q);
        const matchDomain = c.domain.toLowerCase().includes(q);
        if (!matchName && !matchDomain) return false;
      }

      return true;
    });
  }, [data.competencies, filterDomain, cardFilter, searchQuery]);

  // Filter recommendations based on selected provider
  const filteredRecommendations = useMemo(() => {
    if (providerFilter === "all") return data.recommendations;
    return data.recommendations.filter((r) =>
      (r.provider || "iGOT Karmayogi").toLowerCase().includes(providerFilter.toLowerCase())
    );
  }, [data.recommendations, providerFilter]);

  const handleStatCardClick = (type: "all" | "gaps" | "mastered" | "critical") => {
    setCardFilter((prev) => (prev === type ? "all" : type));
  };

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Welcome Banner with Light Radiant Mesh Glow */}
      <div className="relative rounded-3xl bg-gradient-to-br from-white via-indigo-50/30 to-purple-50/25 border border-indigo-100/80 p-6 sm:p-8 shadow-sm overflow-hidden backdrop-blur-md">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-gradient-to-br from-indigo-300/20 to-purple-300/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-8 w-60 h-60 bg-gradient-to-tr from-sky-200/20 to-emerald-200/15 rounded-full blur-2xl pointer-events-none" />

        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-indigo-700 bg-indigo-50/90 px-3 py-1 rounded-full border border-indigo-200/80 shadow-2xs">
                Official Statistical System • MoSPI Capacity Engine
              </span>
              <span className="text-xs text-slate-500 font-medium">
                ISO 9001:2015 Benchmark
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              {t.welcomeBack}{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700">
                {data.employee.email.split("@")[0].replace(".", " ").toUpperCase()}
              </span>
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              {t.assignedRole} <span className="font-semibold text-slate-900 bg-white/80 border border-slate-200/80 px-2.5 py-0.5 rounded-lg shadow-2xs">{data.employee.role_name}</span>.{" "}
              {t.welcomeDesc}
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => onOpenAssessment()}
              className="px-6 py-3 rounded-2xl btn-gradient-primary active:scale-95 text-white font-bold text-sm flex items-center gap-2 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all duration-200"
            >
              <Zap className="w-4 h-4 fill-current text-amber-300" />
              {t.takeAssessment}
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Clickable Stat Cards with Pleasant Soft Gradients */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Required Skills */}
        <div
          onClick={() => handleStatCardClick("all")}
          className={`rounded-2xl p-4 sm:p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "all"
              ? "bg-gradient-to-br from-white to-blue-50/60 border-blue-400 shadow-md ring-2 ring-blue-500/20"
              : "bg-gradient-to-br from-white to-slate-50/60 border-slate-200/90 hover:border-blue-300 hover:shadow-md hover:-translate-y-1"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider">{t.requiredSkills}</span>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-2xs border border-blue-100">
              <Layers className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-2 sm:mt-3">
            {data.summary.total_competencies}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
            <span className="truncate">{t.requiredSkillsDesc}</span>
            <span className="text-[9px] sm:text-[10px] text-indigo-600 font-bold hidden sm:inline">Show all</span>
          </div>
        </div>

        {/* Active Gaps */}
        <div
          onClick={() => handleStatCardClick("gaps")}
          className={`rounded-2xl p-4 sm:p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "gaps"
              ? "bg-gradient-to-br from-white to-amber-50/70 border-amber-400 shadow-md ring-2 ring-amber-500/20"
              : "bg-gradient-to-br from-white to-amber-50/30 border-slate-200/90 hover:border-amber-300 hover:shadow-md hover:-translate-y-1"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] sm:text-xs font-bold text-amber-700 uppercase tracking-wider">{t.activeGaps}</span>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shadow-2xs border border-amber-100">
              <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-600 mt-2 sm:mt-3">
            {data.summary.competencies_with_gaps}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
            <span className="truncate">{t.activeGapsDesc}</span>
            <span className="text-[9px] sm:text-[10px] text-amber-700 font-bold hidden sm:inline">Filter gaps</span>
          </div>
        </div>

        {/* Mastered Skills */}
        <div
          onClick={() => handleStatCardClick("mastered")}
          className={`rounded-2xl p-4 sm:p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "mastered"
              ? "bg-gradient-to-br from-white to-emerald-50/70 border-emerald-400 shadow-md ring-2 ring-emerald-500/20"
              : "bg-gradient-to-br from-white to-emerald-50/30 border-slate-200/90 hover:border-emerald-300 hover:shadow-md hover:-translate-y-1"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] sm:text-xs font-bold text-emerald-700 uppercase tracking-wider">{t.masteredSkills}</span>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-2xs border border-emerald-100">
              <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 mt-2 sm:mt-3">
            {data.summary.mastered_competencies}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
            <span className="truncate">{t.masteredSkillsDesc}</span>
            <span className="text-[9px] sm:text-[10px] text-emerald-700 font-bold hidden sm:inline">Filter</span>
          </div>
        </div>

        {/* Learning Courses */}
        <div
          onClick={() => scrollToSection("learning-pathways")}
          className="rounded-2xl bg-gradient-to-br from-white to-purple-50/30 border border-slate-200/90 p-4 sm:p-5 hover:border-purple-300 hover:shadow-md hover:-translate-y-1 transition-all duration-200 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] sm:text-xs font-bold text-purple-700 uppercase tracking-wider">{t.learningCourses}</span>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shadow-2xs border border-purple-100">
              <BookOpen className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-purple-600 mt-2 sm:mt-3">
            {data.summary.total_recommendations}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
            <span className="truncate">{t.learningCoursesDesc}</span>
            <span className="text-[9px] sm:text-[10px] text-purple-600 font-bold hidden sm:inline">Courses</span>
          </div>
        </div>
      </div>

      {/* 3D Interactive Skill Galaxy */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Brain className="w-5 h-5 text-indigo-600" />
              {t.topographyTitle}
            </h2>
            <p className="text-xs text-slate-500">
              Interactive 3D representation. Hover nodes for details or click any sphere to highlight it in the dashboard.
            </p>
          </div>
        </div>

        <ThreeSkillGalaxy
          activeSkill={selectedCompetency}
          onSelectSkill={(skillName) => {
            setSelectedCompetency(skillName);
            setSearchQuery(skillName);
            scrollToSection("benchmark-matrix");
          }}
        />
      </div>

      {/* Priority Gap Engine & Recommendations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Priority Gap Engine */}
        <div className="lg:col-span-7 space-y-6">
          <div className="pleasant-card rounded-3xl p-6 sm:p-7">
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base sm:text-lg font-extrabold text-slate-900 flex items-center gap-2">
                    <Target className="w-5 h-5 text-amber-600" />
                    {t.skillGapEngineTitle}
                  </h2>
                  <button
                    onClick={() => setShowFormulaHelp(!showFormulaHelp)}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                    title="Explain Formula"
                  >
                    <HelpCircle className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  {t.skillGapEngineFormula}
                </p>
              </div>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/90 text-amber-800 shadow-2xs">
                {data.priority_gaps.length} {t.actionableGaps}
              </span>
            </div>

            {/* Formula Explanation Banner */}
            {showFormulaHelp && (
              <div className="mb-4 p-4 rounded-2xl bg-amber-50/80 border border-amber-200/90 text-xs text-amber-950 space-y-1.5 animate-in fade-in">
                <div className="font-bold flex items-center gap-1.5 text-amber-900">
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  Deterministic Ranking Formula:
                </div>
                <p className="text-slate-800 leading-relaxed font-mono bg-white/70 p-2 rounded-xl border border-amber-200/50">
                  Priority = (Gap × 2) + (Criticality Weight × 3) + Target Level
                </p>
                <p className="text-slate-600 text-[11px]">
                  Where <em>Criticality</em> = 2 if tagged mission-critical for MoSPI operations, and <em>Gap</em> = Required Level − Current Level.
                </p>
              </div>
            )}

            <div className="space-y-3">
              {data.priority_gaps.map((gap, idx) => {
                const isSelected = selectedCompetency === gap.competency_name;
                return (
                  <div
                    key={gap.competency_id}
                    onClick={() => setSelectedCompetency(gap.competency_name)}
                    className={`p-4 sm:p-5 rounded-2xl border transition-all duration-200 cursor-pointer ${
                      isSelected
                        ? "bg-gradient-to-r from-indigo-50/90 via-purple-50/40 to-white border-indigo-300 shadow-sm ring-2 ring-indigo-400/25"
                        : "bg-white/90 border-slate-200/90 hover:border-indigo-200 hover:bg-slate-50/80 hover:shadow-xs"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-bold px-2 py-0.5 rounded-lg bg-slate-100 text-slate-700">
                          #{idx + 1}
                        </span>
                        <span className="font-bold text-slate-900 text-sm sm:text-base">
                          {gap.competency_name}
                        </span>
                        {gap.is_critical && (
                          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-700 shadow-2xs">
                            {t.critical}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-600">
                        {t.priorityScore} <span className="text-amber-700 font-extrabold">{gap.priority_score}</span>
                      </div>
                    </div>

                    {/* Level comparison visual bars */}
                    <div className="flex items-center gap-3 sm:gap-4 mt-3">
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className="text-slate-600 font-medium">
                            {t.currentLevel} <strong className="text-slate-900">Level {gap.current_level} ({gap.current_level_label})</strong>
                          </span>
                          <span className="text-indigo-700 font-bold">
                            {t.targetLevel} <strong>Level {gap.required_level} ({gap.required_level_label})</strong>
                          </span>
                        </div>
                        <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-2xs">
                          <div
                            className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-full rounded-full transition-all"
                            style={{ width: `${(gap.current_level / 5) * 100}%` }}
                            title={`Current Level ${gap.current_level}`}
                          />
                          <div
                            className="bg-gradient-to-r from-amber-400 to-amber-500 h-full transition-all border-l border-white/60"
                            style={{ width: `${(gap.gap / 5) * 100}%` }}
                            title={`Deficit: ${gap.gap} Level(s)`}
                          />
                        </div>
                      </div>
                      <div className="text-right flex items-center gap-2 shrink-0">
                        <span className="text-xs font-bold px-2.5 py-1 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 text-amber-800 border border-amber-200/90 shadow-2xs">
                          -{gap.gap} {t.levelGap}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenAssessment();
                          }}
                          className="p-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-xs hover:shadow-md hover:scale-105 active:scale-95 transition-all"
                          title="Assess Competency"
                        >
                          <Zap className="w-3.5 h-3.5 fill-current text-amber-300" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}

              {data.priority_gaps.length === 0 && (
                <div className="p-8 text-center text-slate-500 text-sm">
                  {t.noGapsDetected}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Recommendations Feed */}
        <div id="learning-pathways" className="lg:col-span-5 space-y-6">
          <div className="pleasant-card rounded-3xl p-6 sm:p-7">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
              <div>
                <h2 className="text-base sm:text-lg font-extrabold text-slate-900 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-indigo-600" />
                  {t.learningPathwaysTitle}
                </h2>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  {t.learningPathwaysSubtitle}
                </p>
              </div>

              {/* Provider Filter */}
              <div className="flex items-center gap-1 bg-slate-100/90 p-0.5 rounded-xl border border-slate-200/80 text-xs">
                <button
                  onClick={() => setProviderFilter("all")}
                  className={`px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all ${
                    providerFilter === "all" ? "bg-white text-indigo-700 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setProviderFilter("igot")}
                  className={`px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all ${
                    providerFilter === "igot" ? "bg-white text-indigo-700 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  iGOT
                </button>
                <button
                  onClick={() => setProviderFilter("tpac")}
                  className={`px-2.5 py-1 rounded-lg font-bold text-[11px] transition-all ${
                    providerFilter === "tpac" ? "bg-white text-indigo-700 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  TPAC
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {filteredRecommendations.slice(0, 6).map((rec, i) => (
                <div
                  key={`${rec.course_id || 'rec'}-${i}`}
                  className="p-4 sm:p-5 rounded-2xl bg-white/90 border border-slate-200/90 hover:border-purple-300 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-purple-50 border border-purple-200/80 text-purple-700 uppercase tracking-wide">
                          {rec.provider || "iGOT Karmayogi"}
                        </span>
                        <span className="text-[11px] text-indigo-600 font-semibold">
                          {t.targets} <strong>{rec.competency_name}</strong>
                        </span>
                        {rec.course_level && (
                          <span className="text-[10px] text-slate-500 bg-slate-100/90 px-2 py-0.5 rounded-md font-medium">
                            {rec.course_level}
                          </span>
                        )}
                      </div>
                      <h3 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {rec.course_title}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                        {rec.reason || `Targets Level ${rec.course_target_level} for ${rec.competency_name}.`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
                    <div className="text-xs text-slate-500 flex items-center gap-2">
                      <span>Duration: <strong className="text-slate-700">{rec.duration_minutes || 180} {t.durationMins}</strong></span>
                      {rec.url && (
                        <a
                          href={rec.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-indigo-600"
                          title="Open Courseware"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                    <button
                      onClick={() => onOpenAssessment(rec.course_id)}
                      className="px-3.5 py-1.5 rounded-xl btn-gradient-primary text-white text-xs font-bold flex items-center gap-1.5 shadow-xs hover:shadow-md transition-all active:scale-95"
                    >
                      {t.launchQuiz}
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}

              {filteredRecommendations.length === 0 && (
                <div className="p-8 text-center text-slate-500 text-sm">
                  {t.noRecommendations}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Role Competency Framework Matrix with Interactive Search & Filter Bar */}
      <div id="benchmark-matrix" className="pleasant-card rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-indigo-600" />
              {t.benchmarkMatrixTitle}
            </h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              {t.benchmarkMatrixDesc}
            </p>
          </div>

          {/* Quick Search Input */}
          <div className="relative w-full md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search competencies..."
              className="w-full pl-9 pr-8 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Domain Filter Pills */}
        <div className="flex items-center justify-between flex-wrap gap-2 border-b border-slate-100 pb-4">
          <div className="flex items-center gap-1.5 flex-wrap">
            {domains.map((dom) => {
              const count = data.competencies.filter((c) =>
                dom === "all" ? true : c.domain.toLowerCase() === dom.toLowerCase()
              ).length;
              return (
                <button
                  key={dom}
                  onClick={() => setFilterDomain(dom)}
                  className={`text-xs px-3 py-1.5 rounded-lg font-medium capitalize transition-all flex items-center gap-1.5 ${
                    filterDomain === dom
                      ? "bg-indigo-600 text-white font-semibold shadow-xs"
                      : "text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200"
                  }`}
                >
                  <span>{dom === "all" ? t.allDomains : dom}</span>
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                      filterDomain === dom ? "bg-white/20 text-white" : "bg-slate-200 text-slate-600"
                    }`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Quick Active Filter Indicator */}
          {cardFilter !== "all" && (
            <div className="flex items-center gap-2 text-xs text-slate-600">
              <span>Filter active: <strong className="capitalize text-slate-900">{cardFilter}</strong></span>
              <button
                onClick={() => setCardFilter("all")}
                className="text-xs text-indigo-600 hover:underline font-medium"
              >
                Clear filter
              </button>
            </div>
          )}
        </div>

        {/* Competencies Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCompetencies.map((comp) => {
            const hasGap = comp.gap > 0;
            const isExpanded = expandedCompId === comp.competency_id;

            return (
              <div
                key={comp.competency_id}
                onClick={() => setExpandedCompId(isExpanded ? null : comp.competency_id)}
                className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer ${
                  hasGap
                    ? "bg-white border-slate-200 hover:border-amber-300 hover:shadow-xs"
                    : "bg-white border-slate-200 hover:border-emerald-300 hover:shadow-xs"
                } ${isExpanded ? "ring-2 ring-indigo-500/20 shadow-sm" : ""}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      {comp.domain}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 mt-0.5">
                      {comp.competency_name}
                    </h4>
                  </div>
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${
                      hasGap
                        ? "bg-amber-50 text-amber-800 border border-amber-200"
                        : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    }`}
                  >
                    {hasGap ? `${t.levelGap} -${comp.gap}` : t.mastered}
                  </span>
                </div>

                <div className="mt-4 space-y-2.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-600">
                      {t.currentLevel} <strong className="text-slate-900">L{comp.current_level} ({comp.current_level_label})</strong>
                    </span>
                    <span className="text-indigo-700 font-semibold">
                      {t.targetLevel} <strong>L{comp.required_level} ({comp.required_level_label})</strong>
                    </span>
                  </div>

                  {/* 5-Step Segmented Proficiency Gauge */}
                  <div className="grid grid-cols-5 gap-1.5 pt-1">
                    {[1, 2, 3, 4, 5].map((lvl) => {
                      const isCurrent = lvl <= comp.current_level;
                      const isRequired = lvl <= comp.required_level;
                      return (
                        <div
                          key={lvl}
                          className={`h-2 rounded-full transition-all duration-300 ${
                            isCurrent
                              ? "bg-indigo-600"
                              : isRequired
                              ? "bg-amber-300"
                              : "bg-slate-200"
                          }`}
                          title={`Level ${lvl}`}
                        />
                      );
                    })}
                  </div>
                </div>

                {/* Expandable Action Drawer */}
                {isExpanded && (
                  <div className="mt-4 pt-3 border-t border-slate-100 space-y-3 animate-in fade-in">
                    <div className="flex items-center justify-between text-xs text-slate-600">
                      <span>Priority: <strong className="text-slate-800">{comp.priority_score}</strong></span>
                      {comp.is_critical && (
                        <span className="text-rose-600 font-semibold text-[11px]">Mission-Critical</span>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenAssessment();
                      }}
                      className="w-full py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border border-indigo-200"
                    >
                      <Zap className="w-3.5 h-3.5 fill-current" />
                      Take Assessment on {comp.competency_name}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredCompetencies.length === 0 && (
          <div className="py-12 text-center text-slate-500 space-y-2">
            <p className="text-sm font-medium">No competencies match your current filter or search query.</p>
            <button
              onClick={() => {
                setFilterDomain("all");
                setCardFilter("all");
                setSearchQuery("");
              }}
              className="text-xs text-indigo-600 hover:underline font-semibold"
            >
              Reset all filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
