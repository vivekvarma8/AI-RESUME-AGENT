from typing import Dict, List, Set
import re

class SkillMatcher:
    """Matches resume skills against job requirements"""
    
    def __init__(self):
        # Common skill variations
        self.skill_aliases = {
            'python': ['python', 'python3'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'docker': ['docker', 'containers', 'containerization'],
            'aws': ['aws', 'amazon web services'],
            'sql': ['sql', 'postgresql', 'postgres', 'mysql'],
            'react': ['react', 'reactjs', 'react.js'],
            'git': ['git', 'github', 'gitlab'],
        }
    
    def extract_skills(self, text: str) -> Set[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        skills = set()
        
        # Common programming languages
        languages = ['python', 'javascript', 'java', 'sql', 'typescript', 
                    'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift']
        
        # Frameworks
        frameworks = ['django', 'flask', 'react', 'angular', 'vue', 
                     'node.js', 'express', 'spring', 'fastapi']
        
        # Tools and technologies
        tools = ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git',
                'jenkins', 'terraform', 'ansible', 'mongodb', 'postgresql',
                'redis', 'kafka', 'rabbitmq', 'graphql', 'rest', 'api']
        
        # Combine all skills
        all_skills = languages + frameworks + tools
        
        for skill in all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.add(skill.lower())
        
        return skills
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill names"""
        skill_lower = skill.lower().strip()
        
        # Check aliases
        for canonical, aliases in self.skill_aliases.items():
            if skill_lower in aliases:
                return canonical
        
        return skill_lower
    
    def match_skills(self, resume_text: str, job_text: str) -> Dict:
        """
        Compare resume skills with job requirements
        Returns detailed matching analysis
        """
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_text)
        
        # Normalize skills
        resume_skills_normalized = {self.normalize_skill(s) for s in resume_skills}
        job_skills_normalized = {self.normalize_skill(s) for s in job_skills}
        
        # Find matches and gaps
        matched_skills = resume_skills_normalized & job_skills_normalized
        missing_skills = job_skills_normalized - resume_skills_normalized
        extra_skills = resume_skills_normalized - job_skills_normalized
        
        # Calculate match percentage
        if len(job_skills_normalized) > 0:
            match_percentage = (len(matched_skills) / len(job_skills_normalized)) * 100
        else:
            match_percentage = 0
        
        return {
            'resume_skills': sorted(list(resume_skills_normalized)),
            'job_skills': sorted(list(job_skills_normalized)),
            'matched_skills': sorted(list(matched_skills)),
            'missing_skills': sorted(list(missing_skills)),
            'extra_skills': sorted(list(extra_skills)),
            'match_percentage': round(match_percentage, 1),
            'total_resume_skills': len(resume_skills_normalized),
            'total_job_skills': len(job_skills_normalized),
            'total_matched': len(matched_skills)
        }