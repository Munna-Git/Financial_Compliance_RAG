"""
Shared state definition for LangGraph agents.
"""

from typing import List, Dict, Optional, TypedDict, Annotated
from langgraph.graph import MessagesState
import operator


class AgentState(TypedDict):
    """State shared across all agents in the workflow."""
    
    # User query
    query: str
    
    # Query classification
    query_type: Optional[str]  # 'compliance', 'risk', 'general', 'greeting'
    requires_retrieval: bool
    
    # Retrieved documents
    retrieved_docs: List[Dict]
    
    # Agent reasoning
    agent_thoughts: Annotated[List[str], operator.add]  # Accumulate thoughts
    
    # Iteration tracking
    iteration: int
    max_iterations: int
    
    # Final response
    response: Optional[str]
    citations: List[Dict]
    
    # Error handling
    error: Optional[str]
