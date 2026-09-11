import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import { Users, Eye } from 'lucide-react';
import { StudentDetailsModal } from './StudentDetailsModal';

export const InstructorDashboard = () => {
  const [data, setData] = useState(null);
  const [learners, setLearners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLearnerId, setSelectedLearnerId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchInstructorData();
  }, []);

  const fetchInstructorData = async () => {
    try {
      setLoading(true);
      const [analyticsRes, learnersRes] = await Promise.all([
        api.get('/analytics/instructor'),
        api.get('/analytics/instructor/learners')
      ]);
      setData(analyticsRes.data);
      setLearners(learnersRes.data || []);
    } catch (err) {
      console.error("Failed to fetch instructor dashboard", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-indigo-400 font-bold">
        Loading Instructor Portal...
      </div>
    );
  }

  if (!data) return null;

  const totalSubmissions = data.total_practice_submissions ?? learners.reduce((acc, l) => acc + (l.total_attempts || 0), 0);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-2xl font-black text-white flex items-center gap-3">
          <Users className="w-7 h-7 text-indigo-400" />
          Instructor Class Analytics & Student Progress
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Monitor enrolled learners, track individual gesture mastery, issue private instructions, and export performance reports.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl">
          <span className="text-xs font-bold text-slate-400 uppercase">Enrolled Students</span>
          <div className="text-4xl font-black text-white mt-2">{data.total_students}</div>
          <p className="text-xs text-indigo-400 mt-1">{learners.length} Active registered learner accounts</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl">
          <span className="text-xs font-bold text-slate-400 uppercase">Class Average Accuracy</span>
          <div className="text-4xl font-black text-indigo-400 mt-2">
            {data.average_class_accuracy !== null ? `${data.average_class_accuracy}%` : 'No data'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Across all real evaluated gesture attempts</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl">
          <span className="text-xs font-bold text-slate-400 uppercase">Total Practice Submissions</span>
          <div className="text-4xl font-black text-white mt-2">{totalSubmissions}</div>
          <p className="text-xs text-emerald-400 mt-1">Real-time landmark evaluations logged</p>
        </div>
      </div>

      {/* Enrolled Students Roster Table with Track Action */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Enrolled Students Roster & Real-Time Tracking</h2>
            <p className="text-xs text-slate-400">Click Track to inspect real individual metrics, sign mastery, and send private instructions.</p>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">
            {learners.length} Total Learners
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="p-3">Learner Name</th>
                <th className="p-3">Email Address</th>
                <th className="p-3">Level</th>
                <th className="p-3">Overall Accuracy</th>
                <th className="p-3">Total Attempts</th>
                <th className="p-3">Streak</th>
                <th className="p-3">Last Practice</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {learners.length === 0 ? (
                <tr>
                  <td colSpan="8" className="p-6 text-center text-slate-400">
                    No enrolled learners found in the database.
                  </td>
                </tr>
              ) : (
                learners.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-800/40 transition-colors">
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
                    <td className="p-3 font-mono text-slate-300">{l.total_attempts}</td>
                    <td className="p-3 text-amber-400 font-bold">{l.practice_streak_days}d</td>
                    <td className="p-3 text-slate-400">
                      {l.last_practice_at ? new Date(l.last_practice_at).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedLearnerId(l.id)}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-1.5 ml-auto shadow-md shadow-indigo-600/20 cursor-pointer transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" /> Track
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Learner Drilldown Modal */}
      {selectedLearnerId && (
        <StudentDetailsModal
          learnerId={selectedLearnerId}
          onClose={() => setSelectedLearnerId(null)}
        />
      )}
    </div>
  );
};
