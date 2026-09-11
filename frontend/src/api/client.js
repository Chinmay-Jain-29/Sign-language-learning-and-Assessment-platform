import axios from 'axios';

let rawUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').trim().replace(/\/+$/, '');
if (!rawUrl.endsWith('/api/v1')) {
  rawUrl = `${rawUrl}/api/v1`;
}
const API_BASE_URL = rawUrl;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('asl_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => {
    // Standard API response unwrapping if envelope present
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (!response.data.success) {
        return Promise.reject(response.data.error || { message: response.data.message });
      }
    }
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('asl_token');
      localStorage.removeItem('asl_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
