import { createContext, useContext, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';

const STORAGE_KEY = 'fci-auth';

function loadStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
}

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const stored = loadStored();
  const [user, setUser] = useState(stored?.user || null);
  const [token, setToken] = useState(stored?.token || null);
  const navigate = useNavigate();

  const login = useCallback(async (username, password) => {
    const data = await api.login(username, password);
    const u = {
      user_id: data.user_id,
      username: data.username,
      display_name: data.display_name,
    };
    setUser(u);
    setToken(data.token);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: u, token: data.token }));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem(STORAGE_KEY);
    navigate('/login');
  }, [navigate]);

  const value = {
    user,
    token,
    isAuthenticated: token !== null,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
