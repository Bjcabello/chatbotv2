import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function RegisterBox() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [user_name, setUser_name] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!email || !password || !user_name) {
      setMessage('Por favor, completa todos los campos.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, user_name }),
      });
      console.log(`el response: ${response}`)

      if (!response.ok) throw new Error('fallo al registrar')
      const data = await response.json();

      // console.log('Register - Respuesta del backend:', data);
      // if (data.access_token) {
      //   setMessage('Registro exitoso');
      //   setEmail('');
      //   setPassword('');
      //   setUser_name('')
      //   // Aquí podrías redirigir al login o guardar el token si el backend lo devuelve
      // } else {
      //   setMessage(data.detail || 'Error al registrar.');
      // }

      // const data = await response.json();
      // if (data.status === 'success') {
      //   setMessage(data.message);
      //   setUser_name('');
      //   setPassword('');
      //   setEmail('');
      // } else {
      //   setMessage(data.error || 'Error al registrar.');
      // }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid bg-light bg-blue border border-4 p-4" style={{ maxWidth: '400px', marginTop: '130px' }}>
      <h3 className="text-center">Registro</h3>
      <form onSubmit={handleRegister} className="row justify-content-center mt-5">
        <div className="form-label fw-bold">
          <label className="form-label fw-bold">Nombre del usuario:</label>
          <input
            type="string"
            className="form-control"
            value={user_name}
            placeholder="Ingrese su nombre"

            onChange={(e) => setUser_name(e.target.value)}
          />
        </div>
        <div className="form-label fw-bold">
          <label className="form-label fw-bold">Correo Electrónico:</label>
          <input
            type="email"
            className="form-control"
            value={email}
            placeholder="Ingrese su email"

            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="form-label fw-bold">
          <label className="form-label fw-bold">Contraseña:</label>
          <input
            type="password"
            className="form-control"
            value={password}
            placeholder="Ingrese su contraseña"
            // style={{ width: '55%' }}
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
      {message && <div className="alert alert-info text-center mt-3" role="alert">{message}</div>}
      <div className="text-center mt-3">
        <p>¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link></p>
      </div>
    </div>
  );
}

export default RegisterBox;