
import React, { useContext, useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    console.log('ProtectedRoute - useEffect - isAuthenticated:', isAuthenticated);
  }, [isAuthenticated]);

  console.log('ProtectedRoute - Render - isAuthenticated:', isAuthenticated);
  if (isAuthenticated === false) {
    console.log('ProtectedRoute - Redirigiendo a /login');
    return <Navigate to="/login" replace />;
  } else if (isAuthenticated === undefined) {
    return <div>Cargando autenticación...</div>;
  }
  return <Outlet />;
};

export default ProtectedRoute;