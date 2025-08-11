# Project Structure 

```
multimodal-rag/
│
├── app/                           # Main application code
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py              # API routes
│   │   └── models.py              # Pydantic models for API
│   │
│   ├── core/                      # Core RAG functionality
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Document processing pipeline
│   │   ├── text_processor.py      # Text extraction and chunking
│   │   ├── image_processor.py     # Image processing
│   │   ├── code_processor.py      # Code snippet processing
│   │   ├── embedder.py            # Vector embedding generation
│   │   ├── retriever.py           # Retrieval logic
│   │   └── llm.py                 # LLM integration
│   │
│   ├── db/                        # Database interactions
│   │   ├── __init__.py
│   │   ├── vector_store.py        # Vector database operations
│   │   └── metadata_store.py      # Metadata storage
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── file_utils.py          # File handling utilities
│       └── evaluation.py          # Evaluation metrics
│
├── frontend/                      # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API service calls
│   │   ├── utils/                 # Frontend utilities
│   │   ├── App.js                 # Main React component
│   │   └── index.js               # Entry point
│   │
│   ├── package.json               # Frontend dependencies
│   └── README.md                  # Frontend documentation
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_document_processor.py
│   ├── test_retriever.py
│   └── test_api.py
│
├── data/                          # Data storage
│   ├── raw/                       # Raw uploaded documents
│   ├── processed/                 # Processed documents
│   └── vectors/                   # Vector database files
│
├── docker/                        # Docker configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment variables
├── README.md                      # Project documentation
└── LICENSE                        # Project license
```

This structure organizes the project into logical components:

1. app/ - Contains all backend Python code
   - api/ - FastAPI routes and models
   - core/ - Core RAG functionality
   - db/ - Database interactions
   - utils/ - Utility functions

2. frontend/ - React frontend application

3. tests/ - Test suite for backend components

4. data/ - Data storage directories

5. docker/ - Docker configuration files

