import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { X, User, Award, CheckCircle2, AlertTriangle, Send, Download, Sparkles, BookOpen, Clock, Activity } from 'lucide-react';
import { MasteryMatrix } from '../../components/common/MasteryMatrix';

export const StudentDetailsModal = ({ learnerId, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [instructionMsg, setInstructionMsg] = useState('');
  const [sendingInstruction, setSendingInstruction] = useState(false);
  const [instructionSuccess, setInstructionSuccess] = useState(null);
  const [instructionError, setInstructionError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    if (learnerId) {
      fetchLearnerDetails();
    }
  }, [learnerId]);

  const fetchLearnerDetails = async () => {
    try {
      setLoading(true);
      setData(null);
      const res = await api.get(`/analytics/learners/${learnerId}`);
      setData(res.data);
    } catch (err) {
      console.error("Failed to fetch learner details", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendInstruction = async (e) => {
    e.preventDefault();
    if (!instructionMsg.trim()) return;

    try {
      setSendingInstruction(true);
      setInstructionSuccess(null);
      setInstructionError(null);

      await api.post('/instructions', {
        learner_id: learnerId,
        message: instructionMsg.trim()
      });

      setInstructionSuccess("Instruction sent successfully! The learner will receive this in their notification feed.");
      setInstructionMsg('');
    } catch (err) {
      console.error("Failed to send instruction:", err);
      setInstructionError(err.response?.data?.message || "Failed to send instruction.");
    } finally {
      setSendingInstruction(false);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      const res = await api.get(`/reports/learners/${learnerId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ASL_Sensei_Learner_${learnerId}_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download learner PDF report", err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 text-indigo-400 font-black text-lg flex items-center justify-center border border-indigo-500/30">
              {data?.user?.full_name?.charAt(0) || 'L'}
            </div>
            <div>
              <h2 className="text-lg font-black text-white">
                {data ? `${data.user.full_name}'s Detailed Progress` : 'Loading Learner Analytics...'}
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                {data?.user?.email} • ID #{learnerId}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {data && (
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-bold border border-slate-700 flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                {downloadingPdf ? 'Generating PDF...' : 'Export PDF'}
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800/80 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
          {loading ? (
            <div className="py-20 text-center text-indigo-400 font-bold text-sm">
              Loading authentic learner telemetry...
            </div>
          ) : !data ? (
            <div className="py-20 text-center text-rose-400 font-bold text-sm">
              Failed to load learner telemetry.
            </div>
          ) : (
            <>
              {/* Lifetime KPIs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Overall Score</span>
                  <div className="text-2xl font-black text-white mt-1">
                    {data.performance?.overall_score !== null ? `${data.performance.overall_score.toFixed(1)}%` : 'No data'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Overall Accuracy</span>
                  <div className="text-2xl font-black text-indigo-400 mt-1">
                    {data.performance?.overall_accuracy !== null ? `${data.performance.overall_accuracy.toFixed(1)}%` : 'No data'}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Total Attempts</span>
                  <div className="text-2xl font-black text-sky-400 mt-1">
                    {data.performance?.total_attempts || 0}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Practice Streak</span>
                  <div className="text-2xl font-black text-amber-400 mt-1">
                    {data.performance?.practice_streak_days || 0} days
                  </div>
                </div>
              </div>

              {/* 29-Sign Alphabet Mastery Matrix Breakdown */}
              <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-emerald-400" /> 29-Sign Alphabet Mastery Matrix
                </h3>
                <MasteryMatrix signClassification={data.sign_classification} />
              </div>

              {/* Private Instruction / Feedback Box */}
              <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Send className="w-4 h-4 text-indigo-400" /> Send Private Instructor Guidance
                </h3>
                <p className="text-xs text-slate-400">
                  This message will only be visible to {data.user.full_name} and will trigger their notification badge.
                </p>

                {instructionSuccess && (
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                    {instructionSuccess}
                  </div>
                )}
                {instructionError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                    {instructionError}
                  </div>
                )}

                <form onSubmit={handleSendInstruction} className="space-y-3">
                  <textarea
                    rows={3}
                    value={instructionMsg}
                    onChange={(e) => setInstructionMsg(e.target.value)}
                    placeholder={`Write a targeted instruction for ${data.user.full_name} (e.g., Practice sign D and I for 10 minutes today)...`}
                    className="w-full p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={sendingInstruction || !instructionMsg.trim()}
                      className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/20 disabled:opacity-50 flex items-center gap-2 cursor-pointer transition-all"
                    >
                      <Send className="w-3.5 h-3.5" />
                      {sendingInstruction ? 'Sending...' : 'Send Private Instruction'}
                    </button>
                  </div>
                </form>
              </div>

              {/* Recent Attempts Feed */}
              <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-sky-400" /> Recent Gesture Practice Attempts
                </h3>
                {data.recent_attempts?.length === 0 ? (
                  <p className="text-xs text-slate-400">No practice attempts recorded for this learner yet.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="text-slate-400 font-semibold border-b border-slate-800">
                        <tr>
                          <th className="pb-2">Target</th>
                          <th className="pb-2">Detected</th>
                          <th className="pb-2">Accuracy</th>
                          <th className="pb-2">Confidence</th>
                          <th className="pb-2">Result</th>
                          <th className="pb-2">Feedback</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-900 text-slate-300">
                        {data.recent_attempts?.slice(0, 8).map((a, idx) => (
                          <tr key={a.id || idx}>
                            <td className="py-2 font-bold text-white">{a.expected_sign}</td>
                            <td className="py-2 font-bold text-sky-400">{a.predicted_sign}</td>
                            <td className="py-2">{a.accuracy !== undefined ? `${a.accuracy}%` : '—'}</td>
                            <td className="py-2">{a.confidence !== undefined ? `${a.confidence}%` : '—'}</td>
                            <td className="py-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                a.is_correct ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                              }`}>
                                {a.is_correct ? 'CORRECT' : 'INCORRECT'}
                              </span>
                            </td>
                            <td className="py-2 text-slate-400 max-w-xs truncate">{a.feedback}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
