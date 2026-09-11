import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { 
  Award, Clock, CheckCircle2, XCircle, FileCheck, 
  HelpCircle, ArrowRight, ShieldCheck, Download
} from 'lucide-react';

export const Assessments = () => {
  const [assessments, setAssessments] = useState([]);
  const [activeAssessment, setActiveAssessment] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [certifications, setCertifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [assRes, certRes] = await Promise.all([
        api.get('/assessment/list'),
        api.get('/certification/list')
      ]);
      setAssessments(assRes.data);
      setCertifications(certRes.data);
    } catch (err) {
      console.error("Failed to load assessments", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId, option) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  const handleSubmit = async () => {
    if (!activeAssessment) return;
    setSubmitting(true);

    const answersList = Object.entries(selectedAnswers).map(([qId, opt]) => ({
      question_id: parseInt(qId),
      selected_option: opt
    }));

    try {
      const res = await api.post('/assessment/submit', {
        assessment_id: activeAssessment.id,
        answers: answersList
      });
      setResult(res.data);
      fetchData();
    } catch (err) {
      alert("Failed to submit assessment.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sky-400 font-bold">
        Loading Assessment Modules...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Top Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-3">
            <Award className="w-7 h-7 text-amber-400" />
            ASL Skill Evaluation & Certification
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Test your sign language knowledge through timed evaluation quizzes and earn official digital certificates.
          </p>
        </div>

        {certifications.length > 0 && (
          <div className="bg-amber-500/10 border border-amber-500/30 px-4 py-3 rounded-xl flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-amber-400" />
            <div>
              <span className="text-xs text-amber-400 font-bold uppercase">Earned Credentials</span>
              <p className="text-sm font-bold text-white">{certifications.length} Certificates Issued</p>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {!activeAssessment ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Quiz Catalog */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white">Available Quizzes & Exams</h2>

            {assessments.map((ass) => (
              <div key={ass.id} className="glass-panel p-6 rounded-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-sky-400 font-bold uppercase tracking-wider">{ass.level} Level</span>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Clock className="w-3.5 h-3.5" /> {ass.time_limit_mins} Mins
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white">{ass.title}</h3>
                  <p className="text-xs text-slate-300 mt-1">{ass.description}</p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                  <span className="text-xs text-slate-400">Passing Threshold: {ass.passing_score}%</span>
                  <button
                    onClick={() => {
                      setActiveAssessment(ass);
                      setSelectedAnswers({});
                      setResult(null);
                    }}
                    className="gradient-btn px-4 py-2 rounded-xl text-white text-xs font-semibold flex items-center gap-1.5 shadow"
                  >
                    Start Assessment <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* User Earned Certifications */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white">Your Certificate Records</h2>

            {certifications.length === 0 ? (
              <div className="glass-panel p-8 rounded-2xl text-center text-slate-400 text-xs">
                No certificates earned yet. Pass an assessment with {'>='} 70% to unlock your digital badge.
              </div>
            ) : (
              certifications.map((cert) => (
                <div key={cert.id} className="glass-panel p-6 rounded-2xl border-l-4 border-l-amber-400 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Verified Certificate</span>
                    <span className="text-[10px] text-slate-400">{new Date(cert.issued_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="text-base font-bold text-white">{cert.title}</h4>
                  <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 font-mono text-xs text-sky-400 font-semibold tracking-wider">
                    {cert.certificate_code}
                  </div>
                </div>
              ))
            )}
          </div>

        </div>
      ) : (
        /* Active Quiz Taking Interface */
        <div className="glass-panel p-8 rounded-2xl space-y-8 max-w-3xl mx-auto">
          
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs text-sky-400 font-bold uppercase">{activeAssessment.level} Evaluation</span>
              <h2 className="text-2xl font-black text-white">{activeAssessment.title}</h2>
            </div>
            <button
              onClick={() => setActiveAssessment(null)}
              className="text-xs text-slate-400 hover:text-white bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800"
            >
              Exit Quiz
            </button>
          </div>

          {result ? (
            /* Result Banner */
            <div className="space-y-6 text-center">
              <div className={`p-6 rounded-2xl border ${
                result.passed ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-rose-500/10 border-rose-500/30'
              }`}>
                {result.passed ? (
                  <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-2" />
                ) : (
                  <XCircle className="w-12 h-12 text-rose-400 mx-auto mb-2" />
                )}
                <h3 className="text-2xl font-black text-white">{result.passed ? 'Assessment Passed!' : 'Assessment Failed'}</h3>
                <p className="text-3xl font-black gradient-text my-2">Score: {result.score}%</p>
                {result.certificate_code && (
                  <div className="mt-4 p-3 rounded-xl bg-slate-900 border border-slate-800 inline-block text-xs font-mono text-amber-400 font-bold">
                    Issued Certificate Code: {result.certificate_code}
                  </div>
                )}
              </div>

              <button
                onClick={() => setActiveAssessment(null)}
                className="gradient-btn px-6 py-2.5 rounded-xl text-white font-semibold text-sm"
              >
                Return to Assessment Portal
              </button>
            </div>
          ) : (
            /* Questions List */
            <div className="space-y-6">
              {activeAssessment.questions.map((q, idx) => (
                <div key={q.id} className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">Question #{idx + 1}</span>
                  <p className="text-sm font-semibold text-white">{q.question_text}</p>

                  <div className="grid grid-cols-2 gap-2 pt-2">
                    {q.options_json.map((opt) => (
                      <button
                        key={opt}
                        onClick={() => handleSelectOption(q.id, opt)}
                        className={`p-3 rounded-xl text-xs font-bold text-left border transition-all ${
                          selectedAnswers[q.id] === opt
                            ? 'bg-sky-600 text-white border-sky-400 shadow-md'
                            : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        Option {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="w-full gradient-btn py-3 rounded-xl text-white font-bold text-sm shadow-lg"
              >
                {submitting ? 'Evaluating Quiz Answers...' : 'Submit Answers & Calculate Score'}
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
};
