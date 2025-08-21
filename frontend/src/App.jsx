import ChatBox from './components/ChatBox'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import RegisterBox from './components/RegisterBox'
import LoginBox from './components/LoginBox'

// import Register from
function App() {
  return (
    <Router>

      <Routes>
        <Route path="/" element={<RegisterBox />} />
        <Route path="/register" element={<RegisterBox />} />
        <Route path="/chat" element={<ChatBox />} />
        <Route path="/login" element={<LoginBox />} />
      </Routes>


    </Router>
  )
}


export default App
