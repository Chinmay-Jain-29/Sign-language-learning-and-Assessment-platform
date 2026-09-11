import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Sparkles, BookOpen, Clock, Target, CheckCircle2, Video, Trophy, ShieldCheck } from 'lucide-react';

export const ExpertPractice = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 bg-slate-950 text-slate-100 min-h-[calc(100vh-4rem)]">
      
      {/* Top Header with Back Navigation */}
      <div className="glass-card p-6 rounded-3xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <Link
            to="/practice"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-bold transition-all border border-slate-700 mb-3"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Practice Modes
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-500 to-rose-600 flex items-center justify-center text-white shadow-lg">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white flex items-center gap-2">
                Expert Practice
              </h1>
              <p className="text-xs text-slate-400">
                Sentence-level signing, speed challenges & expressive conversational fluency
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Expert Mode
          </span>
          <Link
            to="/practice/beginner"
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-bold transition-all border border-slate-700"
          >
            Switch to Beginner
          </Link>
        </div>
      </div>

      {/* Main Container Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Module Scope Card */}
        <div className="lg:col-span-2 glass-card p-6 sm:p-8 rounded-3xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-lg font-extrabold text-white">
                Expert Practice Module
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Mastery speed & full conversational fluency
              </p>
            </div>
            <span className="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Module Unlocked
            </span>
          </div>

          <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-amber-300 flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-400" /> Expert Fluency & Real-Time Cadence
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Expert practice challenges high-proficiency signers with full sentence dialogues, speed drills, and contextual signing evaluation.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <span className="font-bold text-white block">Speed Drills</span>
                <span className="text-slate-400 text-[11px]">Rapid continuous sign sequence recognition</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <span className="font-bold text-white block">Expressive Fluency</span>
                <span className="text-slate-400 text-[11px]">Holistic spatial and structural articulation</span>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-amber-950/20 border border-amber-500/20 space-y-3">
            <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider">
              Practice Recommendations
            </h4>
            <p className="text-xs text-slate-300">
              Expert signing challenges will be accessible here. You can benchmark your letter recognition speed anytime in Beginner Mode.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link
                to="/practice/beginner"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-black transition-all shadow-md shadow-sky-500/20"
              >
                <Video className="w-3.5 h-3.5" /> Launch Real-Time Camera Practice
              </Link>
              <Link
                to="/achievements"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all border border-slate-700"
              >
                <Trophy className="w-3.5 h-3.5 text-amber-400" /> View Sign Achievements
              </Link>
            </div>
          </div>
        </div>

        {/* Level & Objective Sidebar */}
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-400" /> Expert Level Objectives
            </h3>
            <ul className="space-y-2.5 text-xs text-slate-300">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Maintain &gt;90% accuracy at native signing speed</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Seamless transition across compound vocabulary</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Complete all 26 alphabet mastery milestones</span>
              </li>
            </ul>
          </div>

          <div className="glass-card p-6 rounded-3xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-3 text-center">
            <h3 className="text-sm font-bold text-white">Need to refine basic signs?</h3>
            <p className="text-xs text-slate-400">
              Return to single sign recognition anytime to practice specific letters.
            </p>
            <Link
              to="/practice/beginner"
              className="inline-block w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 font-bold text-xs border border-slate-700 transition-all"
            >
              Go to Beginner Practice
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
};
