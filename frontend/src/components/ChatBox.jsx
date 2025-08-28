import React, { useState, useEffect, useContext, Component } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { jwtDecode } from 'jwt-decode';

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ color: 'red', padding: '20px' }}>
          <h2>Error en ChatBox</h2>
          <p>{this.state.error.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

function ChatBox() {
  const [pregunta, setPregunta] = useState('');
  const [respuesta, setRespuesta] = useState(''); 
  const [loading, setLoading] = useState(false);
  const [archivoPDF, setArchivoPDF] = useState(null);
  const { logout, isAuthenticated } = useContext(AuthContext);
  const [contextType, setContextType] = useState('Documentos');
  const navigate = useNavigate();
  const token = localStorage.getItem('token') || '';

  useEffect(() => {
    console.log('ChatBox - Mounted, isAuthenticated:', isAuthenticated, 'Token:', token);
    if (!isAuthenticated) {
      console.log('ChatBox - No autenticado, redirigiendo');
      navigate('/login', { replace: true });
      return;
    }
    const checkTokenExpiration = () => {
      if (token && isAuthenticated) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          console.log('ChatBox - Token expira en:', new Date(decodedToken.exp * 1000));
          if (decodedToken.exp < currentTime) {
            console.log('ChatBox - Token expirado');
            logout();
            navigate('/login', { replace: true });
          }
        } catch (error) {
          console.log('ChatBox - Error decodificando:', error);
          logout();
          navigate('/login', { replace: true });
        }
      }
    };

    checkTokenExpiration();
    const interval = setInterval(checkTokenExpiration, 60000);
    return () => clearInterval(interval);
  }, [token, isAuthenticated, logout, navigate]);

  const handleSubirPDF = async () => {
    if (!archivoPDF) {
      alert('Selecciona un archivo PDF primero');
      return;
    }
    const formData = new FormData();
    formData.append('file', archivoPDF);
    try {
      console.log('ChatBox - Enviando archivo PDF a /api/upload-pdf');
      const response = await fetch('http://localhost:8000/api/upload-pdf', {
        method: 'POST',
        body: formData,
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      console.log('ChatBox - Respuesta de /api/upload-pdf:', data);
      if (data.error) alert('Error al subir: ' + data.error);
      else alert('✅ ' + data.mensaje);
    } catch (error) {
      console.log('ChatBox - Error en /api/upload-pdf:', error);
      alert('Error al subir el PDF: ' + error.message);
    }
  };

  const handleEnviar = async () => {
    if (!pregunta) {
      alert('Completa la pregunta');
      return;
    }
    setRespuesta('');
    setLoading(true);
    try {
      console.log('ChatBox - Enviando pregunta a /api/chat, Pregunta:', pregunta);
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ pregunta, context_type: contextType }),
      });
      if (!response.ok) throw new Error(`Error del servidor: ${response.status} - ${response.statusText}`);
      console.log('ChatBox - Respuesta de /api/chat iniciada');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true }); // ✅ decodificación streaming
        if (chunk.trim()) {
          console.log('ChatBox - Chunk recibido:', chunk);
          setRespuesta((prev) => prev + chunk);
        }
      }
    } catch (error) {
      console.log('ChatBox - Error en /api/chat:', error);
      setRespuesta(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  
  useEffect(() => {
    const box = document.getElementById("respuesta-box");
    if (box) box.scrollTop = box.scrollHeight;
  }, [respuesta]);

  console.log('ChatBox - Render, isAuthenticated:', isAuthenticated, 'Respuesta:', respuesta);
  return (
    <ErrorBoundary>
      <div className="container-fluid bg-lightmt mt-5 mb-5 bg-blue border border-3" style={{ maxWidth: '900px', padding: '20px', borderRadius: '10px' }}>
        <div className="d-flex justify-content-end mt-0 align-items-end text-center">
          <i className="bi bi-box-arrow-in-right m-0 "
            onClick={handleLogout} style={{ cursor: 'pointer', fontSize: '2em' }}>
              
          </i>
        </div>
        <h3 className="text-center m-0">ChatBot Viadocs</h3>
        <div className="row m-0">
          <div className="col-12 d-flex justify-content-between align-items-between">
            <div className='m-4'>
              <label className="form-label fw-bold">Subir PDF:</label>
              <input
                type="file"
                accept=".pdf"
                className="form-control"
                style={{ width: '60%' }}
                onChange={(e) => setArchivoPDF(e.target.files[0])}
              />
              <button className="btn btn-outline-success mt-2" style={{ width: '60%' }} onClick={handleSubirPDF}>
                Subir PDF
              </button>
            </div>
            <div className='m-4'>
              <label htmlFor="contextType" className="form-label fw-bold">Tipo de Contexto:</label>
              <select className="form-select" aria-label="Default select example" value={contextType} onChange={(e) => setContextType(e.target.value)}>
                <option value="Documentos">Documentos</option>
                <option value="Procesos">Procesos</option>
              </select>
            </div>
          </div>
        </div>
        <div className="m-2">
          <label className="form-label fw-bold">Pregunta:</label>
          <input
            type="text"
            className="form-control"
            value={pregunta}
            placeholder="Ingrese su pregunta"
            style={{ width: '100%' }}
            onChange={(e) => setPregunta(e.target.value)}
          />
        </div>
        <div className="d-grid gap-2 d-md-flex justify-content-md-center">
          <button
            className="btn btn-outline-primary icon-link-hover"
            style={{ width: '40%', height: '20%' }}
            onClick={handleEnviar}
            disabled={loading}
          >
            {loading ? 'Cargando...' : 'Enviar'}
          </button>
        </div>
        <div className="d-flex flex-column mt-3">
          <label className="form-label fw-bold">Respuesta:</label>
          <div id="respuesta-box" className="alert alert-secondary overflow-auto" style={{ height: '150px', whiteSpace: 'pre-wrap' }}>
            {respuesta || (loading ? <TitubeandoDot /> : (pregunta ? "...." : ""))}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
  function TitubeandoDot() {
    const [dots, setDots] = useState('');
    useEffect(() => {
      const interval = setInterval(() => {
        setDots((prev) => (prev.length < 3 ? prev + '.' : ''));
      }, 400);
      return () => clearInterval(interval);
    }, []);
    return <span>{dots}</span>;
  }
}

export default ChatBox;
