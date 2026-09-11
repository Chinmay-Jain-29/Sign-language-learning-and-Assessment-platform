import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/common/StatCard';
import { TrendChart } from '../../components/common/TrendChart';
import { MasteryMatrix } from '../../components/common/MasteryMatrix';
import { 
  Trophy, Flame, Clock, Award, Sparkles, ArrowRight, 
  BarChart3, CheckCircle2, Target, AlertTriangle, AlertCircle, RefreshCw, Video
} from 'lucide-react';

export const LearnerDashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/analytics/learner');
      setData(res.data);
    } catch (err) {
      console.error("Failed to load learner dashboard data", err);
      setError("Unable to load dashboard data. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  // 1. Loading State (Clean Skeleton)
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 bg-slate-950 text-slate-100 animate-pulse">
        <div className="h-10 bg-slate-900 rounded-xl w-64"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {[...Array(7)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-900/80 rounded-2xl border border-slate-800"></div>
          ))}
        </div>
        <div className="h-32 bg-slate-900/80 rounded-2xl border border-slate-800"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-64 bg-slate-900/80 rounded-2xl border border-slate-800"></div>
          <div className="h-64 bg-slate-900/80 rounded-2xl border border-slate-800"></div>
        </div>
      </div>
    );
  }

  // 2. API Failure Error State
  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-16 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 inline-flex items-center gap-3">
          <AlertCircle className="w-6 h-6" />
          <span className="font-semibold text-sm">{error}</span>
        </div>
        <div>
          <button
            onClick={fetchDashboardData}
            className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 font-bold text-xs border border-slate-700 inline-flex items-center gap-2 transition-all cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // 3. Extract STRICTLY Authenticated User Real Metrics (No fake fallbacks)
  const userProfile = data.user || {};
  const perf = data.performance || {};
  const totalAttempts = perf.total_attempts ?? 0;
  const totalSessions = perf.total_sessions ?? 0;
  const streakDays = perf.practice_streak_days ?? 0;
  
  // Real numeric values or "No data yet"
  const overallScoreDisplay = perf.overall_score !== null && perf.overall_score !== undefined ? `${perf.overall_score}%` : 'No data yet';
  const overallAccuracyDisplay = perf.overall_accuracy !== null && perf.overall_accuracy !== undefined ? `${perf.overall_accuracy}%` : 'No data yet';
  const sessionAccuracyDisplay = perf.current_session_accuracy !== null && perf.current_session_accuracy !== undefined ? `${perf.current_session_accuracy}%` : 'No data yet';
  const avgConfidenceDisplay = perf.average_confidence !== null && perf.average_confidence !== undefined ? `${perf.average_confidence}%` : 'No data yet';

  const recommendedSign = data.recommended_sign || 'A';
  const recommendationReason = data.recommendation_reason || "Start practicing foundational sign 'A' with your webcam.";
  const trendData = data.session_trend || [];
  const recentAttempts = data.recent_attempts || [];
  
  // Single Source of Truth for all 29 signs
  const signClassification = data.sign_classification || data.mastery_list || [];

  // Strictly filter from canonical signClassification list
  const masteredSignsList = signClassification
    .filter((s) => s.category === 'Mastered')
    .map((s) => s.sign);

  const weakestSignsList = signClassification
    .filter((s) => s.total_attempts > 0 && s.category !== 'Mastered' && s.accuracy < 60.0)
    .map((s) => s.sign);

  const revisionSignsList = signClassification
    .filter((s) => s.category === 'Needs Revision')
    .map((s) => s.sign);

  const userName = userProfile.full_name || user?.full_name || 'Learner';
  const learningLevel = userProfile.learning_level || 'Beginner';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8 bg-slate-950 text-slate-100">
      
      {/* Header & User Profile Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
            {learningLevel} Level • Authenticated Session
          </span>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white mt-0.5">
            Welcome back, {userName}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time performance analytics connected to your verified practice history
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/webcam-practice">
            <button className="bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-slate-950 font-bold px-5 py-2.5 rounded-xl transition-all shadow-lg shadow-sky-500/20 flex items-center gap-2 text-xs sm:text-sm cursor-pointer">
              <Sparkles className="w-4 h-4" /> Start Webcam Practice
            </button>
          </Link>
        </div>
      </div>

      {/* Top Stat Cards Grid (100% Real Data) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <StatCard 
          title="Overall Score" 
          value={overallScoreDisplay} 
          badgeText={totalAttempts > 0 ? "Weighted" : "No history"} 
          badgeColor={totalAttempts > 0 ? "emerald" : "amber"} 
          icon={<Trophy className="w-5 h-5 text-amber-400" />} 
        />
        <StatCard 
          title="Overall Accuracy" 
          value={overallAccuracyDisplay} 
          badgeText={totalAttempts > 0 ? "Verified" : "No history"} 
          badgeColor="sky" 
          icon={<BarChart3 className="w-5 h-5 text-sky-400" />} 
        />
        <StatCard 
          title="Session Accuracy" 
          value={sessionAccuracyDisplay} 
          badgeText={totalSessions > 0 ? "Latest" : "No sessions"} 
          badgeColor="indigo" 
          icon={<Target className="w-5 h-5 text-indigo-400" />} 
        />
        <StatCard 
          title="Total Sessions" 
          value={totalSessions} 
          badgeText="Recorded" 
          badgeColor="sky" 
          icon={<Clock className="w-5 h-5 text-sky-400" />} 
        />
        <StatCard 
          title="Total Attempts" 
          value={totalAttempts} 
          badgeText="Evaluated" 
          badgeColor="emerald" 
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />} 
        />
        <StatCard 
          title="Avg Confidence" 
          value={avgConfidenceDisplay} 
          badgeText={totalAttempts > 0 ? "AI Model" : "No data"} 
          badgeColor="amber" 
          icon={<Award className="w-5 h-5 text-amber-400" />} 
        />
        <StatCard 
          title="Practice Streak" 
          value={`${streakDays} Days`} 
          badgeText={streakDays > 0 ? "Active" : "0 days"} 
          badgeColor={streakDays > 0 ? "rose" : "amber"} 
          icon={<Flame className={`w-5 h-5 ${streakDays > 0 ? 'text-rose-400 animate-bounce' : 'text-slate-500'}`} />} 
        />
      </div>

      {/* AI Recommendation Banner */}
      <div className="glass-card p-6 rounded-2xl bg-gradient-to-r from-sky-950/70 via-slate-900 to-indigo-950/70 border border-sky-500/30 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="p-3.5 rounded-2xl bg-sky-500/20 text-sky-400 border border-sky-500/30">
            <Sparkles className="w-7 h-7 animate-pulse" />
          </div>
          <div>
            <span className="text-[11px] text-sky-400 font-bold uppercase tracking-wider">
              {totalAttempts > 0 ? "Personalized Adaptive Target" : "Recommended First Sign"}
            </span>
            <h2 className="text-xl font-bold text-white mt-0.5">Practice Target: Letter '{recommendedSign}'</h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl leading-relaxed">{recommendationReason}</p>
          </div>
        </div>

        <Link
          to="/webcam-practice"
          className="bg-gradient-to-r from-sky-500 to-indigo-500 hover:from-sky-400 hover:to-indigo-400 px-6 py-3 rounded-xl text-slate-950 font-bold text-sm flex items-center gap-2 shadow-lg shadow-sky-500/20 whitespace-nowrap transition-all cursor-pointer"
        >
          Launch Practice <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Performance Trends & Sign Categorization Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Trend Chart (Data-Driven with Clean Empty State) */}
        <div className="lg:col-span-2">
          <TrendChart 
            data={trendData} 
            title="Session Performance Trend" 
          />
        </div>

        {/* Strongest, Weakest & Revision Signs */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-4">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Sign Classification</h4>

          {/* Mastered Signs */}
          <div>
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 mb-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> Mastered Signs (≥85% Acc & Conf)
            </span>
            {masteredSignsList.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {masteredSignsList.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs">
                    {s}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No signs mastered yet (Requires ≥5 attempts, ≥85% accuracy & confidence).</p>
            )}
          </div>

          {/* Weakest Signs */}
          <div>
            <span className="text-xs font-semibold text-rose-400 flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-3.5 h-3.5" /> Weakest Signs (&lt;60%)
            </span>
            {weakestSignsList.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {weakestSignsList.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-xs">
                    {s}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">None identified yet.</p>
            )}
          </div>

          {/* Needing Revision */}
          <div>
            <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5 mb-2">
              <Clock className="w-3.5 h-3.5" /> Signs Needing Revision
            </span>
            {revisionSignsList.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {revisionSignsList.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold text-xs">
                    {s}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">All signs up to date.</p>
            )}
          </div>
        </div>
      </div>

      {/* 29-Sign Alphabet Mastery Matrix (100% Canonical Sign-Based Mapping) */}
      <MasteryMatrix signClassification={signClassification} />

      {/* Recent Session History Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Recent Attempt History</h3>
          <span className="text-xs text-slate-400 font-medium">
            {recentAttempts.length > 0 ? `Showing last ${recentAttempts.length} attempts` : 'No attempts recorded'}
          </span>
        </div>

        {recentAttempts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Date</th>
                  <th className="p-3">Expected Sign</th>
                  <th className="p-3">Predicted Sign</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Accuracy</th>
                  <th className="p-3">Feedback Suggestion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {recentAttempts.map((attempt) => (
                  <tr key={attempt.id} className="hover:bg-slate-800/40">
                    <td className="p-3">{attempt.created_at ? new Date(attempt.created_at).toLocaleDateString() : 'Today'}</td>
                    <td className="p-3 font-bold text-white">{attempt.expected_sign}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-semibold ${
                        attempt.is_correct ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                      }`}>
                        {attempt.predicted_sign}
                      </span>
                    </td>
                    <td className="p-3">{attempt.confidence}%</td>
                    <td className="p-3 font-bold text-sky-400">{attempt.overall_accuracy}%</td>
                    <td className="p-3 text-slate-400 truncate max-w-xs">{attempt.feedback}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 flex flex-col items-center justify-center text-center space-y-3">
            <div className="p-3 rounded-full bg-slate-900 border border-slate-800 text-slate-500">
              <Video className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-300">No recent activity yet</p>
              <p className="text-xs text-slate-500 mt-0.5">Start practicing with your webcam to see your evaluated attempts and joint feedback here.</p>
            </div>
            <Link to="/webcam-practice">
              <button className="mt-2 px-4 py-2 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 text-xs font-bold border border-sky-500/30 transition-all cursor-pointer">
                Start Practicing
              </button>
            </Link>
          </div>
        )}
      </div>

    </div>
  );
};
