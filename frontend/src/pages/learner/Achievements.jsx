import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import {
  Trophy, Lock, Unlock, CheckCircle2, Sparkles, AlertCircle,
  RefreshCw, Play, Flame, BarChart3, Search, Filter
} from 'lucide-react';

export const Achievements = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('ALL'); // ALL, UNLOCKED, LOCKED
  const [searchQuery, setSearchQuery] = useState('');
  const [activeModalAch, setActiveModalAch] = useState(null);

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await api.get('/achievements');
      setData(res.data);
    } catch (err) {
      console.error("Failed to load achievements", err);
      setErrorMsg(err.response?.data?.message || 'Failed to load sign achievements.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-indigo-400 font-bold gap-3">
        <RefreshCw className="w-6 h-6 animate-spin" />
        <span>Loading alphabet mastery achievements...</span>
      </div>
    );
  }

  const achievements = data?.achievements || [];
  const filteredAchievements = achievements.filter(ach => {
    if (selectedFilter === 'UNLOCKED' && !ach.is_unlocked) return false;
    if (selectedFilter === 'LOCKED' && ach.is_unlocked) return false;
    if (searchQuery) {
      const q = searchQuery.toUpperCase().trim();
      return ach.sign.includes(q) || ach.title.toUpperCase().includes(q);
    }
    return true;
  });

  const unlockedCount = data?.unlocked_count || 0;
  const lockedCount = data?.locked_count || 26;
  const completionRate = data?.completion_percentage || 0.0;
  const masteredCount = data?.mastered_signs_count || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8 text-slate-100">
      
      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800 bg-slate-900/70 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-black uppercase tracking-wider">
              <Trophy className="w-4 h-4" /> ASL Alphabet Milestones
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Sign Mastery Achievements
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Earn permanent trophy badges by achieving canonical <span className="text-emerald-400 font-bold">Mastered</span> status (≥85% accuracy and confidence over ≥5 practice attempts) for each of the 26 ASL alphabet signs.
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full lg:w-auto">
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-center min-w-[100px]">
              <span className="text-xs text-slate-400 font-bold block">Unlocked</span>
              <span className="text-2xl font-black text-amber-400">{unlockedCount}</span>
              <span className="text-[10px] text-slate-500 block">of 26 Total</span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-center min-w-[100px]">
              <span className="text-xs text-slate-400 font-bold block">Remaining</span>
              <span className="text-2xl font-black text-slate-300">{lockedCount}</span>
              <span className="text-[10px] text-slate-500 block">Locked</span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-center min-w-[100px]">
              <span className="text-xs text-slate-400 font-bold block">Mastered</span>
              <span className="text-2xl font-black text-emerald-400">{masteredCount}</span>
              <span className="text-[10px] text-slate-500 block">Current Signs</span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-center min-w-[100px]">
              <span className="text-xs text-slate-400 font-bold block">Completion</span>
              <span className="text-2xl font-black text-indigo-400">{completionRate}%</span>
              <span className="text-[10px] text-slate-500 block">Progress</span>
            </div>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="mt-8 space-y-2 relative z-10">
          <div className="flex justify-between text-xs font-bold text-slate-400">
            <span>Overall Alphabet Mastery Progress</span>
            <span className="text-amber-400">{unlockedCount} / 26 Unlocked ({completionRate}%)</span>
          </div>
          <div className="w-full bg-slate-950/80 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="bg-gradient-to-r from-amber-500 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-700 shadow-lg shadow-amber-500/20"
              style={{ width: `${Math.max(completionRate, 2)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Tab Filters */}
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-900/80 border border-slate-800 w-full sm:w-auto">
          <button
            onClick={() => setSelectedFilter('ALL')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              selectedFilter === 'ALL'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All (26)
          </button>
          <button
            onClick={() => setSelectedFilter('UNLOCKED')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              selectedFilter === 'UNLOCKED'
                ? 'bg-amber-500 text-slate-950 font-black shadow-md'
                : 'text-slate-400 hover:text-amber-300'
            }`}
          >
            <Unlock className="w-3.5 h-3.5" /> Unlocked ({unlockedCount})
          </button>
          <button
            onClick={() => setSelectedFilter('LOCKED')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              selectedFilter === 'LOCKED'
                ? 'bg-slate-800 text-slate-200 shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Lock className="w-3.5 h-3.5" /> Locked ({lockedCount})
          </button>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search sign letter (e.g. A, B)..."
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
          />
        </div>
      </div>

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 26 Alphabet Achievements Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {filteredAchievements.map((ach) => {
          const isUnlocked = ach.is_unlocked;
          return (
            <div
              key={ach.sign}
              onClick={() => setActiveModalAch(ach)}
              className={`p-6 rounded-3xl border transition-all duration-300 relative group cursor-pointer overflow-hidden flex flex-col justify-between ${
                isUnlocked
                  ? 'bg-gradient-to-b from-slate-900/90 to-amber-950/20 border-amber-500/40 hover:border-amber-400 shadow-xl shadow-amber-500/5 hover:-translate-y-1'
                  : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700 opacity-75 hover:opacity-100 hover:-translate-y-0.5'
              }`}
              role="button"
              tabIndex={0}
              aria-label={`${ach.title} - ${isUnlocked ? 'Unlocked' : 'Locked'}`}
            >
              {/* Subtle top glow for unlocked */}
              {isUnlocked && (
                <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
              )}

              {/* Top Row: Icon & Status Badge */}
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-black shadow-lg transition-transform group-hover:scale-105 ${
                  isUnlocked
                    ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-slate-950 shadow-amber-500/20 border border-amber-300'
                    : 'bg-slate-800 text-slate-500 border border-slate-700'
                }`}>
                  {ach.sign}
                </div>

                <div className="text-right">
                  {isUnlocked ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-black uppercase tracking-wider">
                      <CheckCircle2 className="w-3 h-3" /> Unlocked
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl bg-slate-800 border border-slate-700 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                      <Lock className="w-3 h-3" /> Locked
                    </span>
                  )}
                  <span className="block text-[9px] text-slate-500 mt-1">
                    {ach.current_category}
                  </span>
                </div>
              </div>

              {/* Middle Details */}
              <div className="space-y-1 mb-4">
                <h3 className={`text-base font-black ${isUnlocked ? 'text-white' : 'text-slate-300'}`}>
                  {ach.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                  {isUnlocked ? ach.description : `Master sign '${ach.sign}' to unlock this milestone.`}
                </p>
              </div>

              {/* Bottom Metrics / Date */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                {isUnlocked ? (
                  <>
                    <span className="text-amber-400/90 font-bold flex items-center gap-1">
                      <Trophy className="w-3.5 h-3.5" /> Mastered
                    </span>
                    <span className="text-slate-500 text-[10px]">
                      {ach.unlocked_at ? new Date(ach.unlocked_at).toLocaleDateString() : 'Earned'}
                    </span>
                  </>
                ) : (
                  <>
                    <span className="text-slate-500 font-medium flex items-center gap-1">
                      <Lock className="w-3 h-3" /> {ach.total_attempts} attempts
                    </span>
                    <span className="text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1 group-hover:underline">
                      Practice <Play className="w-2.5 h-2.5" />
                    </span>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Detail View */}
      {activeModalAch && (
        <div 
          onClick={(e) => { if (e.target === e.currentTarget) setActiveModalAch(null); }}
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        >
          <div className="glass-card max-w-md w-full p-6 sm:p-8 rounded-3xl border border-slate-800 bg-slate-900 shadow-2xl space-y-6 relative animate-in fade-in zoom-in-95 duration-200">
            
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl font-black shadow-xl ${
                  activeModalAch.is_unlocked
                    ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-slate-950 border border-amber-300'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}>
                  {activeModalAch.sign}
                </div>
                <div>
                  <h3 className="text-xl font-black text-white">{activeModalAch.title}</h3>
                  <p className="text-xs text-slate-400">ASL Alphabet Class</p>
                </div>
              </div>

              <button
                onClick={() => setActiveModalAch(null)}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white cursor-pointer transition-all"
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            {/* Status & Unlocked Timestamp */}
            <div className={`p-4 rounded-2xl border ${
              activeModalAch.is_unlocked
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-slate-950 border-slate-800 text-slate-400'
            }`}>
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span>Achievement Status</span>
                <span className="uppercase">{activeModalAch.is_unlocked ? '🏆 Unlocked' : '🔒 Locked'}</span>
              </div>
              <p className="text-xs opacity-90">
                {activeModalAch.is_unlocked
                  ? `Unlocked on ${new Date(activeModalAch.unlocked_at).toLocaleString()}`
                  : `Requires ≥85% accuracy and confidence over ≥5 practice attempts to master sign '${activeModalAch.sign}'.`}
              </p>
            </div>

            {/* Canonical Performance Stats */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-[10px] text-slate-400 block font-bold">Category</span>
                <span className="text-xs font-black text-white">{activeModalAch.current_category}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-[10px] text-slate-400 block font-bold">Accuracy</span>
                <span className="text-xs font-black text-indigo-400">{activeModalAch.accuracy}%</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-[10px] text-slate-400 block font-bold">Attempts</span>
                <span className="text-xs font-black text-slate-300">{activeModalAch.total_attempts}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setActiveModalAch(null)}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold cursor-pointer transition-all"
              >
                Close
              </button>
              <Link
                to={`/practice/beginner?target=${encodeURIComponent(activeModalAch.sign)}`}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-extrabold flex items-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer transition-all"
              >
                <Play className="w-4 h-4" /> Practice Sign {activeModalAch.sign}
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
