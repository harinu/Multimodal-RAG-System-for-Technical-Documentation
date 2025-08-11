# Multimodal RAG System for Technical Documentation

A powerful retrieval-augmented generation (RAG) system designed to process and answer questions about technical documentation, including text, images, diagrams, and code snippets.

## Overview

This project implements a complete multimodal RAG system that can:

1. Process various document types (PDF, images, Markdown, HTML, text)
2. Extract and understand text, images, and code snippets
3. Generate vector embeddings for efficient retrieval
4. Answer questions using a hybrid search approach
5. Provide accurate responses with citations to source material

The system is built with a Python FastAPI backend and a React frontend, making it a full-stack application that can be deployed locally or to the cloud.

## Features

- **Multimodal Processing**: Handles text, images, and code snippets from various document formats
- **Advanced Text Processing**: Extracts and chunks text from PDFs, Markdown, HTML, and plain text files
- **Image Processing**: Extracts images from PDFs, processes standalone images, and performs OCR
- **Code Analysis**: Identifies and processes code snippets with language detection
- **Vector Embeddings**: Generates embeddings for all content types for semantic search
- **Hybrid Search**: Combines vector similarity with keyword matching for better results
- **LLM Integration**: Uses OpenAI's models for generating accurate responses
- **Citation Support**: Provides citations to source material for verification
- **User-Friendly Interface**: Clean, responsive UI for document upload and querying

## Architecture

The system follows a modular architecture with clear separation of concerns:

- **Document Processing Pipeline**: Handles document ingestion and processing
- **Vector Storage**: Manages embeddings and metadata
- **Retrieval Engine**: Implements hybrid search for finding relevant content
- **Response Generation**: Integrates with LLMs to generate accurate answers
- **Web Interface**: Provides a user-friendly frontend for interaction

For more details, see [architecture.md](architecture.md).

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- LangChain
- ChromaDB (vector database)
- PyPDF, Pillow, pytesseract (document processing)
- Sentence Transformers (embeddings)
- OpenAI API (LLM integration)

### Frontend
- React
- Bootstrap
- Axios
- React Router
- React Markdown

## Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/multimodal-rag.git
   cd multimodal-rag
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Usage

### Running the Backend

From the root directory:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

### Running the Frontend

From the frontend directory:

```
npm start
```

The web interface will be available at http://localhost:3000.

### Using the System

1. **Upload Documents**: Use the Upload page to add technical documentation
2. **View Documents**: See a list of uploaded documents and their metadata
3. **Ask Questions**: Enter questions about your documentation to get AI-generated answers

## Project Structure

```
multimodal-rag/
│
├── app/                           # Main application code
│   ├── api/                       # API endpoints
│   ├── core/                      # Core RAG functionality
│   ├── db/                        # Database interactions
│   └── utils/                     # Utility functions
│
├── frontend/                      # React frontend
│   ├── public/
│   └── src/
│
├── data/                          # Data storage
│   ├── raw/                       # Raw uploaded documents
│   ├── processed/                 # Processed documents
│   └── vectors/                   # Vector database files
│
├── tests/                         # Test suite
│
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## Evaluation

The system includes an evaluation framework to measure:

- Retrieval precision and recall
- Answer relevance and accuracy
- Response time and system performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the LLM capabilities
- LangChain for the RAG framework
- ChromaDB for vector storage
- All open-source libraries used in this project