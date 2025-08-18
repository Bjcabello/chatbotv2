import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './components/Register.jsx';
import Login from './components/Login.jsx';
import ChatBox from './components/ChatBox.jsx';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chat" element={<ChatBox />} />
        <Route path="/" element={<Login />} /> 
      </Routes>
    </Router>
  );
}

export default App;