"""Tools that the agent can use"""

from parsers.skill_matcher import SkillMatcher
import logging

logger = logging.getLogger(__name__)

class AgentTools:
    """Collection of tools for the resume agent"""
    
    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self._knowledge_base = None
        self._kb_initialized = False
    
    def _ensure_kb_loaded(self):
        """Lazy load knowledge base only when needed"""
        if not self._kb_initialized:
            try:
                logger.info("📚 Initializing knowledge base...")
                from rag.vector_store import CareerKnowledgeBase
                self._knowledge_base = CareerKnowledgeBase()
                self._knowledge_base.build_index()
                self._kb_initialized = True
                logger.info("✅ Knowledge base ready!")
            except Exception as e:
                logger.error(f"Failed to load knowledge base: {e}")
                self._kb_initialized = True  # Don't try again
                self._knowledge_base = None
    
    def extract_skills(self, text: str) -> list:
        """Extract skills from text"""
        try:
            skills = self.skill_matcher.extract_skills(text)
            return sorted(list(skills))
        except Exception as e:
            logger.error(f"Skill extraction error: {e}")
            return []
    
    def match_skills(self, resume_text: str, job_text: str) -> dict:
        """Compare resume and job skills"""
        try:
            return self.skill_matcher.match_skills(resume_text, job_text)
        except Exception as e:
            logger.error(f"Skill matching error: {e}")
            return {
                'resume_skills': [],
                'job_skills': [],
                'matched_skills': [],
                'missing_skills': [],
                'extra_skills': [],
                'match_percentage': 0.0,
                'total_resume_skills': 0,
                'total_job_skills': 0,
                'total_matched': 0
            }
    
    def search_knowledge(self, query: str, n_results: int = 3) -> str:
        """Search career knowledge base"""
        self._ensure_kb_loaded()
        
        if self._knowledge_base is None:
            return "Career knowledge temporarily unavailable."
        
        try:
            return self._knowledge_base.get_relevant_context(query, n_results)
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return "Career knowledge search failed."
    
    def calculate_match_percentage(self, matched: int, total: int) -> float:
        """Calculate skill match percentage"""
        if total == 0:
            return 0.0
        return round((matched / total) * 100, 1)