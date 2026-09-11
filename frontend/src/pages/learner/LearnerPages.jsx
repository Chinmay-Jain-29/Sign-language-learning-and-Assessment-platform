import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User, BookOpen, Award, CheckCircle2, Trophy, ArrowRight, Download, Settings as SettingsIcon, Bell, Sparkles } from 'lucide-react';
import api from '../../api/client';

export const Profile = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <User className="w-6 h-6 text-sky-400" /> Learner Profile & Goals
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-sky-500/20 text-sky-400 font-extrabold text-2xl flex items-center justify-center border border-sky-500/30">
          JD
        </div>
        <div>
          <h2 className="text-xl font-bold">Jane Doe</h2>
          <p className="text-xs text-slate-400">Learner Account • Joined August 2026</p>
        </div>
      </div>
    </div>
  </div>
);

export const Courses = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <BookOpen className="w-6 h-6 text-sky-400" /> Course Catalog & Modules
    </h1>
    <div className="grid md:grid-cols-3 gap-6">
      {['ASL Alphabet Fundamentals', 'Numbers & Basic Counting', 'Common Conversational Signs'].map((title, i) => (
        <div key={title} className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded-full border border-sky-500/30">
              Module {i + 1}
            </span>
            <h3 className="text-lg font-bold text-white mt-3">{title}</h3>
            <p className="text-xs text-slate-400 mt-2">Comprehensive ASL module covering canonical hand shapes and spatial tracking.</p>
          </div>
          <Link to={`/courses/${i + 1}`} className="mt-6">
            <button className="w-full bg-slate-800 hover:bg-slate-700 text-sky-400 font-bold px-4 py-2 rounded-xl text-xs border border-slate-700 flex items-center justify-center gap-2">
              View Course Details <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </Link>
        </div>
      ))}
    </div>
  </div>
);

export const CourseDetails = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Course Details: ASL Alphabet Fundamentals</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
      <p className="text-xs text-slate-400">Master all 26 alphabet letters (A-Z) and 3 special tokens (DEL, NOTHING, SPACE).</p>
    </div>
  </div>
);

export const LessonDetails = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Lesson: Vowels & Fist Shapes</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Interactive lesson covering letters A, E, I, O, U.</p>
    </div>
  </div>
);

export const PracticeSelection = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Practice Selection</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400 mb-4">Choose sign category or individual target letters.</p>
      <Link to="/practice">
        <button className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-xs">
          Start Practice Session
        </button>
      </Link>
    </div>
  </div>
);

export const LiveRecognition = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Continuous Live Sign Recognition</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 text-center">
      <p className="text-xs text-slate-400">Continuous translation mode capturing fluid ASL gestures.</p>
    </div>
  </div>
);

export const AssessmentResult = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold text-emerald-400">Assessment Result: Passed (94%)</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Detailed breakdown of joint spatial accuracy and speed.</p>
    </div>
  </div>
);

export const PracticeReview = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Practice Attempt Review</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Anatomical Joint Position Comparison vs Canonical Sign Model.</p>
    </div>
  </div>
);

export const Progress = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Overall Learning Progress</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Historical performance trends and consistency rating.</p>
    </div>
  </div>
);

export const SkillMastery = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Skill Mastery Overview</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Skill level progression across all 29 ASL gesture categories.</p>
    </div>
  </div>
);

export const Recommendations = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Sparkles className="w-6 h-6 text-sky-400" /> Personalized Recommendations
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Data-driven target suggestions derived from recent mistake counts.</p>
    </div>
  </div>
);

export const PracticeHistory = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Practice History Log</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Chronological history of all practice attempts and assessments.</p>
    </div>
  </div>
);

