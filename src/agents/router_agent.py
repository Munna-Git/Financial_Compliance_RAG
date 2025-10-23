"""
Router agent for query classification and routing.
"""

from typing import Dict
from src.agents.state import AgentState
from src.config.settings import settings


class RouterAgent:
    """Routes queries to appropriate agents based on classification."""
    
    def __init__(self):
        """Initialize router agent."""
        self.greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        self.compliance_keywords = ['regulation', 'compliance', 'requirement', 'rule', 'policy']
        self.risk_keywords = ['risk', 'threat', 'vulnerability', 'exposure']
    
    def route(self, state: AgentState) -> AgentState:
        """
        Classify query and determine routing.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with classification
        """
        query = state['query'].lower()
        
        # Check for greeting
        if any(keyword in query for keyword in self.greeting_keywords):
            state['query_type'] = 'greeting'
            state['requires_retrieval'] = False
            state['agent_thoughts'].append("Query classified as greeting - no retrieval needed")
            return state
        
        # Check for compliance query
        if any(keyword in query for keyword in self.compliance_keywords):
            state['query_type'] = 'compliance'
            state['requires_retrieval'] = True
            state['agent_thoughts'].append("Query classified as compliance question - retrieval required")
            return state
        
        # Check for risk query
        if any(keyword in query for keyword in self.risk_keywords):
            state['query_type'] = 'risk'
            state['requires_retrieval'] = True
            state['agent_thoughts'].append("Query classified as risk analysis - retrieval required")
            return state
        
        # Default to general query
        state['query_type'] = 'general'
        state['requires_retrieval'] = True
        state['agent_thoughts'].append("Query classified as general - retrieval required")
        
        return state


def router_node(state: AgentState) -> AgentState:
    """LangGraph node for routing."""
    router = RouterAgent()
    return router.route(state)
