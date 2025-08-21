import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './css/login.css'
function LoginBox() {
    const [email, setEmail] = useState('')
    const [userName, setUserName] = useState('')
    const [password, setPasssword] = useState('')
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
        <div className="login-fondo container-fluid  mt-4 bg-blue " style={{ maxWidth: '600px'}}>
            <h1 class="text-center ">este es el login</h1>
            <form action=""></form>




        </div>

    )


}



export default LoginBox