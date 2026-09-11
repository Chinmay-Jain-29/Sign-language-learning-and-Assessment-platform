import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { Hand, ArrowRight, Video, Award, BookOpen, ShieldCheck, Sparkles, Globe } from 'lucide-react';

export const Landing = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-sky-500 selection:text-slate-950">
      
      {/* Public Top Navigation */}
      <header className="w-full px-6 py-4 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/20">
              <Hand className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-black bg-gradient-to-r from-sky-400 to-indigo-300 bg-clip-text text-transparent tracking-tight">
                ASL Sensei
              </span>
              <span className="block text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                AI Sign Platform
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <Link to="/login">
              <button className="px-4 py-2 text-xs sm:text-sm font-bold text-slate-300 hover:text-white transition-all">
                Sign In
              </button>
            </Link>
            <Link to="/login">
              <button className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs sm:text-sm font-bold shadow-md shadow-sky-500/20 transition-all flex items-center gap-1.5">
                Get Started for Free <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-16 sm:py-24 px-6 max-w-7xl mx-auto text-center flex flex-col items-center justify-center flex-1">
        {/* Background glow accents */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold uppercase tracking-wider mb-6 animate-pulse">
          <Sparkles className="w-3.5 h-3.5" />
          AI-Powered Sign Language Accessibility & Learning Platform
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight max-w-4xl leading-tight sm:leading-tight">
          Master American Sign Language with Real-Time{' '}
          <span className="bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            AI Hand Tracking
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl leading-relaxed">
          Interactive webcam practice, 21-keypoint 3D anatomical feedback, dynamic learner state tracking, and WCAG 2.1 AA accessible learning paths.
        </p>

        {/* Primary CTA Buttons */}
        <div className="mt-10 flex flex-wrap gap-4 justify-center">
          <Link to="/login">
            <button className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-slate-950 font-black text-base shadow-xl shadow-sky-500/25 transition-all flex items-center gap-2 transform hover:-translate-y-0.5">
              Get Started for Free
              <ArrowRight className="w-5 h-5" />
            </button>
          </Link>
          <Link to="/how-it-works">
            <button className="px-8 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 font-bold text-base border border-slate-800 hover:border-slate-700 transition-all">
              Explore Architecture
            </button>
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl">
            <div className="w-12 h-12 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center text-xl font-bold mb-4 border border-sky-500/20">
              <Video className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">21 3D Landmark Tracking</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Sub-millimeter spatial coordinate normalization with wrist translation and scale invariance evaluated at 30 FPS.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl font-bold mb-4 border border-emerald-500/20">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Adaptive Learning Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              5-stage state transitions (Not Attempted → Learning → Improving → Mastered → Needs Revision) based on real performance.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xl font-bold mb-4 border border-indigo-500/20">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Certified Assessments</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Official skill evaluations, downloadable PDF/Excel progress reports, and verified proficiency credentials.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full px-6 py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        <p>© 2026 ASL Sensei Platform. Built with MediaPipe & Clean Architecture.</p>
      </footer>
    </div>
  );
};
