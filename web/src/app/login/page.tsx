'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { ShieldCheck, Mail, Lock, Eye, EyeOff, Loader2 } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/api/accounts/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.non_field_errors?.[0] || 'Invalid email or password');
      }

      const { access, refresh } = await res.json();

      document.cookie = `access_token=${access}; path=/; max-age=3600; SameSite=Lax`;
      document.cookie = `refresh_token=${refresh}; path=/; max-age=604800; SameSite=Lax`;

      window.location.href = '/dashboard/admin';
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#040a08' }}>
      {/* Background glows */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[700px] rounded-full blur-3xl" style={{ background: 'rgba(16,185,129,0.06)' }} />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full blur-3xl" style={{ background: 'rgba(20,184,166,0.04)' }} />
      </div>

      <div className="relative w-full max-w-md">
        {/* Brand */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4" style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)' }}>
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">HealthGuard</h1>
          <p className="mt-1 text-sm" style={{ color: '#6b8f7e' }}>Food Safety Intelligence Platform</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl p-8 shadow-2xl" style={{ background: 'rgba(10,26,22,0.9)', border: '1px solid rgba(16,185,129,0.12)' }}>
          <h2 className="text-lg font-semibold text-white mb-1">Sign in to your account</h2>
          <p className="text-sm mb-6" style={{ color: '#6b8f7e' }}>Enter your credentials to access the dashboard</p>

          {error && (
            <div className="mb-5 rounded-lg px-4 py-3" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
              <span className="text-rose-400 text-sm">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#a3c4b5' }}>
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" style={{ color: '#4b7a65' }} />
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg text-white text-sm placeholder-[#3d6b59] outline-none transition-all"
                  style={{ background: 'rgba(7,18,16,0.8)', border: '1px solid rgba(16,185,129,0.15)' }}
                  onFocus={e => { e.currentTarget.style.border = '1px solid rgba(16,185,129,0.5)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(16,185,129,0.08)'; }}
                  onBlur={e => { e.currentTarget.style.border = '1px solid rgba(16,185,129,0.15)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#a3c4b5' }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" style={{ color: '#4b7a65' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 rounded-lg text-white text-sm placeholder-[#3d6b59] outline-none transition-all"
                  style={{ background: 'rgba(7,18,16,0.8)', border: '1px solid rgba(16,185,129,0.15)' }}
                  onFocus={e => { e.currentTarget.style.border = '1px solid rgba(16,185,129,0.5)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(16,185,129,0.08)'; }}
                  onBlur={e => { e.currentTarget.style.border = '1px solid rgba(16,185,129,0.15)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                  style={{ color: '#4b7a65' }}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="mt-2 w-full flex items-center justify-center gap-2 rounded-lg text-white text-sm font-semibold py-2.5 transition-all"
              style={{ background: loading ? 'rgba(16,185,129,0.4)' : '#059669' }}
              onMouseOver={e => { if (!loading) e.currentTarget.style.background = '#10b981'; }}
              onMouseOut={e => { if (!loading) e.currentTarget.style.background = '#059669'; }}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm" style={{ color: '#6b8f7e' }}>
            Don&apos;t have an account?{' '}
            <Link href="/register" className="font-medium text-emerald-400 hover:text-emerald-300 transition-colors">
              Create one
            </Link>
          </p>
        </div>

        <p className="mt-6 text-center text-xs" style={{ color: '#2d4a3e' }}>
          &copy; {new Date().getFullYear()} HealthGuard — Open-source under Apache 2.0
        </p>
      </div>
    </div>
  );
}
