"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Star,
  MessageSquareHeart,
  Send,
  CheckCircle2,
  Layers,
  GraduationCap,
  Compass,
} from "lucide-react";
import {
  submitExperienceReview,
  getMyExperienceReviews,
  ExperienceReviewItem,
} from "@/lib/api";

interface ExperienceReviewFormProps {
  token: string;
}

const CATEGORIES: Array<{
  key: "platform" | "training_program" | "onboarding";
  label: string;
  icon: React.ElementType;
  description: string;
}> = [
  {
    key: "platform",
    label: "Platform Experience",
    icon: Layers,
    description: "Assessment arena, 3D galaxy navigation, AI recommendations",
  },
  {
    key: "training_program",
    label: "Training Programs",
    icon: GraduationCap,
    description: "iGOT Karmayogi & TPAC courses, material relevance, pacing",
  },
  {
    key: "onboarding",
    label: "Onboarding & Induction",
    icon: Compass,
    description: "Role competency framework clarity, initial guidance",
  },
];

const RATING_LABELS: Record<number, string> = {
  1: "Needs Attention",
  2: "Fair",
  3: "Good",
  4: "Very Good",
  5: "Outstanding",
};

export default function ExperienceReviewForm({ token }: ExperienceReviewFormProps) {
  const [selectedCategory, setSelectedCategory] = useState<
    "platform" | "training_program" | "onboarding"
  >("platform");
  const [rating, setRating] = useState<number>(5);
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [comments, setComments] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successToast, setSuccessToast] = useState(false);
  const [myReviews, setMyReviews] = useState<ExperienceReviewItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const fetchMyReviews = useCallback(async () => {
    try {
      const data = await getMyExperienceReviews(token);
      setMyReviews(data);
    } catch (err) {
      console.error("Failed to load my reviews:", err);
    }
  }, [token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchMyReviews();
  }, [fetchMyReviews]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      const newReview = await submitExperienceReview(
        token,
        selectedCategory,
        rating,
        comments.trim() || undefined
      );
      setMyReviews((prev) => [newReview, ...prev]);
      setComments("");
      setSuccessToast(true);
      setTimeout(() => setSuccessToast(false), 4000);
    } catch (err) {
      console.error("Failed to submit experience review:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const activeCatInfo = CATEGORIES.find((c) => c.key === selectedCategory)!;

  return (
    <div className="pleasant-card rounded-3xl p-6 sm:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              Continuous Institutional Improvement
            </span>
          </div>
          <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <MessageSquareHeart className="w-5 h-5 text-indigo-600" />
            Employee Experience Review
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Your anonymous and direct feedback shapes official training design, platform workflows, and onboarding.
          </p>
        </div>

        {myReviews.length > 0 && (
          <button
            type="button"
            onClick={() => setShowHistory(!showHistory)}
            className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-slate-600 hover:text-indigo-600 text-xs font-semibold self-start sm:self-auto transition-colors cursor-pointer"
          >
            {showHistory ? "Hide My Submissions" : `View My Submissions (${myReviews.length})`}
          </button>
        )}
      </div>

      {/* Success Notification */}
      {successToast && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center gap-2.5 animate-in fade-in duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Thank you! Your experience feedback has been submitted to Ministry analytics.</span>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Category Tabs */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            Select Review Category
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {CATEGORIES.map((cat) => {
              const Icon = cat.icon;
              const isSelected = selectedCategory === cat.key;
              return (
                <button
                  type="button"
                  key={cat.key}
                  onClick={() => setSelectedCategory(cat.key)}
                  className={`p-3.5 rounded-2xl border text-left transition-all cursor-pointer ${
                    isSelected
                      ? "border-indigo-600 bg-indigo-50/50 shadow-xs ring-2 ring-indigo-500/20"
                      : "border-slate-200 hover:border-slate-300 bg-white"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div
                      className={`w-6 h-6 rounded-lg flex items-center justify-center ${
                        isSelected ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-slate-900">{cat.label}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                    {cat.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Rating Stars */}
        <div className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span className="text-xs font-bold text-slate-700">
              Rate your experience with {activeCatInfo.label}:
            </span>
            <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200 self-start sm:self-auto">
              {RATING_LABELS[hoverRating || rating]} ({hoverRating || rating} / 5)
            </span>
          </div>

          <div className="flex items-center gap-1.5 pt-1">
            {[1, 2, 3, 4, 5].map((star) => {
              const filled = (hoverRating || rating) >= star;
              return (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(null)}
                  className="p-1 text-slate-300 hover:scale-115 transition-transform cursor-pointer"
                  title={`${star} star - ${RATING_LABELS[star]}`}
                >
                  <Star
                    className={`w-7 h-7 ${
                      filled
                        ? "fill-amber-400 text-amber-400 drop-shadow-xs"
                        : "text-slate-300 hover:text-amber-200"
                    }`}
                  />
                </button>
              );
            })}
          </div>
        </div>

        {/* Comments Box */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Constructive Feedback & Suggestions (Optional)
          </label>
          <textarea
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder={`Share what worked well or what needs improvement in ${activeCatInfo.label.toLowerCase()}...`}
            rows={3}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none resize-y"
          />
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold flex items-center gap-2 shadow-xs hover:shadow-md transition-all cursor-pointer disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            {submitting ? "Submitting..." : "Submit Experience Review"}
          </button>
        </div>
      </form>

      {/* Submitted History Drawer */}
      {showHistory && (
        <div className="pt-4 border-t border-slate-100 space-y-3">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Your Previously Submitted Feedback
          </h4>
          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            {myReviews.map((rev) => (
              <div
                key={rev.id}
                className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 capitalize">
                      {rev.category.replace("_", " ")}
                    </span>
                    <div className="flex items-center gap-0.5 text-amber-500">
                      {Array.from({ length: rev.rating }).map((_, si) => (
                        <Star key={si} className="w-3 h-3 fill-current" />
                      ))}
                    </div>
                  </div>
                  {rev.comments && (
                    <p className="text-slate-600 text-[11px] leading-relaxed italic">
                      &ldquo;{rev.comments}&rdquo;
                    </p>
                  )}
                </div>
                <span className="text-[10px] text-slate-400 shrink-0">
                  {new Date(rev.created_at).toLocaleDateString("en-IN", {
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
