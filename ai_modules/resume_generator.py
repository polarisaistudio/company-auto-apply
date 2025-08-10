# ai_modules/resume_generator.py
import json
import openai
from typing import Dict, List
import logging

from scrapers.company_scraper import JobPosting

class AIResumeGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        
    def customize_resume(self, base_resume: Dict, job_posting: JobPosting) -> Dict:
        """Customize resume for company-specific job posting"""
        
        prompt = self.create_company_resume_prompt(base_resume, job_posting)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional resume optimization expert specializing in company-specific applications. Customize resumes to highlight the most relevant experience and skills for specific companies and roles. Keep all information truthful and don't fabricate experience. Focus on aligning existing skills with company values and job requirements."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            customized_resume = json.loads(response.choices[0].message.content)
            
            # Validate and enhance the generated resume
            cleaned_resume = self.validate_and_enhance_resume(customized_resume, base_resume)
            
            self.logger.info(f"Successfully customized resume for {job_posting.title} at {job_posting.company}")
            return cleaned_resume
            
        except Exception as e:
            self.logger.error(f"Resume customization failed: {e}")
            return base_resume  # Return original resume as fallback
    
    def create_company_resume_prompt(self, base_resume: Dict, job_posting: JobPosting) -> str:
        """Create role-specific and company-specific resume optimization prompt"""
        
        # Determine role-specific focus based on resume template
        role_focus = self._get_role_specific_focus(base_resume)
        
        return f"""
        Please customize this {role_focus} resume for a specific company application:

        **Target Company:** {job_posting.company}
        **Position:** {job_posting.title}
        **Department:** {job_posting.department}
        **Location:** {job_posting.location}

        **Job Description:**
        {job_posting.description[:1200]}

        **Key Requirements:**
        {job_posting.requirements[:600]}

        **Current Resume:**
        {json.dumps(base_resume, indent=2, ensure_ascii=False)}

        **{role_focus.upper()} CUSTOMIZATION INSTRUCTIONS:**
        {self._get_role_specific_instructions(role_focus)}

        **Company-Specific Optimization:**
        1. **Company Alignment**: Incorporate knowledge about {job_posting.company}'s values, mission, and industry position
        2. **Role-Specific Optimization**: Reorganize experience to highlight the most relevant {role_focus.lower()} projects and achievements
        3. **Technical Keywords**: Naturally integrate relevant technical keywords from the job description
        4. **Skills Prioritization**: Reorder technical and soft skills to match job requirements and {role_focus.lower()} best practices
        5. **Professional Summary**: Craft a compelling summary that shows fit for this specific {role_focus.lower()} role at {job_posting.company}
        6. **Impact Metrics**: Emphasize quantifiable impacts that would appeal to {job_posting.company}'s business objectives
        7. **Cultural Fit**: Demonstrate alignment with {job_posting.company}'s engineering culture and values

        **Important Guidelines:**
        - Keep all information truthful - do not invent experience or skills
        - Maintain the original resume structure and formatting
        - Preserve all contact information exactly as provided
        - Focus on reordering, rewording, and emphasizing rather than adding new content
        - Ensure the customization feels natural and authentic
        - Highlight {role_focus.lower()}-specific achievements and technical expertise

        **Output Format:**
        Return the complete optimized resume in JSON format, maintaining the exact structure of the original.
        """
    
    def _get_role_specific_focus(self, resume: Dict) -> str:
        """Determine the role focus based on resume template"""
        
        target_roles = resume.get("target_roles", [])
        
        if any("AI" in role or "Machine Learning" in role for role in target_roles):
            return "AI ENGINEER"
        elif any("Cloud" in role or "DevOps" in role or "SRE" in role for role in target_roles):
            return "CLOUD ENGINEER"
        elif any("Data Scientist" in role or "Analytics" in role for role in target_roles):
            return "DATA SCIENTIST"
        else:
            return "SOFTWARE ENGINEER"
    
    def _get_role_specific_instructions(self, role_focus: str) -> str:
        """Get role-specific customization instructions"""
        
        instructions = {
            "AI ENGINEER": """
        1. **ML/AI Focus**: Prioritize machine learning, AI, and deep learning experience
        2. **Technical Stack**: Highlight Python, PyTorch/TensorFlow, transformers, and ML frameworks
        3. **Model Development**: Emphasize model training, deployment, and optimization experience
        4. **Data Pipeline**: Show experience with data preprocessing, feature engineering, and MLOps
        5. **Research Impact**: Highlight publications, research contributions, or novel AI implementations
        6. **Production Systems**: Demonstrate experience deploying AI/ML systems at scale
        7. **Domain Expertise**: Align with specific AI domains (NLP, computer vision, etc.) mentioned in job
            """,
            "CLOUD ENGINEER": """
        1. **Infrastructure Focus**: Prioritize cloud infrastructure, DevOps, and platform engineering experience
        2. **Cloud Platforms**: Highlight experience with AWS, GCP, Azure, and multi-cloud architectures
        3. **Automation**: Emphasize Infrastructure as Code, CI/CD pipelines, and automation frameworks
        4. **Monitoring & Reliability**: Show experience with monitoring, logging, and maintaining high availability
        5. **Containerization**: Highlight Docker, Kubernetes, and container orchestration experience
        6. **Security**: Demonstrate cloud security, compliance, and best practices knowledge
        7. **Scaling**: Show experience managing infrastructure for high-traffic applications
            """,
            "DATA SCIENTIST": """
        1. **Analytics Focus**: Prioritize data analysis, statistical modeling, and business intelligence experience
        2. **Statistical Methods**: Highlight expertise in statistics, hypothesis testing, and experimental design
        3. **Business Impact**: Emphasize how data insights drove business decisions and revenue
        4. **Visualization**: Show proficiency in data visualization and storytelling with data
        5. **Tools & Frameworks**: Highlight Python/R, SQL, Tableau, and analytics platforms
        6. **Domain Expertise**: Align with specific business domains (marketing analytics, product analytics, etc.)
        7. **Cross-functional**: Demonstrate ability to work with product, engineering, and business teams
            """,
            "SOFTWARE ENGINEER": """
        1. **Development Focus**: Prioritize software development, system design, and engineering experience
        2. **Technical Skills**: Highlight programming languages, frameworks, and development tools
        3. **System Design**: Show experience with scalable systems, APIs, and architecture
        4. **Code Quality**: Emphasize testing, code review, and engineering best practices
        5. **Collaboration**: Demonstrate teamwork, mentoring, and cross-functional collaboration
        6. **Problem Solving**: Highlight complex technical challenges and innovative solutions
        7. **Product Impact**: Show how technical contributions drove product success and user value
            """
        }
        
        return instructions.get(role_focus, instructions["SOFTWARE ENGINEER"])
    
    def validate_and_enhance_resume(self, ai_resume: Dict, original_resume: Dict) -> Dict:
        """Validate and enhance AI-generated resume"""
        
        # Ensure all required sections exist
        required_sections = ["personal_info", "summary", "experience", "skills", "education"]
        
        for section in required_sections:
            if section not in ai_resume:
                ai_resume[section] = original_resume.get(section, {})
        
        # Preserve original contact information (never let AI modify this)
        if "personal_info" in original_resume:
            ai_resume["personal_info"] = original_resume["personal_info"]
        
        # Validate experience section integrity
        if "experience" in ai_resume and "experience" in original_resume:
            self._validate_experience_section(ai_resume["experience"], original_resume["experience"])
        
        # Ensure education section is preserved
        if "education" in original_resume:
            ai_resume["education"] = original_resume["education"]
        
        # Validate skills section doesn't add non-existent skills
        if "skills" in ai_resume and "skills" in original_resume:
            ai_resume["skills"] = self._validate_skills_section(
                ai_resume["skills"], original_resume["skills"]
            )
        
        return ai_resume
    
    def _validate_experience_section(self, ai_experience: List[Dict], original_experience: List[Dict]):
        """Ensure experience section maintains integrity"""
        
        for ai_exp in ai_experience:
            # Find corresponding original experience
            original_exp = None
            for orig_exp in original_experience:
                if (orig_exp.get("company") == ai_exp.get("company") and 
                    orig_exp.get("title") == ai_exp.get("title")):
                    original_exp = orig_exp
                    break
            
            if original_exp:
                # Preserve critical fields that shouldn't change
                for field in ["start_date", "end_date", "company", "title"]:
                    if field in original_exp:
                        ai_exp[field] = original_exp[field]
    
    def _validate_skills_section(self, ai_skills: Dict, original_skills: Dict) -> Dict:
        """Validate that skills section doesn't add false skills"""
        
        validated_skills = {}
        
        for category, skills_list in ai_skills.items():
            if category in original_skills:
                # Only keep skills that exist in original or are reasonable variations
                original_skills_lower = [skill.lower() for skill in original_skills[category]]
                validated_list = []
                
                for skill in skills_list:
                    if (skill.lower() in original_skills_lower or
                        any(original_skill in skill.lower() or skill.lower() in original_skill 
                            for original_skill in original_skills_lower)):
                        validated_list.append(skill)
                
                validated_skills[category] = validated_list
            else:
                # If it's a new category, be very conservative
                validated_skills[category] = skills_list[:3]  # Limit to 3 skills max
        
        return validated_skills
    
    def generate_company_focused_summary(self, job_posting: JobPosting, experience: List[Dict]) -> str:
        """Generate a company-focused professional summary"""
        
        prompt = f"""
        Create a professional summary (2-3 sentences) for a candidate applying to {job_posting.company} for the {job_posting.title} position.

        **Company:** {job_posting.company}
        **Position:** {job_posting.title}
        **Key Requirements:** {job_posting.requirements[:400]}

        **Candidate Experience:**
        {json.dumps(experience[:3], indent=2, ensure_ascii=False)}

        **Requirements:**
        1. Show genuine interest in {job_posting.company} and their mission
        2. Highlight the most relevant experience for this specific role
        3. Use terminology and keywords from the job description
        4. Demonstrate understanding of the company's industry and challenges
        5. Keep it concise, powerful, and authentic
        6. Avoid generic statements that could apply to any company

        Focus on what makes this candidate a great fit specifically for {job_posting.company}, not just the role in general.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at writing company-specific professional summaries that demonstrate genuine interest and strong fit."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate company-focused summary: {e}")
            return f"Experienced professional with strong background in software development and a genuine interest in contributing to {job_posting.company}'s mission and growth."