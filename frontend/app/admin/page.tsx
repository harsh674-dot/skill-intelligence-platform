import React from "react";
import { useLanguage } from "@/context/LanguageContext";

export default function AdminPage() {
  const { t } = useLanguage();

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Admin Studio
          </h1>
          <p className="mt-2 text-slate-500">
            Manage users, courses, questions, audit logs, and DPDP consent records.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                title: "User Management",
                desc: "View and manage all employee accounts including access roles.",
                icon: "👥",
                route: "/admin/users",
              },
              {
                title: "Course Catalog",
                desc: "Create, update, and organize training courses.",
                icon: "📚",
                route: "/courses",
              },
              {
                title: "Question Bank",
                desc: "Manage assessment questions by competency and difficulty.",
                icon: "❓",
                route: "/questions",
              },
              {
                title: "Audit Logs",
                desc: "Review all system actions and API activity logs.",
                icon: "📋",
                route: "/audit",
              },
              {
                title: "DPDP Consent",
                desc: "Manage Data Protection and Privacy consent records.",
                icon: "🔒",
                route: "/dpdp",
              },
              {
                title: "Analytics",
                desc: "View predictive skill gaps and training effectiveness metrics.",
                icon: "📊",
                route: "/analytics",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="text-3xl">{card.icon}</div>
                <h3 className="mt-3 text-lg font-semibold text-slate-800">
                  {card.title}
                </h3>
                <p className="mt-1 text-sm text-slate-500">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
