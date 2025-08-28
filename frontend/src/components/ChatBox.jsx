import { Component, useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const token = localStorage.getItem('token') || '';
  const [contextType, setContextType] = useState('Documents');

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
      alert("Selecciona un archivo PDF primero");
      return;
    }

    const formData = new FormData();
    formData.append("file", archivoPDF);

    try {
      const response = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.error) {
        alert("Error al subir: " + data.error);
      } else {
        alert("✅ " + data.mensaje);
      }
    } catch (error) {
      alert("Error al subir el PDF: " + error.message);
    }
  };

  const handlersubirPdf = async () => {
    if (!fileUploaded) {
      return alert("no has subido ningun archivo")

    }

  }
  const handleEnviar = async () => {
    setRespuesta('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pregunta
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        setRespuesta(prev => prev + chunk);
      }
    } catch (error) {
      setRespuesta(` Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // ✅ scroll automático cuando llega respuesta
  useEffect(() => {
    const box = document.getElementById("respuesta-box");
    if (box) box.scrollTop = box.scrollHeight;
  }, [respuesta]);

  return (
    <ErrorBoundary>
      <div className='container-fluid bg-light mt-4 bg-blue border border-3  ' style={{ maxWidth: "900px" }} >
        <div className="d-flex justify-content-end mt-0 align-items-end text-center">
          <i className="bi bi-door-closed-fill"
            onClick={handleLogout} style={{ cursor: 'pointer', fontSize: '2em' }}>
          </i>
        </div>

        <h3 className='text-center'>ChatBot 🤖 Viadocs</h3>
        <div className='row justify-content-center mt-5'>
          <div className="row m-0">
            <div className='col-12 d-flex justify-content-between align-items-between'>
              <div className='m-4'>
                <label className='form-label fw-bold'>Subir PDF:</label>
                <input
                  type="file"
                  accept=".pdf"
                  className='form-control'
                  style={{ width: "80%" }}
                  onChange={e => setArchivoPDF(e.target.files[0])}
                />
                <button
                  className='btn btn-outline-success mt-2'
                  style={{ width: "80%" }}
                  onClick={handleSubirPDF}>
                  Subir PDF
                </button>
              </div>
              <div className='m-5'>
                <label htmlFor="contextType" className="form-label fw-bold">Tipo de Contexto:</label>
                <select className="form-select" aria-label="Default select example" value={contextType} onChange={(e) => setContextType(e.target.value)}>
                  <option value="Documentos">Documentos(PDFS)</option>
                  <option value="Procesos">Procesos</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div className='m-5'>
          <label className='form-label fw-bold'>Pregunta:</label>
          <input
            type="text"
            className='form-control'
            value={pregunta}
            placeholder='Ingrese su pregunta'
            style={{ width: "100%" }}
            onChange={e => setPregunta(e.target.value)}
          />
        </div>

        <div className='text-center'>
          <button
            className='btn btn-outline-primary icon-link-hover'
            style={{ width: "40%" }}
            onClick={handleEnviar}
            disabled={loading}>
            {loading ? 'cargando respuesta ....' : 'Enviar'}
          </button>
        </div>

        <div className='d-flex flex-column mt-3s'>
          <label className='form-label fw-bold'>Respuesta:</label>
          <div className='alert alert-secondary overflow-auto' style={{ height: "400px" }}>
            {respuesta}
          </div>
        </div>

      </div>

    </ErrorBoundary>

  );
}

export default ChatBox;
