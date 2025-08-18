import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setMessage('Por favor, completa todos los campos.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setMessage(data.message);
        setEmail('');
        setPassword('');
      } else {
        setMessage(data.error || 'Error al registrar.');
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid bg-light mt-4 bg-blue border border-3" style={{ maxWidth: '900px' }}>
      <h3 className="text-center">Registro</h3>
      <form onSubmit={handleRegister} className="row justify-content-center mt-5">
        <div className="col-12 col-md-6 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold">Correo Electrónico:</label>
          <input
            type="email"
            className="form-control"
            value={email}
            placeholder="Ingrese su email"
            style={{ width: '55%' }}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="col-12 col-md-6 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold">Contraseña:</label>
          <input
            type="password"
            className="form-control"
            value={password}
            placeholder="Ingrese su contraseña"
            style={{ width: '55%' }}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="text-center">
          <button
            className="btn btn-outline-primary icon-link-hover"
            style={{ width: '40%' }}
            type="submit"
            disabled={loading}
          >
            {loading ? 'Registrando...' : 'Registrarse'}
          </button>
        </div>
      </form>
      {message && (
        <div className="alert alert-info text-center mt-3" role="alert">
          {message}
        </div>
      )}
      <div className="text-center mt-3">
        <p>¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link></p>
      </div>
    </div>
  );
}

export default Register;