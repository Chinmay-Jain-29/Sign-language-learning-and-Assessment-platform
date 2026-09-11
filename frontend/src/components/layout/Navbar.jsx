import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Hand, LayoutDashboard, Video, BookOpen, Award, FileText, 
  LogOut, UserCheck, ShieldCheck, Bell, CheckCircle2, MessageSquare, Trophy
} from 'lucide-react';
import api from '../../api/client';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [unreadCount, setUnreadCount] = useState(0);
  const [instructions, setInstructions] = useState([]);
  const [systemNotifications, setSystemNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef(null);
  const isFetchingRef = useRef(false);

  useEffect(() => {
    // Immediately clear state on user or role change to eliminate cross-session leakage
    setInstructions([]);
    setSystemNotifications([]);
    setUnreadCount(0);
    setShowNotifications(false);

    if (user?.id) {
      fetchNotifications();
      // Poll notifications every 60 seconds
      const interval = setInterval(fetchNotifications, 60000);
      return () => clearInterval(interval);
    }
  }, [user?.id, user?.role]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    if (isFetchingRef.current || !user?.id) return;
    isFetchingRef.current = true;
    try {
      if (user?.role === 'Learner') {
        const res = await api.get('/instructions/me');
        const list = res.data || [];
        setInstructions(list);
        setSystemNotifications([]);
        const unread = list.filter(i => !i.is_read).length;
        setUnreadCount(unread);
      } else {
        setInstructions([]);
        const res = await api.get('/notifications/');
        const list = (res.data || []).filter(n => n.type !== 'instruction');
        setSystemNotifications(list);
        const unread = list.filter(n => !n.is_read).length;
        setUnreadCount(unread);
      }
    } catch (err) {
      // Quiet fail if not logged in
    } finally {
      isFetchingRef.current = false;
    }
  };

  const markInstructionRead = async (id) => {
    try {
      await api.patch(`/instructions/${id}/read`);
      setInstructions(prev => prev.map(i => i.id === id ? { ...i, is_read: true } : i));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Failed to mark instruction as read", err);
    }
  };

  const markSystemNotificationRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setSystemNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Failed to mark notification as read", err);
    }
  };

  if (!user) return null;

  const isActive = (path) => {
    if (path === '/dashboard') return location.pathname === '/dashboard';
    if (path === '/webcam-practice' || path === '/practice') return location.pathname.startsWith('/practice') || location.pathname === '/webcam-practice';
    if (path === '/lessons') return location.pathname === '/lessons' || location.pathname.startsWith('/courses') || location.pathname.startsWith('/lessons');
    if (path === '/quizzes') return location.pathname === '/quizzes' || location.pathname === '/assessments';
    if (path === '/certificate') return location.pathname === '/certificate' || location.pathname === '/certification';
    return location.pathname === path;
  };

  const handleLogout = async () => {
    setInstructions([]);
    setSystemNotifications([]);
    setUnreadCount(0);
    await logout();
    navigate('/');
  };

  return (
    <nav className="glass-panel sticky top-0 z-50 px-6 py-3 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="p-2 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/20">
            <Hand className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <span className="text-xl font-black bg-gradient-to-r from-sky-400 to-indigo-300 bg-clip-text text-transparent tracking-tight">
              SignVerse
            </span>
            <span className="text-[10px] block font-mono text-slate-400 -mt-1 tracking-widest uppercase">
              AI ASL Learning
            </span>
          </div>
        </Link>

        {/* Dynamic Role Navigation Links */}
        <div className="hidden md:flex items-center gap-1">
          
          {/* Learner Links */}
          {user.role === 'Learner' && (
            <>
              <Link
                to="/dashboard"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/dashboard') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>

              <Link
                to="/practice"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/practice') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Video className="w-4 h-4" />
                Practice
              </Link>

              <Link
                to="/lessons"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/lessons') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                Lessons
              </Link>

              <Link
                to="/quizzes"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/quizzes') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Award className="w-4 h-4" />
                Quizzes
              </Link>

              <Link
                to="/achievements"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/achievements') ? 'bg-amber-500 text-slate-950 font-black shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Trophy className="w-4 h-4 text-amber-400" />
                Achievements
              </Link>

              <Link
                to="/reports"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive('/reports') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <FileText className="w-4 h-4" />
                Reports
              </Link>
            </>
          )}

          {/* Instructor Links */}
          {user.role === 'Instructor' && (
            <Link
              to="/instructor"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                isActive('/instructor') ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              Instructor Portal
            </Link>
          )}

          {/* Trainer Links */}
          {user.role === 'Accessibility Trainer' && (
            <Link
              to="/trainer"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                isActive('/trainer') ? 'bg-sky-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Hand className="w-4 h-4" />
              Trainer Portal
            </Link>
          )}

          {/* Administrator Links */}
          {user.role === 'Administrator' && (
            <Link
              to="/admin"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                isActive('/admin') ? 'bg-rose-600 text-white shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              Admin Portal
            </Link>
          )}
        </div>

        {/* User Profile & Actions */}
        <div className="flex items-center gap-3">
          
          {/* Notification Bell Badge Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer"
              title={user.role === 'Learner' ? "Instructor Guidance" : "System Notifications"}
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white font-black text-[9px] flex items-center justify-center animate-pulse">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Floating Notification Panel */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-4 space-y-3 z-50">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                    {user.role === 'Learner'
                      ? `Instructor Guidance (${unreadCount} New)`
                      : `System Notifications (${unreadCount} New)`}
                  </span>
                  {user.role === 'Learner' && (
                    <Link
                      to="/notifications"
                      onClick={() => setShowNotifications(false)}
                      className="text-[10px] text-sky-400 hover:underline font-bold"
                    >
                      View All
                    </Link>
                  )}
                </div>

                <div className="max-h-72 overflow-y-auto space-y-2 text-xs">
                  {user.role === 'Learner' ? (
                    instructions.length === 0 ? (
                      <div className="py-6 text-center text-slate-500">
                        No instructor guidance at this time.
                      </div>
                    ) : (
                      instructions.slice(0, 5).map((inst) => (
                        <div
                          key={inst.id}
                          className={`p-3 rounded-xl border transition-all ${
                            inst.is_read
                              ? 'bg-slate-950/40 border-slate-800 text-slate-400'
                              : 'bg-indigo-950/30 border-indigo-500/40 text-slate-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-indigo-300">
                              {inst.instructor_name}
                            </span>
                            <span className="text-[9px] text-slate-500">
                              {new Date(inst.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          <p className="mt-1 text-slate-200">{inst.message}</p>
                          {!inst.is_read && (
                            <button
                              onClick={() => markInstructionRead(inst.id)}
                              className="mt-2 text-[10px] text-indigo-400 hover:text-indigo-300 font-bold underline cursor-pointer"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      ))
                    )
                  ) : (
                    systemNotifications.length === 0 ? (
                      <div className="py-6 text-center text-slate-500">
                        No system notifications at this time.
                      </div>
                    ) : (
                      systemNotifications.slice(0, 5).map((n) => (
                        <div
                          key={n.id}
                          className={`p-3 rounded-xl border transition-all ${
                            n.is_read
                              ? 'bg-slate-950/40 border-slate-800 text-slate-400'
                              : 'bg-indigo-950/30 border-indigo-500/40 text-slate-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-200">{n.title}</span>
                            <span className="text-[9px] text-slate-500">
                              {n.created_at ? new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                            </span>
                          </div>
                          <p className="mt-1 text-slate-300 text-xs">{n.message}</p>
                          {!n.is_read && (
                            <button
                              onClick={() => markSystemNotificationRead(n.id)}
                              className="mt-2 text-[10px] text-indigo-400 hover:text-indigo-300 font-bold underline cursor-pointer"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      ))
                    )
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User Profile Avatar Link */}
          <Link
            to="/profile"
            className="flex items-center gap-2.5 p-1.5 pr-2.5 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/40 transition-all group"
            title="View Personal Profile"
          >
            <div className="w-8 h-8 rounded-xl overflow-hidden bg-gradient-to-br from-indigo-600 to-purple-800 flex items-center justify-center text-white font-black text-xs shadow-md border border-slate-700 flex-shrink-0">
              {user.profile_photo_url ? (
                <img
                  src={user.profile_photo_url}
                  alt={user.full_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span>
                  {user.full_name
                    ? user.full_name.trim().split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
                    : 'U'}
                </span>
              )}
            </div>

            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                {user.full_name}
              </span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-sky-400 font-bold inline-block w-fit border border-sky-500/20">
                {user.role}
              </span>
            </div>
          </Link>

          <button
            onClick={handleLogout}
            className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 transition-all cursor-pointer"
            title="Logout and return to Landing Page"
            aria-label="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>

      </div>
    </nav>
  );
};
