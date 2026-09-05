"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

export default function Home() {
  const [health, setHealth] = useState<{
    status: string;
    service: string;
  } | null>(null);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold">
          Skill Intelligence Platform
        </h1>

        <p className="mt-4 text-gray-600">
          Frontend ↔ Backend Connection
        </p>

        {health && (
          <div className="mt-8 rounded-lg border p-6">
            <p className="text-green-600">
              Backend Status: {health.status}
            </p>

            <p className="mt-2">
              Service: {health.service}
            </p>
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-lg border border-red-500 p-6">
            <p className="text-red-500">
              Backend connection failed: {error}
            </p>
          </div>
        )}

        {!health && !error && (
          <p className="mt-8">
            Connecting to backend...
          </p>
        )}
      </div>
    </main>
  );
}