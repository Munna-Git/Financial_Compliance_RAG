"""
LangGraph workflow orchestrating the multi-agent RAG system.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.router_agent import router_node
from src.agents.retrieval_agent import retrieval_node
from src.config.settings import settings


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for agentic RAG.
    
    Returns:
        Compiled StateGraph workflow
    """
    # Initialize workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieval", retrieval_node)
    
    # Define routing logic
    def should_retrieve(state: AgentState) -> Literal["retrieval", "end"]:
        """Determine if retrieval is needed."""
        if state['requires_retrieval']:
            return "retrieval"
        else:
            # Generate direct response for greetings
            state['response'] = "Hello! I'm your Financial Compliance Assistant. How can I help you today?"
            return "end"
    
    def should_continue(state: AgentState) -> Literal["retrieval", "end"]:
        """Determine if we should continue iterating."""
        if state.get('response'):
            return "end"
        elif state['iteration'] >= state['max_iterations']:
            return "end"
        else:
            return "retrieval"
    
    # Add edges
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        should_retrieve,
        {
            "retrieval": "retrieval",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "retrieval",
        should_continue,
        {
            "retrieval": "retrieval",
            "end": END
        }
    )
    
    # Compile workflow
    app = workflow.compile()
    
    return app


def run_query(query: str) -> dict:
    """
    Run a query through the agentic RAG workflow.
    
    Args:
        query: User query string
        
    Returns:
        Dictionary with response and metadata
    """
    # Create workflow
    app = create_workflow()
    
    # Initialize state
    initial_state = {
        'query': query,
        'query_type': None,
        'requires_retrieval': True,
        'retrieved_docs': [],
        'agent_thoughts': [],
        'iteration': 1,
        'max_iterations': settings.MAX_ITERATIONS,
        'response': None,
        'citations': [],
        'error': None
    }
    
    # Run workflow
    print(f"\n{'='*60}")
    print(f"Processing query: {query}")
    print(f"{'='*60}\n")
    
    try:
        final_state = app.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print("AGENT REASONING:")
        for thought in final_state.get('agent_thoughts', []):
            print(f"  - {thought}")
        print(f"{'='*60}\n")
        
        return {
            'query': query,
            'response': final_state.get('response', 'No response generated'),
            'citations': final_state.get('citations', []),
            'query_type': final_state.get('query_type'),
            'documents_retrieved': len(final_state.get('retrieved_docs', [])),
            'iterations': final_state.get('iteration', 0),
            'agent_thoughts': final_state.get('agent_thoughts', [])
        }
        
    except Exception as e:
        print(f"Error in workflow: {e}")
        return {
            'query': query,
            'response': f"Error processing query: {str(e)}",
            'citations': [],
            'error': str(e)
        }
