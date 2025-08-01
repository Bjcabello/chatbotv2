import { useState } from 'react';

function ChatBox() {
  const [usuario, setUsuario] = useState('');
  const [dni, setDni] = useState('');
  const [tipoUsuario, setTipoUsuario] = useState('');
  const [pregunta, setPregunta] = useState('');
  const [respuesta, setRespuesta] = useState('');
  const [loading, setLoading] = useState(false);
  const [archivoPDF, setArchivoPDF] = useState(null);

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
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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
    if (!usuario || !dni || !tipoUsuario || !pregunta) {
      alert('Completa todos los campos');
      return;
    }

    setRespuesta('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          usuario,
          dni,
          tipo_usuario: tipoUsuario,
          pregunta,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setRespuesta((prev) => prev + chunk);
      }
    } catch (error) {
      setRespuesta(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid bg-light mt-4 border border-3" style={{ maxWidth: '900px' }}>
      <h3 className="text-center">ChatBot  Viadocs</h3>
      <div className="row justify-content-center mt-5">
        <div className="col-12 col-md-4 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold" htmlFor="usuario">
            Nombre del Usuario:
          </label>
          <input
            type="text"
            id="usuario"
            className="form-control"
            value={usuario}
            placeholder="Ingrese nombre"
            style={{ maxWidth: '200px' }}
            onChange={(e) => setUsuario(e.target.value)}
            aria-label="Nombre del usuario"
          />
        </div>

        <div className="col-12 col-md-4 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold" htmlFor="dni">
            DNI:
          </label>
          <input
            type="text"
            id="dni"
            className="form-control"
            value={dni}
            placeholder="Ingrese DNI"
            style={{ maxWidth: '200px' }}
            onChange={(e) => setDni(e.target.value)}
            aria-label="DNI del usuario"
          />
        </div>

        <div className="col-12 col-md-4 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold" htmlFor="tipoUsuario">
            Tipo de Usuario:
          </label>
          <input
            type="text"
            id="tipoUsuario"
            className="form-control"
            value={tipoUsuario}
            placeholder="Ingrese rol"
            style={{ maxWidth: '200px' }}
            onChange={(e) => setTipoUsuario(e.target.value)}
            aria-label="Tipo de usuario"
          />
        </div>

        <div className="col-12 col-md-4 mb-3 d-flex flex-column align-items-center">
          <label className="form-label fw-bold" htmlFor="archivoPDF">
            Adjunta PDF:
          </label>
          <input
            type="file"
            id="archivoPDF"
            accept=".pdf"
            className="form-control"
            style={{ Width: '250px' }}
            onChange={(e) => setArchivoPDF(e.target.files[0])}
            aria-label="Subir archivo PDF"
          />
          <button
            className="btn btn-outline-success mt-2"
            style={{ width: '200px' }}
            onClick={handleSubirPDF}
          >
            Subir PDF
          </button>
        </div>
      </div>

      <div className="m-5">
        <label className="form-label fw-bold" htmlFor="pregunta">
          Pregunta:
        </label>
        <input
          type="text"
          id="pregunta"
          className="form-control"
          value={pregunta}
          placeholder="Ingrese su pregunta"
          onChange={(e) => setPregunta(e.target.value)}
          aria-label="Pregunta para el chatbot"
        />
      </div>

      <div className="text-center">
        <button
          className="btn btn-outline-primary"
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