import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';
import { formatApiError } from '../api/client';
import { Flame, Lock, Mail, AlertCircle, ArrowRight, Eye, EyeOff, ShieldCheck, Cpu, Activity, Award } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await authApi.login(email, password);
      await login(res.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(formatApiError(err, 'login'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090D16] flex flex-col lg:flex-row font-sans text-slate-100">
      {/* Left Branding & Highlights Panel */}
      <div className="lg:flex-1 bg-gradient-to-br from-[#0F172A] via-[#090D16] to-[#030712] p-8 lg:p-16 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800/80 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Top Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl text-slate-950 shadow-lg shadow-amber-500/20">
            <Flame className="w-7 h-7 font-bold" />
          </div>
          <div>
            <span className="font-extrabold text-slate-100 text-lg tracking-wide block leading-tight">
              OIL INDIA LIMITED
            </span>
            <span className="text-xs text-amber-500 font-mono tracking-wider font-bold uppercase block">
              SIF Precursor AI Platform
            </span>
          </div>
        </div>

        {/* Main Hero Copy */}
        <div className="my-12 space-y-6 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/30 rounded-full text-xs text-amber-400 font-mono font-semibold uppercase">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Enterprise HSE Command Center</span>
          </div>
          <h2 className="text-3xl lg:text-4xl font-extrabold text-slate-100 leading-tight">
            AI-Assisted Precursor Intelligence & Safety Analytics
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Real-time evaluation of Serious Injury & Fatality (SIF) precursor indicators across Oil & Gas operations, powered by 5x5 Risk Matrices, Life-Saving Rules, and incident pattern analysis.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800/80">
            <div className="flex items-start gap-3">
              <Cpu className="w-5 h-5 text-amber-400 mt-1 flex-shrink-0" />
              <div>
                <span className="text-xs font-bold text-slate-200 block">Trained ML Engine</span>
                <span className="text-[11px] text-slate-500">TF-IDF + Logistic Classifier</span>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Activity className="w-5 h-5 text-amber-400 mt-1 flex-shrink-0" />
              <div>
                <span className="text-xs font-bold text-slate-200 block">Risk Matrix 5x5</span>
                <span className="text-[11px] text-slate-500">Severity × Likelihood Score</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-xs text-slate-500 border-t border-slate-800/80 pt-4 flex items-center justify-between">
          <span>Problem Statement ID: SIH26165</span>
          <span>Oil India Limited © 2026</span>
        </div>
      </div>

      {/* Right Login Form Card */}
      <div className="lg:w-[480px] p-8 lg:p-12 flex flex-col justify-center bg-[#0B1220]">
        <div className="max-w-sm w-full mx-auto space-y-6">
          <div>
            <h3 className="text-2xl font-extrabold text-slate-100">Sign In</h3>
            <p className="text-xs text-slate-400 mt-1">
              Enter credentials to access the HSE Safety Intelligence Portal
            </p>
          </div>

          {error && (
            <div className="p-3.5 bg-red-950/80 border border-red-800/80 rounded-xl text-red-300 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Username or Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="testuser or test@example.com"
                  className="w-full bg-[#090D16] border border-slate-800 rounded-xl py-3 pl-10 pr-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#090D16] border border-slate-800 rounded-xl py-3 pl-10 pr-10 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md shadow-amber-500/10 flex items-center justify-center gap-2 disabled:opacity-50 uppercase tracking-wider"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In to Safety Portal</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="pt-6 border-t border-slate-800/80 text-center space-y-3">
            <p className="text-xs text-slate-400">
              Need an HSE personnel account?{' '}
              <Link to="/register" className="text-amber-400 font-bold hover:underline">
                Register Account
              </Link>
            </p>

            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl text-[11px] text-slate-400 space-y-1">
              <span className="font-bold text-slate-300 block">Default Demo Credentials:</span>
              <div className="flex justify-between items-center px-2">
                <span>Safety Officer:</span>
                <code className="text-amber-400 font-mono">testuser / Test@12345</code>
              </div>
              <div className="flex justify-between items-center px-2">
                <span>Administrator:</span>
                <code className="text-amber-400 font-mono">admin@oil.in / password123</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


