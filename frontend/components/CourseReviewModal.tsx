"use client";

import React, { useState, useEffect } from "react";
import {
  submitCourseReview,
  getCourseReviewStats,
  CourseReviewItem,
} from "@/lib/api";

interface CourseReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  token: string;
  courseId: string;
  courseTitle: string;
  onReviewSubmitted?: () => void;
}

const RATING_LABELS: Record<number, string> = {
  1: "Needs Improvement / Not Helpful",
  2: "Basic / Slightly Helpful",
  3: "Adequate / Moderately Helpful",
  4: "Very Helpful & Practical",
  5: "Exceptional / Highly Recommended",
};

export default function CourseReviewModal({
  isOpen,
  onClose,
  token,
  courseId,
  courseTitle,
  onReviewSubmitted,
}: CourseReviewModalProps) {
  const [rating, setRating] = useState<number>(5);
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [comments, setComments] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [statsLoading, setStatsLoading] = useState<boolean>(false);
  const [existingReviews, setExistingReviews] = useState<CourseReviewItem[]>([]);
  const [avgRating, setAvgRating] = useState<number>(0);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !courseId) return;

    let isMounted = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStatsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    getCourseReviewStats(courseId, token)
      .then((data) => {
        if (isMounted && data) {
          setExistingReviews(data.reviews || []);
          setAvgRating(data.average_helpfulness || 0);
          setTotalCount(data.total_reviews || 0);
        }
      })
      .catch((err) => {
        console.error("Failed to load course review stats:", err);
      })
      .finally(() => {
        if (isMounted) setStatsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, courseId, token]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating < 1 || rating > 5) {
      setErrorMsg("Please select a valid rating from 1 to 5 stars.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await submitCourseReview(token, courseId, rating, comments.trim() || undefined);
      setSuccessMsg("Thank you! Your course review has been saved.");
      if (onReviewSubmitted) {
        onReviewSubmitted();
      }
      setTimeout(() => {
        onClose();
      }, 1400);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit review.";
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  const activeRating = hoverRating !== null ? hoverRating : rating;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-6 text-slate-100 flex flex-col gap-5"
        role="dialog"
        aria-modal="true"
        aria-labelledby="course-review-modal-title"
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4">
          <div>
            <span className="text-xs font-semibold tracking-wider text-amber-400 uppercase">
              Course Telemetry & Helpfulness
            </span>
            <h2 id="course-review-modal-title" className="text-lg font-bold text-white mt-0.5 line-clamp-1">
              {courseTitle}
            </h2>
            <div className="flex items-center gap-2 mt-1 text-xs text-slate-400">
              <span className="flex items-center text-amber-300 font-semibold">
                ★ {avgRating > 0 ? avgRating.toFixed(1) : "New"}
              </span>
              <span>•</span>
              <span>{totalCount} {totalCount === 1 ? "review" : "reviews"} from certified completers</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-slate-800"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Feedback alerts */}
        {errorMsg && (
          <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 p-3 text-sm text-rose-300">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-3 text-sm text-emerald-300">
            {successMsg}
          </div>
        )}

        {/* Submission Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
              Rate Helpfulness & Practicality
            </label>
            <div className="flex items-center gap-1.5">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(null)}
                  className="text-2xl transition-transform hover:scale-125 focus:outline-none"
                  aria-label={`Rate ${star} star`}
                >
                  <span
                    className={
                      star <= activeRating
                        ? "text-amber-400"
                        : "text-slate-600"
                    }
                  >
                    ★
                  </span>
                </button>
              ))}
              <span className="ml-3 text-xs font-medium text-amber-300">
                {RATING_LABELS[activeRating] || ""}
              </span>
            </div>
          </div>

          <div>
            <label
              htmlFor="course-review-comments"
              className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider"
            >
              Feedback & Key Takeaways (Optional)
            </label>
            <textarea
              id="course-review-comments"
              rows={3}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="How did this course help you close your competency gap or apply skills on the job?"
              className="w-full rounded-xl bg-slate-800/80 border border-slate-700 p-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-xs font-semibold text-slate-900 bg-amber-400 hover:bg-amber-300 disabled:opacity-50 rounded-lg transition-colors shadow-md shadow-amber-500/20"
            >
              {loading ? "Submitting..." : "Submit Review"}
            </button>
          </div>
        </form>

        {/* Existing peer reviews */}
        <div className="border-t border-slate-800 pt-4 flex flex-col gap-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Completer Reviews ({existingReviews.length})
          </h3>
          {statsLoading ? (
            <p className="text-xs text-slate-500">Loading reviews...</p>
          ) : existingReviews.length === 0 ? (
            <p className="text-xs text-slate-500 italic">
              No reviews yet. Be the first completer to rate this course!
            </p>
          ) : (
            <div className="flex flex-col gap-2.5 max-h-48 overflow-y-auto pr-1">
              {existingReviews.map((rev) => (
                <div
                  key={rev.id}
                  className="rounded-lg bg-slate-800/50 border border-slate-700/60 p-3 text-xs flex flex-col gap-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200">
                      {rev.user_name}
                    </span>
                    <span className="text-amber-400 font-bold">
                      {"★".repeat(rev.helpfulness_rating)}
                      <span className="text-slate-600">
                        {"★".repeat(5 - rev.helpfulness_rating)}
                      </span>
                    </span>
                  </div>
                  {rev.comments && (
                    <p className="text-slate-300 leading-relaxed mt-0.5">
                      {rev.comments}
                    </p>
                  )}
                  <span className="text-[10px] text-slate-500">
                    {new Date(rev.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
