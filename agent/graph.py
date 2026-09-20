"""LangGraph workflow definition"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    parse_resume_node,
    analyze_job_node,
    match_skills_node,
    retrieve_knowledge_node,
    generate_ai_recommendations_node,  # NEW
    generate_report_node
)

def create_agent_graph():
    """Create the LangGraph workflow"""
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("analyze_job", analyze_job_node)
    workflow.add_node("match_skills", match_skills_node)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
    workflow.add_node("ai_recommendations", generate_ai_recommendations_node)  # NEW
    workflow.add_node("generate_report", generate_report_node)
    
    # Define edges (workflow)
    workflow.set_entry_point("parse_resume")
    workflow.add_edge("parse_resume", "analyze_job")
    workflow.add_edge("analyze_job", "match_skills")
    workflow.add_edge("match_skills", "retrieve_knowledge")
    workflow.add_edge("retrieve_knowledge", "ai_recommendations")  # NEW
    workflow.add_edge("ai_recommendations", "generate_report")  # UPDATED
    workflow.add_edge("generate_report", END)
    
    # Compile
    app = workflow.compile()
    
    return app