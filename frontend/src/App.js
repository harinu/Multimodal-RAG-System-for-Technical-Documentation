import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import components
import Home from './components/Home';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QueryInterface from './components/QueryInterface';

function App() {
  return (
    <div className="app">
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <Link className="navbar-brand" to="/">Multimodal RAG System</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav">
              <li className="nav-item">
                <Link className="nav-link" to="/">Home</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/upload">Upload Documents</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/documents">View Documents</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/query">Ask Questions</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div className="container app-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<DocumentUpload />} />
          <Route path="/documents" element={<DocumentList />} />
          <Route path="/query" element={<QueryInterface />} />
        </Routes>
      </div>

      <footer className="bg-light text-center text-muted py-4 mt-5">
        <div className="container">
          <p>Multimodal RAG System for Technical Documentation</p>
          <p className="mb-0">© 2023 - Portfolio Project</p>
        </div>
      </footer>
    </div>
  );
}

export default App;