import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { ShieldCheck, Server, Users, UserCheck, GraduationCap, Eye, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { AdminUserActivityModal } from './AdminUserActivityModal';

export const AdminDashboard = () => {
  const [counts, setCounts] = useState({ learner_count: 0, trainer_count: 0, instructor_count: 0 });
  const [selectedRole, setSelectedRole] = useState('Learner');
  const [usersList, setUsersList] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 15;

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    setPage(1);
    fetchUsers(selectedRole, searchTerm, 1);
  }, [selectedRole]);

  // Debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      setPage(1);
      fetchUsers(selectedRole, searchTerm, 1);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/counts');
      setCounts(res.data);
    } catch (err) {
      console.error("Failed to fetch admin counts", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async (role, search, pageNum) => {
    try {
      setTableLoading(true);
      const params = new URLSearchParams();
      params.append('role', role);
      if (search && search.trim()) params.append('search', search.trim());
      params.append('page', pageNum);
      params.append('limit', limit);

      const res = await api.get(`/admin/users-by-role?${params.toString()}`);
      if (res.data && res.data.items) {
        setUsersList(res.data.items);
        setTotalPages(res.data.total_pages || 1);
        setTotalCount(res.data.total || 0);
      } else if (Array.isArray(res.data)) {
        setUsersList(res.data);
        setTotalPages(1);
        setTotalCount(res.data.length);
      }
    } catch (err) {
      console.error(`Failed to fetch users for role ${role}`, err);
    } finally {
      setTableLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
      fetchUsers(selectedRole, searchTerm, newPage);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-rose-400 font-bold">
        Loading System Administrator Portal...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl">
        <h1 className="text-2xl font-black text-white flex items-center gap-3">
          <ShieldCheck className="w-7 h-7 text-rose-400" />
          System Administration & Governance
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Monitor system health, review real-time role distributions, and inspect individual learner, trainer, or instructor telemetry.
        </p>
      </div>

      {/* THREE REQUIRED ROLE SUMMARY CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* 1. Learner Summary Card */}
        <div className={`glass-panel p-6 rounded-2xl border transition-all ${
          selectedRole === 'Learner' ? 'border-sky-500 shadow-lg shadow-sky-500/10' : 'border-slate-800'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">Learners</span>
            <Users className="w-5 h-5 text-sky-400" />
          </div>
          <div className="text-4xl font-black text-white mt-3">{counts.learner_count}</div>
          <p className="text-xs text-slate-400 mt-1">Active registered learners</p>
          <button
            onClick={() => { setSelectedRole('Learner'); setSearchTerm(''); }}
            className={`mt-4 w-full py-2 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-2 ${
              selectedRole === 'Learner'
                ? 'bg-sky-500 text-slate-950 shadow-md shadow-sky-500/20'
                : 'bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700'
            }`}
          >
            View Learners
          </button>
        </div>

        {/* 2. Trainer Summary Card */}
        <div className={`glass-panel p-6 rounded-2xl border transition-all ${
          selectedRole === 'Accessibility Trainer' ? 'border-purple-500 shadow-lg shadow-purple-500/10' : 'border-slate-800'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Trainers</span>
            <UserCheck className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-4xl font-black text-white mt-3">{counts.trainer_count}</div>
          <p className="text-xs text-slate-400 mt-1">Accessibility specialists</p>
          <button
            onClick={() => { setSelectedRole('Accessibility Trainer'); setSearchTerm(''); }}
            className={`mt-4 w-full py-2 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-2 ${
              selectedRole === 'Accessibility Trainer'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20'
                : 'bg-slate-800 hover:bg-slate-700 text-purple-400 border border-slate-700'
            }`}
          >
            View Trainers
          </button>
        </div>

        {/* 3. Instructor Summary Card */}
        <div className={`glass-panel p-6 rounded-2xl border transition-all ${
          selectedRole === 'Instructor' ? 'border-indigo-500 shadow-lg shadow-indigo-500/10' : 'border-slate-800'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Instructors</span>
            <GraduationCap className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-4xl font-black text-white mt-3">{counts.instructor_count}</div>
          <p className="text-xs text-slate-400 mt-1">Teaching faculty members</p>
          <button
            onClick={() => { setSelectedRole('Instructor'); setSearchTerm(''); }}
            className={`mt-4 w-full py-2 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-2 ${
              selectedRole === 'Instructor'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                : 'bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-slate-700'
            }`}
          >
            View Instructors
          </button>
        </div>
      </div>

      {/* Filtered User Table & Search */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Filter className="w-4 h-4 text-rose-400" />
              Registered {selectedRole === 'Accessibility Trainer' ? 'Trainer' : selectedRole}s ({totalCount})
            </h2>
            <p className="text-xs text-slate-400">
              Only authentic database records with role '{selectedRole}' are shown below.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={`Search by name or email...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-rose-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="p-3">Name</th>
                <th className="p-3">Email / ID</th>
                {selectedRole === 'Learner' && <th className="p-3">Level</th>}
                {selectedRole === 'Learner' && <th className="p-3">Attempts</th>}
                {selectedRole === 'Instructor' && <th className="p-3">Instructions Sent</th>}
                <th className="p-3">Joined</th>
                <th className="p-3">Last Activity</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {tableLoading ? (
                <tr>
                  <td colSpan="10" className="p-8 text-center text-rose-400 font-bold">
                    Querying {selectedRole} records...
                  </td>
                </tr>
              ) : usersList.length === 0 ? (
                <tr>
                  <td colSpan="10" className="p-8 text-center text-slate-400">
                    No {selectedRole.toLowerCase()}s found.
                  </td>
                </tr>
              ) : (
                usersList.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3 font-bold text-white flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-rose-500/20 text-rose-300 text-[10px] font-bold flex items-center justify-center border border-rose-500/30">
                        {u.full_name?.charAt(0) || 'U'}
                      </div>
                      {u.full_name}
                    </td>
                    <td className="p-3 font-mono text-slate-400">
                      {u.email} <span className="text-slate-600">#{u.id}</span>
                    </td>
                    {selectedRole === 'Learner' && (
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-sky-400 font-semibold border border-slate-700">
                          {u.learning_level}
                        </span>
                      </td>
                    )}
                    {selectedRole === 'Learner' && (
                      <td className="p-3 font-mono text-slate-300">{u.total_attempts}</td>
                    )}
                    {selectedRole === 'Instructor' && (
                      <td className="p-3 font-mono text-slate-300">{u.instructions_sent}</td>
                    )}
                    <td className="p-3 text-slate-400">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="p-3 text-slate-400">
                      {u.last_activity ? new Date(u.last_activity).toLocaleDateString() : 'None'}
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                        u.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                      }`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedUserId(u.id)}
                        className="px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white font-bold text-xs flex items-center gap-1.5 ml-auto border border-rose-500/30 transition-all cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" /> TRACK
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs text-slate-400">
            <div>
              Showing Page {page} of {totalPages} ({totalCount} total)
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-white transition-all cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-3 py-1 bg-slate-900 rounded-lg text-white font-mono font-bold">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-white transition-all cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Dedicated Activity Drilldown / Track Modal */}
      {selectedUserId && (
        <AdminUserActivityModal
          userId={selectedUserId}
          onClose={() => setSelectedUserId(null)}
        />
      )}
    </div>
  );
};
