"use client";

import React, { useState, useEffect } from "react";
import confetti from "canvas-confetti";
import {
  X,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Zap,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import {
  startAssessment,
  submitAnswer,
  finishAssessment,
  scoreAssessment,
  QuizQuestion,
  ScoreAssessmentResponse,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface AssessmentModalProps {
  token: string;
  courseId?: string;
  onClose: () => void;
  onAssessmentCompleted: () => void;
}

export default function AssessmentModal({
  token,
  courseId,
  onClose,
  onAssessmentCompleted,
}: AssessmentModalProps) {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [answersSubmitted, setAnswersSubmitted] = useState<boolean>(false);
  const [answerResults, setAnswerResults] = useState<Array<{
    questionId: string;
    questionText: string;
    options: Record<string, string>;
    selectedAnswer: string;
    correctAnswer: string;
    isCorrect: boolean;
    explanation?: string;
  }>>([]);

  const [completedResults, setCompletedResults] = useState<ScoreAssessmentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initQuiz() {
      try {
        setLoading(true);
        const assessmentType = courseId ? "reassessment" : "initial";
        const res = await startAssessment(token, assessmentType, 15, courseId);
        setAssessmentId(res.assessment_id);
        setQuestions(res.questions);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to start quiz.");
      } finally {
        setLoading(false);
      }
    }
    initQuiz();
  }, [token, courseId]);

  const currentQ = questions[currentIndex];

  const handleSelectOption = async (optionKey: string) => {
    if (submitting || answersSubmitted || !currentQ) return;
    setSelectedOption(optionKey);
    setSubmitting(true);

    try {
      if (!assessmentId) return;
      const res = await submitAnswer(token, assessmentId, currentQ.id, optionKey);
      setAnswerResults((prev) => [
        ...prev,
        {
          questionId: currentQ.id,
          questionText: currentQ.question_text,
          options: currentQ.options,
          selectedAnswer: optionKey,
          correctAnswer: res.correct_answer || currentQ.correct_answer || "",
          isCorrect: res.is_correct,
          explanation: res.explanation || "",
        },
      ]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit answer.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = async () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedOption(null);
    } else {
      await finishAssessmentFlow();
    }
  };

  const finishAssessmentFlow = async () => {
    try {
      setSubmitting(true);
      if (!assessmentId) return;
      await finishAssessment(token, assessmentId);
      const scoreRes = await scoreAssessment(token, assessmentId);
      setCompletedResults(scoreRes);
      setAnswersSubmitted(true);

      try {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      } catch {
        // ignore if canvas unavailable
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to finalize score.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl bg-white border border-slate-200 p-4 sm:p-8 shadow-2xl max-h-[92vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {loading ? (
          <div className="py-16 text-center space-y-4">
            <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-slate-600 font-medium">{t.assemblingQuestions}</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center space-y-4">
            <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
            <p className="text-sm text-rose-700 font-medium">{error}</p>
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium text-xs"
            >
              Close
            </button>
          </div>
        ) : completedResults ? (
          /* Assessment Results & Closed Loop Summary */
          <div className="space-y-6 animate-in zoom-in-95 duration-200">
            <div className="text-center space-y-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" /> {t.competencyLoopClosed}
              </div>
              <h2 className="text-2xl font-bold text-slate-900">
                {t.competencyLoopClosed}
              </h2>
              <p className="text-xs text-slate-600">
                {t.ruleAppliedDesc}
              </p>
            </div>

            {/* Score Ring Summary */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium uppercase">{t.totalScore}</span>
                <div className="text-2xl font-bold text-indigo-600 mt-1">
                  {Math.round(completedResults.overall_score || completedResults.accuracy)}%
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium uppercase">{t.correct}</span>
                <div className="text-2xl font-bold text-emerald-600 mt-1">
                  {completedResults.correct_answers} / {completedResults.total_questions}
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 font-medium uppercase">{t.upgrades}</span>
                <div className="text-2xl font-bold text-purple-600 mt-1">
                  +{completedResults.competency_updates?.length || 0}
                </div>
              </div>
            </div>

            {/* Competency Updates List */}
            <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {t.progressionDeltas}
              </h4>
              {(completedResults.competency_updates || []).map((update) => (
                <div
                  key={update.competency_id}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between"
                >
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      {update.competency_name}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {t.evidenceLevel} <strong className="text-indigo-600">Level {update.evidence_level}</strong>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right text-xs">
                      <span className="text-slate-400 line-through mr-1">
                        L{update.previous_level}
                      </span>
                      <ArrowRight className="w-3 h-3 inline text-slate-400 mx-1" />
                      <span className="text-emerald-700 font-bold text-sm">
                        L{update.updated_level}
                      </span>
                    </div>

                    <span className="text-xs px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium">
                      Gap: {update.previous_gap} → {update.new_gap}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Answer Review */}
            {answerResults.length > 0 && (
              <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Answer Review
                </h4>
                {answerResults.map((result) => (
                  <div
                    key={result.questionId}
                    className={`p-3.5 rounded-xl border ${
                      result.isCorrect
                        ? "bg-emerald-50 border-emerald-200"
                        : "bg-rose-50 border-rose-200"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="text-sm font-semibold text-slate-900">
                          {result.questionText}
                        </div>
                        <div className="text-xs text-slate-600 mt-1">
                          <span className="font-medium">Your answer:</span> {result.selectedAnswer}
                          <span className="mx-1.5 text-slate-400">|</span>
                          <span className="font-medium">Correct:</span> {result.correctAnswer}
                        </div>
                        {result.explanation && (
                          <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                            {result.explanation}
                          </p>
                        )}
                      </div>
                      <div className="shrink-0 mt-0.5">
                        {result.isCorrect ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-rose-600" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="pt-2">
              <button
                onClick={() => {
                  onAssessmentCompleted();
                  onClose();
                }}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl text-sm font-semibold transition-colors shadow-xs"
              >
                {t.updateDashboardBtn}
              </button>
            </div>
          </div>
        ) : (
          /* Active Question Carousel */
          <div className="space-y-5">
            {/* Header: Progress Bar */}
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
                <span className="font-medium">
                  {t.questionOf} {currentIndex + 1} / {questions.length}
                </span>
                <span className="text-indigo-600 font-semibold uppercase tracking-wider">
                  {t.difficulty} {currentQ?.difficulty}
                </span>
              </div>
              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-600 transition-all duration-300"
                  style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                />
              </div>
            </div>

            {/* Question Text */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="text-base font-semibold text-slate-900 leading-snug">
                {currentQ?.question_text}
              </h3>
            </div>

            {/* Options */}
            <div className="space-y-2">
              {currentQ &&
                Object.entries(currentQ.options).map(([key, text]) => {
                  const isSelected = selectedOption === key;
                  const optionStyles = isSelected
                    ? "bg-indigo-50 border-indigo-600 text-indigo-950 font-semibold shadow-xs"
                    : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/70 text-slate-800";

                  return (
                    <button
                      key={key}
                      onClick={() => handleSelectOption(key)}
                      disabled={submitting || answersSubmitted}
                      className={`w-full p-3 rounded-xl text-left border text-sm transition-all flex items-start gap-3 ${optionStyles}`}
                    >
                      <span className="w-6 h-6 rounded-md bg-slate-100 border border-slate-200 flex items-center justify-center font-semibold text-xs shrink-0 mt-0.5 text-slate-700">
                        {key}
                      </span>
                      <span className="flex-1 leading-relaxed">{text}</span>
                    </button>
                  );
                })}
            </div>

            {/* Next / Finish Button */}
            {selectedOption && !answersSubmitted && (
              <button
                onClick={handleNext}
                disabled={submitting}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition-colors shadow-xs"
              >
                {submitting ? (
                  t.calculatingNext
                ) : currentIndex < questions.length - 1 ? (
                  <>
                    {t.nextQuestion} <ArrowRight className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    {t.submitAndUpgrade} <Zap className="w-4 h-4 fill-current" />
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
