from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    """State that flows through the LangGraph workflow"""
    
    # Input
    resume_text: str
    job_description: str
    
    # Extracted information
    resume_skills: List[str]
    job_skills: List[str]
    
    # Analysis results
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    
    # RAG context
    rag_context: str
    
    # Recommendations
    recommendations: str
    
    # Final output
    final_report: str
    
    # Metadata
    current_step: str
    errors: List[str]