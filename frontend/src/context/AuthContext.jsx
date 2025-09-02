import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token',
    !!localStorage.getItem('api_key')

  ));
  // const [userId, setUserId] = useState(localStorage.getItem('userId') || null);

  const login = (token, apiKey, apiKeyExpiresAt) => {
    localStorage.setItem('token', token);
    // localStorage.setItem('userId', userId);
    localStorage.setItem('apiKey', apiKey);
    localStorage.setItem('expires_at', apiKeyExpiresAt)
    setIsAuthenticated(true);
    // setUserId(userId);
  };

  const logout = () => {
    localStorage.removeItem('token');
    // localStorage.removeItem('userId');
    localStorage.removeItem('apiKey');
    localStorage.removeItem('expires_at')
    setIsAuthenticated(false);
    // setUserId(null);
  };

  useEffect(() => {
    const checkToken = () => {
      const token = localStorage.getItem('token');
      const apiKey = localStorage.getItem('api_key');
      const apiKeyExpiresAt = localStorage.getItem('expires_at');
      if (token && apiKey) {
        // Aquí podrías usar jwt-decode para verificar expiración
        const expiresAt = new Date(apiKeyExpiresAt);
        if (expiresAt < new Date()) {
          console.log('AuthContext - API Key expired, logging out');
          logout();
        } else {
          setIsAuthenticated(true);
        }
      } else {
        setIsAuthenticated(false);
      }
    };
    checkToken();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};