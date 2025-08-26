import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  // const [userId, setUserId] = useState(localStorage.getItem('userId') || null);

  const login = (token) => {
    localStorage.setItem('token', token);
    // localStorage.setItem('userId', userId);
    setIsAuthenticated(true);
    // setUserId(userId);
  };

  const logout = () => {
    localStorage.removeItem('token');
    // localStorage.removeItem('userId');
    setIsAuthenticated(false);
    // setUserId(null);
  };

  useEffect(() => {
    const checkToken = () => {
      const token = localStorage.getItem('token');
      if (token) {
        // Aquí podrías usar jwt-decode para verificar expiración
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    };
    checkToken();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout}}>
      {children}
    </AuthContext.Provider>
  );
};