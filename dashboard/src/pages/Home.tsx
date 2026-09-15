import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Flame,
  ShieldCheck,
  Brain,
  AlertTriangle,
  BookOpen,
  PieChart,
  CheckSquare,
  UserCheck,
  ArrowRight,
  ChevronRight,
  Lock,
  Activity,
  Award,
} from 'lucide-react';

export const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased flex flex-col selection:bg-amber-500 selection:text-slate-950">
      {/* Top Header Navigation */}
      <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Logo & Branding */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl text-slate-950 shadow-md shadow-amber-500/20 group-hover:scale-105 transition-transform">
              <Flame className="w-5 h-5 font-bold" />
            </div>
            <div>
              <span className="font-extrabold text-slate-100 text-sm tracking-wide block leading-tight">
                OIL INDIA LIMITED
              </span>
              <span className="text-[10px] text-amber-500 font-mono tracking-wider font-semibold uppercase block">
                HSE Safety Intelligence Platform
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-slate-300">
            <a href="#hero" className="hover:text-amber-400 transition-colors">
              Home
            </a>
            <a href="#features" className="hover:text-amber-400 transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-amber-400 transition-colors">
              How It Works
            </a>
            <a href="#about" className="hover:text-amber-400 transition-colors">
              About
            </a>
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold rounded-xl transition-all shadow-md shadow-amber-500/20"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-slate-100 hover:bg-slate-800 rounded-xl border border-slate-800 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold rounded-xl transition-all shadow-md shadow-amber-500/20"
                >
                  <span>Sign Up</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <section id="hero" className="relative py-20 lg:py-28 overflow-hidden border-b border-slate-800/80">
          {/* Background Ambient Glows */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-amber-500/10 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px] pointer-events-none" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
            
            {/* Pill Tag */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold font-mono mb-6 shadow-sm">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span>SIH26165 • OIL HSE Safety Intelligence</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-slate-100 tracking-tight max-w-4xl mx-auto leading-tight sm:leading-none">
              AI-Powered HSE Intelligence for{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600">
                Safer Operations
              </span>
            </h1>

            {/* Subtitle */}
            <p className="mt-6 text-sm sm:text-base text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
              AI/NLP Engine designed for Oil India Limited to analyze safety reports, identify potential{' '}
              <strong className="text-slate-100 font-semibold">Serious Injury & Fatality (SIF) precursor indicators</strong>, map Life-Saving Rules, and evaluate operational risk.
            </p>

            {/* CTAs */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              {isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold text-sm rounded-xl transition-all shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2"
                >
                  <span>Open HSE Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold text-sm rounded-xl transition-all shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2"
                  >
                    <span>Get Started</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto px-8 py-3.5 bg-slate-900 hover:bg-slate-800 text-slate-200 font-bold text-sm rounded-xl border border-slate-800 transition-colors flex items-center justify-center gap-2"
                  >
                    <Lock className="w-4 h-4 text-amber-400" />
                    <span>Sign In</span>
                  </Link>
                </>
              )}
            </div>

            {/* Highlight Badges */}
            <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto pt-8 border-t border-slate-800/60">
              <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                <p className="text-xs font-bold text-slate-200">Natural Language NLP</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Report Text Analysis</p>
              </div>
              <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                <p className="text-xs font-bold text-slate-200">9 Life-Saving Rules</p>
                <p className="text-[11px] text-slate-400 mt-0.5">OIL Standard Mapping</p>
              </div>
              <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                <p className="text-xs font-bold text-slate-200">Multi-Factor Risk</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Severity × Likelihood</p>
              </div>
              <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                <p className="text-xs font-bold text-slate-200">Human Review</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Safety Officer Oversight</p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 border-b border-slate-800/80 bg-slate-950/40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <span className="text-xs font-mono text-amber-500 font-semibold uppercase tracking-wider">
                CORE CAPABILITIES
              </span>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-100 mt-2">
                Comprehensive HSE Intelligence Features
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-3 max-w-xl mx-auto">
                End-to-end safety intelligence suite built to ingest, analyze, and manage Unsafe-Act, Unsafe-Condition, and Near-Miss reports.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Feature 1 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-amber-500/10 rounded-xl text-amber-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <Brain className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">1. AI/NLP SIF Detection</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Extracts safety observations from report descriptions, detecting potential Serious Injury & Fatality (SIF) precursor indicators with confidence metrics.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-red-500/10 rounded-xl text-red-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">2. Risk Assessment</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Evaluates operational risk levels (Low, Medium, High, Critical) by calculating event severity and occurrence likelihood matrix.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <BookOpen className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">3. Life-Saving Rules</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Maps safety observations against Oil India Limited’s 9 mandatory Life-Saving Rules (Work at Height, Confined Space, Hot Work, LOTO, etc.).
                </p>
              </div>

              {/* Feature 4 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <PieChart className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">4. Pattern Analysis</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Identifies recurring hazard trends, activity patterns, barrier failures, and location-specific safety risks across drilling and refinery sites.
                </p>
              </div>

              {/* Feature 5 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <CheckSquare className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">5. Corrective Actions</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Generates automated immediate and preventive action items, assigning due dates and tracking completion status for safety personnel.
                </p>
              </div>

              {/* Feature 6 */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl hover:border-amber-500/40 transition-all group">
                <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <UserCheck className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-100">6. Human Review</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Enables Safety Officers to inspect low-confidence AI classifications, confirm or override SIF flags, and submit audit-logged decision notes.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-20 border-b border-slate-800/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <span className="text-xs font-mono text-amber-500 font-semibold uppercase tracking-wider">
                WORKFLOW PIPELINE
              </span>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-100 mt-2">
                How The SIF Precursor AI Engine Works
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-3 max-w-xl mx-auto">
                Step-by-step intelligence pipeline transforming raw safety observation text into actionable HSE insights.
              </p>
            </div>

            {/* Horizontal / Grid Flowchart */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 text-center">
              {[
                { step: '01', title: 'Safety Report', desc: 'Field observation submission' },
                { step: '02', title: 'AI/NLP Analysis', desc: 'Text preprocessing & NLP' },
                { step: '03', title: 'SIF Indicator', desc: 'Precursor identification' },
                { step: '04', title: 'Risk Assessment', desc: 'Likelihood × Severity' },
                { step: '05', title: 'Rule Mapping', desc: '9 Life-Saving Rules' },
                { step: '06', title: 'Safety Action', desc: 'Corrective action items' },
                { step: '07', title: 'Human Review', desc: 'Safety Officer validation' },
                { step: '08', title: 'HSE Analytics', desc: 'Pattern & trend dashboard' },
              ].map((item, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-800 p-4 rounded-xl relative flex flex-col items-center justify-between">
                  <span className="text-[10px] font-mono text-amber-500 font-extrabold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    STEP {item.step}
                  </span>
                  <div className="my-3">
                    <p className="text-xs font-bold text-slate-100">{item.title}</p>
                    <p className="text-[10px] text-slate-400 mt-1">{item.desc}</p>
                  </div>
                  {idx < 7 && (
                    <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-amber-500 font-bold">
                      →
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/20 border border-slate-800 p-8 sm:p-12 rounded-3xl relative overflow-hidden">
              <div className="max-w-3xl relative z-10">
                <div className="flex items-center gap-2 mb-4">
                  <Award className="w-5 h-5 text-amber-500" />
                  <span className="text-xs font-mono text-amber-400 font-bold uppercase tracking-wider">
                    OIL INDIA LIMITED • HSE COMMITMENT
                  </span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-100">
                  Proactive Safety Intelligence for Zero Harm
                </h2>
                <p className="text-xs sm:text-sm text-slate-300 mt-4 leading-relaxed">
                  Oil India Limited is dedicated to maintaining the highest safety standards across drilling, exploration, production, and processing facilities. This SIF Precursor AI Engine assists HSE personnel by highlighting safety observation indicators before incidents occur, supporting continuous safety improvement.
                </p>
                <div className="mt-8 flex flex-wrap gap-4">
                  {isAuthenticated ? (
                    <Link
                      to="/dashboard"
                      className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-lg shadow-amber-500/20 flex items-center gap-2"
                    >
                      <span>Access HSE Portal</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  ) : (
                    <Link
                      to="/register"
                      className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-lg shadow-amber-500/20 flex items-center gap-2"
                    >
                      <span>Create Personnel Account</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-8 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-3">
          <div className="flex items-center justify-center gap-2">
            <Flame className="w-4 h-4 text-amber-500" />
            <span className="font-bold text-slate-200">OIL INDIA LIMITED (OIL)</span>
          </div>
          <p className="text-[11px] text-slate-400">
            SIH26165 — AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in Unsafe-Act/Condition and Near-Miss Reports
          </p>
          <p className="text-[10px] text-slate-400 font-mono">
            &copy; {new Date().getFullYear()} Oil India Limited. All Rights Reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
