"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle2,
  Database,
  Layers,
  Edit3,
  Check,
  X,
  AlertCircle,
  RefreshCw,
  Cpu,
  ShieldAlert,
} from "lucide-react";
import {
  uploadLearningContent,
  getLearningContents,
  getContentChunks,
  generateAIQuestions,
  getAIQuestions,
  reviewAIQuestion,
  getCompetencies,
  LearningMaterial,
  ContentChunkItem,
  AIGeneratedQuestionItem,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface AdminStudioProps {
  token: string;
  onSwitchToAdmin?: () => void;
}

export default function AdminStudio({ token, onSwitchToAdmin }: AdminStudioProps) {
  const { t } = useLanguage();
  const [activeSubTab, setActiveSubTab] = useState<"upload" | "generate" | "review">("upload");
  const [isAdminRequired, setIsAdminRequired] = useState(false);

  // Ingestion State
  const [materials, setMaterials] = useState<LearningMaterial[]>([]);
  const [selectedMaterialId, setSelectedMaterialId] = useState<string | null>(null);
  const [chunks, setChunks] = useState<ContentChunkItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // AI Generator State
  const [selectedDocForGen, setSelectedDocForGen] = useState<string>("");
  const [genDifficulty, setGenDifficulty] = useState<"beginner" | "intermediate" | "advanced">("beginner");
  const [genCount, setGenCount] = useState<number>(3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genMessage, setGenMessage] = useState<string | null>(null);

  // Review Queue State
  const [aiQuestions, setAiQuestions] = useState<AIGeneratedQuestionItem[]>([]);
  const [reviewFilter, setReviewFilter] = useState<"all" | "pending" | "approved" | "rejected">("pending");
  const [competencies, setCompetencies] = useState<Array<{ id: string; name: string }>>([]);
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editText, setEditText] = useState<string>("");
  const [editExplanation, setEditExplanation] = useState<string>("");
  const [editCompetencyId, setEditCompetencyId] = useState<string>("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setIsAdminRequired(false);
      const [contents, qList, comps] = await Promise.all([
        getLearningContents(token),
        getAIQuestions(token),
        getCompetencies(),
      ]);
      setMaterials(contents);
      if (contents.length > 0 && !selectedDocForGen) {
        setSelectedDocForGen(contents[0].id);
      }
      setAiQuestions(qList);
      setCompetencies(comps);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      if (message.includes("Admin access required") || message.includes("403")) {
        setIsAdminRequired(true);
      } else {
        console.error("Error loading admin data:", err);
      }
    }
  }, [token, selectedDocForGen]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
  }, [loadData]);

  // Load chunks when a material is selected
  useEffect(() => {
    if (!selectedMaterialId) return;
    getContentChunks(token, selectedMaterialId)
      .then(setChunks)
      .catch((err) => console.error("Error loading chunks:", err));
  }, [selectedMaterialId, token]);

  // Handle Document Ingestion (PDF / DOCX / TXT)
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await uploadLearningContent(token, file);
      setUploadSuccess(`Successfully ingested "${res.file_name}" into ${res.chunk_count} vector chunks!`);
      await loadData();
      setSelectedMaterialId(res.content_id);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed.";
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle LLM Question Generation
  const handleGenerateQuestions = async () => {
    if (!selectedDocForGen) return;

    setIsGenerating(true);
    setGenMessage(null);

    try {
      const res = await generateAIQuestions(token, selectedDocForGen, genDifficulty, genCount);
      setGenMessage(`Generated ${res.generated_count} MCQs grounded in RAG chunks! Added to review queue.`);
      await loadData();
      setActiveSubTab("review");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Generation error";
      setGenMessage(`Generation error: ${message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle Review Actions (Approve, Reject, Edit)
  const handleReview = async (
    questionId: string,
    decision: "approved" | "rejected"
  ) => {
    setActionLoading(questionId);
    try {
      const isEditing = editingQuestionId === questionId;
      const payload: {
        status: "approved" | "rejected";
        question_text?: string;
        options?: Record<string, string>;
        correct_answer?: string;
        explanation?: string;
        competency_id?: string;
      } = { status: decision };
      if (isEditing) {
        if (editText) payload.question_text = editText;
        if (editExplanation) payload.explanation = editExplanation;
        if (editCompetencyId) payload.competency_id = editCompetencyId;
      }

      await reviewAIQuestion(token, questionId, payload);
      setEditingQuestionId(null);
      await loadData();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Review action failed";
      alert(`Review action failed: ${message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const filteredAIQuestions = aiQuestions.filter((q) => {
    if (reviewFilter === "all") return true;
    return q.status === reviewFilter;
  });

  if (isAdminRequired) {
    return (
      <div className="py-16 text-center space-y-4 rounded-2xl bg-white border border-amber-200 p-8 shadow-xs max-w-xl mx-auto my-8">
        <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-900">
          Admin Privileges Required
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          The RAG Learning Studio and GenAI Question Authoring tools require System Administrator access.
        </p>
        {onSwitchToAdmin && (
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

  return (
    <div className="space-y-8 pb-16">
      {/* Studio Header */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-200">
                Phase 4 & 5 RAG + Human-in-the-Loop AI
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
              <Sparkles className="w-7 h-7 text-indigo-600" />
              {t.aiStudioTitle}
            </h1>
            <p className="text-sm text-slate-600 mt-2 max-w-2xl leading-relaxed">
              {t.aiStudioSubtitle}
            </p>
          </div>

          {/* Sub-tab Switcher */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 overflow-x-auto no-scrollbar max-w-full">
            <button
              onClick={() => setActiveSubTab("upload")}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeSubTab === "upload"
                  ? "bg-white text-indigo-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Upload className="w-3.5 h-3.5" />
              {t.subtabIngestion}
            </button>
            <button
              onClick={() => setActiveSubTab("generate")}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeSubTab === "generate"
                  ? "bg-white text-indigo-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              {t.subtabGenerate}
            </button>
            <button
              onClick={() => setActiveSubTab("review")}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeSubTab === "review"
                  ? "bg-white text-indigo-700 shadow-xs border border-slate-200 font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {t.subtabReviewQueue} ({aiQuestions.filter((q) => q.status === "pending").length})
            </button>
          </div>
        </div>
      </div>

      {/* SUBTAB 1: Ingestion & Chunks */}
      {activeSubTab === "upload" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* File Upload Box */}
          <div className="lg:col-span-5 space-y-6">
            <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-1">
                <Upload className="w-4 h-4 text-indigo-600" /> {t.uploadCourseMaterial}
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                {t.uploadDesc}
              </p>

              <label className="border-2 border-dashed border-slate-300 hover:border-indigo-400 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all bg-slate-50/60 hover:bg-slate-50 group">
                <FileText className="w-10 h-10 text-slate-400 group-hover:text-indigo-600 transition-colors mb-2" />
                <span className="text-xs font-semibold text-slate-800">
                  {isUploading ? t.uploadingStatus : t.dragOrClickUpload}
                </span>
                <span className="text-xs text-slate-500 mt-1">
                  PDF, DOCX or TXT up to 25MB
                </span>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="hidden"
                />
              </label>

              {uploadError && (
                <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {uploadError}
                </div>
              )}

              {uploadSuccess && (
                <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  {uploadSuccess}
                </div>
              )}
            </div>

            {/* Ingested Materials List */}
            <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-3">
                <Database className="w-4 h-4 text-indigo-600" /> {t.ingestedLibrary}
              </h2>
              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {materials.map((mat) => {
                  const isSelected = selectedMaterialId === mat.id;
                  return (
                    <div
                      key={mat.id}
                      onClick={() => setSelectedMaterialId(mat.id)}
                      className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                        isSelected
                          ? "bg-indigo-50 border-indigo-200 text-indigo-900 font-semibold shadow-xs"
                          : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
                        <span className="truncate">{mat.title || mat.file_name}</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                        {mat.chunk_count} {t.chunksCount}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Chunks Inspector */}
          <div className="lg:col-span-7">
            <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-indigo-600" /> {t.ragInspectorTitle}
                  </h2>
                  <p className="text-xs text-slate-500">
                    {selectedMaterialId ? `${t.viewingChunks} (${chunks.length})` : t.selectDocToInspect}
                  </p>
                </div>
              </div>

              {selectedMaterialId ? (
                <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-2">
                  {chunks.map((chunk) => (
                    <div
                      key={chunk.id}
                      className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 hover:border-slate-300 transition-all"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-900 font-semibold">
                          {t.chunkLabel}{chunk.chunk_index + 1}
                        </span>
                        <span className="text-emerald-700 flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
                          <CheckCircle2 className="w-3 h-3" /> {t.vectorEmbedded}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
                        {chunk.chunk_text}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-24 text-center text-slate-400 text-xs">
                  {t.clickDocLeft}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SUBTAB 2: Generate MCQs */}
      {activeSubTab === "generate" && (
        <div className="max-w-2xl mx-auto rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
          <div className="text-center space-y-1.5">
            <h2 className="text-2xl font-bold text-slate-900 flex items-center justify-center gap-2">
              <Cpu className="w-6 h-6 text-indigo-600" /> {t.aiGeneratorTitle}
            </h2>
            <p className="text-xs text-slate-600">
              {t.aiGeneratorSubtitle}
            </p>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-700 mb-1 font-semibold uppercase tracking-wider">
                {t.targetMaterialLabel}
              </label>
              <select
                value={selectedDocForGen}
                onChange={(e) => setSelectedDocForGen(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-white border border-slate-300 text-slate-900 focus:border-indigo-600 outline-none"
              >
                {materials.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.title || m.file_name} ({m.chunk_count} {t.chunksCount})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-700 mb-1 font-semibold uppercase tracking-wider">
                  {t.difficultyLevelLabel}
                </label>
                <select
                  value={genDifficulty}
                  onChange={(e) => setGenDifficulty(e.target.value as "beginner" | "intermediate" | "advanced")}
                  className="w-full p-2.5 rounded-xl bg-white border border-slate-300 text-slate-900 focus:border-indigo-600 outline-none"
                >
                  <option value="beginner">{t.diffBeginner}</option>
                  <option value="intermediate">{t.diffIntermediate}</option>
                  <option value="advanced">{t.diffAdvanced}</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 mb-1 font-semibold uppercase tracking-wider">
                  {t.questionCountLabel}
                </label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={genCount}
                  onChange={(e) => setGenCount(parseInt(e.target.value) || 3)}
                  className="w-full p-2.5 rounded-xl bg-white border border-slate-300 text-slate-900 focus:border-indigo-600 outline-none"
                />
              </div>
            </div>

            {genMessage && (
              <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-800 text-xs">
                {genMessage}
              </div>
            )}

            <button
              onClick={handleGenerateQuestions}
              disabled={isGenerating || !selectedDocForGen}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 mt-4 transition-colors shadow-xs"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> {t.generatingStatus}
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 fill-current" /> {t.btnGenerateRAG}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* SUBTAB 3: Review Queue */}
      {activeSubTab === "review" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl bg-white p-4 border border-slate-200 shadow-xs">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 uppercase font-semibold">{t.filterStatusLabel}</span>
              {(["all", "pending", "approved", "rejected"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setReviewFilter(st)}
                  className={`text-xs px-3 py-1.5 rounded-lg capitalize transition-all ${
                    reviewFilter === st
                      ? "bg-indigo-600 text-white font-semibold shadow-xs"
                      : "bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  {st === "all" ? t.filterAll : st === "pending" ? t.filterPending : st === "approved" ? t.filterApproved : t.filterRejected}
                </button>
              ))}
            </div>

            <span className="text-xs text-slate-500">
              {t.showingQuestions}: {filteredAIQuestions.length}
            </span>
          </div>

          <div className="space-y-4">
            {filteredAIQuestions.map((q) => {
              const isEditing = editingQuestionId === q.id;
              const isPending = q.status === "pending";

              return (
                <div
                  key={q.id}
                  className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs space-y-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2.5">
                      <span
                        className={`text-[10px] px-2.5 py-0.5 rounded-full uppercase font-semibold border ${
                          q.status === "approved"
                            ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                            : q.status === "rejected"
                            ? "bg-rose-50 text-rose-800 border-rose-200"
                            : "bg-amber-50 text-amber-800 border-amber-200"
                        }`}
                      >
                        {q.status}
                      </span>
                      <span className="text-xs text-slate-500">
                        {t.difficulty} <strong className="text-slate-800">{q.difficulty}</strong>
                      </span>
                    </div>

                    {isPending && !isEditing && (
                      <button
                        onClick={() => {
                          setEditingQuestionId(q.id);
                          setEditText(q.question_text);
                          setEditExplanation(q.explanation || "");
                        }}
                        className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
                      >
                        <Edit3 className="w-3.5 h-3.5" /> {t.btnEditQuestion}
                      </button>
                    )}
                  </div>

                  {/* Question Content / Editing */}
                  {isEditing ? (
                    <div className="space-y-3 text-xs">
                      <div>
                        <label className="text-slate-700 font-medium block mb-1">{t.questionOf}</label>
                        <textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="w-full p-3 rounded-xl bg-white border border-slate-300 text-slate-900"
                          rows={3}
                        />
                      </div>
                      <div>
                        <label className="text-slate-700 font-medium block mb-1">{t.explanationLabel}</label>
                        <input
                          type="text"
                          value={editExplanation}
                          onChange={(e) => setEditExplanation(e.target.value)}
                          className="w-full p-2.5 rounded-xl bg-white border border-slate-300 text-slate-900"
                        />
                      </div>
                      <div>
                        <label className="text-slate-700 font-medium block mb-1">Competency</label>
                        <select
                          value={editCompetencyId}
                          onChange={(e) => setEditCompetencyId(e.target.value)}
                          className="w-full p-2.5 rounded-xl bg-white border border-slate-300 text-slate-900"
                        >
                          <option value="">Select Competency</option>
                          {competencies.map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-base font-bold text-slate-900 mb-3">
                        {q.question_text}
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        {Object.entries(q.options).map(([k, opt]) => {
                          const isCorrect = q.correct_answer === k;
                          return (
                            <div
                              key={k}
                              className={`p-2.5 rounded-xl border flex items-center gap-2 ${
                                isCorrect
                                  ? "bg-emerald-50 border-emerald-200 text-emerald-900 font-medium"
                                  : "bg-slate-50 border-slate-200 text-slate-700"
                              }`}
                            >
                              <span className="font-bold text-slate-900">{k}.</span>
                              <span>{opt}</span>
                            </div>
                          );
                        })}
                      </div>
                      {q.explanation && (
                        <p className="text-xs text-slate-600 mt-3 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                          💡 <strong>{t.explanationLabel}</strong> {q.explanation}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  {isPending && (
                    <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
                      <button
                        onClick={() => handleReview(q.id, "rejected")}
                        disabled={actionLoading === q.id}
                        className="px-4 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        <X className="w-4 h-4" /> {t.btnReject}
                      </button>

                      <button
                        onClick={() => handleReview(q.id, "approved")}
                        disabled={actionLoading === q.id}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-xs"
                      >
                        <Check className="w-4 h-4" /> {t.btnApprove}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}

            {filteredAIQuestions.length === 0 && (
              <div className="py-16 text-center text-slate-500 text-sm rounded-2xl bg-white p-8 border border-slate-200">
                No questions found.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
