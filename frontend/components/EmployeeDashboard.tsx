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
      {/* Welcome Banner with Light Gradient Glow */}
      <div className="relative rounded-3xl bg-gradient-to-br from-white via-indigo-50/25 to-sky-50/30 border border-slate-200/90 p-6 sm:p-8 shadow-xs overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-72 h-72 bg-gradient-to-br from-indigo-200/20 to-purple-200/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200 shadow-2xs">
                Official Statistical System • MoSPI Capacity Engine
              </span>
              <span className="text-xs text-slate-500 font-medium">
                ISO 9001:2015 Benchmark
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
              {t.welcomeBack}{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-indigo-800">
                {data.employee.email.split("@")[0].replace(".", " ").toUpperCase()}
              </span>
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              {t.assignedRole} <span className="font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">{data.employee.role_name}</span>.{" "}
              {t.welcomeDesc}
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => onOpenAssessment()}
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:scale-98 text-white font-semibold text-sm flex items-center gap-2 shadow-xs hover:shadow-md transition-all duration-150"
            >
              <Zap className="w-4 h-4 fill-current" />
              {t.takeAssessment}
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Clickable Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Required Skills */}
        <div
          onClick={() => handleStatCardClick("all")}
          className={`rounded-2xl p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "all"
              ? "bg-white border-indigo-400 shadow-sm ring-2 ring-indigo-500/20"
              : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm hover:-translate-y-0.5"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t.requiredSkills}</span>
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-2xs">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900 mt-3">
            {data.summary.total_competencies}
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
            <span>{t.requiredSkillsDesc}</span>
            <span className="text-[10px] text-indigo-600 font-semibold">Click to show all</span>
          </div>
        </div>

        {/* Active Gaps */}
        <div
          onClick={() => handleStatCardClick("gaps")}
          className={`rounded-2xl p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "gaps"
              ? "bg-amber-50/40 border-amber-400 shadow-sm ring-2 ring-amber-500/20"
              : "bg-white border-slate-200 hover:border-amber-300 hover:shadow-sm hover:-translate-y-0.5"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider">{t.activeGaps}</span>
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shadow-2xs">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-600 mt-3">
            {data.summary.competencies_with_gaps}
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
            <span>{t.activeGapsDesc}</span>
            <span className="text-[10px] text-amber-700 font-semibold">Filter gaps</span>
          </div>
        </div>

        {/* Mastered Skills */}
        <div
          onClick={() => handleStatCardClick("mastered")}
          className={`rounded-2xl p-5 border transition-all duration-200 cursor-pointer ${
            cardFilter === "mastered"
              ? "bg-emerald-50/40 border-emerald-400 shadow-sm ring-2 ring-emerald-500/20"
              : "bg-white border-slate-200 hover:border-emerald-300 hover:shadow-sm hover:-translate-y-0.5"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">{t.masteredSkills}</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-2xs">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-emerald-600 mt-3">
            {data.summary.mastered_competencies}
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
            <span>{t.masteredSkillsDesc}</span>
            <span className="text-[10px] text-emerald-700 font-semibold">Filter mastered</span>
          </div>
        </div>

        {/* Learning Courses */}
        <div
          onClick={() => scrollToSection("learning-pathways")}
          className="rounded-2xl bg-white border border-slate-200 p-5 hover:border-purple-300 hover:shadow-sm hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-purple-700 uppercase tracking-wider">{t.learningCourses}</span>
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shadow-2xs">
              <BookOpen className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-purple-600 mt-3">
            {data.summary.total_recommendations}
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
            <span>{t.learningCoursesDesc}</span>
            <span className="text-[10px] text-purple-600 font-semibold flex items-center gap-0.5">
              Jump to courses <ArrowUpRight className="w-3 h-3" />
            </span>
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
          <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Target className="w-5 h-5 text-amber-600" />
                    {t.skillGapEngineTitle}
                  </h2>
                  <button
                    onClick={() => setShowFormulaHelp(!showFormulaHelp)}
                    className="text-slate-400 hover:text-slate-600"
                    title="Explain Formula"
                  >
                    <HelpCircle className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-slate-500">
                  {t.skillGapEngineFormula}
                </p>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800">
                {data.priority_gaps.length} {t.actionableGaps}
              </span>
            </div>

            {/* Formula Explanation Banner */}
            {showFormulaHelp && (
              <div className="mb-4 p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-1.5 animate-in fade-in">
                <div className="font-bold flex items-center gap-1.5">
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  Deterministic Ranking Formula:
                </div>
                <p className="text-slate-700 leading-relaxed font-mono">
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
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? "bg-indigo-50/70 border-indigo-300 shadow-xs ring-1 ring-indigo-400/30"
                        : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/60"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                          #{idx + 1}
                        </span>
                        <span className="font-semibold text-slate-900 text-sm">
                          {gap.competency_name}
                        </span>
                        {gap.is_critical && (
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-700">
                            {t.critical}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-600">
                        {t.priorityScore} <span className="text-amber-700 font-bold">{gap.priority_score}</span>
                      </div>
                    </div>

                    {/* Level comparison visual bars */}
                    <div className="flex items-center gap-3 mt-3">
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-600">
                            {t.currentLevel} <strong className="text-slate-900">Level {gap.current_level} ({gap.current_level_label})</strong>
                          </span>
                          <span className="text-indigo-700 font-semibold">
                            {t.targetLevel} <strong>Level {gap.required_level} ({gap.required_level_label})</strong>
                          </span>
                        </div>
                        <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-2xs">
                          <div
                            className="bg-indigo-600 h-full rounded-full transition-all"
                            style={{ width: `${(gap.current_level / 5) * 100}%` }}
                            title={`Current Level ${gap.current_level}`}
                          />
                          <div
                            className="bg-amber-400 h-full transition-all border-l border-white"
                            style={{ width: `${(gap.gap / 5) * 100}%` }}
                            title={`Deficit: ${gap.gap} Level(s)`}
                          />
                        </div>
                      </div>
                      <div className="text-right flex items-center gap-2">
                        <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-200">
                          -{gap.gap} {t.levelGap}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenAssessment();
                          }}
                          className="p-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200"
                          title="Assess Competency"
                        >
                          <Zap className="w-3.5 h-3.5 fill-current" />
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
          <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-indigo-600" />
                  {t.learningPathwaysTitle}
                </h2>
                <p className="text-xs text-slate-500">
                  {t.learningPathwaysSubtitle}
                </p>
              </div>

              {/* Provider Filter */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
                <button
                  onClick={() => setProviderFilter("all")}
                  className={`px-2 py-0.5 rounded-md font-medium text-[11px] ${
                    providerFilter === "all" ? "bg-white text-indigo-700 shadow-2xs font-semibold" : "text-slate-600"
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setProviderFilter("igot")}
                  className={`px-2 py-0.5 rounded-md font-medium text-[11px] ${
                    providerFilter === "igot" ? "bg-white text-indigo-700 shadow-2xs font-semibold" : "text-slate-600"
                  }`}
                >
                  iGOT
                </button>
                <button
                  onClick={() => setProviderFilter("tpac")}
                  className={`px-2 py-0.5 rounded-md font-medium text-[11px] ${
                    providerFilter === "tpac" ? "bg-white text-indigo-700 shadow-2xs font-semibold" : "text-slate-600"
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
                  className="p-4 rounded-xl bg-white border border-slate-200 hover:border-slate-300 hover:shadow-xs transition-all group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-50 border border-purple-200 text-purple-700 uppercase">
                          {rec.provider || "iGOT Karmayogi"}
                        </span>
                        <span className="text-[11px] text-indigo-600 font-medium">
                          {t.targets} <strong>{rec.competency_name}</strong>
                        </span>
                        {rec.course_level && (
                          <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                            {rec.course_level}
                          </span>
                        )}
                      </div>
                      <h3 className="text-sm font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {rec.course_title}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 line-clamp-2">
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
                      className="px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 active:scale-98 text-indigo-700 text-xs font-semibold flex items-center gap-1.5 transition-all border border-indigo-200 shadow-2xs"
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
      <div id="benchmark-matrix" className="rounded-3xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-indigo-600" />
              {t.benchmarkMatrixTitle}
            </h2>
            <p className="text-xs text-slate-500">
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
