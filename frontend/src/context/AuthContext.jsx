import React, { createContext, useContext, useState } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('asl_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('asl_token') || null);
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('asl_refresh_token') || null);
  const [loading, setLoading] = useState(false);

  const login = async (id, password, role = 'Learner') => {
    setLoading(true);
    try {
      const res = await api.post('/auth/login', {
        id: String(id).trim(),
        password,
        role
      });

      const { access_token, refresh_token, user_id, role: userRole, full_name, email } = res.data;
      const userData = { id: user_id, email, full_name, role: userRole };

      localStorage.setItem('asl_token', access_token);
      localStorage.setItem('asl_refresh_token', refresh_token);
      localStorage.setItem('asl_user', JSON.stringify(userData));

      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      setUser(userData);
      return { success: true, user: userData };
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.message || err.message || 'Invalid login credentials.',
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, fullName, password, role = 'Learner', preferredLanguage = 'English', learningLevel = 'Beginner') => {
    setLoading(true);
    try {
      const res = await api.post('/auth/register', {
        email: String(email).trim(),
        full_name: String(fullName).trim(),
        password,
        role,
        preferred_language: preferredLanguage,
        learning_level: learningLevel
      });
      return { success: true, data: res.data };
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.message || err.message || 'Registration failed.',
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    const refToken = localStorage.getItem('asl_refresh_token');
    if (refToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refToken });
      } catch (e) {
        console.warn("Logout notification error", e);
      }
    }
    localStorage.removeItem('asl_token');
    localStorage.removeItem('asl_refresh_token');
    localStorage.removeItem('asl_user');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, refreshToken, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
