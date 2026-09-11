import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { Award, HeartHandshake, Activity, FileText, CheckCircle2 } from 'lucide-react';

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
    return <div className="min-h-screen flex items-center justify-center text-teal-400 font-bold">Loading Trainer Portal...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 text-slate-100">
      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h1 className="text-2xl font-black text-white flex items-center gap-3">
          <HeartHandshake className="w-7 h-7 text-teal-400" /> Accessibility Trainer Dashboard
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Track accessibility compliance, individual trainee sign acquisition speed, and assistance queues.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
          <span className="text-xs font-bold text-slate-400 uppercase">Assigned Trainees</span>
          <div className="text-4xl font-black text-white mt-2">12</div>
          <p className="text-xs text-teal-400 mt-1">Active learning paths</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
          <span className="text-xs font-bold text-slate-400 uppercase">Accessibility Rating</span>
          <div className="text-4xl font-black text-teal-400 mt-2">100%</div>
          <p className="text-xs text-slate-400 mt-1">WCAG 2.1 AA Compliant</p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
          <span className="text-xs font-bold text-slate-400 uppercase">Verified Certifications</span>
          <div className="text-4xl font-black text-white mt-2">8</div>
          <p className="text-xs text-emerald-400 mt-1">Level 1 & Level 2 ASL</p>
        </div>
      </div>
    </div>
  );
};

export const LearnerEngagement = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Learner Engagement & Frequency Metrics</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Tracking practice session duration and weekly consistency.</p>
    </div>
  </div>
);

export const SkillDevelopment = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Sign Acquisition & Skill Development</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Rate of sign mastery acquisition per trainee over time.</p>
    </div>
  </div>
);

export const TrainerAssessmentAnalytics = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Assessment Analytics</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Evaluating accessible testing outcomes.</p>
    </div>
  </div>
);

export const CertificationMonitoring = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Award className="w-6 h-6 text-teal-400" /> Certification Verification & Level Exam Monitoring
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Reviewing level exam submissions and issuing official ASL certificates.</p>
    </div>
  </div>
);

export const TrainerReports = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <FileText className="w-6 h-6 text-teal-400" /> Trainer Compliance & Development Reports
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Generate PDF and Excel reports for accessibility training programs.</p>
    </div>
  </div>
);
