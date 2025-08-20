// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = ({ isAuthenticated }) => {
  console.log('ProtectedRoute - isAuthenticated:', isAuthenticated);
  if (!isAuthenticated) {
    console.log('Redirigiendo a /login por falta de autenticación');
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
};

export default ProtectedRoute;