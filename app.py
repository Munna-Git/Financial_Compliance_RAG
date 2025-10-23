"""
Main application entry point for the Financial Compliance RAG system.
Simple FastAPI-like interface (can be extended to actual FastAPI).
"""

from src.graph.workflow import run_query
from src.vectorstore.chroma_manager import get_chroma_manager
from src.config.settings import settings


def main():
    """Main application function."""
    print("\n" + "="*60)
    print("FINANCIAL COMPLIANCE AGENTIC RAG SYSTEM")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  LLM Model: {settings.OLLAMA_MODEL}")
    print(f"  Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"  Vector Store: ChromaDB")
    print(f"  Collection: {settings.COLLECTION_NAME}")
    print("="*60 + "\n")
    
    # Check if collection has documents
    try:
        chroma_manager = get_chroma_manager()
        doc_count = chroma_manager.get_count()
        
        if doc_count == 0:
            print("⚠️  WARNING: No documents in the vector store!")
            print("   Please run: python ingest.py data/raw/\n")
            return
        
        print(f"✓ Vector store initialized with {doc_count} documents\n")
        
    except Exception as e:
        print(f"Error initializing system: {e}\n")
        return
    
    # Run interactive query loop
    print("Starting interactive query mode...")
    print("Type your questions or 'quit' to exit.\n")
    
    while True:
        try:
            query = input("\n📝 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Process query through agentic workflow
            result = run_query(query)
            
            # Display response
            print(f"\n{'='*60}")
            print("🤖 RESPONSE:")
            print(f"{'='*60}")
            print(result['response'])
            
            # Display citations if available
            if result['citations']:
                print(f"\n📚 CITATIONS:")
                for citation in result['citations']:
                    print(f"  [{citation['index']}] {citation['filename']} (chunk {citation['chunk_index']})")
                    if citation['compliance_categories']:
                        print(f"      Categories: {', '.join(citation['compliance_categories'])}")
            
            print(f"\n📊 METADATA:")
            print(f"  Query Type: {result['query_type']}")
            print(f"  Documents Retrieved: {result['documents_retrieved']}")
            print(f"  Iterations: {result['iterations']}")
            print(f"{'='*60}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
