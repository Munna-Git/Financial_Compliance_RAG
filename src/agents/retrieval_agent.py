"""
Retrieval agent implementing ReAct pattern.
Handles document retrieval and response synthesis.
"""

from typing import Dict, List
from src.agents.state import AgentState
from src.vectorstore.chroma_manager import get_chroma_manager
from src.tools.retrieval_tools import retrieve_documents, rerank_documents
from src.tools.synthesis_tools import generate_response
from src.config.settings import settings


class RetrievalAgent:
    """Agent that retrieves and synthesizes information using ReAct pattern."""
    
    def __init__(self):
        """Initialize retrieval agent."""
        self.chroma_manager = get_chroma_manager()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process query using ReAct pattern: Think -> Act -> Observe.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with retrieval results
        """
        # THINK: Analyze what we need
        state['agent_thoughts'].append(
            f"Iteration {state['iteration']}: Analyzing query '{state['query']}'"
        )
        
        # ACT: Perform retrieval
        if not state['retrieved_docs']:
            state['agent_thoughts'].append("No documents retrieved yet - performing semantic search")
            
            # Retrieve documents
            retrieved = retrieve_documents(
                query=state['query'],
                chroma_manager=self.chroma_manager,
                top_k=settings.TOP_K_RETRIEVAL
            )
            
            # Rerank documents
            if retrieved:
                state['agent_thoughts'].append(f"Retrieved {len(retrieved)} documents - reranking")
                reranked = rerank_documents(
                    query=state['query'],
                    documents=retrieved,
                    top_k=settings.TOP_K_FINAL
                )
                state['retrieved_docs'] = reranked
            else:
                state['retrieved_docs'] = []
        
        # OBSERVE: Check if we have sufficient information
        if len(state['retrieved_docs']) >= settings.TOP_K_FINAL:
            state['agent_thoughts'].append(
                f"Sufficient documents retrieved ({len(state['retrieved_docs'])}) - generating response"
            )
            
            # Generate response with citations
            response, citations = generate_response(
                query=state['query'],
                documents=state['retrieved_docs'],
                query_type=state['query_type']
            )
            
            state['response'] = response
            state['citations'] = citations
            
        elif state['iteration'] >= state['max_iterations']:
            state['agent_thoughts'].append("Max iterations reached - generating response with available docs")
            
            # Generate response even with limited docs
            response, citations = generate_response(
                query=state['query'],
                documents=state['retrieved_docs'],
                query_type=state['query_type']
            )
            
            state['response'] = response
            state['citations'] = citations
        else:
            state['agent_thoughts'].append("Insufficient documents - will iterate")
            state['iteration'] += 1
        
        return state


def retrieval_node(state: AgentState) -> AgentState:
    """LangGraph node for retrieval."""
    agent = RetrievalAgent()
    return agent.process(state)
