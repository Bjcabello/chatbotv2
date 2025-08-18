import React, { useState, useEffect } from 'react';

function ChatBox() {
  const [pregunta, setPregunta] = useState('');
  const [respuesta, setRespuesta] = useState('');
  const [loading, setLoading] = useState(false);
  const [archivoPDF, setArchivoPDF] = useState(null);
  const token = localStorage.getItem('token') || '';

  useEffect(() => {
    if (!token) {
      alert('Debes iniciar sesión para usar el chat.');
    }
  }, [token]);

  const handleSubirPDF = async () => {
    if (!archivoPDF) {
      alert('Selecciona un archivo PDF primero');
      return;
    }

    const formData = new FormData();
    formData.append('file', archivoPDF);

    try {
      const response = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();
      if (data.error) {
        alert('Error al subir: ' + data.error);
      } else {
        alert('✅ ' + data.mensaje);
      }
    } catch (error) {
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
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ pregunta }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        setRespuesta((prev) => prev + chunk);
      }
    } catch (error) {
      setRespuesta(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid bg-light mt-4 bg-blue border border-3" style={{ maxWidth: '900px' }}>
      <h3 className="text-center">ChatBot  Viadocs</h3>
      <div className="row justify-content-center mt-5">
        <div className="col-12 col-md-4 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold">Subir PDF:</label>
          <input
            type="file"
            accept=".pdf"
            className="form-control"
            style={{ width: '100%' }}
            onChange={(e) => setArchivoPDF(e.target.files[0])}
          />
          <button className="btn btn-outline-success mt-2" style={{ width: '100%' }} onClick={handleSubirPDF}>
            Subir PDF
          </button>
        </div>
      </div>
      <div className="m-5">
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
      <div className="text-center">
        <button
          className="btn btn-outline-primary icon-link-hover"
          style={{ width: '40%' }}
          onClick={handleEnviar}
          disabled={loading}
        >
          {loading ? 'Cargando...' : 'Enviar'}
        </button>
      </div>
      <div className="d-flex flex-column mt-3">
        <label className="form-label fw-bold">Respuesta:</label>
        <div className="alert alert-secondary overflow-auto" style={{ height: '200px' }}>
          {respuesta}
        </div>
      </div>
    </div>
  );
}

export default ChatBox;