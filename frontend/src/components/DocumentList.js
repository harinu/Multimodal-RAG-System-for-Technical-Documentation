import React, { useState, useEffect } from 'react';
import { getDocuments, getDocumentMetadata, getRawDocumentUrl } from '../services/api';

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get list of document IDs
      const documentIds = await getDocuments();
      
      // Fetch metadata for each document
      const documentPromises = documentIds.map(async (docId) => {
        try {
          // This endpoint might need to be implemented in the backend
          // For now, we'll create a placeholder with basic info
          const metadata = { 
            document_id: docId,
            filename: `Document ${docId.substring(0, 8)}`,
            document_type: 'unknown',
            num_text_chunks: 0,
            num_images: 0,
            num_code_snippets: 0
          };
          
          return {
            id: docId,
            ...metadata
          };
        } catch (err) {
          console.error(`Error fetching metadata for document ${docId}:`, err);
          return {
            id: docId,
            filename: `Document ${docId.substring(0, 8)}`,
            error: 'Failed to load metadata'
          };
        }
      });
      
      const documentsWithMetadata = await Promise.all(documentPromises);
      setDocuments(documentsWithMetadata);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentClick = (document) => {
    setSelectedDocument(selectedDocument?.id === document.id ? null : document);
  };

  const getDocumentTypeIcon = (documentType) => {
    switch (documentType) {
      case 'pdf':
        return <i className="fas fa-file-pdf text-danger"></i>;
      case 'image':
        return <i className="fas fa-file-image text-primary"></i>;
      case 'markdown':
        return <i className="fas fa-file-alt text-success"></i>;
      case 'html':
        return <i className="fas fa-file-code text-warning"></i>;
      case 'text':
        return <i className="fas fa-file-alt text-secondary"></i>;
      default:
        return <i className="fas fa-file text-secondary"></i>;
    }
  };

  const renderDocumentDetails = (document) => {
    if (!document) return null;

    return (
      <div className="card mb-4">
        <div className="card-header bg-light">
          <h5 className="mb-0">Document Details</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <p><strong>Document ID:</strong> {document.id}</p>
              <p><strong>Filename:</strong> {document.filename}</p>
              <p><strong>Type:</strong> {document.document_type}</p>
            </div>
            <div className="col-md-6">
              <p><strong>Text Chunks:</strong> {document.num_text_chunks}</p>
              <p><strong>Images:</strong> {document.num_images}</p>
              <p><strong>Code Snippets:</strong> {document.num_code_snippets}</p>
            </div>
          </div>
          
          {document.document_type === 'image' && document.filename && (
            <div className="mt-3">
              <h6>Preview:</h6>
              <img 
                src={getRawDocumentUrl(document.id, document.filename)} 
                alt={document.filename}
                className="img-fluid mt-2 border rounded"
                style={{ maxHeight: '200px' }}
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-2">Loading documents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <i className="fas fa-exclamation-circle me-2"></i>
        {error}
        <button 
          className="btn btn-outline-danger btn-sm float-end"
          onClick={fetchDocuments}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="document-list">
      <h2 className="mb-4">Your Documents</h2>
      
      {documents.length === 0 ? (
        <div className="alert alert-info" role="alert">
          <i className="fas fa-info-circle me-2"></i>
          No documents found. Please upload some documents first.
        </div>
      ) : (
        <div className="row">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Documents ({documents.length})</h5>
                <button 
                  className="btn btn-sm btn-outline-primary"
                  onClick={fetchDocuments}
                >
                  <i className="fas fa-sync-alt me-1"></i> Refresh
                </button>
              </div>
              <ul className="list-group list-group-flush">
                {documents.map((doc) => (
                  <li 
                    key={doc.id}
                    className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${selectedDocument?.id === doc.id ? 'active' : ''}`}
                    onClick={() => handleDocumentClick(doc)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div>
                      <span className="me-2">{getDocumentTypeIcon(doc.document_type)}</span>
                      {doc.filename}
                    </div>
                    <span className="badge bg-primary rounded-pill">
                      {doc.num_text_chunks + doc.num_images + doc.num_code_snippets || '?'} chunks
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="col-md-6">
            {selectedDocument ? (
              renderDocumentDetails(selectedDocument)
            ) : (
              <div className="card">
                <div className="card-body text-center text-muted">
                  <i className="fas fa-file-alt fa-3x mb-3"></i>
                  <p>Select a document to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentList;