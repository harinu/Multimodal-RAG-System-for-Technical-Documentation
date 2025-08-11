import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vector DB
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/vectors")

# Document Storage
RAW_DOCUMENTS_DIR = os.getenv("RAW_DOCUMENTS_DIR", "./data/raw")
PROCESSED_DOCUMENTS_DIR = os.getenv("PROCESSED_DOCUMENTS_DIR", "./data/processed")

# Ensure directories exist
Path(CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)
Path(RAW_DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
Path(PROCESSED_DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)

# Embedding Model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-vision-preview")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))

# Chunking Configuration
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200