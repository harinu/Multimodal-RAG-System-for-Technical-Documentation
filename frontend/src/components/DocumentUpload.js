import React, { useState, useRef } from 'react';
import { uploadDocument } from '../services/api';

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setUploadStatus(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      setError(null);
      setUploadStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setIsUploading(true);
      setError(null);
      
      console.log('Uploading file:', file);
      const response = await uploadDocument(file);
      console.log('Upload response:', response);
      
      setUploadStatus({
        success: true,
        documentId: response.document_id,
        filename: response.filename,
        message: 'Document uploaded successfully and is being processed.'
      });
      
      // Reset file selection
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'An error occurred during upload');
      console.log("Error object:", err);
      setUploadStatus({
        success: false,
        message: 'Upload failed'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const getSupportedFormats = () => {
    return (
      <div className="mt-3">
        <h5>Supported Formats:</h5>
        <ul className="list-unstyled d-flex flex-wrap">
          <li className="me-3"><span className="badge bg-primary">PDF</span></li>
          <li className="me-3"><span className="badge bg-primary">Images (JPG, PNG)</span></li>
          <li className="me-3"><span className="badge bg-primary">Markdown</span></li>
          <li className="me-3"><span className="badge bg-primary">HTML</span></li>
          <li className="me-3"><span className="badge bg-primary">Text</span></li>
        </ul>
      </div>
    );
  };

  return (
    <div className="document-upload">
      <h2 className="mb-4">Upload Documents</h2>
      
      <div className="card mb-4">
        <div className="card-body">
          <p className="card-text">
            Upload your technical documentation to enable the RAG system to answer questions about it.
            The system supports various file formats and will automatically extract text, images, and code.
          </p>
          {getSupportedFormats()}
        </div>
      </div>

      <div 
        className="upload-container mb-4"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
      >
        <div className="upload-icon">
          <i className="fas fa-cloud-upload-alt"></i>
        </div>
        <h3>Drag & Drop or Click to Upload</h3>
        <p className="text-muted">{file ? file.name : 'No file selected'}</p>
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange} 
          style={{ display: 'none' }}
          accept=".pdf,.jpg,.jpeg,.png,.md,.html,.htm,.txt"
        />
      </div>

      <div className="d-grid gap-2 col-6 mx-auto">
        <button 
          className="btn btn-primary" 
          onClick={handleUpload}
          disabled={!file || isUploading}
        >
          {isUploading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Uploading...
            </>
          ) : 'Upload Document'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger mt-4" role="alert">
          <i className="fas fa-exclamation-circle me-2"></i>
          {error}
        </div>
      )}

      {uploadStatus && uploadStatus.success && (
        <div className="alert alert-success mt-4" role="alert">
          <i className="fas fa-check-circle me-2"></i>
          {uploadStatus.message}
          <div className="mt-2">
            <strong>Document ID:</strong> {uploadStatus.documentId}<br />
            <strong>Filename:</strong> {uploadStatus.filename}
          </div>
        </div>
      )}

      <div className="card mt-5">
        <div className="card-header">
          <h5 className="mb-0">Processing Information</h5>
        </div>
        <div className="card-body">
          <p>
            After uploading, your document will be processed in the background:
          </p>
          <ol>
            <li>Text will be extracted and chunked into smaller pieces</li>
            <li>Images will be processed using OCR and image recognition</li>
            <li>Code snippets will be identified and analyzed</li>
            <li>Vector embeddings will be created for efficient retrieval</li>
          </ol>
          <p className="mb-0">
            Processing time depends on the document size and complexity. You can start asking questions
            once processing is complete.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;