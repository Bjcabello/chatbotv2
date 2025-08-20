import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initializeAuth = () => {
      const token = localStorage.getItem('token');
      console.log('AuthContext - Inicialización - Token:', token);
      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          const isValid = decodedToken.exp > currentTime;
          console.log('AuthContext - Inicialización - Token válido:', isValid);
          setIsAuthenticated(isValid);
        } catch (error) {
          console.log('AuthContext - Inicialización - Error:', error);
          localStorage.removeItem('token');
          setIsAuthenticated(false);
        }
      }
    };

    initializeAuth();

    const checkTokenExpiration = () => {
      const token = localStorage.getItem('token');
      console.log('AuthContext - Chequeo - Token:', token);
      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          if (decodedToken.exp < currentTime) {
            console.log('AuthContext - Chequeo - Token expirado');
            localStorage.removeItem('token');
            setIsAuthenticated(false);
          }
        } catch (error) {
          console.log('AuthContext - Chequeo - Error:', error);
          localStorage.removeItem('token');
          setIsAuthenticated(false);
        }
      }
    };

    const interval = setInterval(checkTokenExpiration, 60000);
    return () => clearInterval(interval);
  }, []);

  const login = useCallback((token) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
    console.log('AuthContext - Login - isAuthenticated actualizado a:', true, 'Token:', token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    console.log('AuthContext - Logout - isAuthenticated actualizado a:', false);
  }, []);

  console.log('AuthContext - Render - isAuthenticated:', isAuthenticated);
  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};