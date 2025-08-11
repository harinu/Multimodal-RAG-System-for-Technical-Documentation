import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document API functions
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};

export const getDocuments = async () => {
  try {
    const response = await api.get('/documents');
    return response.data.document_ids;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

export const getDocumentMetadata = async (documentId) => {
  try {
    const response = await api.get(`/documents/${documentId}/metadata`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching metadata for document ${documentId}:`, error);
    throw error;
  }
};

// Query API functions
export const queryDocuments = async (query, documentIds = null, includeImages = true, maxResults = 5) => {
  try {
    const response = await api.post('/query', {
      query,
      document_ids: documentIds,
      include_images: includeImages,
      max_results: maxResults,
    });
    return response.data;
  } catch (error) {
    console.error('Error querying documents:', error);
    throw error;
  }
};

// Helper function to get raw document URL
export const getRawDocumentUrl = (documentId, filename) => {
  return `/api/documents/${documentId}/raw/${filename}`;
};

// Error handling interceptors
api.interceptors.request.use(
  config => {
    // Do something before request is sent
    return config;
  },
  error => {
    console.error('Network error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error codes
    if (error.response) {
      const { status, data } = error.response;
      
      if (status === 400) {
        console.error('Bad request:', data.detail);
      } else if (status === 404) {
        console.error('Resource not found:', data.detail);
      } else if (status === 500) {
        console.error('Server error:', data.detail || 'An unexpected error occurred');
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;