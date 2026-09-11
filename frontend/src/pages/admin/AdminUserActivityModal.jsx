import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { X, ShieldCheck, User, Award, Activity, Download, Mail, Calendar, MessageSquare, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { MasteryMatrix } from '../../components/common/MasteryMatrix';

export const AdminUserActivityModal = ({ userId, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  
  // Admin Instruction state
  const [instructionText, setInstructionText] = useState('');
  const [sendingInstruction, setSendingInstruction] = useState(false);
  const [instructionStatus, setInstructionStatus] = useState(null);

  // Admin Learning Level management state
  const [selectedLevel, setSelectedLevel] = useState('');
  const [isEditingLevel, setIsEditingLevel] = useState(false);
  const [savingLevel, setSavingLevel] = useState(false);
  const [levelStatus, setLevelStatus] = useState(null);

  useEffect(() => {
    if (userId) {
      fetchUserActivity();
      setInstructionText('');
      setInstructionStatus(null);
      setIsEditingLevel(false);
      setLevelStatus(null);
    }
  }, [userId]);

  const fetchUserActivity = async () => {
    try {
      setLoading(true);
      setData(null);
      const res = await api.get(`/admin/users/${userId}/activity`);
      setData(res.data);
      if (res.data?.user?.learning_level) {
        setSelectedLevel(res.data.user.learning_level);
      }
    } catch (err) {
      console.error("Failed to fetch admin user activity", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveLevel = async (e) => {
    e.preventDefault();
    if (!selectedLevel) return;

    try {
      setSavingLevel(true);
      setLevelStatus(null);
      const res = await api.patch(`/admin/learners/${userId}/level`, {
        learning_level: selectedLevel
      });
      setLevelStatus({
        type: 'success',
        text: res.data.message || `Level successfully updated to ${selectedLevel}!`
      });
      setIsEditingLevel(false);
      // Refresh real telemetry
      await fetchUserActivity();
    } catch (err) {
      console.error("Failed to update learner level", err);
      setLevelStatus({
        type: 'error',
        text: err.response?.data?.message || err.response?.data?.detail || 'Failed to update level.'
      });
    } finally {
      setSavingLevel(false);
    }
  };

  const handleSendInstruction = async (e) => {
    e.preventDefault();
    if (!instructionText.trim()) return;

    try {
      setSendingInstruction(true);
      setInstructionStatus(null);
      await api.post('/admin/instructions', {
        recipient_id: userId,
        message: instructionText.trim()
      });
      setInstructionStatus({
        type: 'success',
        text: `Directive successfully dispatched to ${data?.user?.full_name || 'user'}!`
      });
      setInstructionText('');
    } catch (err) {
      console.error("Failed to send admin instruction", err);
      setInstructionStatus({
        type: 'error',
        text: err.response?.data?.message || 'Failed to dispatch instruction.'
      });
    } finally {
      setSendingInstruction(false);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      const res = await api.get(`/reports/learners/${userId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ASL_Admin_Audit_Learner_${userId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download audit PDF", err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-rose-500/20 text-rose-400 font-black text-lg flex items-center justify-center border border-rose-500/30">
              {data?.user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <h2 className="text-lg font-black text-white">
                {data ? `${data.user.full_name} (${data.user.role})` : 'Loading Account Telemetry...'}
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                {data?.user?.email} • ID #{userId}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {data?.type === 'learner' && (
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-bold border border-slate-700 flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                {downloadingPdf ? 'Generating PDF...' : 'Export Audit PDF'}
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

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
          {loading ? (
            <div className="py-20 text-center text-rose-400 font-bold text-sm">
              Loading authentic activity telemetry...
            </div>
          ) : !data ? (
            <div className="py-20 text-center text-rose-400 font-bold text-sm">
              Failed to load user activity.
            </div>
          ) : (
            <>
              {/* Account Overview */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Account Role</span>
                  <div className="text-lg font-black text-rose-400 mt-1">{data.user.role}</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Account Status</span>
                  <div className="text-lg font-black text-emerald-400 mt-1">
                    {data.user.is_active ? 'Active' : 'Inactive'}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Joined Date</span>
                  <div className="text-sm font-bold text-slate-200 mt-1">
                    {data.user.created_at ? new Date(data.user.created_at).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-bold uppercase text-slate-400">
                    {data.type === 'learner' ? 'Total Attempts' : (data.type === 'instructor' ? 'Instructions Sent' : 'Level')}
                  </span>
                  <div className="text-lg font-black text-white mt-1">
                    {data.type === 'learner' 
                      ? (data.analytics?.performance?.total_attempts ?? 0)
                      : (data.type === 'instructor' ? data.total_instructions_issued : (data.user.learning_level || 'Trainer'))}
                  </div>
                </div>
              </div>

              {/* Specific Content by Role */}
              {data.type === 'learner' && data.analytics && (
                <>
                  {/* LEARNING LEVEL CONTROL SECTION (Admin Only) */}
                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
                      <div>
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <ShieldCheck className="w-4 h-4 text-sky-400" /> LEARNING LEVEL
                        </h3>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          Admin-controlled learner level determining access to Beginner, Intermediate, and Expert practice modes.
                        </p>
                      </div>

                      {!isEditingLevel && (
                        <button
                          onClick={() => {
                            setSelectedLevel(data.user.learning_level || 'Beginner');
                            setIsEditingLevel(true);
                            setLevelStatus(null);
                          }}
                          className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/20 cursor-pointer shrink-0"
                        >
                          Change Level
                        </button>
                      )}
                    </div>

                    {levelStatus && (
                      <div className={`p-3 rounded-xl text-xs font-bold flex items-center gap-2 ${
                        levelStatus.type === 'success'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                      }`}>
                        {levelStatus.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                        <span>{levelStatus.text}</span>
                      </div>
                    )}

                    {isEditingLevel ? (
                      <form onSubmit={handleSaveLevel} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                          <div className="flex-1 space-y-1">
                            <label className="text-xs font-bold text-slate-300">Select New Learning Level</label>
                            <select
                              value={selectedLevel}
                              onChange={(e) => setSelectedLevel(e.target.value)}
                              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-sky-500 transition-all cursor-pointer"
                            >
                              <option value="Beginner">Beginner</option>
                              <option value="Intermediate">Intermediate</option>
                              <option value="Expert">Expert</option>
                            </select>
                          </div>

                          <div className="flex items-center gap-2 sm:self-end pt-1">
                            <button
                              type="button"
                              onClick={() => setIsEditingLevel(false)}
                              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all cursor-pointer"
                            >
                              Cancel
                            </button>
                            <button
                              type="submit"
                              disabled={savingLevel}
                              className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-black transition-all shadow-md shadow-sky-500/20 cursor-pointer disabled:opacity-50"
                            >
                              {savingLevel ? 'Saving...' : 'Save Level'}
                            </button>
                          </div>
                        </div>
                      </form>
                    ) : (
                      <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Current Level</span>
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/30 text-xs font-black mt-1">
                            {data.user.learning_level || 'Beginner'}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">Authorized Modes</span>
                          <span className="text-xs font-bold text-slate-300 mt-1 block">
                            {data.user.learning_level === 'Expert' 
                              ? 'Beginner + Intermediate + Expert (3 / 3)' 
                              : (data.user.learning_level === 'Intermediate' 
                                ? 'Beginner + Intermediate (2 / 3)' 
                                : 'Beginner Only (1 / 3)')}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Level Change Audit Trail */}
                    {data.level_history && data.level_history.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-800/60">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                          Level Change Audit History
                        </span>
                        <div className="space-y-1.5 max-h-32 overflow-y-auto">
                          {data.level_history.map((h, i) => (
                            <div key={h.id || i} className="flex items-center justify-between text-[11px] p-2 rounded-lg bg-slate-900/40 border border-slate-800/60 text-slate-300">
                              <span className="font-bold text-indigo-400">
                                {h.old_level || 'Initial'} → {h.new_level}
                              </span>
                              <span className="text-slate-400">
                                By {h.changed_by} on {new Date(h.changed_at).toLocaleDateString()}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Current Performance Metrics */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Overall Accuracy</span>
                      <div className="text-xl font-black text-indigo-400 mt-1">
                        {data.analytics.performance.overall_accuracy !== null ? `${data.analytics.performance.overall_accuracy}%` : '—'}
                      </div>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Avg Confidence</span>
                      <div className="text-xl font-black text-sky-400 mt-1">
                        {data.analytics.performance.average_confidence !== null ? `${data.analytics.performance.average_confidence}%` : '—'}
                      </div>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Practice Streak</span>
                      <div className="text-xl font-black text-amber-400 mt-1">
                        {data.analytics.performance.practice_streak_days} days
                      </div>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Total Sessions</span>
                      <div className="text-xl font-black text-purple-400 mt-1">
                        {data.analytics.performance.total_sessions}
                      </div>
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <Award className="w-4 h-4 text-emerald-400" /> Canonical 29-Sign Alphabet Mastery Matrix
                    </h3>
                    <MasteryMatrix signClassification={data.analytics.sign_classification} />
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <Activity className="w-4 h-4 text-sky-400" /> Recent Gesture Practice Evaluation Attempts
                    </h3>
                    {data.analytics.recent_attempts?.length === 0 ? (
                      <p className="text-xs text-slate-400">No attempts logged yet.</p>
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
                            {data.analytics.recent_attempts?.slice(0, 8).map((a, idx) => (
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

              {data.type === 'instructor' && (
                <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-indigo-400" /> Instructor Dispatch Telemetry
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Total Instructions Sent</span>
                      <div className="text-2xl font-black text-indigo-400 mt-1">{data.total_instructions_issued}</div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Last Instruction Dispatched</span>
                      <div className="text-xs font-semibold text-slate-200 mt-2">
                        {data.last_instruction_sent_at ? new Date(data.last_instruction_sent_at).toLocaleString() : 'Never'}
                      </div>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-500 italic">
                    Private instructional communications are strictly isolated to the designated learner recipient.
                  </p>
                </div>
              )}

              {data.type === 'trainer' && (
                <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-purple-400" /> Accessibility Specialist Profile & Status
                  </h3>
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Role Status:</span>
                      <span className="text-emerald-400 font-bold">{data.status || 'Active trainer profile'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Account Standing:</span>
                      <span className="text-slate-200 font-bold">{data.user.is_active ? 'In Good Standing' : 'Suspended'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Admin Private Instruction / Comment Box */}
              <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-rose-400" /> Private Administrative Directive / Instruction
                </h3>
                <p className="text-xs text-slate-400">
                  Send a confidential, recipient-specific instruction directly to {data.user.full_name}. Only this user will receive the notification.
                </p>

                {instructionStatus && (
                  <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                    instructionStatus.type === 'success'
                      ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                      : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                  }`}>
                    {instructionStatus.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {instructionStatus.text}
                  </div>
                )}

                <form onSubmit={handleSendInstruction} className="space-y-3">
                  <textarea
                    rows={3}
                    placeholder={`Write a private directive or guidance for ${data.user.full_name}...`}
                    value={instructionText}
                    onChange={(e) => setInstructionText(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-rose-500 transition-all resize-none"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={sendingInstruction || !instructionText.trim()}
                      className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-rose-600/20 cursor-pointer transition-all"
                    >
                      <Send className="w-3.5 h-3.5" />
                      {sendingInstruction ? 'Dispatching Directive...' : 'Send Directive'}
                    </button>
                  </div>
                </form>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
