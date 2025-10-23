# Financial_Compliance_RAG

## Project Structure

```
financial-compliance-rag/
│
├── data/                          # Document storage
│   ├── raw/                       # Original PDFs
│   ├── processed/                 # Processed chunks with metadata
│   └── sample_docs/               # Test documents
│
├── src/                           # Main source code
│   ├── __init__.py
│   │
│   ├── config/                    # Configuration
│   │   ├── __init__.py
│   │   └── settings.py            # All config parameters
│   │
│   ├── ingestion/                 # Document processing
│   │   ├── __init__.py
│   │   ├── document_loader.py     # Load PDFs with unstructured
│   │   ├── chunker.py             # Semantic chunking logic
│   │   └── metadata_extractor.py  # Extract hierarchical metadata
│   │
│   ├── vectorstore/               # Vector database management
│   │   ├── __init__.py
│   │   ├── chroma_manager.py      # ChromaDB operations
│   │   └── embeddings.py          # Embedding generation
│   │
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py
│   │   ├── state.py               # Shared state definition
│   │   ├── router_agent.py        # Query classification
│   │   └── retrieval_agent.py     # Retrieval & synthesis
│   │
│   ├── tools/                     # Agent tools
│   │   ├── __init__.py
│   │   ├── retrieval_tools.py     # Hybrid search, reranking
│   │   └── synthesis_tools.py     # Response generation
│   │
│   └── graph/                     # LangGraph orchestration
│       ├── __init__.py
│       └── workflow.py            # Main agent workflow graph
│
├── app.py                         # Main application entry point
├── ingest.py                      # Script to process & index documents
├── query.py                       # Script to test queries
│
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── langgraph.json                 # LangGraph configuration (optional)
│
├── notebooks/                     # Jupyter notebooks for experimentation
│   └── exploration.ipynb
│
├── tests/                         # Unit tests
│   ├── test_chunker.py
│   └── test_retrieval.py
│
└── README.md                      # Project documentation
```
