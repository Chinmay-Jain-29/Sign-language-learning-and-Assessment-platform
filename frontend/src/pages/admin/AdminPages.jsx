import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { Shield, Server, Activity, Users, Lock, FileText, Bell, Database, Cpu, HardDrive } from 'lucide-react';
export { AdminDashboard } from './Dashboard';

export const UserManagement = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Users className="w-6 h-6 text-purple-400" /> User Account Management & Activation
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Manage user accounts, password reset requests, and account status.</p>
    </div>
  </div>
);

export const RoleManagement = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Lock className="w-6 h-6 text-purple-400" /> Role-Based Access Control (RBAC) Management
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Assign role permissions across Learner, Instructor, Accessibility Trainer, and Administrator.</p>
    </div>
  </div>
);

export const AdminCourseManagement = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold">System-Wide Course & Curriculum Registry</h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Manage platform courses, modules, and lessons.</p>
    </div>
  </div>
);

export const ContentManagement = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Database className="w-6 h-6 text-purple-400" /> Content & Dataset Asset Management
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Manage landmark CSV files, image datasets, and canonical sign references.</p>
    </div>
  </div>
);

export const PlatformAnalytics = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Activity className="w-6 h-6 text-purple-400" /> Platform Usage & Traffic Analytics
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">System throughput, daily active users, and API traffic metrics.</p>
    </div>
  </div>
);

export const SystemMonitoring = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Server className="w-6 h-6 text-purple-400" /> System Latency & Infrastructure Monitoring
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Server health, CPU load, memory utilization, and PostgreSQL pool status.</p>
    </div>
  </div>
);

export const ModelAIMonitoring = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Cpu className="w-6 h-6 text-purple-400" /> ML Classifier Model & Drift Monitoring
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Track model accuracy drift, classification confidence distributions, and retraining triggers.</p>
    </div>
  </div>
);

export const AdminNotifications = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <Bell className="w-6 h-6 text-purple-400" /> System Broadcast & Alert Manager
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Send platform-wide notifications and maintenance alerts to users.</p>
    </div>
  </div>
);

export const AuditLogs = () => (
  <div className="max-w-6xl mx-auto px-6 py-8 text-slate-100 space-y-6">
    <h1 className="text-2xl font-extrabold flex items-center gap-2">
      <FileText className="w-6 h-6 text-purple-400" /> Security & API Audit Trail Logs
    </h1>
    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
      <p className="text-xs text-slate-400">Detailed security audit log tracking user logins, role modifications, and admin actions.</p>
    </div>
  </div>
);
