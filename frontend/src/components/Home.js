import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="home">
      <div className="hero-section text-center">
        <div className="container">
          <h1 className="hero-title">Multimodal RAG System for Technical Documentation</h1>
          <p className="hero-subtitle">
            A powerful retrieval-augmented generation system that processes text, images, and code
            to provide accurate answers to your technical questions.
          </p>
          <div className="d-flex justify-content-center gap-3">
            <Link to="/upload" className="btn btn-primary btn-lg">
              Upload Documents
            </Link>
            <Link to="/query" className="btn btn-outline-primary btn-lg">
              Ask Questions
            </Link>
          </div>
        </div>
      </div>

      <div className="container mt-5">
        <h2 className="text-center mb-4">Key Features</h2>
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card feature-card">
              <div className="card-body text-center">
                <div className="feature-icon">
                  <i className="fas fa-file-alt"></i>
                </div>
                <h3 className="card-title">Multimodal Processing</h3>
                <p className="card-text">
                  Process and understand content from various sources including text documents,
                  images, diagrams, and code snippets.
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card feature-card">
              <div className="card-body text-center">
                <div className="feature-icon">
                  <i className="fas fa-search"></i>
                </div>
                <h3 className="card-title">Semantic Search</h3>
                <p className="card-text">
                  Find information based on meaning rather than just keywords, using advanced
                  vector embeddings and hybrid search techniques.
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card feature-card">
              <div className="card-body text-center">
                <div className="feature-icon">
                  <i className="fas fa-robot"></i>
                </div>
                <h3 className="card-title">AI-Powered Answers</h3>
                <p className="card-text">
                  Get accurate, contextual answers to your questions with citations to the source
                  material for verification.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mt-5">
        <h2 className="text-center mb-4">How It Works</h2>
        <div className="row">
          <div className="col-lg-8 offset-lg-2">
            <div className="card">
              <div className="card-body">
                <ol className="mb-0">
                  <li className="mb-3">
                    <strong>Upload Documents</strong> - Start by uploading your technical documentation
                    in various formats (PDF, images, Markdown, HTML, or plain text).
                  </li>
                  <li className="mb-3">
                    <strong>Processing</strong> - The system automatically extracts text, images, and code
                    snippets, and creates vector embeddings for efficient retrieval.
                  </li>
                  <li className="mb-3">
                    <strong>Ask Questions</strong> - Enter your technical questions in natural language.
                  </li>
                  <li className="mb-3">
                    <strong>Get Answers</strong> - The system retrieves relevant information from your
                    documents and generates accurate answers with citations.
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mt-5">
        <div className="text-center">
          <h2 className="mb-4">Ready to Get Started?</h2>
          <div className="d-flex justify-content-center gap-3">
            <Link to="/upload" className="btn btn-primary">
              Upload Your First Document
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;