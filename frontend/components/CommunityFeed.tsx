"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Users,
  MessageSquare,
  Heart,
  Tag,
  Plus,
  Trash2,
  Search,
  Send,
  Sparkles,
  Shield,
  Filter,
} from "lucide-react";
import {
  getCommunityPosts,
  createCommunityPost,
  deleteCommunityPost,
  toggleCommunityLike,
  PostItem,
  UserResponse,
} from "@/lib/api";

interface CommunityFeedProps {
  token: string;
  currentUser: UserResponse | null;
  onSelectPost: (postId: string) => void;
  selectedPostId?: string | null;
}

const POPULAR_TAGS = [
  "All",
  "Sampling",
  "Machine Learning",
  "Assessment Tips",
  "Data Quality",
  "Official Statistics",
  "Policy",
];

export default function CommunityFeed({
  token,
  currentUser,
  onSelectPost,
  selectedPostId,
}: CommunityFeedProps) {
  const [posts, setPosts] = useState<PostItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTag, setSelectedTag] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [isComposerOpen, setIsComposerOpen] = useState(false);

  // Composer form state
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [newTags, setNewTags] = useState<string[]>(["Official Statistics"]);
  const [customTagInput, setCustomTagInput] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      const tagParam = selectedTag === "All" ? undefined : selectedTag;
      const data = await getCommunityPosts(token, tagParam, searchQuery || undefined);
      setPosts(data);
    } catch (err) {
      console.error("Failed to load community posts:", err);
    } finally {
      setLoading(false);
    }
  }, [token, selectedTag, searchQuery]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchPosts();
  }, [fetchPosts]);

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newBody.trim() || submitting) return;

    try {
      setSubmitting(true);
      const created = await createCommunityPost(token, newTitle.trim(), newBody.trim(), newTags);
      setPosts((prev) => [created, ...prev]);
      setNewTitle("");
      setNewBody("");
      setNewTags(["Official Statistics"]);
      setIsComposerOpen(false);
      onSelectPost(created.id);
    } catch (err) {
      console.error("Failed to create post:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeletePost = async (postId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this post?")) return;

    try {
      await deleteCommunityPost(token, postId);
      setPosts((prev) => prev.filter((p) => p.id !== postId));
    } catch (err) {
      console.error("Failed to delete post:", err);
    }
  };

  const handleToggleLike = async (postId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await toggleCommunityLike(token, postId);
      setPosts((prev) =>
        prev.map((p) =>
          p.id === postId
            ? { ...p, has_liked: res.liked, likes_count: res.likes_count }
            : p
        )
      );
    } catch (err) {
      console.error("Failed to toggle like:", err);
    }
  };

  const toggleNewTag = (t: string) => {
    if (newTags.includes(t)) {
      setNewTags(newTags.filter((x) => x !== t));
    } else {
      setNewTags([...newTags, t]);
    }
  };

  const addCustomTag = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && customTagInput.trim()) {
      e.preventDefault();
      const clean = customTagInput.trim().replace(/^#/, "");
      if (!newTags.includes(clean)) {
        setNewTags([...newTags, clean]);
      }
      setCustomTagInput("");
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Action */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-200">
              Employee Knowledge Exchange
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-600" />
            Statistical Community Space
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Collaborate, share assessment insights, ask curriculum questions, and discuss official statistical methodologies.
          </p>
        </div>

        <button
          onClick={() => setIsComposerOpen(!isComposerOpen)}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-xs shrink-0 cursor-pointer"
        >
          {isComposerOpen ? <Users className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {isComposerOpen ? "View Discussions" : "Start New Discussion"}
        </button>
      </div>

      {/* Post Composer Drawer */}
      {isComposerOpen && (
        <div className="rounded-2xl bg-white border border-indigo-200 p-6 shadow-sm space-y-4 animate-in slide-in-from-top-3 duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              Compose New Knowledge Discussion
            </h3>
            <span className="text-[11px] text-slate-500">Posting as {currentUser?.full_name}</span>
          </div>

          <form onSubmit={handleCreatePost} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Topic Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Best strategies for Survey Sampling in Rural Districts..."
                required
                className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Discussion Content</label>
              <textarea
                value={newBody}
                onChange={(e) => setNewBody(e.target.value)}
                placeholder="Share your practical tips, reference documents, or questions for peer statistical officers..."
                rows={4}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none resize-y"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-indigo-500" />
                Select Tags
              </label>
              <div className="flex items-center gap-1.5 flex-wrap">
                {POPULAR_TAGS.filter((t) => t !== "All").map((tag) => {
                  const selected = newTags.includes(tag);
                  return (
                    <button
                      type="button"
                      key={tag}
                      onClick={() => toggleNewTag(tag)}
                      className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all ${
                        selected
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      #{tag}
                    </button>
                  );
                })}
              </div>

              <div className="mt-2">
                <input
                  type="text"
                  value={customTagInput}
                  onChange={(e) => setCustomTagInput(e.target.value)}
                  onKeyDown={addCustomTag}
                  placeholder="Type custom tag and press Enter..."
                  className="w-48 px-3 py-1 text-[11px] rounded-lg border border-slate-200 outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setIsComposerOpen(false)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !newTitle.trim() || !newBody.trim()}
                className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50 transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                {submitting ? "Publishing..." : "Publish Post"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 ml-1 mr-0.5" />
          {POPULAR_TAGS.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-3 py-1 rounded-xl text-xs font-medium shrink-0 transition-all ${
                selectedTag === tag
                  ? "bg-slate-900 text-white shadow-xs font-bold"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-60">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search discussions..."
            className="w-full pl-8 pr-3 py-1.5 rounded-xl border border-slate-200 text-xs outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="py-16 text-center space-y-3">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500">Loading community discussions...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-white border border-slate-200 space-y-2 shadow-xs">
          <Users className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-700">No discussions found</h3>
          <p className="text-xs text-slate-500">
            {selectedTag !== "All"
              ? `No posts tagged with #${selectedTag}. Try selecting another tag or create the first post!`
              : "Be the first to share an insight with the statistical officer community!"}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {posts.map((post) => {
            const isSelected = selectedPostId === post.id;
            const canDelete =
              currentUser?.id === post.author_id || currentUser?.access_role === "admin";

            return (
              <div
                key={post.id}
                onClick={() => onSelectPost(post.id)}
                className={`p-5 rounded-2xl bg-white border transition-all duration-200 cursor-pointer ${
                  isSelected
                    ? "border-indigo-500 ring-2 ring-indigo-500/20 shadow-md bg-indigo-50/10"
                    : "border-slate-200/90 hover:border-indigo-300 hover:shadow-md"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                      {post.author.full_name.charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900">
                          {post.author.full_name}
                        </span>
                        {post.author.access_role === "admin" && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-50 text-purple-700 border border-purple-200 font-semibold flex items-center gap-0.5">
                            <Shield className="w-2.5 h-2.5" /> Admin
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500">
                        {post.author.designation || "Statistical Officer"} •{" "}
                        {post.author.department || "National Statistical Office"}
                      </p>
                    </div>
                  </div>

                  {canDelete && (
                    <button
                      onClick={(e) => handleDeletePost(post.id, e)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                      title={currentUser?.access_role === "admin" ? "Admin Moderate / Delete" : "Delete Post"}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="mt-3 space-y-1.5">
                  <h3 className="text-sm font-bold text-slate-900 hover:text-indigo-600 transition-colors">
                    {post.title}
                  </h3>
                  <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {post.body}
                  </p>
                </div>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <div className="flex items-center gap-1.5 mt-3 flex-wrap">
                    {post.tags.map((t, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200/60"
                      >
                        #{t}
                      </span>
                    ))}
                  </div>
                )}

                {/* Card Footer Actions */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={(e) => handleToggleLike(post.id, e)}
                      className={`flex items-center gap-1.5 font-semibold transition-colors ${
                        post.has_liked ? "text-rose-600 font-bold" : "text-slate-500 hover:text-rose-600"
                      }`}
                    >
                      <Heart className={`w-4 h-4 ${post.has_liked ? "fill-current text-rose-500" : ""}`} />
                      <span>{post.likes_count}</span>
                    </button>

                    <span className="flex items-center gap-1.5 font-semibold text-slate-600">
                      <MessageSquare className="w-4 h-4 text-indigo-500" />
                      <span>{post.comments_count} {post.comments_count === 1 ? "comment" : "comments"}</span>
                    </span>
                  </div>

                  <span className="text-[11px] text-slate-400">
                    {new Date(post.created_at).toLocaleDateString("en-IN", {
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
