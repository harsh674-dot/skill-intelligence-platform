import React from "react";
import { useLanguage } from "@/context/LanguageContext";

export default function AssessmentsPage() {
  const { t } = useLanguage();

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Assessment History
          </h1>
          <p className="mt-2 text-slate-500">
            View all your past assessments and results.
          </p>

          <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="flex flex-col items-center justify-center gap-4 py-12 text-center">
              <h3 className="text-xl font-semibold text-slate-700">
                Assessment History
              </h3>
              <p className="max-w-md text-sm text-slate-500">
                Your past assessments will appear here once you complete
                diagnostic or learning quizzes. Start an assessment from your
                dashboard to see results here.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
