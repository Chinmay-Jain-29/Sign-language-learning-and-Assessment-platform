import React, { useState, useEffect } from 'react';
import { Navigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';
import { Lock, ArrowLeft, ShieldAlert, BookOpen } from 'lucide-react';

const LEVEL_RANKS = {
  'Beginner': 1,
  'Intermediate': 2,
  'Expert': 3,
  'Advanced': 3
};

/**
 * Route Guard for Level-Specific Practice Modules.
 * Prevents unauthorized direct URL access if the learner's profile
 * level does not meet the required level rank.
 */
export const PracticeLevelGuard = ({ children, requiredLevel }) => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/users/profile');
      setProfile(res.data);
    } catch (err) {
      console.error("PracticeLevelGuard profile fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm font-medium">Verifying practice authorization...</span>
        </div>
      </div>
    );
  }

  const userLevel = profile?.learning_level || 'Beginner';
  const userRank = LEVEL_RANKS[userLevel] || 1;
  const requiredRank = LEVEL_RANKS[requiredLevel] || 1;

  // If user rank is insufficient, block access with clear explanation and redirection option
  if (userRank < requiredRank) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto shadow-xl">
          <Lock className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-black text-white">
            {requiredLevel} Practice Mode Locked
          </h2>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            This practice module requires <strong className="text-amber-400">{requiredLevel}</strong> level or higher. Your current profile learning level is <strong className="text-indigo-400">{userLevel}</strong>.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 max-w-md mx-auto space-y-2">
          <div className="flex justify-between">
            <span className="text-slate-400">Current Level:</span>
            <span className="font-bold text-white">{userLevel}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Required Level:</span>
            <span className="font-bold text-amber-400">{requiredLevel}</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
          <Link
            to="/practice"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/20"
          >
            <ArrowLeft className="w-4 h-4" /> Return to Practice Modes
          </Link>
          <Link
            to="/practice/beginner"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all border border-slate-700"
          >
            <BookOpen className="w-4 h-4 text-sky-400" /> Start Beginner Practice
          </Link>
        </div>
      </div>
    );
  }

  return children;
};
