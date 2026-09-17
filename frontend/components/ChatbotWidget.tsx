"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  X,
  Send,
  Bot,
  User as UserIcon,
  RotateCcw,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  sendChatMessage,
  getChatHistory,
  ChatMessageItem,
  ChatSourceItem,
  UserResponse,
} from "@/lib/api";

interface ChatbotWidgetProps {
  token: string | null;
  currentUser?: UserResponse | null;
}

interface MessageWithSources extends ChatMessageItem {
  sources?: ChatSourceItem[];
  grounded_gaps?: string[];
  recommended_courses?: string[];
}

export default function ChatbotWidget({ token, currentUser }: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<MessageWithSources[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showSourcesMap, setShowSourcesMap] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const idCounter = useRef(0);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Load session from storage if present
  useEffect(() => {
    if (typeof window !== "undefined" && currentUser?.email) {
      const savedSession = sessionStorage.getItem(`chat_session_${currentUser.email}`);
      if (savedSession && token) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setSessionId(savedSession);
        getChatHistory(token, savedSession)
          .then((history) => {
            if (history && history.length > 0) {
              setMessages(history);
            }
          })
          .catch(() => {
            sessionStorage.removeItem(`chat_session_${currentUser.email}`);
            setSessionId(null);
          });
      }
    }
  }, [currentUser?.email, token]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || !token || isLoading) return;

    const userText = text.trim();
    setInputMessage("");
    setIsLoading(true);

    // Optimistic user message
    idCounter.current += 1;
    const msgId = `temp-${idCounter.current}`;
    const tempUserMsg: MessageWithSources = {
      id: msgId,
      session_id: sessionId || "new",
      user_id: currentUser?.id || "me",
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendChatMessage(token, userText, sessionId || undefined);
      
      setSessionId(response.session_id);
      if (typeof window !== "undefined" && currentUser?.email) {
        sessionStorage.setItem(`chat_session_${currentUser.email}`, response.session_id);
      }

      const assistantMsg: MessageWithSources = {
        ...response.assistant_message,
        sources: response.sources,
        grounded_gaps: response.grounded_gaps,
        recommended_courses: response.recommended_courses,
      };

      setMessages((prev) => {
        // Replace temp or append
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...filtered, response.user_message, assistantMsg];
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get AI response";
      idCounter.current += 1;
      const errId = `err-${idCounter.current}`;
      const errorAssistantMsg: MessageWithSources = {
        id: errId,
        session_id: sessionId || "new",
        user_id: "system",
        role: "assistant",
        content: `⚠️ Error connecting to Skill Assistant: ${errorMessage}. Please verify backend status.`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorAssistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSession = () => {
    setSessionId(null);
    setMessages([]);
    if (typeof window !== "undefined" && currentUser?.email) {
      sessionStorage.removeItem(`chat_session_${currentUser.email}`);
    }
  };

  const toggleSourceView = (msgId: string) => {
    setShowSourcesMap((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const quickPrompts = [
    "What are my main competency gaps?",
    "Which course should I take next?",
    "How do I reach Level 4 in Statistical Modeling?",
    "Explain sampling error formulas",
  ];

  return (
    <>
      {/* Floating Launcher Button */}
      <aside aria-label="Skill AI Assistant">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="fixed bottom-6 right-6 z-40 group flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 text-white shadow-xl hover:shadow-indigo-500/25 transition-all duration-300 hover:scale-105 active:scale-95 border border-white/20"
        title="Open AI Competency Assistant"
        aria-label="Open AI Competency Assistant"
      >
        <div className="relative">
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
          </div>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 border-2 border-indigo-700 rounded-full" />
        </div>
        <div className="text-left hidden sm:block">
          <div className="text-xs font-bold leading-tight">Skill AI</div>
          <div className="text-[10px] text-indigo-200">Grounded RAG</div>
        </div>
      </button>

      {/* Floating Chat Drawer */}
      {isOpen && (
        <div className="fixed bottom-22 right-4 sm:right-6 z-40 w-[calc(100vw-2rem)] sm:w-[420px] max-h-[640px] h-[80vh] flex flex-col rounded-3xl bg-white/95 backdrop-blur-xl border border-slate-200/90 shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5 fade-in duration-200">
          {/* Header */}
          <div className="px-5 py-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 text-white flex items-center justify-between border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-md">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold flex items-center gap-1.5">
                  Skill Intelligence Assistant
                  <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium">
                    RAG Grounded
                  </span>
                </h3>
                <p className="text-[11px] text-slate-300">
                  {currentUser ? `${currentUser.full_name} • Personalized` : "Institutional Knowledge Base"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleResetSession}
                className="p-1.5 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
                title="Start New Conversation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {messages.length === 0 && (
              <div className="space-y-4 py-4">
                <div className="p-4 rounded-2xl bg-indigo-50/80 border border-indigo-100 text-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-700 font-bold">
                    <Sparkles className="w-4 h-4" />
                    Welcome to your Personal Upskilling AI
                  </div>
                  <p className="text-[11px] leading-relaxed text-slate-600">
                    I am directly integrated with your competency assessments, role benchmark requirements, and official learning content. Ask me anything about your current deficits or recommended coursework!
                  </p>
                </div>

                <div className="space-y-1.5">
                  <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-1">
                    Suggested Focus Questions
                  </div>
                  <div className="grid grid-cols-1 gap-1.5">
                    {quickPrompts.map((prompt, i) => (
                      <button
                        key={i}
                        onClick={() => handleSendMessage(prompt)}
                        className="text-left p-2.5 rounded-xl bg-slate-50 hover:bg-indigo-50/80 border border-slate-200/80 hover:border-indigo-200 text-slate-700 transition-all font-medium flex items-center justify-between group"
                      >
                        <span>{prompt}</span>
                        <Send className="w-3 h-3 text-slate-400 group-hover:text-indigo-600 transition-colors" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {messages.map((msg) => {
              const isUser = msg.role === "user";
              const showSources = showSourcesMap[msg.id] || false;

              return (
                <div
                  key={msg.id}
                  className={`flex gap-2.5 ${isUser ? "justify-end" : "justify-start"}`}
                >
                  {!isUser && (
                    <div className="w-7 h-7 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div className={`max-w-[85%] space-y-2`}>
                    <div
                      className={`p-3.5 rounded-2xl leading-relaxed whitespace-pre-line ${
                        isUser
                          ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-xs shadow-xs"
                          : "bg-slate-50 border border-slate-200/90 text-slate-800 rounded-tl-xs shadow-xs"
                      }`}
                    >
                      {msg.content}
                    </div>

                    {/* Grounded Tags & Sources (Assistant Only) */}
                    {!isUser && (
                      <div className="space-y-1.5 pt-1">
                        {/* Competency Gap Pills */}
                        {msg.grounded_gaps && msg.grounded_gaps.length > 0 && (
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-[10px] font-semibold text-slate-400">Gaps:</span>
                            {msg.grounded_gaps.map((gap, gi) => (
                              <span
                                key={gi}
                                className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-medium"
                              >
                                {gap}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Verified Sources Toggle */}
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="rounded-xl border border-slate-200 bg-white p-2">
                            <button
                              onClick={() => toggleSourceView(msg.id)}
                              className="w-full flex items-center justify-between text-[11px] font-bold text-slate-600 hover:text-indigo-600"
                            >
                              <span className="flex items-center gap-1.5">
                                <BookOpen className="w-3 h-3 text-indigo-500" />
                                Verified RAG Sources ({msg.sources.length})
                              </span>
                              {showSources ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            </button>

                            {showSources && (
                              <div className="mt-2 space-y-2 pt-2 border-t border-slate-100 text-[10px] text-slate-600">
                                {msg.sources.map((src, si) => (
                                  <div key={si} className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                                    <div className="flex items-center justify-between text-indigo-700 font-semibold mb-1">
                                      <span>Chunk Ref #{si + 1}</span>
                                      <span>Sim: {(src.similarity * 100).toFixed(1)}%</span>
                                    </div>
                                    <p className="line-clamp-3 italic">&ldquo;{src.text}&rdquo;</p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-7 h-7 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center shrink-0 mt-0.5">
                      <UserIcon className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              );
            })}

            {isLoading && (
              <div className="flex gap-2.5 justify-start">
                <div className="w-7 h-7 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-slate-500 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
                  <span className="text-[11px] font-medium">Retrieving personal gaps & learning chunks...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input Bar */}
          <div className="p-3 bg-white border-t border-slate-200/90 space-y-2">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about your skill gaps, courses, or concepts..."
                disabled={isLoading}
                className="flex-1 px-3.5 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-xs text-slate-800 placeholder-slate-400 outline-none disabled:opacity-60 bg-slate-50/50"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="p-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-xs disabled:opacity-40 transition-all cursor-pointer disabled:cursor-not-allowed"
                title="Send"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="text-[10px] text-center text-slate-400 flex items-center justify-center gap-1">
              <span>Grounded in official competencies & pgvector RAG</span>
            </div>
          </div>
        </div>
      )}
      </aside>
    </>
  );
}
