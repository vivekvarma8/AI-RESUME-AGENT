"""LangGraph nodes - each step in the workflow"""

from agent.state import AgentState
from agent.tools import AgentTools
import logging

logger = logging.getLogger(__name__)

tools = AgentTools()

def parse_resume_node(state: AgentState) -> AgentState:
    """Node: Extract skills from resume"""
    logger.info("📄 Parsing resume...")
    
    try:
        resume_skills = tools.extract_skills(state['resume_text'])
        state['resume_skills'] = resume_skills
        state['current_step'] = 'parse_resume'
        logger.info(f"Found {len(resume_skills)} resume skills")
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        state['resume_skills'] = []
        state['errors'].append(f"Resume parsing: {str(e)}")
    
    return state

def analyze_job_node(state: AgentState) -> AgentState:
    """Node: Extract skills from job description"""
    logger.info("💼 Analyzing job description...")
    
    try:
        job_skills = tools.extract_skills(state['job_description'])
        state['job_skills'] = job_skills
        state['current_step'] = 'analyze_job'
        logger.info(f"Found {len(job_skills)} job skills")
    except Exception as e:
        logger.error(f"Job analysis error: {e}")
        state['job_skills'] = []
        state['errors'].append(f"Job analysis: {str(e)}")
    
    return state

def match_skills_node(state: AgentState) -> AgentState:
    """Node: Compare skills and find gaps"""
    logger.info("🔍 Matching skills...")
    
    try:
        match_results = tools.match_skills(
            state['resume_text'],
            state['job_description']
        )
        
        state['matched_skills'] = match_results['matched_skills']
        state['missing_skills'] = match_results['missing_skills']
        state['match_percentage'] = match_results['match_percentage']
        state['current_step'] = 'match_skills'
        
        logger.info(f"Match: {match_results['match_percentage']}%")
    except Exception as e:
        logger.error(f"Skill matching error: {e}")
        state['matched_skills'] = []
        state['missing_skills'] = []
        state['match_percentage'] = 0.0
        state['errors'].append(f"Skill matching: {str(e)}")
    
    return state

def retrieve_knowledge_node(state: AgentState) -> AgentState:
    """Node: Search RAG knowledge base"""
    logger.info("📚 Retrieving career knowledge...")
    
    try:
        query = f"Skills and career path for: {state['job_description'][:200]}"
        rag_context = tools.search_knowledge(query, n_results=3)
        state['rag_context'] = rag_context
        state['current_step'] = 'retrieve_knowledge'
        logger.info(f"Retrieved {len(rag_context)} chars of context")
    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        state['rag_context'] = "Knowledge retrieval unavailable."
        state['errors'].append(f"RAG: {str(e)}")
    
    return state

def generate_ai_recommendations_node(state: AgentState) -> AgentState:
    """Node: Generate AI-powered recommendations using Gemini"""
    logger.info("🤖 Generating AI recommendations...")
    
    try:
        from google import genai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("No Gemini API key found")
            state['recommendations'] = "AI recommendations unavailable - API key not configured."
            state['current_step'] = 'ai_recommendations'
            return state
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an expert career advisor. Analyze this skill match and provide actionable recommendations.

MATCHED SKILLS ({len(state['matched_skills'])}):
{', '.join(state['matched_skills'])}

MISSING SKILLS ({len(state['missing_skills'])}):
{', '.join(state['missing_skills'])}

MATCH PERCENTAGE: {state['match_percentage']}%

CAREER KNOWLEDGE:
{state['rag_context'][:800]}

Provide:

1. **QUICK ASSESSMENT** (2-3 sentences)
   - Should they apply now?
   - Overall readiness level

2. **TOP 3 PRIORITY SKILLS TO LEARN**
   - For each missing skill that matters most:
     * Why it's important
     * How to learn it (specific resource)
     * Time estimate

3. **RESUME IMPROVEMENTS** (3 specific tips)
   - How to better showcase existing skills
   - Keywords to add

4. **INTERVIEW PREP** (2-3 key topics)

Keep it concise, practical, and encouraging.
"""

        # Try multiple models
        models = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-flash-latest"]
        
        recommendations = ""
        for model_name in models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                recommendations = response.text
                logger.info(f"✅ Got recommendations from {model_name}")
                break
            except Exception as e:
                logger.warning(f"{model_name} failed: {str(e)[:50]}")
                continue
        
        if not recommendations:
            match_pct = state['match_percentage']
            recommendations = f"""
⚠️ AI recommendations temporarily unavailable.

**Based on your {match_pct}% match:**

**Status**: {"Good match! Consider applying." if match_pct >= 60 else "Learn more skills before applying."}

**Priority Missing Skills**:
{chr(10).join(f'• {skill}' for skill in state['missing_skills'][:3])}

**Your Strengths**:
{chr(10).join(f'• {skill}' for skill in state['matched_skills'][:5])}
"""
        
        state['recommendations'] = recommendations
        
    except Exception as e:
        logger.error(f"AI recommendation error: {e}")
        state['recommendations'] = f"AI recommendations unavailable: {str(e)}"
        state['errors'].append(f"AI recommendations: {str(e)}")
    
    state['current_step'] = 'ai_recommendations'
    return state

def generate_report_node(state: AgentState) -> AgentState:
    """Node: Generate final report"""
    logger.info("📝 Generating final report...")
    
    try:
        report = f"""
{'='*70}
📊 RESUME & JOB MATCH ANALYSIS
{'='*70}

📈 OVERALL MATCH: {state['match_percentage']}%

✅ MATCHED SKILLS ({len(state['matched_skills'])}):
{chr(10).join(f'   • {skill}' for skill in state['matched_skills'][:10])}

❌ MISSING SKILLS ({len(state['missing_skills'])}):
{chr(10).join(f'   • {skill}' for skill in state['missing_skills'][:10])}

📚 RELEVANT CAREER KNOWLEDGE:
{state.get('rag_context', 'No context available')[:500]}...

{'='*70}
"""
        
        state['final_report'] = report
        state['current_step'] = 'complete'
        logger.info("✅ Report generated")
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        state['final_report'] = f"Report generation failed: {str(e)}"
        state['errors'].append(f"Report: {str(e)}")
    
    return state