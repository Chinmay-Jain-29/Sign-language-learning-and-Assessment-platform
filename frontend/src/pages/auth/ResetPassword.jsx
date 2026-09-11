import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Lock, CheckCircle2 } from 'lucide-react';
import api from '../../api/client';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { ErrorMessage } from '../../components/common/ErrorMessage';

export const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [token, setToken] = useState(searchParams.get('token') || '');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.post('/auth/reset-password', {
        reset_token: token,
        new_password: newPassword
      });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.message || 'Password reset failed. Invalid or expired token.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 relative overflow-hidden">
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-black text-white">Set New Password</h1>
          <p className="text-slate-400 text-xs">Enter your reset token and new password</p>
        </div>

        {error && <ErrorMessage message={error} />}

        {success ? (
          <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-center space-y-4">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
            <h2 className="text-base font-bold text-white">Password Updated!</h2>
            <p className="text-xs text-slate-300">Your password has been successfully updated. You may now log in with your new password.</p>
            <Button onClick={() => navigate('/login')} className="w-full">
              Proceed to Login
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Reset Token"
              type="text"
              required
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste your reset token"
            />

            <Input
              label="New Password"
              icon={Lock}
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
            />

            <Button type="submit" isLoading={loading} className="w-full">
              Update Password
            </Button>
          </form>
        )}

        <p className="text-center text-xs text-slate-400 pt-2">
          Remembered your password?{' '}
          <Link to="/login" className="text-sky-400 font-semibold hover:underline">
            Back to Login
          </Link>
        </p>
      </div>
    </div>
  );
};
