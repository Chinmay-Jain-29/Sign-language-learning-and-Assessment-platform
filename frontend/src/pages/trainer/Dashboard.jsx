import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { UserCheck, AlertTriangle, Activity, TrendingUp } from 'lucide-react';

export const TrainerDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrainerData();
  }, []);

  const fetchTrainerData = async () => {
    try {
      const res = await api.get('/analytics/trainer');
      setData(res.data);
    } catch (err) {
      console.error("Failed to fetch trainer dashboard", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-purple-400 font-bold">
        Loading Accessibility Trainer Portal...
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-2xl font-black text-white flex items-center gap-3">
          <UserCheck className="w-7 h-7 text-purple-400" />
          Accessibility Trainer Dashboard
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Identify struggling learners, analyze high-friction sign gestures, and optimize learning paths.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl">
          <span className="text-xs font-bold text-slate-400 uppercase">Total Learners</span>
          <div className="text-4xl font-black text-white mt-2">{data.total_learners}</div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-amber-500">
          <span className="text-xs font-bold text-amber-400 uppercase">Struggling Learners</span>
          <div className="text-4xl font-black text-amber-400 mt-2">{data.struggling_learners_count}</div>
          <p className="text-xs text-slate-400 mt-1">Performance score {'<'} 60%</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl">
          <span className="text-xs font-bold text-slate-400 uppercase">Platform Engagement Rate</span>
          <div className="text-4xl font-black text-purple-400 mt-2">{data.engagement_rate}%</div>
        </div>
      </div>

      {/* Weakest Signs Analytics */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h2 className="text-lg font-bold text-white">Highest Friction Sign Gestures</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {data.common_weak_signs.map((ws) => (
            <div key={ws.sign} className="glass-card p-4 rounded-xl text-center">
              <span className="text-3xl font-black text-white">{ws.sign}</span>
              <div className="text-xs font-bold text-rose-400 mt-2">Avg Mastery: {ws.average_mastery}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
