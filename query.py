"""
Query script for testing the RAG system.
"""

import sys
from src.graph.workflow import run_query


def main():
    """Run interactive query loop."""
    print("\n" + "="*60)
    print("FINANCIAL COMPLIANCE RAG SYSTEM")
    print("="*60)
    print("\nCommands:")
    print("  - Type your question")
    print("  - Type 'quit' or 'exit' to stop")
    print("="*60 + "\n")
    
    while True:
        # Get user input
        query = input("\nYour question: ").strip()
        
        if not query:
            continue
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Process query
        result = run_query(query)
        
        # Display response
        print(f"\n{'='*60}")
        print("RESPONSE:")
        print(f"{'='*60}")
        print(result['response'])
        
        # Display citations
        if result['citations']:
            print(f"\n{'='*60}")
            print("CITATIONS:")
            print(f"{'='*60}")
            for citation in result['citations']:
                print(f"[Document {citation['index']}]:")
                print(f"  File: {citation['filename']}")
                print(f"  Chunk: {citation['chunk_index']}")
                if citation['compliance_categories']:
                    print(f"  Categories: {', '.join(citation['compliance_categories'])}")
        
        print(f"\n{'='*60}")
        print(f"Query Type: {result['query_type']}")
        print(f"Documents Retrieved: {result['documents_retrieved']}")
        print(f"Iterations: {result['iterations']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        result = run_query(query)
        print(f"\nResponse: {result['response']}\n")
    else:
        # Interactive mode
        main()