export const Reports = () => {
  const [downloading, setDownloading] = useState(false);
  const [downloadType, setDownloadType] = useState(null);
  const [error, setError] = useState(null);

  const handleDownload = async (type) => {
    try {
      setDownloading(true);
      setDownloadType(type);
      setError(null);
      const endpoint = type === 'pdf' ? '/reports/me/pdf' : '/reports/performance/excel';
      const res = await api.get(endpoint, { responseType: 'blob' });
      const mime = type === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      const blob = new Blob([res.data], { type: mime });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = type === 'pdf' ? 'ASL_Sensei_Official_Report.pdf' : 'ASL_Sensei_Performance_Data.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download report:", err);
      setError("Failed to generate or download report. Please try again.");
    } finally {
      setDownloading(false);
      setDownloadType(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white flex items-center gap-2">
          <Download className="w-6 h-6 text-sky-400" />
          Official Learner Performance Reports
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Export your 100% data-driven, verified practice performance and 29-sign alphabet mastery analytics.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold">
          {error}
        </div>
      )}

      <div className="glass-panel p-6 rounded-2xl space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-white">Comprehensive Progress PDF Document</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Includes profile summary, lifetime metrics, color-coded 29-sign alphabet mastery matrix, and recent attempts log.
            </p>
          </div>
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center gap-2 cursor-pointer transition-all"
          >
            <Download className="w-4 h-4" />
            {downloading && downloadType === 'pdf' ? 'Generating PDF...' : 'Download PDF Report'}
          </button>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-white">Full Raw Practice History Excel Worksheet</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Exports raw landmark evaluation metrics, timestamped attempts, and sign statistics in .xlsx format.
            </p>
          </div>
          <button
            onClick={() => handleDownload('excel')}
            disabled={downloading}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 text-xs font-bold border border-slate-700 disabled:opacity-50 flex items-center gap-2 cursor-pointer transition-all"
          >
            <Download className="w-4 h-4" />
            {downloading && downloadType === 'excel' ? 'Exporting Excel...' : 'Download Excel (.xlsx)'}
          </button>
        </div>
      </div>
    </div>
  );
};

export const Certification = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Award className="w-6 h-6 text-amber-400" /> ASL Certification & Skill Level Exams
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Take official level certification examinations to prove ASL proficiency.</p>
    </div>
  </div>
);

export const Notifications = () => {
  const [instructions, setInstructions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstructions();
  }, []);

  const fetchInstructions = async () => {
    try {
      const res = await api.get('/instructions/me');
      setInstructions(res.data || []);
    } catch (err) {
      console.error("Failed to fetch instructions", err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.patch(`/instructions/${id}/read`);
      setInstructions(prev => prev.map(i => i.id === id ? { ...i, is_read: true } : i));
    } catch (err) {
      console.error("Failed to mark instruction as read", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
      <h1 className="text-2xl font-black flex items-center gap-2 text-white">
        <Bell className="w-6 h-6 text-sky-400" /> Notifications & Private Instructor Guidance
      </h1>
      
      {loading ? (
        <div className="text-xs text-slate-400">Loading instructions feed...</div>
      ) : instructions.length === 0 ? (
        <div className="glass-panel p-8 rounded-2xl text-center text-slate-400 text-xs">
          No notifications or instructor instructions yet. Keep practicing!
        </div>
      ) : (
        <div className="space-y-3">
          {instructions.map((inst) => (
            <div
              key={inst.id}
              className={`p-4 rounded-2xl border transition-all ${
                inst.is_read
                  ? 'bg-slate-900/40 border-slate-800/80 text-slate-300'
                  : 'bg-indigo-950/30 border-indigo-500/40 text-white shadow-lg shadow-indigo-500/5'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-indigo-400">
                      Instruction from {inst.instructor_name}
                    </span>
                    {!inst.is_read && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500 text-white">
                        NEW
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium mt-1.5 text-slate-100">{inst.message}</p>
                  <span className="text-[10px] text-slate-400 mt-2 block">
                    {new Date(inst.created_at).toLocaleString()}
                  </span>
                </div>
                {!inst.is_read && (
                  <button
                    onClick={() => markAsRead(inst.id)}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 text-xs font-bold border border-indigo-500/30 cursor-pointer"
                  >
                    Mark as Read
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const Settings = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <SettingsIcon className="w-6 h-6 text-sky-400" /> Accessibility & Account Settings
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
      <div className="flex items-center justify-between text-xs">
        <span>High Contrast Mode</span>
        <input type="checkbox" className="accent-sky-500 w-4 h-4" />
      </div>
    </div>
  </div>
);
