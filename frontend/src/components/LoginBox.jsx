import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './css/login.css'
import { AuthContext } from '../context/AuthContext';
// import { AuthContext } from '../context/AuthContext';
// import jwtDecode from 'jwt-decode'; // Instala con: npm install jwt-decode
function LoginBox() {
    const [email, setEmail] = useState('')
    // const [userName, setUserName] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    // Redirige a /chat si ya está autenticado
    useEffect(() => {
    });

    const handleLogin = async (e) => {
        if (!email || !password) {
            setMessage('Por favor, completa todos los campos.');
            return;

        }

        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al iniciar sesión');
            }

        } catch (error) {
            setMessage(`Error: ${error.message}`);
            console.log('Login - Error en fetch:', error);
        } finally {
            setLoading(false);
        }

    }
    return (
        <div className="login-fondo container-fluid bg-blue p-4" style={{ maxWidth: '400px', marginTop: '130px' }}>
            <h3 className="text-center ">login</h3>
            <form onSubmit={handleLogin} className="row justify-content-center">
                <div>
                    <label className="form-label fw-bold">Correo Electrónico:</label>
                    <input
                        type="email"
                        className="form-control"
                        value={email}
                        placeholder="Ingrese su email"
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div><br />
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
                <p>¿no tienes una cuenta? <Link to="/register">registrate aqui</Link></p>
            </div>




        </div>

    )


}



export default LoginBox