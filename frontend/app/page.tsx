"use client";

import React, { useEffect, useState, useCallback } from "react";
import Navbar, { DemoPersona, DEMO_PERSONAS } from "@/components/Navbar";
import EmployeeDashboard from "@/components/EmployeeDashboard";
import AssessmentModal from "@/components/AssessmentModal";
import AdminStudio from "@/components/AdminStudio";
import WorkforceAnalytics from "@/components/WorkforceAnalytics";
import JudgeTourGuide from "@/components/JudgeTourGuide";
import {
  getHealth,
  login,
  getMe,
  getEmployeeDashboard,
  EmployeeDashboardData,
  UserResponse,
} from "@/lib/api";
import { AlertCircle, Zap } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function Home() {
  const { t } = useLanguage();
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);
  const [currentTab, setCurrentTab] = useState<"employee" | "assessments" | "rag_studio" | "admin">("employee");
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);

  // Employee Dashboard Data
  const [dashboardData, setDashboardData] = useState<EmployeeDashboardData | null>(null);
  const [loadingDashboard, setLoadingDashboard] = useState<boolean>(false);
  const [dashboardError, setDashboardError] = useState<string | null>(null);

  // Assessment Modal state
  const [isAssessmentOpen, setIsAssessmentOpen] = useState<boolean>(false);
  const [assessmentCourseId, setAssessmentCourseId] = useState<string | undefined>(undefined);

  // Pleasant interactive toast notification
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((current) => (current === msg ? null : current));
    }, 3200);
  }, []);

  // Check health and initialize default demo session (Ananya Sharma)
  useEffect(() => {
    getHealth()
      .then(() => setIsBackendOnline(true))
      .catch(() => setIsBackendOnline(false));

    // Default to Ananya Sharma
    handleSwitchPersona(DEMO_PERSONAS[0]);
  }, []);

  const handleSwitchPersona = async (persona: DemoPersona) => {
    try {
      setDashboardError(null);

      // 1. Optimistic instant UI update
      setCurrentUser({
        id: "demo-" + persona.email,
        email: persona.email,
        full_name: persona.name,
        access_role: persona.access_role,
      });

      // Auto-switch tabs based on persona
      if (persona.access_role === "admin") {
        setCurrentTab("admin");
      } else {
        setCurrentTab("employee");
      }

      showToast(`Active Persona: ${persona.name} (${persona.role})`);

      // 2. Instant cache hydration (Stale-While-Revalidate)
      let hasCachedData = false;
      if (typeof window !== "undefined") {
        try {
          const cached = sessionStorage.getItem("cache_dash_" + persona.email);
          if (cached) {
            setDashboardData(JSON.parse(cached));
            hasCachedData = true;
          }
        } catch {}
      }

      if (!hasCachedData && persona.access_role === "employee") {
        setLoadingDashboard(true);
      }

      // 3. Fast token retrieval (use cached token or authenticate)
      let authToken = typeof window !== "undefined" ? sessionStorage.getItem("token_" + persona.email) : null;
      if (!authToken) {
        const authRes = await login(persona.email, "Demo@12345");
        authToken = authRes.access_token;
        if (typeof window !== "undefined") {
          try {
            sessionStorage.setItem("token_" + persona.email, authToken);
          } catch {}
        }
      }
      setToken(authToken);

      // 4. Parallel fetch for profile and dashboard
      if (persona.access_role === "employee") {
        const [me, dash] = await Promise.all([
          getMe(authToken).catch(() => null),
          getEmployeeDashboard(authToken).catch((err) => {
            console.warn("Could not fetch employee dashboard:", err);
            return null;
          }),
        ]);

        if (me) setCurrentUser(me);
        if (dash) {
          setDashboardData(dash);
          if (typeof window !== "undefined") {
            try {
              sessionStorage.setItem("cache_dash_" + persona.email, JSON.stringify(dash));
            } catch {}
          }
        }
      } else {
        const me = await getMe(authToken).catch(() => null);
        if (me) setCurrentUser(me);
      }
    } catch (err: any) {
      setDashboardError(err.message || "Failed to switch persona.");
    } finally {
      setLoadingDashboard(false);
    }
  };

  const refreshDashboard = useCallback(async () => {
    if (!token) return;
    try {
      setLoadingDashboard(true);
      const dash = await getEmployeeDashboard(token);
      setDashboardData(dash);
      showToast("40/60 Rule Applied: Competency level updated & gaps refreshed!");
      if (typeof window !== "undefined" && currentUser?.email) {
        try {
          sessionStorage.setItem("cache_dash_" + currentUser.email, JSON.stringify(dash));
        } catch {}
      }
    } catch (err: any) {
      console.error("Dashboard refresh error:", err);
    } finally {
      setLoadingDashboard(false);
    }
  }, [token, currentUser?.email, showToast]);

  const handleOpenAssessment = (courseId?: string) => {
    setAssessmentCourseId(courseId);
    setIsAssessmentOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      {/* Top Navbar */}
      <Navbar
        currentUser={currentUser}
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onSwitchPersona={handleSwitchPersona}
        isBackendOnline={isBackendOnline}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 pt-6 sm:pt-8 pb-24 md:pb-12">
        {dashboardError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{dashboardError}</span>
            </div>
            <button
              onClick={() => handleSwitchPersona(DEMO_PERSONAS[0])}
              className="underline hover:text-rose-900"
            >
              {t.retryBtn}
            </button>
          </div>
        )}

        {/* Tab 1: Employee Dashboard */}
        {currentTab === "employee" && (
          <div>
            {loadingDashboard && !dashboardData ? (
              <div className="py-24 text-center space-y-4">
                <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-sm text-slate-600 font-medium">{t.loadingMatrix}</p>
              </div>
            ) : dashboardData ? (
              <EmployeeDashboard
                data={dashboardData}
                onOpenAssessment={handleOpenAssessment}
              />
            ) : (
              <div className="py-24 text-center space-y-3">
                <p className="text-slate-500 text-sm">
                  {t.noActiveRole}
                </p>
                <button
                  onClick={() => handleSwitchPersona(DEMO_PERSONAS[0])}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold"
                >
                  {t.loadAnanya}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Assessment Arena */}
        {currentTab === "assessments" && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center space-y-4 shadow-xs">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
                <Zap className="w-6 h-6 fill-current" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
                {t.assessmentArenaTitle}
              </h1>
              <p className="text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
                {t.assessmentArenaDesc}
              </p>

              <div className="pt-2 flex items-center justify-center gap-4">
                <button
                  onClick={() => handleOpenAssessment()}
                  className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold flex items-center gap-2 transition-colors shadow-xs"
                >
                  <Zap className="w-4 h-4 fill-current" />
                  {t.launchAssessment}
                </button>
              </div>
            </div>

            {/* If dashboard data is available, show the gaps ready for assessment */}
            {dashboardData && (
              <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
                <h2 className="text-base font-bold text-slate-900">
                  {t.targetedCompetencies}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {dashboardData.priority_gaps.slice(0, 6).map((gap) => (
                    <div
                      key={gap.competency_id}
                      className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between"
                    >
                      <span className="text-xs font-semibold text-slate-900">
                        {gap.competency_name}
                      </span>
                      <span className="text-xs font-medium px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                        {t.totalPriority} {gap.priority_score}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: RAG & AI Studio */}
        {currentTab === "rag_studio" && token && (
          <AdminStudio
            token={token}
            onSwitchToAdmin={() => handleSwitchPersona(DEMO_PERSONAS[3])}
          />
        )}

        {/* Tab 4: Workforce Analytics (Admin) */}
        {currentTab === "admin" && token && (
          <WorkforceAnalytics
            token={token}
            onSwitchToAdmin={() => handleSwitchPersona(DEMO_PERSONAS[3])}
          />
        )}
      </main>

      {/* Assessment Modal Dialog */}
      {isAssessmentOpen && token && (
        <AssessmentModal
          token={token}
          courseId={assessmentCourseId}
          onClose={() => setIsAssessmentOpen(false)}
          onAssessmentCompleted={refreshDashboard}
        />
      )}

      {/* Floating Interactive Judge Tour Ribbon */}
      <JudgeTourGuide
        onSelectTab={setCurrentTab}
        onSwitchPersona={handleSwitchPersona}
        onOpenAssessment={() => handleOpenAssessment()}
      />

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-20 md:bottom-6 left-4 md:left-6 z-50 animate-in slide-in-from-bottom-3 fade-in duration-200">
          <div className="flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-slate-900 text-white shadow-xl border border-slate-800 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
}