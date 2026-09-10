"use client";

import React, { useState } from "react";
import {
  Compass,
  ChevronRight,
  ChevronLeft,
  X,
} from "lucide-react";
import { DemoPersona, DEMO_PERSONAS } from "./Navbar";
import { useLanguage } from "@/context/LanguageContext";

interface Step {
  id: number;
  title: string;
  description: string;
  tab: "employee" | "assessments" | "rag_studio" | "admin";
  personaEmail: string;
  actionLabel?: string;
}

const TOUR_STEPS_EN: Step[] = [
  {
    id: 1,
    title: "1. Employee Baseline & Required Levels",
    description: "Inspect Ananya Sharma (Statistical Officer) benchmarked against MoSPI required competency levels (1–5 scale).",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 2,
    title: "2. Priority Engine Calculation",
    description: "Review gaps ranked by formula: Priority = (Gap × 2) + Criticality Weight + Organizational Priority.",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 3,
    title: "3. Targeted Course Recommendations",
    description: "Inspect courses from iGOT Karmayogi and TPAC dynamically matched to highest-priority skill gaps.",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 4,
    title: "4. Admin Courseware Ingestion & RAG",
    description: "Switch to Admin (Rohit Kumar), upload PDF/DOCX content, and inspect the 384D vector chunks.",
    tab: "rag_studio",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
  {
    id: 5,
    title: "5. Grounded AI Question Generation",
    description: "Prompt the LLM to synthesize MCQs grounded strictly in RAG chunks and approve questions into the live bank.",
    tab: "rag_studio",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
  {
    id: 6,
    title: "6. Employee Quiz & Reassessment",
    description: "Switch back to Employee and launch the assessment arena to test newly acquired learning.",
    tab: "assessments",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 7,
    title: "7. Closing the Loop (40/60 Rule)",
    description: "Submit quiz: 40% previous + 60% evidence updates competency level, reduces gaps, and refreshes recommendations.",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 8,
    title: "8. Workforce Gap Analytics",
    description: "View aggregated macro telemetry across statistical divisions and measure overall training effectiveness.",
    tab: "admin",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
];

const TOUR_STEPS_HI: Step[] = [
  {
    id: 1,
    title: "1. कर्मचारी बेसलाइन और आवश्यक स्तर",
    description: "सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय के आवश्यक दक्षता स्तरों (1-5 पैमाना) के विरुद्ध अनन्या शर्मा (सांख्यिकी अधिकारी) की समीक्षा करें।",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 2,
    title: "2. प्राथमिकता इंजन गणना",
    description: "सूत्र द्वारा श्रेणीबद्ध अंतरालों की समीक्षा करें: प्राथमिकता = (अंतराल × 2) + गंभीरता भार + संगठनात्मक प्राथमिकता।",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 3,
    title: "3. लक्षित पाठ्यक्रम सिफारिशें",
    description: "उच्चतम प्राथमिकता वाले कौशल अंतरालों से गतिशील रूप से मेल खाते iGOT कर्मयोगी और TPAC के पाठ्यक्रमों का अन्वेषण करें।",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 4,
    title: "4. व्यवस्थापक सामग्री प्रविष्टि एवं आरएजी",
    description: "प्रशासक (रोहित कुमार) पर स्विच करें, PDF/DOCX सामग्री अपलोड करें, और 384D वेक्टर भागों का निरीक्षण करें।",
    tab: "rag_studio",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
  {
    id: 5,
    title: "5. आधार-सत्यापित एआई प्रश्न निर्माण",
    description: "आरएजी भागों पर आधारित एमसीक्यू उत्पन्न करने के लिए मॉडल को निर्देश दें और लाइव बैंक में प्रश्नों को अनुमोदित करें।",
    tab: "rag_studio",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
  {
    id: 6,
    title: "6. कर्मचारी क्विज़ एवं पुनर्मूल्यांकन",
    description: "पुनः कर्मचारी पर स्विच करें और नए अधिगम का परीक्षण करने हेतु मूल्यांकन अखाड़ा प्रारंभ करें।",
    tab: "assessments",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 7,
    title: "7. लूप समापन (40/60 नियम)",
    description: "क्विज़ जमा करें: 40% पिछली दक्षता + 60% नया साक्ष्य स्तर को अद्यतन करता है, अंतरालों को कम करता है और सिफारिशों को ताज़ा करता है।",
    tab: "employee",
    personaEmail: "ananya.sharma@demo.gov.in",
  },
  {
    id: 8,
    title: "8. कार्यबल अंतराल विश्लेषण",
    description: "सांख्यिकीय प्रभागों में संकलित मैक्रो टेलीमेट्री देखें और समग्र प्रशिक्षण प्रभावशीलता को मापें।",
    tab: "admin",
    personaEmail: "rohit.kumar@demo.gov.in",
  },
];

interface JudgeTourGuideProps {
  onSelectTab: (tab: "employee" | "assessments" | "rag_studio" | "admin") => void;
  onSwitchPersona: (persona: DemoPersona) => void;
  onOpenAssessment: () => void;
}

export default function JudgeTourGuide({
  onSelectTab,
  onSwitchPersona,
  onOpenAssessment,
}: JudgeTourGuideProps) {
  const { language, t } = useLanguage();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const steps = language === "hi" ? TOUR_STEPS_HI : TOUR_STEPS_EN;
  const step = steps[currentStepIndex];

  const applyStep = (idx: number) => {
    setCurrentStepIndex(idx);
    const targetStep = steps[idx];
    const persona = DEMO_PERSONAS.find((p) => p.email === targetStep.personaEmail);
    if (persona) {
      onSwitchPersona(persona);
    }
    onSelectTab(targetStep.tab);

    if (targetStep.id === 6) {
      onOpenAssessment();
    }
  };

  const nextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      applyStep(currentStepIndex + 1);
    }
  };

  const prevStep = () => {
    if (currentStepIndex > 0) {
      applyStep(currentStepIndex - 1);
    }
  };

  if (isCollapsed) {
    return (
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsCollapsed(false)}
          className="bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 px-4 py-2.5 rounded-xl flex items-center gap-2 text-xs font-semibold shadow-lg transition-all"
        >
          <Compass className="w-4 h-4 text-indigo-600" />
          {t.tourGuideCollapsed} ({currentStepIndex + 1}/8)
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-40 max-w-md w-full px-4 animate-in slide-in-from-bottom-5 duration-200">
      <div className="rounded-2xl bg-white/95 backdrop-blur-md border border-slate-200 shadow-xl relative overflow-hidden">
        {/* Animated Progress Bar */}
        <div className="h-1 w-full bg-slate-100">
          <div
            className="h-full bg-indigo-600 transition-all duration-300 ease-out"
            style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
          />
        </div>

        <div className="p-4 space-y-2">
          {/* Top Header */}
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse" />
              <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">
                {t.tourGuideTitle} ({t.tourGuideStepOf} {step.id} / 8)
              </span>
            </div>

            <button
              onClick={() => setIsCollapsed(true)}
              className="text-slate-400 hover:text-slate-700 text-xs p-1 rounded-md hover:bg-slate-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

        {/* Step Content */}
        <div className="py-2.5 space-y-1">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            {step.title}
          </h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            {step.description}
          </p>
        </div>

        {/* Step Navigation Dots & Buttons */}
        <div className="flex items-center justify-between pt-2.5 border-t border-slate-100">
          <div className="flex items-center gap-1">
            {steps.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => applyStep(idx)}
                className={`h-1.5 rounded-full transition-all ${
                  idx === currentStepIndex
                    ? "w-4 bg-indigo-600"
                    : "w-1.5 bg-slate-200 hover:bg-slate-300"
                }`}
                title={s.title}
              />
            ))}
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={prevStep}
              disabled={currentStepIndex === 0}
              className="p-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <button
              onClick={nextStep}
              disabled={currentStepIndex === steps.length - 1}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg font-medium flex items-center gap-1 disabled:opacity-40 transition-colors shadow-xs"
            >
              {t.stepNext} <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);
}
