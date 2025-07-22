import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import Chat from './components/Chat';
import StoryViewer from './components/StoryViewer';
import logoImage from './assets/script.png'; 

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const setAuthToken = (newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
    setToken(newToken);
  };

  const logout = () => {
    setAuthToken(null);
  };

  return (
    <Router>
      <header className="app-header">
        
        <Link to="/" className="logo">
          <img src={logoImage} alt="AI Story Weaver Logo" className="logo-image" />
          <h1>AI Story Weaver</h1>
        </Link>
        <nav>
          {token && <button onClick={logout}>Logout</button>}
        </nav>
      </header>
      <main className="container">
        <Routes>
          <Route path="/auth" element={!token ? <Auth setToken={setAuthToken} /> : <Navigate to="/" />} />
          <Route path="/chat" element={token ? <Chat token={token} /> : <Navigate to="/auth" />} />
          <Route path="/story/:storyId" element={token ? <StoryViewer token={token} /> : <Navigate to="/auth" />} />
          <Route path="/" element={token ? <Dashboard token={token} /> : <Navigate to="/auth" />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;