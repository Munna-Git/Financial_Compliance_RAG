
# **Financial Compliance RAG System**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An advanced, production-ready Retrieval-Augmented Generation (RAG) system for financial compliance documents with multi-agent orchestration, multi-modal support, and interactive web interface.

---

## **Overview**

**Financial Compliance RAG** is a full-stack AI application that helps compliance officers, auditors, and risk analysts instantly find accurate information from complex regulatory documents. The system combines:

- **Agentic AI Architecture**: Multi-agent system using LangGraph with ReAct pattern
- **Multi-Modal Processing**: Handles both text and images/charts in PDFs
- **Local & Secure**: Runs entirely on your machine using Ollama
- **Production-Ready API**: FastAPI backend with async ingestion
- **Modern UI**: React frontend with real-time feedback and citations

**Why This Matters**: In financial compliance, accuracy and auditability are critical. This system provides transparent, cited answers from authoritative documents, essential for regulatory compliance, audits, and risk management.

---

## **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (React)                   │
│  - Query Input  - Document Upload  - Citation Display       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST (Axios)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                       │
│  /api/query  │  /api/ingest  │  /health  │  /api/stats      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENTIC RAG WORKFLOW (LangGraph)               │
│                                                             │
│  ┌──────────────┐      ┌─────────────────────┐              │
│  │ Router Agent │─────→│ Retrieval Agent     │              │
│  │ (Classify)   │      │ (ReAct Pattern)     │              │
│  └──────────────┘      └──────────┬──────────┘              │
│                                   │                         │
└───────────────────────────────────┼─────────────────────────┘
                                    │
                      ┌─────────────┴──────────────┐
                      ▼                            ▼
        ┌─────────────────────┐      ┌──────────────────────┐
        │  Vector Store       │      │                      │
        │  (ChromaDB)         │      │  LLM (Ollama)        │
        │  - Embeddings       │      │ - Phi-3 Mini         │
        │  - Metadata         │      │                      │
        └─────────────────────┘      └──────────────────────┘
                      ▲
                      │
        ┌─────────────┴──────────────┐
        │  INGESTION PIPELINE        │
        │  1. PDF Loading (PyPDF2)   │
        │  2. Image Detection        │
        │  3. BLIP Captioning        │
        │  4. Semantic Chunking      │
        │  5. Metadata Extraction    │
        │  6. Embedding Generation   │
        └────────────────────────────┘
```

---
## Tech Stack

- **Backend:** Python 3.11+, FastAPI, ChromaDB, sentence-transformers, PyPDF2, BLIP (transformers/torch for vision), LangGraph, Ollama.
- **Frontend:** React (Vite), Axios, react-hot-toast, CSS-in-JS.


## **Key Features**

### **Agentic Architecture**
- **Router Agent**: Classifies queries (compliance, risk, general, greeting)
- **Retrieval Agent**: Uses ReAct pattern (Think-Act-Observe) for intelligent retrieval
- **Iterative Refinement**: Dynamically refines search until sufficient context is gathered

### **Multi-Modal Document Processing**
- **Smart Image Detection**: Only processes pages with actual images/charts
- **BLIP Vision Model**: Generates descriptive captions for charts and diagrams
- **Structured Data**: Extracts tables and converts to markdown format
- **Optimized Performance**: Processes only relevant pages (10-20x faster than brute-force)

### **Advanced Retrieval**
- **Semantic Chunking**: Context-aware splitting with sentence boundaries
- **Hierarchical Metadata**: Document type, compliance category, section headers
- **Hybrid Search**: Dense vector search with metadata filtering
- **Reranking**: Prioritizes most relevant results before LLM synthesis

### **Modern Web Interface**
- **Responsive Design**: Full-width, gradient UI with clear sections
- **Real-time Feedback**: Toast notifications for all operations
- **Citation Display**: Every answer shows source documents with page/chunk references
- **Async Upload**: Non-blocking document ingestion with background processing

### **Privacy & Security**
- **100% Local**: All processing happens on your machine
- **No Data Leakage**: Documents never leave your infrastructure
- **Configurable**: Easy to deploy behind enterprise firewalls

---

## **Prerequisites**

- **Python**: 3.11 (recommended for compatibility)
- **RAM**: 8GB minimum (16GB recommended)
- **Ollama**: Installed and running
- **Node.js**: 16+ (for React frontend)
- **OS**: Windows, Linux, or macOS

---

## **Installation & Setup**

### 1. Clone the Repository

```
git clone https://github.com/Munna-Git/Financial_Compliance_RAG.git
cd Financial_Compliance_RAG
```

### 2. Backend Setup (Python)

```
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install and Configure Ollama

