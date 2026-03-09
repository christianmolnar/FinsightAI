/**
 * Centralized API client.
 * Reads JWT from localStorage and injects the Authorization header
 * on every request. Handles 401 by clearing the session and reloading.
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('finsight_token');
}

async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Token expired or invalid — clear session and redirect to login
    localStorage.removeItem('finsight_token');
    localStorage.removeItem('finsight_user');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }

  // 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

export const apiClient = {
  get:    (path, options = {}) => request(path, { ...options, method: 'GET' }),
  post:   (path, body, options = {}) => request(path, { ...options, method: 'POST',   body: JSON.stringify(body) }),
  put:    (path, body, options = {}) => request(path, { ...options, method: 'PUT',    body: JSON.stringify(body) }),
  patch:  (path, body, options = {}) => request(path, { ...options, method: 'PATCH',  body: JSON.stringify(body) }),
  delete: (path, options = {}) => request(path, { ...options, method: 'DELETE' }),
};

export default apiClient;
