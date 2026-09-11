import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Hand, Lock, Mail, User, Shield, Globe, Award, ArrowRight, AlertCircle, CheckCircle2, Eye, EyeOff } from 'lucide-react';

export const Login = () => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState(location.state?.tab === 'register' ? 'register' : 'login'); // 'login' | 'register'
  
  useEffect(() => {
    if (location.state?.tab === 'register') {
      setActiveTab('register');
    }
  }, [location.state]);
  
  // Login Form State
  const [loginId, setLoginId] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginRole, setLoginRole] = useState('Learner');
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  // Register Form State
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regRole, setRegRole] = useState('Learner');
  const [regLanguage, setRegLanguage] = useState('English');
  const [regLevel, setRegLevel] = useState('Beginner');
  const [showRegPassword, setShowRegPassword] = useState(false);

  // Feedback State
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const { login, register, loading } = useAuth();
  const navigate = useNavigate();

  // Valid Roles from existing system RBAC
  const validRoles = [
    { value: 'Learner', label: 'Learner' },
    { value: 'Instructor', label: 'Instructor' },
    { value: 'Accessibility Trainer', label: 'Accessibility Trainer' },
    { value: 'Administrator', label: 'Administrator' },
  ];

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!loginId.trim()) {
      setError('Please enter your ID.');
      return;
    }
    if (!loginPassword) {
      setError('Please enter your password.');
      return;
    }
    if (!loginRole) {
      setError('Please select a role.');
      return;
    }

    const res = await login(loginId, loginPassword, loginRole);
    if (res.success) {
      const userRole = res.user.role;
      if (userRole === 'Instructor') navigate('/instructor');
      else if (userRole === 'Accessibility Trainer') navigate('/trainer');
      else if (userRole === 'Administrator') navigate('/admin');
      else navigate('/dashboard');
    } else {
      setError(res.error);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!regFullName.trim()) {
      setError('Please enter your full name.');
      return;
    }
    if (!regEmail.trim()) {
      setError('Please enter your email / ID.');
      return;
    }
    if (!regPassword) {
      setError('Please enter a password.');
      return;
    }
    if (regPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (regPassword !== regConfirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    const res = await register(regEmail, regFullName, regPassword, regRole, regLanguage, regLevel);
    if (res.success) {
      setSuccessMessage('Account created successfully. Please sign in with your credentials.');
      setLoginId(regEmail);
      setLoginPassword('');
      setLoginRole(regRole);
      setActiveTab('login');
      // Clear registration form
      setRegFullName('');
      setRegEmail('');
      setRegPassword('');
      setRegConfirmPassword('');
    } else {
      setError(res.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-slate-950 relative overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md glass-panel p-6 sm:p-8 rounded-2xl relative z-10 border border-slate-800 shadow-2xl">
        
        {/* Logo & Header */}
        <div className="flex flex-col items-center mb-6 text-center">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-xl shadow-sky-500/20 mb-3">
            <Hand className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-black text-white">
            {activeTab === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            {activeTab === 'login' ? 'Sign in to continue learning' : 'Join the AI Sign Language Platform'}
          </p>
        </div>

        {/* Two Options Segmented Tab Control */}
        <div className="grid grid-cols-2 p-1 bg-slate-900/90 rounded-xl border border-slate-800 mb-6">
          <button
            type="button"
            onClick={() => { setActiveTab('login'); setError(''); setSuccessMessage(''); }}
            className={`py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
              activeTab === 'login'
                ? 'bg-sky-500 text-slate-950 shadow-md shadow-sky-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('register'); setError(''); setSuccessMessage(''); }}
            className={`py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
              activeTab === 'register'
                ? 'bg-sky-500 text-slate-950 shadow-md shadow-sky-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {/* Success Alert */}
        {successMessage && (
          <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs sm:text-sm flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs sm:text-sm flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* 1. LOGIN FORM */}
        {activeTab === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            
            {/* Field 1: ID / Email */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                ID / Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <input
                  type="text"
                  required
                  value={loginId}
                  onChange={(e) => setLoginId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-4 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                  placeholder="name@example.com"
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Field 2: Password */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Password
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <input
                  type={showLoginPassword ? 'text' : 'password'}
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-10 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 focus:outline-none"
                  aria-label={showLoginPassword ? 'Hide password' : 'Show password'}
                >
                  {showLoginPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Field 3: Role Dropdown */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Role
              </label>
              <div className="relative">
                <Shield className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <select
                  value={loginRole}
                  onChange={(e) => setLoginRole(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all appearance-none cursor-pointer"
                >
                  {validRoles.map((r) => (
                    <option key={r.value} value={r.value} className="bg-slate-900 text-white">
                      {r.label}
                    </option>
                  ))}
                </select>
                <div className="absolute right-3.5 top-3.5 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-slate-400" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 py-3 rounded-xl text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 disabled:opacity-50 transition-all mt-6 cursor-pointer"
            >
              {loading ? 'Logging in...' : 'Login'}
              <ArrowRight className="w-4 h-4" />
            </button>

            <p className="mt-6 text-center text-xs text-slate-400">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => { setActiveTab('register'); setError(''); setSuccessMessage(''); }}
                className="text-sky-400 hover:underline font-bold ml-1 focus:outline-none"
              >
                Register
              </button>
            </p>
          </form>
        )}

        {/* 2. REGISTER FORM */}
        {activeTab === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
            
            {/* Full Name */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <input
                  type="text"
                  required
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                  placeholder="Jane Doe"
                />
              </div>
            </div>

            {/* Email / ID */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Email Address (ID)
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                  placeholder="jane@example.com"
                />
              </div>
            </div>

            {/* Password & Confirm Password in 2 Columns */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500 pointer-events-none" />
                  <input
                    type={showRegPassword ? 'text' : 'password'}
                    required
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-9 pr-8 py-2.5 text-white text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowRegPassword(!showRegPassword)}
                    className="absolute right-2.5 top-2.5 text-slate-500 hover:text-slate-300 focus:outline-none"
                    aria-label={showRegPassword ? 'Hide password' : 'Show password'}
                  >
                    {showRegPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500 pointer-events-none" />
                  <input
                    type={showRegPassword ? 'text' : 'password'}
                    required
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-9 pr-4 py-2.5 text-white text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
                    placeholder="••••••••"
                  />
                </div>
              </div>
            </div>

            {/* Language & Level */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Language
                </label>
                <div className="relative">
                  <Globe className="w-4 h-4 absolute left-3 top-3 text-slate-500 pointer-events-none" />
                  <select
                    value={regLanguage}
                    onChange={(e) => setRegLanguage(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-9 pr-3 py-2.5 text-white text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all appearance-none cursor-pointer"
                  >
                    <option value="English">English</option>
                    <option value="Spanish">Spanish</option>
                    <option value="French">French</option>
                    <option value="German">German</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Learning Level
                </label>
                <div className="relative">
                  <Award className="w-4 h-4 absolute left-3 top-3 text-slate-500 pointer-events-none" />
                  <select
                    value={regLevel}
                    onChange={(e) => setRegLevel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-9 pr-3 py-2.5 text-white text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all appearance-none cursor-pointer"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Expert">Expert</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Role */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Account Role
              </label>
              <div className="relative">
                <Shield className="w-4 h-4 absolute left-3.5 top-3 text-slate-500 pointer-events-none" />
                <select
                  value={regRole}
                  onChange={(e) => setRegRole(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-sky-500 rounded-xl pl-10 pr-4 py-2.5 text-white text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all appearance-none cursor-pointer"
                >
                  <option value="Learner">Learner (Standard Public Account)</option>
                  <option value="Instructor">Instructor</option>
                  <option value="Accessibility Trainer">Accessibility Trainer</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 py-3 rounded-xl text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 disabled:opacity-50 transition-all mt-5 cursor-pointer"
            >
              {loading ? 'Creating Account...' : 'Register'}
              <ArrowRight className="w-4 h-4" />
            </button>

            <p className="mt-5 text-center text-xs text-slate-400">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => { setActiveTab('login'); setError(''); setSuccessMessage(''); }}
                className="text-sky-400 hover:underline font-bold ml-1 focus:outline-none"
              >
                Login
              </button>
            </p>
          </form>
        )}

      </div>
    </div>
  );
};
