import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Users, BarChart2, BookOpen, AlertTriangle, FileText, ArrowRight, Eye, Send, Download, Award, Activity } from 'lucide-react';
import api from '../../api/client';
import { MasteryMatrix } from '../../components/common/MasteryMatrix';
import { StudentDetailsModal } from './StudentDetailsModal';

export { InstructorDashboard } from './Dashboard';

export const Students = () => {
  const [learners, setLearners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLearnerId, setSelectedLearnerId] = useState(null);

  useEffect(() => {
    fetchLearners();
  }, []);

  const fetchLearners = async () => {
    try {
      setLoading(true);
      const res = await api.get('/analytics/instructor/learners');
      setLearners(res.data || []);
    } catch (err) {
      console.error("Failed to fetch students roster", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black flex items-center gap-2 text-white">
            <Users className="w-6 h-6 text-indigo-400" /> Student Roster & Enrolled Class List
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real registered learner accounts with live gesture evaluation records.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-bold border border-indigo-500/20">
          {learners.length} Enrolled Learners
        </span>
      </div>

      <div className="glass-panel p-6 rounded-2xl space-y-4">
        {loading ? (
          <div className="text-center py-12 text-indigo-400 font-bold text-xs">
            Loading student roster...
          </div>
        ) : learners.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            No registered students found in database.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="p-3">Learner</th>
                  <th className="p-3">Email Address</th>
                  <th className="p-3">Level</th>
                  <th className="p-3">Accuracy</th>
                  <th className="p-3">Attempts</th>
                  <th className="p-3">Streak</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {learners.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-800/40">
                    <td className="p-3 font-bold text-white flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-300 font-bold text-xs flex items-center justify-center border border-indigo-500/30">
                        {l.full_name?.charAt(0) || 'L'}
                      </div>
                      {l.full_name}
                    </td>
                    <td className="p-3 font-mono text-slate-400">{l.email}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-sky-400 font-semibold border border-slate-700">
                        {l.learning_level}
                      </span>
                    </td>
                    <td className="p-3 font-bold text-indigo-400">
                      {l.overall_accuracy !== null ? `${l.overall_accuracy}%` : '—'}
                    </td>
                    <td className="p-3">{l.total_attempts}</td>
                    <td className="p-3 text-amber-400 font-bold">{l.practice_streak_days}d</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedLearnerId(l.id)}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-1.5 ml-auto shadow-md shadow-indigo-600/20 cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" /> Track
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedLearnerId && (
        <StudentDetailsModal
          learnerId={selectedLearnerId}
          onClose={() => setSelectedLearnerId(null)}
        />
      )}
    </div>
  );
};

export const StudentDetails = () => {
  const { studentId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (studentId) {
      fetchStudent();
    }
  }, [studentId]);

  const fetchStudent = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/analytics/learners/${studentId}`);
      setData(res.data);
    } catch (err) {
      console.error("Failed to fetch student details", err);
    } finally {
      setLoading(false);
    }
  };

  if (!studentId) {
    return <Students />;
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
      <h1 className="text-2xl font-black text-white">
        Student Analytics Drilldown #{studentId}
      </h1>
      {loading ? (
        <div className="text-center py-12 text-indigo-400 font-bold text-xs">
          Loading student telemetry...
        </div>
      ) : !data ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          Student not found.
        </div>
      ) : (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <h2 className="text-lg font-bold text-white">{data.user.full_name}</h2>
            <p className="text-xs text-slate-400">{data.user.email} • {data.user.learning_level}</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <h3 className="text-sm font-bold text-white">29-Sign Alphabet Mastery Matrix</h3>
            <MasteryMatrix signClassification={data.sign_classification} />
          </div>
        </div>
      )}
    </div>
  );
};

export const ClassProgress = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Class-Wide Progress Analytics</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Aggregated sign mastery percentages across enrolled learners.</p>
    </div>
  </div>
);

export const AssessmentAnalytics = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Assessment Analytics & Score Distribution</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Evaluation of exam pass rates and joint positioning scores.</p>
    </div>
  </div>
);

export const WeakAreas = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <AlertTriangle className="w-6 h-6 text-rose-400" /> Class-Wide Weak Gesture Identification
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Identification of top confused sign pairs across the class (e.g. M vs N, A vs S).</p>
    </div>
  </div>
);

export const CourseManagement = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <BookOpen className="w-6 h-6 text-indigo-400" /> Course Creation & Module Registry
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Create and modify ASL curriculum modules.</p>
    </div>
  </div>
);

export const LessonManagement = () => (
  <div className="max-w-5xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">Lesson Content Management</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Edit individual lesson instructions and canonical hand positions.</p>
    </div>
  </div>
);

export const InstructorReports = () => (
  <div className="max-w-4xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <FileText className="w-6 h-6 text-indigo-400" /> Instructor Class Reports
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Export class progress reports in PDF & Excel formats.</p>
    </div>
  </div>
);
