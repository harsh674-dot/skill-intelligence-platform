"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ArrowLeft,
  MessageSquare,
  Send,
  Trash2,
  Heart,
  Shield,
  Clock,
} from "lucide-react";
import {
  getCommunityPost,
  addCommunityComment,
  deleteCommunityComment,
  toggleCommunityLike,
  PostDetailItem,
  UserResponse,
} from "@/lib/api";

interface PostThreadProps {
  postId: string;
  token: string;
  currentUser: UserResponse | null;
  onBack: () => void;
}

export default function PostThread({
  postId,
  token,
  currentUser,
  onBack,
}: PostThreadProps) {
  const [post, setPost] = useState<PostDetailItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [commentBody, setCommentBody] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);

  const fetchPost = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getCommunityPost(token, postId);
      setPost(data);
    } catch (err) {
      console.error("Failed to load post detail:", err);
    } finally {
      setLoading(false);
    }
  }, [token, postId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchPost();
  }, [fetchPost]);

  const handleToggleLike = async () => {
    if (!post) return;
    try {
      const res = await toggleCommunityLike(token, post.id);
      setPost({
        ...post,
        has_liked: res.liked,
        likes_count: res.likes_count,
      });
    } catch (err) {
      console.error("Failed to toggle like:", err);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentBody.trim() || submittingComment || !post) return;

    try {
      setSubmittingComment(true);
      const newComment = await addCommunityComment(token, post.id, commentBody.trim());
      setPost({
        ...post,
        comments_count: post.comments_count + 1,
        comments: [...post.comments, newComment],
      });
      setCommentBody("");
    } catch (err) {
      console.error("Failed to add comment:", err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!confirm("Are you sure you want to delete this comment?")) return;
    try {
      await deleteCommunityComment(token, commentId);
      if (post) {
        setPost({
          ...post,
          comments_count: Math.max(post.comments_count - 1, 0),
          comments: post.comments.filter((c) => c.id !== commentId),
        });
      }
    } catch (err) {
      console.error("Failed to delete comment:", err);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3 rounded-2xl bg-white border border-slate-200 p-8 shadow-xs">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-500">Loading discussion thread...</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="p-8 text-center rounded-2xl bg-white border border-slate-200 space-y-3 shadow-xs">
        <p className="text-xs text-slate-500">This discussion could not be found or has been deleted.</p>
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold inline-flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Discussions
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-indigo-600 transition-colors cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Community Feed</span>
      </button>

      {/* Main Post Card */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        {/* Author Header */}
        <div className="flex items-start justify-between gap-4 pb-5 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              {post.author.full_name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-slate-900">{post.author.full_name}</h4>
                {post.author.access_role === "admin" && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 font-semibold flex items-center gap-1">
                    <Shield className="w-3 h-3" /> System Admin
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">
                {post.author.designation || "Statistical Officer"} • {post.author.department || "National Statistical Office"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>
              {new Date(post.created_at).toLocaleDateString("en-IN", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>
          </div>
        </div>

        {/* Post Title & Full Body */}
        <div className="space-y-3">
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 leading-tight">
            {post.title}
          </h1>
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
            {post.body}
          </div>
        </div>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap pt-2">
            {post.tags.map((t, idx) => (
              <span
                key={idx}
                className="text-xs font-semibold px-3 py-1 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200/60"
              >
                #{t}
              </span>
            ))}
          </div>
        )}

        {/* Interaction Bar */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div className="flex items-center gap-4">
            <button
              onClick={handleToggleLike}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                post.has_liked
                  ? "bg-rose-50 border-rose-200 text-rose-600"
                  : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200"
              }`}
            >
              <Heart className={`w-4 h-4 ${post.has_liked ? "fill-current text-rose-500" : ""}`} />
              <span>{post.likes_count} {post.likes_count === 1 ? "Like" : "Likes"}</span>
            </button>

            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
              <MessageSquare className="w-4 h-4 text-indigo-600" />
              <span>{post.comments_count} {post.comments_count === 1 ? "Response" : "Responses"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Comment Section */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-indigo-600" />
          Responses ({post.comments.length})
        </h3>

        {/* Comment Composer */}
        <form onSubmit={handleAddComment} className="rounded-2xl bg-white border border-slate-200 p-4 shadow-xs space-y-3">
          <textarea
            value={commentBody}
            onChange={(e) => setCommentBody(e.target.value)}
            placeholder={`Add your constructive response or official insight as ${currentUser?.full_name || "Statistical Officer"}...`}
            rows={3}
            required
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none resize-y"
          />
          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-slate-400">Be professional and adhere to government knowledge sharing standards.</span>
            <button
              type="submit"
              disabled={submittingComment || !commentBody.trim()}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50 transition-all cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              {submittingComment ? "Posting..." : "Post Response"}
            </button>
          </div>
        </form>

        {/* Threaded Comments List */}
        <div className="space-y-3">
          {post.comments.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-white border border-slate-200 space-y-1">
              <p className="text-xs font-medium text-slate-600">No responses yet</p>
              <p className="text-[11px] text-slate-400">Share your expertise to assist your peer officers!</p>
            </div>
          ) : (
            post.comments.map((comment) => {
              const canDeleteComment =
                currentUser?.id === comment.author_id || currentUser?.access_role === "admin";

              return (
                <div
                  key={comment.id}
                  className="p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-slate-600 to-slate-800 text-white flex items-center justify-center font-bold text-xs">
                        {comment.author.full_name.charAt(0)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-900">
                            {comment.author.full_name}
                          </span>
                          {comment.author.access_role === "admin" && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-50 text-purple-700 border border-purple-200 font-semibold flex items-center gap-0.5">
                              <Shield className="w-2.5 h-2.5" /> Admin
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-slate-400">
                          {comment.author.designation || "Statistical Officer"} • {comment.author.department || "NSO"}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-400">
                        {new Date(comment.created_at).toLocaleDateString("en-IN", {
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                      {canDeleteComment && (
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors"
                          title="Delete response"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed pl-10 whitespace-pre-line">
                    {comment.body}
                  </p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
