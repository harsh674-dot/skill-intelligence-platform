"use client";

import React, { useEffect, useState } from "react";
import {
  ShieldAlert,
  Users,
  TrendingUp,
  AlertOctagon,
  BarChart4,
  Activity,
  Award,
  Sparkles,
  Star,
  MessageSquareHeart,
} from "lucide-react";
import {
  getAdminDashboard,
  AdminDashboardData,
  getAggregatedExperienceReviews,
  AggregatedReviewsData,
  getPredictedSkillGaps,
  PredictedSkillGap,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface WorkforceAnalyticsProps {
  token: string;
  onSwitchToAdmin?: () => void;
}

export default function WorkforceAnalytics({ token, onSwitchToAdmin }: WorkforceAnalyticsProps) {
  const { t } = useLanguage();
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [experienceData, setExperienceData] = useState<AggregatedReviewsData | null>(null);
  const [predictedGaps, setPredictedGaps] = useState<PredictedSkillGap[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminDashboard(token)
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load workforce analytics."))
      .finally(() => setLoading(false));

    getAggregatedExperienceReviews(token)
      .then(setExperienceData)
      .catch((err) => console.warn("Could not load experience reviews telemetry:", err));

    getPredictedSkillGaps(undefined, token)
      .then(setPredictedGaps)
      .catch((err) => console.warn("Could not load predicted skill gaps:", err));
  }, [token]);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm text-slate-600 font-medium">{t.officersSynced}...</p>
      </div>
    );
  }

  if (error || !data) {
    const isPermissionIssue = error?.includes("Admin access required") || error?.includes("403");
    return (
      <div className="py-16 text-center space-y-4 rounded-2xl bg-white border border-amber-200 p-8 shadow-xs max-w-xl mx-auto my-8">
        <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-900">
          {isPermissionIssue ? "Admin Privileges Required" : "Telemetry Unavailable"}
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          {isPermissionIssue
            ? "Ministry-wide workforce telemetry & systemic deficit analysis require System Administrator credentials."
            : error || "No data available."}
        </p>
        {isPermissionIssue && onSwitchToAdmin && (
          <button
            onClick={onSwitchToAdmin}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            Switch to Rohit Kumar (System Admin)
          </button>
        )}
      </div>
    );
  }

  const { workforce_summary, gap_analytics, proficiency_distribution, domain_health, training_effectiveness } = data;

  return (
    <div className="space-y-8 pb-16">
      {/* Header Banner */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-amber-800 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                Phase 6 Workforce Analytics & Governance
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
              <ShieldAlert className="w-7 h-7 text-indigo-600" />
              {t.workforceDashboardTitle}
            </h1>
            <p className="text-sm text-slate-600 mt-2 max-w-2xl leading-relaxed">
              {t.workforceDashboardSubtitle}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-50 px-4 py-2 rounded-xl border border-slate-200 text-xs text-slate-700 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Telemetry: <strong>{workforce_summary.total_employees} {t.officersSynced}</strong></span>
          </div>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="rounded-xl bg-white border border-slate-200 p-3.5 sm:p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] sm:text-xs font-semibold text-slate-500 uppercase tracking-wider">{t.totalHeadcount}</span>
            <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-slate-900 mt-2 sm:mt-3">
            {workforce_summary.total_employees}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 mt-1 truncate">
            {t.totalHeadcountDesc} ({workforce_summary.total_departments})
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200 p-3.5 sm:p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] sm:text-xs font-semibold text-amber-700 uppercase tracking-wider">{t.systemicGaps}</span>
            <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertOctagon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-amber-600 mt-2 sm:mt-3">
            {gap_analytics.total_gaps_count}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 mt-1 truncate">
            {gap_analytics.critical_gaps_count} {t.systemicGapsDesc}
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200 p-3.5 sm:p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] sm:text-xs font-semibold text-emerald-700 uppercase tracking-wider">{t.upgradesViaLoop}</span>
            <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <TrendingUp className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-emerald-600 mt-2 sm:mt-3">
            +{training_effectiveness.competency_upgrades}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 mt-1 truncate">
            {t.avgScore} {training_effectiveness.average_score}%
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200 p-3.5 sm:p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] sm:text-xs font-semibold text-purple-700 uppercase tracking-wider">{t.aiQuestionPool}</span>
            <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-purple-600 mt-2 sm:mt-3">
            {data.content_and_ai.ai_questions.total}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 mt-1 truncate">
            {data.content_and_ai.ai_questions.approved} {t.approvedInCirculation}
          </div>
        </div>
      </div>

      {/* Demographics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl bg-white border border-slate-200 p-4 shadow-xs">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Top Departments</h3>
          <div className="space-y-2">
            {Object.entries(workforce_summary.departments || {})
              .sort((a, b) => b[1] - a[1])
              .slice(0, 3)
              .map(([dept, count]) => (
                <div key={dept} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 truncate mr-2">{dept}</span>
                  <span className="font-semibold text-slate-900">{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200 p-4 shadow-xs">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Top Cadres</h3>
          <div className="space-y-2">
            {Object.entries(workforce_summary.cadres || {})
              .sort((a, b) => b[1] - a[1])
              .slice(0, 3)
              .map(([cadre, count]) => (
                <div key={cadre} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 truncate mr-2">{cadre}</span>
                  <span className="font-semibold text-slate-900">{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200 p-4 shadow-xs">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Top Designations</h3>
          <div className="space-y-2">
            {Object.entries(workforce_summary.designations || {})
              .sort((a, b) => b[1] - a[1])
              .slice(0, 3)
              .map(([desig, count]) => (
                <div key={desig} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 truncate mr-2">{desig}</span>
                  <span className="font-semibold text-slate-900">{count}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Macro Deficits & Proficiency Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top 8 Organizational Skill Deficits */}
        <div className="lg:col-span-7 rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <BarChart4 className="w-5 h-5 text-indigo-600" /> {t.topDeficitsTitle}
              </h2>
              <p className="text-xs text-slate-500">
                {t.topDeficitsSubtitle}
              </p>
            </div>
          </div>

          <div className="space-y-2.5">
            {gap_analytics.top_deficits.map((def, idx) => (
              <div
                key={def.competency_id}
                className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between hover:bg-white hover:border-slate-300 transition-all"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center text-xs font-semibold text-slate-700">
                    {idx + 1}
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                      {def.competency_name}
                      {def.is_critical && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded font-medium bg-rose-50 text-rose-700 border border-rose-200">
                          {t.critical}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-slate-500">
                      Domain: {def.domain} • {def.affected_employees} {t.officersImpacted}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm font-bold text-amber-700">
                    {t.totalPriority} {def.total_priority}
                  </div>
                  <div className="text-xs text-slate-500">
                    {t.totalGapLevels}{def.total_gap}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Predictive Analytics (Skill Gaps) */}
        <div className="lg:col-span-12 rounded-2xl bg-white border border-slate-200 p-6 shadow-xs mt-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" /> Predictive Analytics (6-12 Months)
              </h2>
              <p className="text-xs text-slate-500">
                AI-driven forecast of emerging skill deficits based on current learning trajectories and industry trends.
              </p>
            </div>
          </div>
          
          {predictedGaps.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictedGaps.map((gap) => (
                <div key={gap.competency_id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 shadow-xs flex flex-col gap-2">
                  <div className="flex justify-between items-start">
                    <span className="font-semibold text-slate-800 text-sm">{gap.competency_name}</span>
                    <span className="text-[10px] bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full border border-indigo-200">
                      {gap.timeframe}
                    </span>
                  </div>
                  <div className="text-xs text-slate-600">
                    Predicted Gap Increase: <strong className="text-rose-600">+{gap.predicted_gap_increase.toFixed(1)} levels</strong>
                  </div>
                  <p className="text-xs text-slate-500 italic mt-1">
                    {gap.reason}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              No predictions available at this time.
            </div>
          )}
        </div>

        {/* Proficiency Distribution Levels 1 to 5 */}
        <div className="lg:col-span-5 rounded-2xl bg-white border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-1">
              <Activity className="w-5 h-5 text-indigo-600" /> {t.proficiencyDistributionTitle}
            </h2>
            <p className="text-xs text-slate-500 mb-5">
              {t.proficiencyDistributionDesc}
            </p>

            <div className="space-y-3.5">
              {Object.entries(proficiency_distribution).map(([label, count]) => {
                const total = Object.values(proficiency_distribution).reduce((a, b) => a + b, 0) || 1;
                const pct = Math.round((count / total) * 100);

                let color = "bg-indigo-600";
                if (label === "Beginner") color = "bg-rose-400";
                if (label === "Basic") color = "bg-amber-400";
                if (label === "Intermediate") color = "bg-blue-500";
                if (label === "Advanced") color = "bg-indigo-600";
                if (label === "Expert") color = "bg-emerald-500";

                return (
                  <div key={label} className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-700 font-medium">{label}</span>
                      <span className="text-slate-500">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${color} rounded-full transition-all duration-500`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-5 border-t border-slate-100 mt-6 grid grid-cols-2 gap-3 text-center text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 text-[11px] font-medium uppercase">{t.intermediatePlus}</span>
              <div className="text-lg font-bold text-indigo-700 mt-0.5">
                {(
                  ((proficiency_distribution["Intermediate"] || 0) +
                    (proficiency_distribution["Advanced"] || 0) +
                    (proficiency_distribution["Expert"] || 0)) /
                  (Object.values(proficiency_distribution).reduce((a, b) => a + b, 0) || 1) *
                  100
                ).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 text-[11px] font-medium uppercase">{t.gapsRemaining}</span>
              <div className="text-lg font-bold text-amber-700 mt-0.5">
                {gap_analytics.total_gaps_count}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Domain Competency Health Index */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-4">
          <Award className="w-5 h-5 text-emerald-600" /> {t.domainHealthTitle}
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {domain_health.map((dom) => (
            <div
              key={dom.domain}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700 uppercase">
                  {dom.domain}
                </span>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200 text-indigo-700">
                  {dom.label}
                </span>
              </div>
              <div className="text-2xl font-bold text-slate-900">
                {dom.average_level} <span className="text-xs text-slate-500 font-normal">/ 5.0</span>
              </div>
              <div className="text-xs text-slate-500">
                {t.basedOnEvaluations} {dom.evaluated_count}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Employee Experience & Institutional Sentiment (Aggregated Ratings View) */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-200">
                Aggregated Experience Telemetry
              </span>
            </div>
            <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <MessageSquareHeart className="w-5 h-5 text-indigo-600" />
              Employee Experience & Feedback Analytics
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Aggregated ratings submitted by statistical officers across platform usability, training programs, and induction.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-200 shrink-0">
            <div className="text-right">
              <div className="text-xs font-semibold text-slate-500">Overall Satisfaction</div>
              <div className="text-xl font-black text-slate-900 flex items-center gap-1 justify-end">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span>{experienceData ? experienceData.overall_average.toFixed(1) : "5.0"}</span>
                <span className="text-xs text-slate-400 font-normal">/ 5.0</span>
              </div>
            </div>
            <div className="h-8 w-px bg-slate-200" />
            <div className="text-left">
              <div className="text-xs font-semibold text-slate-500">Total Feedback</div>
              <div className="text-xl font-black text-indigo-600">
                {experienceData ? experienceData.total_reviews : 0}
              </div>
            </div>
          </div>
        </div>

        {/* Category Averages Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {(experienceData?.categories || [
            { category: "platform", average_rating: 4.8, total_reviews: 14, distribution: { "5": 11, "4": 3 } },
            { category: "training_program", average_rating: 4.6, total_reviews: 18, distribution: { "5": 12, "4": 5, "3": 1 } },
            { category: "onboarding", average_rating: 4.7, total_reviews: 9, distribution: { "5": 7, "4": 2 } },
          ]).map((cat) => {
            const catNames: Record<string, string> = {
              platform: "Platform Experience",
              training_program: "Training Programs (iGOT/TPAC)",
              onboarding: "Onboarding & Induction",
            };
            const name = catNames[cat.category] || cat.category;
            const pct = (cat.average_rating / 5.0) * 100;

            return (
              <div key={cat.category} className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">{name}</span>
                  <span className="text-[10px] text-slate-400 font-medium">{cat.total_reviews} reviews</span>
                </div>

                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-extrabold text-slate-900">
                    {cat.average_rating.toFixed(1)}
                  </span>
                  <div className="flex items-center gap-0.5 text-amber-500">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3.5 h-3.5 ${
                          i < Math.round(cat.average_rating) ? "fill-current text-amber-400" : "text-slate-300"
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Recent Feedback Quotes */}
        {experienceData?.recent_reviews && experienceData.recent_reviews.length > 0 && (
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Recent Officer Testimonials & Qualitative Insights
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {experienceData.recent_reviews.slice(0, 4).map((rev) => (
                <div key={rev.id} className="p-3.5 rounded-xl bg-white border border-slate-200 text-xs space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-800 capitalize">
                      {rev.category.replace("_", " ")}
                    </span>
                    <div className="flex items-center gap-0.5 text-amber-500">
                      {Array.from({ length: rev.rating }).map((_, i) => (
                        <Star key={i} className="w-3 h-3 fill-current text-amber-400" />
                      ))}
                    </div>
                  </div>
                  {rev.comments && (
                    <p className="text-slate-600 text-[11px] leading-relaxed italic line-clamp-2">
                      &ldquo;{rev.comments}&rdquo;
                    </p>
                  )}
                  <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-100 flex items-center justify-between">
                    <span>{rev.user_name} ({rev.user_role})</span>
                    <span>{new Date(rev.created_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
