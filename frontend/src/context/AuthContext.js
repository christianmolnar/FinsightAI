import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);       // { email, username }
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true); // true while restoring session

  // Restore session from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('finsight_token');
    const storedUser = localStorage.getItem('finsight_user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('finsight_token', data.access_token);
    localStorage.setItem('finsight_user', JSON.stringify({ email: data.email, username: data.username }));
    setToken(data.access_token);
    setUser({ email: data.email, username: data.username });
    return data;
  }, []);

  const register = useCallback(async (email, username, password) => {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    const data = await res.json();
    localStorage.setItem('finsight_token', data.access_token);
    localStorage.setItem('finsight_user', JSON.stringify({ email: data.email, username: data.username }));
    setToken(data.access_token);
    setUser({ email: data.email, username: data.username });
    return data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('finsight_token');
    localStorage.removeItem('finsight_user');
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
