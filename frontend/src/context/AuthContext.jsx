// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
// Cambia 'import jwtDecode from 'jwt-decode';' a:
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const token = localStorage.getItem('token');
    console.log('Verificando token inicial:', token);
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        const isValid = decodedToken.exp > currentTime;
        console.log('Token válido:', isValid, 'Expira en:', new Date(decodedToken.exp * 1000).toISOString());
        return isValid;
      } catch (error) {
        console.log('Error decodificando token inicial:', error);
        localStorage.removeItem('token');
        return false;
      }
    }
    return false;
  });

  useEffect(() => {
    const checkTokenExpiration = () => {
      const token = localStorage.getItem('token');
      console.log('Chequeando expiración, token:', token);
      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          if (decodedToken.exp < currentTime) {
            console.log('Token expirado, eliminando...');
            localStorage.removeItem('token');
            setIsAuthenticated(false);
          } else {
            console.log('Token aún válido, expira en:', new Date(decodedToken.exp * 1000).toISOString());
          }
        } catch (error) {
          console.log('Error en chequeo de token:', error);
          localStorage.removeItem('token');
          setIsAuthenticated(false);
        }
      } else {
        console.log('No hay token, isAuthenticated:', isAuthenticated);
      }
    };

    checkTokenExpiration();
    const interval = setInterval(checkTokenExpiration, 60000);
    return () => clearInterval(interval);
  }, []);

  const login = (token) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
    console.log('Login exitoso, token guardado:', token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    console.log('Logout ejecutado');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};