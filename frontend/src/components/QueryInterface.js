import React, { useState, useEffect } from 'react';
import { getDocuments, queryDocuments, getRawDocumentUrl } from '../services/api';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [includeImages, setIncludeImages] = useState(true);
  const [maxResults, setMaxResults] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const documentIds = await getDocuments();
      setDocuments(documentIds.map(id => ({ id, name: `Document ${id.substring(0, 8)}` })));
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setResult(null);
      
      const response = await queryDocuments(
        query,
        selectedDocuments.length > 0 ? selectedDocuments : null,
        includeImages,
        maxResults
      );
      
      setResult(response);
    } catch (err) {
      console.error('Error querying documents:', err);
      setError(err.response?.data?.detail || 'An error occurred while processing your query');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentSelection = (docId) => {
    setSelectedDocuments(prev => {
      if (prev.includes(docId)) {
        return prev.filter(id => id !== docId);
      } else {
        return [...prev, docId];
      }
    });
  };

  const renderCitations = (citations) => {
    if (!citations || citations.length === 0) {
      return null;
    }

    return (
      <div className="citations mt-4">
        <h5>Sources:</h5>
        {citations.map((citation, index) => (
          <div key={index} className="citation card mb-2">
            <div className="card-body py-2">
              <h6 className="card-subtitle mb-2 text-muted">
                {citation.document_name}
                {citation.page_number && ` (Page ${citation.page_number})`}
              </h6>
              
              {citation.text && (
                <p className="card-text small mb-1">{citation.text.length > 200 
                  ? `${citation.text.substring(0, 200)}...` 
                  : citation.text}
                </p>
              )}
              
              {citation.image_url && (
                <img 
                  src={citation.image_url} 
                  alt={`Citation from ${citation.document_name}`}
                  className="img-fluid mt-2 border rounded"
                  style={{ maxHeight: '150px' }}
                />
              )}
              
              <div className="text-end">
                <small className="text-muted">
                  Confidence: {Math.round(citation.confidence * 100)}%
                </small>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderMarkdown = (text) => {
    return (
      <ReactMarkdown
        children={text}
        components={{
          code({node, inline, className, children, ...props}) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                children={String(children).replace(/\n$/, '')}
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                {...props}
                className="code-block"
              />
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          }
        }}
      />
    );
  };

  return (
    <div className="query-interface">
      <h2 className="mb-4">Ask Questions</h2>
      
      <div className="card mb-4">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="query" className="form-label">Your Question:</label>
              <textarea
                id="query"
                className="form-control query-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about your technical documentation..."
                rows="3"
                required
              />
            </div>
            
            <div className="mb-3">
              <button
                type="button"
                className="btn btn-link p-0"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <i className={`fas fa-chevron-${showAdvanced ? 'up' : 'down'} me-1`}></i>
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
              </button>
            </div>
            
            {showAdvanced && (
              <div className="card mb-3">
                <div className="card-body">
                  <div className="mb-3">
                    <label className="form-label">Select Documents to Query:</label>
                    <div className="document-selection">
                      {documents.length === 0 ? (
                        <p className="text-muted">No documents available</p>
                      ) : (
                        <div className="row">
                          {documents.map((doc) => (
                            <div key={doc.id} className="col-md-6 mb-2">
                              <div className="form-check">
                                <input
                                  className="form-check-input"
                                  type="checkbox"
                                  id={`doc-${doc.id}`}
                                  checked={selectedDocuments.includes(doc.id)}
                                  onChange={() => handleDocumentSelection(doc.id)}
                                />
                                <label className="form-check-label" htmlFor={`doc-${doc.id}`}>
                                  {doc.name}
                                </label>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      <small className="text-muted d-block mt-2">
                        {selectedDocuments.length === 0 
                          ? 'All documents will be searched' 
                          : `${selectedDocuments.length} document(s) selected`}
                      </small>
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label htmlFor="maxResults" className="form-label">Max Results:</label>
                        <input
                          type="number"
                          className="form-control"
                          id="maxResults"
                          min="1"
                          max="20"
                          value={maxResults}
                          onChange={(e) => setMaxResults(parseInt(e.target.value))}
                        />
                        <small className="text-muted">Number of context chunks to retrieve</small>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label d-block">Include Images:</label>
                        <div className="form-check form-switch">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="includeImages"
                            checked={includeImages}
                            onChange={(e) => setIncludeImages(e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="includeImages">
                            {includeImages ? 'Yes' : 'No'}
                          </label>
                        </div>
                        <small className="text-muted">Include image content in search results</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="d-grid">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search me-2"></i>
                    Get Answer
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          <i className="fas fa-exclamation-circle me-2"></i>
          {error}
        </div>
      )}
      
      {result && (
        <div className="query-result">
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="mb-0">Answer</h5>
            </div>
            <div className="card-body">
              <div className="answer-text">
                {renderMarkdown(result.answer)}
              </div>
              
              {renderCitations(result.citations)}
              
              <div className="text-end mt-3">
                <small className="text-muted">
                  Processing time: {result.processing_time.toFixed(2)}s
                </small>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryInterface;