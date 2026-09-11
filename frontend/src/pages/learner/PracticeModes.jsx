import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';
import {
  Video, Lock, Unlock, ArrowRight, ShieldCheck, CheckCircle2,
  Sparkles, Layers, BookOpen, Award, AlertCircle, RefreshCw, Zap
} from 'lucide-react';

const LEVEL_RANKS = {
  'Beginner': 1,
  'Intermediate': 2,
  'Expert': 3,
  'Advanced': 3 // Backward compatibility mapping
};

export const PracticeModes = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/users/profile');
      setProfile(res.data);
    } catch (err) {
      console.error("Failed to fetch learner profile for practice modes:", err);
      setError("Unable to load learner profile level. Using default level.");
    } finally {
      setLoading(false);
    }
  };

  // Determine user's real authenticated learning level
  const userLevel = profile?.learning_level || (profile?.learning_level === null ? 'Not Set' : 'Beginner');
  const userRank = profile?.learning_level ? (LEVEL_RANKS[profile.learning_level] || 1) : 1;

  // Define exactly the 3 required practice modes
  const practiceModes = [
    {
      id: 'beginner',
      title: 'Beginner',
      tagline: 'Build your foundation with single alphabet letter recognition and fundamental handshapes.',
      requiredRank: 1,
      minLevelName: 'Beginner',
      path: '/practice/beginner',
      icon: BookOpen,
      accentColor: 'sky',
      badgeColor: 'border-sky-500/30 bg-sky-500/10 text-sky-400',
      highlights: [
        'Real-Time MediaPipe 21-Landmark Hand Tracking',
        '26 ASL Alphabet Classes (A to Z)',
        'Immediate Accuracy & Confidence Feedback',
        'Single Sign Mastery Analytics Integration'
      ]
    },
    {
      id: 'intermediate',
      title: 'Intermediate',
      tagline: 'Strengthen your skills with word formation, dynamic gestures, and compound signs.',
      requiredRank: 2,
      minLevelName: 'Intermediate',
      path: '/practice/intermediate',
      icon: Layers,
      accentColor: 'indigo',
      badgeColor: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-400',
      highlights: [
        'Word Formation & Common ASL Vocabulary',
        'Two-Hand Gestures & Complex Postures',
        'Transition Timing & Rhythm Recognition',
        'Phrase-Level Practice Modules'
      ]
    },
    {
      id: 'expert',
      title: 'Expert',
      tagline: 'Challenge your mastery with sentence-level signing, speed drills, and expressive fluency.',
      requiredRank: 3,
      minLevelName: 'Expert',
      path: '/practice/expert',
      icon: Sparkles,
      accentColor: 'amber',
      badgeColor: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
      highlights: [
        'Continuous Sentence & Dialogue Signing',
        'Real-Time Cadence & Speed Analysis',
        'Expressive Posture & Hand Symmetry Assessment',
        'Speed & Fluency Certification Challenges'
      ]
    }
  ];

  // Calculate real counts from actual user authorization state
  const unlockedCount = practiceModes.filter(m => userRank >= m.requiredRank).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 bg-slate-950 text-slate-100 min-h-[calc(100vh-4rem)]">
      
      {/* Header Section */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800/80 bg-slate-900/60 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider">
              <Video className="w-3.5 h-3.5" /> Practice Navigation
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Practice Modes
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl">
              Choose the practice level that matches your current learning journey. Unlocked modes are available immediately for real-time practice.
            </p>
          </div>

          <button
            onClick={fetchProfile}
            disabled={loading}
            className="self-start md:self-auto flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-xs font-bold text-slate-300 hover:text-white transition-all cursor-pointer disabled:opacity-50"
            title="Refresh learning level from profile"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
            Refresh Level
          </button>
        </div>

        {/* Real User Level Information Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-800/80">
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Current Learning Level
            </span>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xl font-black text-white">
                {userLevel}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
                Active
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Unlocked Modes
            </span>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xl font-black text-emerald-400">
                {unlockedCount} / 3
              </span>
              <span className="text-[10px] text-slate-400">
                Available now
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              AI Gesture Engine
            </span>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm font-bold text-sky-400 font-mono">
                MediaPipe + RF v001
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3 Practice Modes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {practiceModes.map((mode) => {
          const isUnlocked = userRank >= mode.requiredRank;
          const ModeIcon = mode.icon;

          return (
            <div
              key={mode.id}
              className={`rounded-3xl p-6 sm:p-7 flex flex-col justify-between transition-all relative overflow-hidden border ${
                isUnlocked
                  ? 'bg-slate-900/80 border-slate-700/80 shadow-xl hover:border-indigo-500/50 hover:shadow-2xl hover:shadow-indigo-500/10'
                  : 'bg-slate-950/40 border-slate-800/60 opacity-70 cursor-not-allowed'
              }`}
            >
              {/* Top Row: Icon & Status Badge */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg ${
                      isUnlocked
                        ? mode.id === 'beginner'
                          ? 'bg-gradient-to-br from-sky-500 to-indigo-600 text-white'
                          : mode.id === 'intermediate'
                          ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
                          : 'bg-gradient-to-br from-amber-500 to-rose-600 text-white'
                        : 'bg-slate-800 text-slate-500'
                    }`}
                  >
                    <ModeIcon className="w-6 h-6" />
                  </div>

                  {/* Accessible Lock / Unlock Status Indicator */}
                  {isUnlocked ? (
                    <span
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                      aria-label={`${mode.title} mode unlocked`}
                    >
                      <Unlock className="w-3.5 h-3.5" />
                      UNLOCKED
                    </span>
                  ) : (
                    <span
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700"
                      aria-label={`${mode.title} mode locked`}
                    >
                      <Lock className="w-3.5 h-3.5" />
                      LOCKED
                    </span>
                  )}
                </div>

                {/* Title & Tagline */}
                <h3 className={`text-xl font-black tracking-tight ${isUnlocked ? 'text-white' : 'text-slate-400'}`}>
                  {mode.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed min-h-[2.5rem]">
                  {mode.tagline}
                </p>

                {/* Module Highlights */}
                <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-2.5">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                    Curriculum Scope
                  </span>
                  <ul className="space-y-2 text-xs">
                    {mode.highlights.map((item, idx) => (
                      <li
                        key={idx}
                        className={`flex items-start gap-2 ${
                          isUnlocked ? 'text-slate-300' : 'text-slate-500'
                        }`}
                      >
                        <CheckCircle2
                          className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${
                            isUnlocked ? 'text-indigo-400' : 'text-slate-600'
                          }`}
                        />
                        <span className="leading-tight">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Action Button & Explanatory Lock Information */}
              <div className="mt-8 pt-4 border-t border-slate-800/80 space-y-3">
                {isUnlocked ? (
                  <Link
                    to={mode.path}
                    className={`w-full py-3 px-4 rounded-xl font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-lg cursor-pointer ${
                      mode.id === 'beginner'
                        ? 'bg-sky-500 hover:bg-sky-400 text-slate-950 shadow-sky-500/20'
                        : mode.id === 'intermediate'
                        ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                        : 'bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/20'
                    }`}
                  >
                    Start {mode.title} Practice <ArrowRight className="w-4 h-4" />
                  </Link>
                ) : (
                  <div>
                    <button
                      disabled
                      aria-disabled="true"
                      className="w-full py-3 px-4 rounded-xl font-bold text-xs uppercase tracking-wider bg-slate-800/80 text-slate-500 border border-slate-700/60 cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <Lock className="w-4 h-4" /> Locked
                    </button>
                    <p className="text-[11px] text-slate-500 text-center mt-2 leading-tight">
                      Reach <strong className="text-slate-400">{mode.minLevelName}</strong> level in your profile to unlock this mode.
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
