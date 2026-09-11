import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowRight, CheckCircle2 } from 'lucide-react';
import api from '../../api/client';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { ErrorMessage } from '../../components/common/ErrorMessage';

export const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const res = await api.post('/auth/forgot-password', { email });
      setMessage(res.data.message || 'Password reset request received.');
      if (res.data.data?.reset_token) {
        setResetToken(res.data.data.reset_token);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to request password reset.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 relative overflow-hidden">
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-black text-white">Reset Password</h1>
          <p className="text-slate-400 text-xs">Enter your email address to generate a secure reset token</p>
        </div>

        {error && <ErrorMessage message={error} />}

        {message ? (
          <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-center space-y-4">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <p className="text-sm font-semibold text-emerald-300">{message}</p>
            {resetToken && (
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-left space-y-1">
                <span className="text-[10px] font-bold uppercase text-slate-400">Generated Demo Token:</span>
                <p className="text-xs font-mono text-sky-400 break-all">{resetToken}</p>
                <Link
                  to={`/reset-password?token=${resetToken}`}
                  className="inline-block text-xs font-bold text-sky-400 hover:underline pt-2"
                >
                  Proceed to Reset Password &rarr;
                </Link>
              </div>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              icon={Mail}
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="learner@example.com"
            />

            <Button type="submit" isLoading={loading} className="w-full">
              Send Reset Token
            </Button>
          </form>
        )}

        <p className="text-center text-xs text-slate-400 pt-2">
          Remember your password?{' '}
          <Link to="/login" className="text-sky-400 font-semibold hover:underline">
            Back to Login
          </Link>
        </p>
      </div>
    </div>
  );
};