```
# Install Ollama from https://ollama.com

# Pull the LLM model
ollama pull phi3:mini

# Or for lower memory usage:
ollama pull tinyllama
```

### 4. Configure Environment Variables

Edit `.env` file:

```
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Vector Store
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
COLLECTION_NAME=financial_compliance

# Multi-Modal Settings
MAX_IMAGE_PAGES=50
MIN_IMAGE_SIZE=10000
ENABLE_IMAGE_FILTERING=true
```

### 5. Frontend Setup (React)

```
cd frontend
npm install
```

---

## **Usage**

### Step 1: Ingest Documents

Place your compliance PDFs in `data/raw/` directory, then run:

```
# Basic text-only ingestion
python ingest.py data/raw/

# With multi-modal support (images/charts)
python ingest.py data/raw/ --multimodal

# Reset collection and reingest
python ingest.py data/raw/ --reset --multimodal
```

**Example Output:**
```
============================================================
DOCUMENT INGESTION PIPELINE
Multi-Modal Mode: ENABLED
============================================================

Step 1: Loading documents...
[1/3] Processing: Basel_III_Guidelines.pdf
  Total pages: 85
  ✓ Extracted text from 85 pages
  Scanning for images/charts...
  Detected 12 pages with images out of 85 total pages
  Processing 12 pages with images...
  ✓ Added 12 image descriptions

✓ Loaded 3 document(s) with 312 total elements

Step 2: Chunking documents...
✓ Created 1,847 total chunks

Step 3: Extracting metadata...
✓ Extracted metadata for 1,847 chunks

Step 4: Initializing vector store...
✓ ChromaDB initialized

Step 5: Adding documents to vector store...
✓ Successfully added 1,847 documents

============================================================
INGESTION COMPLETE
============================================================
Total documents in collection: 1,847
  Text chunks: 1,835
  Image/chart chunks: 12
============================================================
```

### Step 2: Start the Backend API

```
python api.py
```

API will be available at: `http://127.0.0.1:8000`

Interactive docs: `http://127.0.0.1:8000/docs`

### Step 3: Start the Frontend

```
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## **Using the System**

### Web Interface

1. **Ask Questions**: Type financial compliance questions in the query box
2. **Upload Documents**: Drag and drop or select PDFs to ingest
3. **View Citations**: Every answer shows source documents with references

**Example Queries:**
- "What are the Basel III capital requirements?"
- "Explain KYC customer due diligence procedures"
- "What documents are required for AML compliance?"
- "Describe the liquidity coverage ratio under Basel III"

### API Endpoints

**Query the RAG system:**
```
curl -X POST "http://127.0.0.1:8000/api/query" ^
  -H "Content-Type: application/json" ^
  -d '{"query": "What are Basel III liquidity guidelines?"}'
```

**Upload and ingest document:**
```
curl -X POST "http://127.0.0.1:8000/api/ingest" ^
  -F "file=@data/raw/compliance_policy.pdf" ^
  -F "multimodal=true"
