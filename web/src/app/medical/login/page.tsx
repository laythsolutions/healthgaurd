"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { verifyInstitutionKey } from "@/lib/medical-api";

export default function MedicalLoginPage() {
  const router = useRouter();
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const valid = await verifyInstitutionKey(key.trim());
      if (valid) {
        localStorage.setItem("med_inst_key", key.trim());
        router.push("/medical");
      } else {
        setError("Invalid institution key. Please check your key and try again.");
      }
    } catch {
      setError("Could not reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/20 mb-4">
            <svg className="w-7 h-7 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">Medical Reporting Portal</h1>
          <p className="text-slate-400 mt-1 text-sm">
            Secure, anonymized foodborne illness case submission
          </p>
        </div>

        {/* Privacy notice */}
        <div className="bg-blue-900/20 border border-blue-700/30 rounded-xl p-4 mb-6">
          <div className="flex gap-3">
            <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            <div>
              <p className="text-sm text-blue-300 font-medium">Privacy by design</p>
              <p className="text-xs text-blue-400/80 mt-0.5 leading-relaxed">
                Patient identifiers are anonymized before storage. No names, dates of birth,
                or contact information are retained. Location is truncated to geohash precision-5
                (approx. 5 km cell).
              </p>
            </div>
          </div>
        </div>

        {/* Login form */}
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-700/50 rounded-2xl p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Institution API Key
            </label>
            <input
              type="password"
              value={key}
              onChange={e => setKey(e.target.value)}
              placeholder="Enter your institution key"
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500/30 text-sm"
              required
              autoComplete="off"
            />
            <p className="text-xs text-slate-500 mt-1.5">
              Provided by your jurisdiction's public health authority.
            </p>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-700/30 rounded-lg px-4 py-3">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !key.trim()}
            className="w-full bg-teal-500 hover:bg-teal-400 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold rounded-lg py-2.5 text-sm transition-colors"
          >
            {loading ? "Verifying…" : "Access Portal"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-600 mt-6">
          Authorized reporting institutions only. Misuse is subject to applicable law.
        </p>
      </div>
    </div>
  );
}
