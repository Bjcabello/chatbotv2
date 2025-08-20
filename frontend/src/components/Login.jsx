// src/components/Login.jsx
import React, { useState, useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    console.log('Login - useEffect - isAuthenticated:', isAuthenticated);
    if (isAuthenticated) {
      console.log('Login - Redirigiendo a /chatbox por isAuthenticated');
      navigate('/chatbox', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    console.log('Login - HandleLogin - Formulario enviado, email:', email, 'password:', password);
    if (!email || !password) {
      setMessage('Por favor, completa todos los campos.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log('Login - Respuesta del backend:', data);
      if (data.status === 'success' && data.token) {
        setMessage(data.message);
        login(data.token);
      } else {
        setMessage(data.error || 'Error: Credenciales inválidas.');
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
      console.log('Login - Error en fetch:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
      <div className="container-fluid bg-blue border border-3" style={{ maxWidth: '900px', padding: '20px' }}>
        <h3 className="text-center mb-4">Inicio de Sesión</h3>
        <form onSubmit={handleLogin} className="row justify-content-center">
          <div className="col-12 mb-3">
            <label className="form-label fw-bold">Correo Electrónico:</label>
            <input
              type="email"
              className="form-control"
              value={email}
              placeholder="Ingrese su email"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="col-12 mb-3">
            <label className="form-label fw-bold">Contraseña:</label>
            <input
              type="password"
              className="form-control"
              value={password}
              placeholder="Ingrese su contraseña"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="text-center col-12">
            <button
              className="btn btn-outline-primary icon-link-hover"
              style={{ width: '40%' }}
              type="submit"
              disabled={loading}
            >
              {loading ? 'Iniciando...' : 'Iniciar Sesión'}
            </button>
          </div>
        </form>
        {message && <div className="alert alert-info text-center mt-3" role="alert">{message}</div>}
        <div className="text-center mt-3">
          <p>¿No tienes cuenta? <Link to="/register">Regístrate aquí</Link></p>
        </div>
      </div>
    </div>
  );
}

export default Login;