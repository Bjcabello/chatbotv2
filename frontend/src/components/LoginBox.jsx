import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './css/login.css'
function LoginBox() {
    const [email, setEmail] = useState('')
    const [userName, setUserName] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();


    const handleLogin = async (e) => {
        if (!email || !password || !userName) {
            setMessage('Por favor, completa todos los campos.');
            return;

        }

        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, userName }),
            });

            const data = await response.json();
            console.log('Login - Respuesta del backend:', data);
            if (data.status === 'success' && data.token) {
                setMessage(data.message);
                // login(data.token);
            } else {
                setMessage(data.error || 'Error: Credenciales inválidas.');
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
            <h3 class="text-center ">login</h3>
            <form onSubmit={handleLogin} className="row justify-content-center">
                <div className="col-12 mb-3"><br />
                    <label className="form-label fw-bold">nombre de usuario:</label>
                    <input
                        type="text"
                        className="form-control"
                        value={userName}
                        placeholder="Ingrese su nombre"
                        onChange={(e) => setUserName(e.target.value)}
                    />
                </div>
                <div>
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
                <p>¿no tienes una cuenta? <Link to="/register">registrate aqui</Link></p>
            </div>




        </div>

    )


}



export default LoginBox