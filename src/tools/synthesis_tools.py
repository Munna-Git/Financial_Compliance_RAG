"""
Tools for response generation and synthesis.
"""

from typing import List, Dict, Tuple
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import settings


def generate_response(
    query: str,
    documents: List[Dict],
    query_type: str = 'general'
) -> Tuple[str, List[Dict]]:
    """
    Generate response using retrieved documents.
    
    Args:
        query: User query
        documents: Retrieved documents
        query_type: Type of query (compliance, risk, general, greeting)
        
    Returns:
        Tuple of (response text, citations list)
    """
    # Handle greeting separately
    if query_type == 'greeting':
        response = "Hello! I'm your Financial Compliance Assistant. I can help you with questions about regulations, compliance requirements, risk assessment, and financial policies. How can I assist you today?"
        return response, []
    
    # Handle case with no documents
    if not documents:
        response = "I apologize, but I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing your query or ask about a different topic."
        return response, []
    
    # Prepare context from documents
    context_parts = []
    citations = []
    
    for idx, doc in enumerate(documents, 1):
        context_parts.append(f"[Document {idx}]:\n{doc['text']}\n")
        
        # Parse comma-separated string back to list for display
        categories_str = doc['metadata'].get('compliance_categories', '')
        categories_list = categories_str.split(',') if categories_str else []
        
        citations.append({
            'index': idx,
            'filename': doc['metadata'].get('filename', 'unknown'),
            'chunk_index': doc['metadata'].get('chunk_index', 0),
            'compliance_categories': categories_list  # Now a list again
        })
    
    context = "\n".join(context_parts)
    
    # Create prompt based on query type
    if query_type == 'compliance':
        system_message = """You are a Financial Compliance Expert. Answer the user's compliance-related question based ONLY on the provided documents.

Instructions:
- Provide accurate, detailed answers with specific references
- Cite document numbers in your response [Document X]
- If the documents don't contain enough information, say so
- Focus on regulatory requirements and compliance obligations
- Be precise and professional"""

    elif query_type == 'risk':
        system_message = """You are a Risk Analysis Expert. Answer the user's risk-related question based ONLY on the provided documents.

Instructions:
- Identify and explain risks clearly
- Provide mitigation strategies if available in the documents
- Cite document numbers in your response [Document X]
- Be analytical and objective
- If the documents don't contain enough information, say so"""

    else:  # general
        system_message = """You are a Financial Compliance Assistant. Answer the user's question based ONLY on the provided documents.

Instructions:
- Provide clear, accurate answers
- Cite document numbers in your response [Document X]
- If the documents don't contain enough information, say so
- Be helpful and professional"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", """Context from documents:
{context}

User Question: {query}

Please provide a comprehensive answer based on the documents above. Remember to cite specific documents using [Document X] notation.""")
    ])
    
    # Initialize LLM
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE
    )
    
    # Generate response
    chain = prompt | llm
    
    print("Generating response with LLM...")
    result = chain.invoke({
        "context": context,
        "query": query
    })
    
    response = result.content
    
    print("✓ Response generated")
    
    return response, citations
