import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';
import {
  User, Mail, Phone, Globe, BookOpen, Briefcase, Award,
  Building, Shield, Camera, Trash2, Edit3, Check, X,
  AlertCircle, Sparkles, CheckCircle2, RefreshCw, Lock
} from 'lucide-react';

export const Profile = () => {
  const { user, login } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form State
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    full_name: '',
    phone: '',
    bio: '',
    preferred_language: 'English',
    learning_level: 'Beginner',
    title: '',
    specialization: '',
    qualification: '',
    experience_years: '',
    department: '',
    designation: ''
  });

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await api.get('/users/profile');
      const data = res.data;
      setProfile(data);
      setFormData({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        full_name: data.full_name || '',
        phone: data.phone || '',
        bio: data.bio || '',
        preferred_language: data.preferred_language || 'English',
        learning_level: data.learning_level || 'Beginner',
        title: data.title || '',
        specialization: data.specialization || '',
        qualification: data.qualification || '',
        experience_years: data.experience_years !== null && data.experience_years !== undefined ? String(data.experience_years) : '',
        department: data.department || '',
        designation: data.designation || ''
      });
    } catch (err) {
      console.error("Failed to load profile", err);
      setErrorMsg(err.response?.data?.message || 'Failed to load profile details.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const payload = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        full_name: formData.full_name,
        phone: formData.phone,
        bio: formData.bio,
        preferred_language: formData.preferred_language
      };

      if (profile?.role === 'Learner') {
        // Only include learning_level if not yet established (first-time setup)
        if (!profile.learning_level && formData.learning_level) {
          payload.learning_level = formData.learning_level;
        }
      } else if (profile?.role === 'Accessibility Trainer') {
        payload.title = formData.title;
        payload.specialization = formData.specialization;
        payload.qualification = formData.qualification;
        payload.experience_years = formData.experience_years ? parseInt(formData.experience_years, 10) : null;
      } else if (profile?.role === 'Instructor') {
        payload.title = formData.title;
        payload.department = formData.department;
        payload.specialization = formData.specialization;
        payload.qualification = formData.qualification;
        payload.experience_years = formData.experience_years ? parseInt(formData.experience_years, 10) : null;
      } else if (profile?.role === 'Administrator') {
        payload.department = formData.department;
        payload.designation = formData.designation;
      }

      const res = await api.put('/users/profile', payload);
      setProfile(res.data);
      setIsEditing(false);
      setSuccessMsg('Profile updated successfully!');
      
      // Update local storage user full name if changed
      const stored = localStorage.getItem('asl_user');
      if (stored) {
        const parsed = JSON.parse(stored);
        parsed.full_name = res.data.full_name;
        localStorage.setItem('asl_user', JSON.stringify(parsed));
      }
    } catch (err) {
      console.error("Failed to update profile", err);
      setErrorMsg(err.response?.data?.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setErrorMsg('Unsupported image format. Please select a JPG, PNG, or WebP image.');
      return;
    }

    // Validate size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('File size exceeds 5MB limit. Please upload a smaller image.');
      return;
    }

    setUploadingPhoto(true);
    setErrorMsg('');
    setSuccessMsg('');

    const uploadFormData = new FormData();
    uploadFormData.append('file', file);

    try {
      const res = await api.post('/users/profile/photo', uploadFormData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProfile(prev => ({ ...prev, profile_photo_url: res.data.profile_photo_url }));
      setSuccessMsg('Profile photo updated successfully!');

      // Update local storage user photo if stored
      const stored = localStorage.getItem('asl_user');
      if (stored) {
        const parsed = JSON.parse(stored);
        parsed.profile_photo_url = res.data.profile_photo_url;
        localStorage.setItem('asl_user', JSON.stringify(parsed));
      }
    } catch (err) {
      console.error("Photo upload failed", err);
      setErrorMsg(err.response?.data?.message || 'Failed to upload profile photo.');
    } finally {
      setUploadingPhoto(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handlePhotoDelete = async () => {
    if (!window.confirm('Are you sure you want to remove your profile photo?')) return;

    setUploadingPhoto(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await api.delete('/users/profile/photo');
      setProfile(prev => ({ ...prev, profile_photo_url: null }));
      setSuccessMsg('Profile photo removed.');

      const stored = localStorage.getItem('asl_user');
      if (stored) {
        const parsed = JSON.parse(stored);
        parsed.profile_photo_url = null;
        localStorage.setItem('asl_user', JSON.stringify(parsed));
      }
    } catch (err) {
      console.error("Photo delete failed", err);
      setErrorMsg(err.response?.data?.message || 'Failed to remove profile photo.');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8 animate-pulse">
        <div className="glass-card p-8 rounded-3xl border border-slate-800 bg-slate-900/50 flex flex-col md:flex-row items-center gap-6">
          <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-3xl bg-slate-800" />
          <div className="flex-1 space-y-3 w-full">
            <div className="h-8 bg-slate-800 rounded-xl w-48" />
            <div className="h-4 bg-slate-800/60 rounded-lg w-64" />
            <div className="h-3 bg-slate-800/40 rounded-lg w-36" />
          </div>
        </div>
        <div className="glass-card p-8 rounded-3xl border border-slate-800 bg-slate-900/50 space-y-6">
          <div className="h-6 bg-slate-800 rounded-lg w-40" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-14 bg-slate-800/60 rounded-xl" />
            <div className="h-14 bg-slate-800/60 rounded-xl" />
            <div className="h-14 bg-slate-800/60 rounded-xl" />
            <div className="h-14 bg-slate-800/60 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (errorMsg && !profile) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 glass-card rounded-3xl border border-rose-500/30 bg-slate-900/80 shadow-2xl text-center space-y-5 text-slate-100">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
          <AlertCircle className="w-7 h-7" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white">Unable to load your profile.</h2>
          <p className="text-xs text-slate-400">{errorMsg}</p>
        </div>
        <button
          onClick={fetchProfile}
          className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 mx-auto cursor-pointer transition-all shadow-lg shadow-indigo-600/30"
        >
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 glass-card rounded-3xl border border-amber-500/30 bg-slate-900/80 shadow-2xl text-center space-y-5 text-slate-100">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
          <User className="w-7 h-7" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white">Your profile is not set up yet.</h2>
          <p className="text-xs text-slate-400">Initialize your account profile details to get started.</p>
        </div>
        <button
          onClick={() => { setProfile({ full_name: user?.full_name || 'User', email: user?.email || '', role: user?.role || 'Learner' }); setIsEditing(true); }}
          className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 mx-auto cursor-pointer transition-all shadow-lg shadow-indigo-600/30"
        >
          <Edit3 className="w-4 h-4" /> Complete Profile
        </button>
      </div>
    );
  }

  const roleColors = {
    'Learner': 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    'Instructor': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    'Accessibility Trainer': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'Administrator': 'bg-rose-500/10 text-rose-400 border-rose-500/30'
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8 text-slate-100">
      
      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800 bg-slate-900/70 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row items-center gap-6 relative z-10">
          {/* Avatar Section */}
          <div className="relative group">
            <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-3xl overflow-hidden border-2 border-slate-700 bg-slate-950 flex items-center justify-center shadow-xl">
              {profile?.profile_photo_url ? (
                <img
                  src={profile.profile_photo_url}
                  alt={profile.full_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-indigo-600 to-purple-800 flex items-center justify-center text-white font-black text-3xl sm:text-4xl shadow-inner">
                  {getInitials(profile?.full_name)}
                </div>
              )}
            </div>

            {/* Quick photo upload button overlay */}
            <label
              htmlFor="profile-photo-input"
              className="absolute -bottom-2 -right-2 p-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg cursor-pointer border border-indigo-400/40 transition-all hover:scale-105"
              title="Upload new photo"
            >
              <Camera className="w-4 h-4" />
            </label>
            <input
              id="profile-photo-input"
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.webp"
              onChange={handlePhotoSelect}
              className="hidden"
            />
          </div>

          {/* User Bio Header Info */}
          <div className="flex-1 text-center md:text-left space-y-2">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
              <h1 className="text-2xl sm:text-3xl font-black text-white">{profile?.full_name}</h1>
              <span className={`text-xs font-black uppercase tracking-wider px-3 py-1 rounded-xl border ${roleColors[profile?.role] || 'bg-slate-800 text-slate-300'}`}>
                {profile?.role}
              </span>
            </div>

            <p className="text-sm text-slate-400 flex items-center justify-center md:justify-start gap-2">
              <Mail className="w-4 h-4 text-slate-500" /> {profile?.email}
            </p>

            <p className="text-xs text-slate-500">
              Account created on {new Date(profile?.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          {/* Profile Actions & Completeness */}
          <div className="flex flex-col items-center md:items-end gap-3 w-full md:w-auto">
            <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800 w-full sm:w-48 text-center md:text-right">
              <div className="flex items-center justify-between text-xs font-bold text-slate-400 mb-1">
                <span>Completeness</span>
                <span className="text-indigo-400">{profile?.completeness_percentage || 100}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-sky-400 h-full transition-all duration-500"
                  style={{ width: `${profile?.completeness_percentage || 100}%` }}
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer transition-all"
                >
                  <Edit3 className="w-4 h-4" /> Edit Profile
                </button>
              ) : (
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs flex items-center gap-2 cursor-pointer transition-all"
                >
                  <X className="w-4 h-4" /> Cancel
                </button>
              )}

              {profile?.profile_photo_url && (
                <button
                  onClick={handlePhotoDelete}
                  disabled={uploadingPhoto}
                  className="p-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 cursor-pointer transition-all"
                  title="Remove Profile Photo"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Notification Messages */}
      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Profile Form / Details View */}
      <form onSubmit={handleSave} className="space-y-6">
        
        {/* Personal Details Card */}
        <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl space-y-6">
          <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <User className="w-5 h-5 text-indigo-400" /> Personal Information
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* First Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">First Name</label>
              {isEditing ? (
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="e.g. Alex"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                />
              ) : (
                <p className="text-sm font-semibold text-slate-200">{profile?.first_name || 'Not provided'}</p>
              )}
            </div>

            {/* Last Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Last Name</label>
              {isEditing ? (
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="e.g. Learner"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                />
              ) : (
                <p className="text-sm font-semibold text-slate-200">{profile?.last_name || 'Not provided'}</p>
              )}
            </div>

            {/* Display / Full Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Display Name</label>
              {isEditing ? (
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="e.g. Alex Learner"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                />
              ) : (
                <p className="text-sm font-semibold text-slate-200">{profile?.full_name}</p>
              )}
            </div>

            {/* Email (Read-Only) */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email Address</label>
                <span className="text-[10px] text-slate-500">Primary Authentication ID</span>
              </div>
              <input
                type="email"
                value={profile?.email}
                disabled
                className="w-full bg-slate-950/40 border border-slate-800/80 rounded-xl px-4 py-2.5 text-xs text-slate-400 cursor-not-allowed"
              />
            </div>

            {/* Phone */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Phone Number</label>
              {isEditing ? (
                <input
                  type="text"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="e.g. +1 (555) 019-2834"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                />
              ) : (
                <p className="text-sm font-semibold text-slate-200">{profile?.phone || 'Not provided'}</p>
              )}
            </div>

            {/* Preferred Language */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Preferred Language</label>
              {isEditing ? (
                <select
                  name="preferred_language"
                  value={formData.preferred_language}
                  onChange={handleInputChange}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                >
                  <option value="English">English</option>
                  <option value="Spanish">Spanish</option>
                  <option value="French">French</option>
                  <option value="German">German</option>
                  <option value="American Sign Language">American Sign Language</option>
                </select>
              ) : (
                <p className="text-sm font-semibold text-slate-200">{profile?.preferred_language || 'English'}</p>
              )}
            </div>
          </div>

          {/* Bio / About */}
          <div className="space-y-1.5 pt-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">About Me / Bio</label>
            {isEditing ? (
              <textarea
                name="bio"
                rows={3}
                value={formData.bio}
                onChange={handleInputChange}
                placeholder="Write a brief introduction or your learning motivations..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all resize-none"
              />
            ) : (
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
                {profile?.bio || 'No bio provided yet.'}
              </p>
            )}
          </div>
        </div>

        {/* Role-Specific Information Card */}
        <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl space-y-6">
          <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            {profile?.role === 'Learner' && <BookOpen className="w-5 h-5 text-sky-400" />}
            {profile?.role === 'Instructor' && <Award className="w-5 h-5 text-indigo-400" />}
            {profile?.role === 'Accessibility Trainer' && <Briefcase className="w-5 h-5 text-emerald-400" />}
            {profile?.role === 'Administrator' && <Shield className="w-5 h-5 text-rose-400" />}
            {profile?.role} Profile Details
          </h2>

          {/* Learner Fields */}
          {profile?.role === 'Learner' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  Learning Level
                  {profile?.learning_level && <Lock className="w-3.5 h-3.5 text-amber-400" />}
                </label>
                
                {profile?.learning_level ? (
                  <div>
                    <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/30 text-xs font-bold">
                      <Lock className="w-3.5 h-3.5 text-amber-400" />
                      <span>{profile.learning_level}</span>
                      <span className="text-[10px] text-slate-400 font-normal border-l border-slate-700 pl-2">Controlled</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5 leading-relaxed">
                      Learning level can only be changed by an administrator.
                    </p>
                  </div>
                ) : isEditing ? (
                  <div>
                    <select
                      name="learning_level"
                      value={formData.learning_level || 'Beginner'}
                      onChange={handleInputChange}
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-sky-500 transition-all cursor-pointer"
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Expert">Expert</option>
                    </select>
                    <p className="text-[11px] text-sky-400 mt-1.5">
                      Select your initial level. Once saved, future adjustments are managed by an administrator.
                    </p>
                  </div>
                ) : (
                  <div>
                    <span className="inline-block px-3 py-1 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-bold">
                      Learning level not set
                    </span>
                    <p className="text-[11px] text-slate-400 mt-1.5">
                      Click Edit Profile to select your initial learning level.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Trainer Fields */}
          {profile?.role === 'Accessibility Trainer' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Professional Title</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g. Lead Accessibility Coach"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.title || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Specialization</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="specialization"
                    value={formData.specialization}
                    onChange={handleInputChange}
                    placeholder="e.g. ADA Workplace Inclusivity & ASL"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.specialization || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Qualifications</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="qualification"
                    value={formData.qualification}
                    onChange={handleInputChange}
                    placeholder="e.g. Certified Accessibility Specialist"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.qualification || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Years of Experience</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleInputChange}
                    placeholder="e.g. 7"
                    min="0"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">
                    {profile?.experience_years !== null && profile?.experience_years !== undefined ? `${profile.experience_years} Years` : 'Not provided'}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Instructor Fields */}
          {profile?.role === 'Instructor' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Academic Title</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g. Senior Professor of Linguistics"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.title || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Department</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="department"
                    value={formData.department}
                    onChange={handleInputChange}
                    placeholder="e.g. Deaf Studies & Sign Linguistics"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.department || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Specialization</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="specialization"
                    value={formData.specialization}
                    onChange={handleInputChange}
                    placeholder="e.g. Tactile ASL & Non-Manual Signals"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.specialization || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Qualifications</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="qualification"
                    value={formData.qualification}
                    onChange={handleInputChange}
                    placeholder="e.g. Ph.D. in Cognitive Linguistics"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.qualification || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Years of Experience</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleInputChange}
                    placeholder="e.g. 12"
                    min="0"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">
                    {profile?.experience_years !== null && profile?.experience_years !== undefined ? `${profile.experience_years} Years` : 'Not provided'}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Administrator Fields */}
          {profile?.role === 'Administrator' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Department</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="department"
                    value={formData.department}
                    onChange={handleInputChange}
                    placeholder="e.g. Platform Infrastructure & Security"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-rose-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.department || 'Not provided'}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Designation</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="designation"
                    value={formData.designation}
                    onChange={handleInputChange}
                    placeholder="e.g. Platform Administrator"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-rose-500 transition-all"
                  />
                ) : (
                  <p className="text-sm font-semibold text-slate-200">{profile?.designation || 'Not provided'}</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons for Edit Mode */}
        {isEditing && (
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs cursor-pointer transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer transition-all disabled:opacity-50"
            >
              {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        )}
      </form>
    </div>
  );
};
