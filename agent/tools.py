"""Tools that the agent can use"""

from parsers.skill_matcher import SkillMatcher
from rag.vector_store import CareerKnowledgeBase

class AgentTools:
    """Collection of tools for the resume agent"""
    
    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self.knowledge_base = CareerKnowledgeBase()
        # Build index on initialization
        print("Building knowledge base index...")
        self.knowledge_base.build_index()
    
    def extract_skills(self, text: str) -> list:
        """Extract skills from text"""
        skills = self.skill_matcher.extract_skills(text)
        return sorted(list(skills))
    
    def match_skills(self, resume_text: str, job_text: str) -> dict:
        """Compare resume and job skills"""
        return self.skill_matcher.match_skills(resume_text, job_text)
    
    def search_knowledge(self, query: str, n_results: int = 3) -> str:
        """Search career knowledge base"""
        return self.knowledge_base.get_relevant_context(query, n_results)
    
    def calculate_match_percentage(self, matched: int, total: int) -> float:
        """Calculate skill match percentage"""
        if total == 0:
            return 0.0
        return round((matched / total) * 100, 1)