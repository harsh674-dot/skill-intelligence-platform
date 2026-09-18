"use client";

import { useState, useEffect, useCallback } from "react";
import Navbar, { DemoPersona, DEMO_PERSONAS } from "@/components/Navbar";
import CommunityFeed from "@/components/CommunityFeed";
import PostThread from "@/components/PostThread";
import ChatbotWidget from "@/components/ChatbotWidget";
import { getHealth, login, getMe, UserResponse } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function CommunityPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);

  const handleSwitchPersona = useCallback(async (persona: DemoPersona) => {
    try {
      const authRes = await login(persona.email, "Demo@12345");
      const authToken = authRes.access_token;
      setToken(authToken);

      const me = await getMe(authToken).catch(() => null);
      if (me) {
        setCurrentUser(me);
      } else {
        setCurrentUser({
          id: "demo-user",
          email: persona.email,
          full_name: persona.name,
          access_role: persona.access_role,
        });
      }
    } catch (err) {
      console.error("Persona switch error in community:", err);
      // Fallback
      setCurrentUser({
        id: "demo-user",
        email: persona.email,
        full_name: persona.name,
        access_role: persona.access_role,
      });
    }
  }, []);

  useEffect(() => {
    getHealth()
      .then(() => setIsBackendOnline(true))
      .catch(() => setIsBackendOnline(false));

    // eslint-disable-next-line react-hooks/set-state-in-effect
    handleSwitchPersona(DEMO_PERSONAS[0]);
  }, [handleSwitchPersona]);

  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col font-sans">
      {/* Universal Navigation Bar */}
      <Navbar
        currentUser={currentUser}
        currentTab="employee"
        onSelectTab={(tab) => {
          if (tab !== "employee") {
            router.push("/");
          } else {
            router.push("/");
          }
        }}
        onSwitchPersona={handleSwitchPersona}
        isBackendOnline={isBackendOnline}
        onReturnTo3D={() => router.push("/")}
      />

      {/* Main Community Workspace */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {token && (
          <>
            {selectedPostId ? (
              <PostThread
                postId={selectedPostId}
                token={token}
                currentUser={currentUser}
                onBack={() => setSelectedPostId(null)}
              />
            ) : (
              <CommunityFeed
                token={token}
                currentUser={currentUser}
                onSelectPost={(id) => setSelectedPostId(id)}
              />
            )}
          </>
        )}
      </main>

      {/* Floating Grounded AI Chatbot Widget */}
      <ChatbotWidget token={token} currentUser={currentUser} />
    </div>
  );
}