```

**Check system health:**
```
curl http://127.0.0.1:8000/health
```

**Get statistics:**
```
curl http://127.0.0.1:8000/api/stats
```

---

## **Project Structure**

```
financial-compliance-rag/
├── data/
│   ├── raw/                    # Original PDF documents
│   ├── processed/              # Processed chunks and images
│   └── chroma_db/              # Vector database storage
├── src/
│   ├── config/
│   │   └── settings.py         # Centralized configuration
│   ├── ingestion/
│   │   ├── document_loader.py  # PDF parsing with multi-modal
│   │   ├── chunker.py          # Semantic chunking
│   │   ├── metadata_extractor.py # Metadata extraction
│   │   └── image_processor.py  # BLIP image captioning
│   ├── vectorstore/
│   │   ├── embeddings.py       # Sentence transformer embeddings
│   │   └── chroma_manager.py   # ChromaDB operations
│   ├── agents/
│   │   ├── state.py            # Shared agent state
│   │   ├── router_agent.py     # Query classification
│   │   └── retrieval_agent.py  # ReAct retrieval
│   ├── tools/
│   │   ├── retrieval_tools.py  # Search and reranking
│   │   └── synthesis_tools.py  # Response generation
│   └── graph/
│       └── workflow.py         # LangGraph orchestration
├── frontend/
│   └── src/
│       └── App.jsx             # React application
├── api.py                      # FastAPI server
├── ingest.py                   # Document ingestion script
├── query.py                    # CLI query interface
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## **Configuration Options**

### Memory Optimization (8GB RAM)

**In `.env`:**
```
OLLAMA_MODEL=tinyllama          # Use smallest model
MAX_IMAGE_PAGES=20              # Limit image processing
CHUNK_SIZE=512                  # Smaller chunks
```

**System-level:**
- Close unnecessary applications
- Increase Windows virtual memory (pagefile)
- Monitor Task Manager during operation

### Performance Tuning

**For faster ingestion:**
```
MAX_IMAGE_PAGES=10              # Process fewer image pages
ENABLE_IMAGE_FILTERING=true     # Skip small images/logos
```

**For better accuracy:**
```
TOP_K_RETRIEVAL=15              # Retrieve more documents
TOP_K_FINAL=5                   # Use more context
MAX_ITERATIONS=5                # Allow more ReAct iterations
```

---

## **Domain: Financial Compliance**

This system is optimized for financial compliance documents including:

- **Regulatory Frameworks**: Basel III, Dodd-Frank, GDPR, SOX
- **Compliance Policies**: AML (Anti-Money Laundering), KYC (Know Your Customer)
- **Industry Standards**: FCRA, TILA, RESPA
- **Audit Documents**: Compliance reports, risk assessments
- **Internal Policies**: Credit risk, operational risk, governance

### Supported Compliance Categories

- **AML**: Anti-Money Laundering regulations
- **KYC**: Customer identification and verification
- **Basel III**: Banking capital and liquidity requirements
- **GDPR**: Data protection and privacy
- **SOX**: Financial reporting and internal controls
- **FCRA**: Fair credit reporting standards
- **TILA**: Truth in lending disclosures
- **RESPA**: Real estate settlement procedures

---

## **Testing**

### Test with Sample Documents

1. Download sample compliance PDFs:
   - [RBI Basel III Guidelines](https://www.rbi.org.in/)
   - [Sample KYC Policy](https://www.ecofy.co.in/assets/policies/KYC-and-AML-policy.pdf)

2. Place in `data/raw/` and run ingestion

3. Test queries:
```
python query.py "What are the minimum CET1 capital requirements?"
```

---

## 🚀 Future Enhancements

- [ ] **Advanced Reranking**: Cross-encoder models for improved precision
- [ ] **Hybrid Search**: Combine semantic + keyword (BM25) retrieval
- [ ] **Query Decomposition**: Break complex queries into sub-questions
- [ ] **Graph RAG**: Knowledge graph integration for entity relationships
- [ ] **Streaming Responses**: Real-time token streaming to frontend
- [ ] **Multi-language Support**: Handle documents in multiple languages
- [ ] **Fine-tuned Models**: Domain-specific LLM training
- [ ] **Authentication**: OAuth/SSO for enterprise deployment
- [ ] **Audit Logging**: Track all queries and responses for compliance
- [ ] **Batch Processing**: Queue-based ingestion with Celery/Redis

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Munna**
- GitHub: [@Munna-Git](https://github.com/Munna-Git)
- LinkedIn: [[Contact through LinkedIn](https://www.linkedin.com/in/munna-a4ab07253/)]

---

