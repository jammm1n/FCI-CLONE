import { createContext, useContext, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const navigate = useNavigate();

  const login = useCallback(async (username) => {
    const data = await api.login(username);
    setUser({
      user_id: data.user_id,
      username: data.username,
      display_name: data.display_name,
    });
    setToken(data.token);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
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
