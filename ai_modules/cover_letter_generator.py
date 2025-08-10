# ai_modules/cover_letter_generator.py
import openai
from typing import Dict
import logging

from scrapers.company_scraper import JobPosting

class CoverLetterGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def generate_cover_letter(self, resume: Dict, job_posting: JobPosting, personal_info: Dict) -> str:
        """Generate a company-specific, personalized cover letter"""
        
        prompt = self.create_company_cover_letter_prompt(resume, job_posting, personal_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cover letter expert who specializes in company-specific applications. Write compelling, personalized cover letters that demonstrate genuine interest in the company and deep understanding of their business, culture, and challenges. Avoid generic templates and focus on why this specific candidate wants to work at this specific company."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Slightly higher for more creative, personalized output
                max_tokens=800
            )
            
            cover_letter_content = response.choices[0].message.content.strip()
            
            # Format with proper header and structure
            formatted_letter = self.format_company_cover_letter(
                cover_letter_content, personal_info, job_posting
            )
            
            self.logger.info(f"Successfully generated company-specific cover letter for {job_posting.company}")
            return formatted_letter
            
        except Exception as e:
            self.logger.error(f"Cover letter generation failed: {e}")
            return self.create_fallback_company_cover_letter(personal_info, job_posting)
    
    def create_company_cover_letter_prompt(self, resume: Dict, job_posting: JobPosting, personal_info: Dict) -> str:
        """Create comprehensive prompt for company-specific cover letter"""
        
        # Extract key experiences and achievements
        key_experiences = []
        for exp in resume.get("experience", [])[:3]:
            achievements = exp.get('achievements', [])
            if achievements:
                key_experiences.append(
                    f"- {exp.get('title', '')} at {exp.get('company', '')}: {achievements[0]}"
                )
        
        # Extract relevant skills
        technical_skills = resume.get("skills", {}).get("technical", [])[:6]
        soft_skills = resume.get("skills", {}).get("soft", [])[:4]
        
        return f"""
        Write a compelling, company-specific cover letter for this application:

        **CANDIDATE PROFILE:**
        Name: {personal_info.get('name', '')}
        Professional Summary: {resume.get('summary', '')}
        
        Key Achievements:
        {chr(10).join(key_experiences)}
        
        Technical Skills: {', '.join(technical_skills)}
        Core Strengths: {', '.join(soft_skills)}

        **TARGET OPPORTUNITY:**
        Company: {job_posting.company}
        Position: {job_posting.title}
        Department: {job_posting.department}
        Location: {job_posting.location}

        **JOB CONTEXT:**
        {job_posting.description[:800]}

        **KEY REQUIREMENTS:**
        {job_posting.requirements[:500]}

        **COVER LETTER REQUIREMENTS:**

        1. **Company Research & Genuine Interest:**
           - Demonstrate specific knowledge about {job_posting.company}
           - Show understanding of their business model, products, or industry challenges
           - Express authentic enthusiasm for their mission and values
           - Avoid generic statements that could apply to any company

        2. **Role-Specific Connection:**
           - Explain why this specific position excites you
           - Connect your background to the unique aspects of this role
           - Show understanding of how this position contributes to company goals

        3. **Value Proposition:**
           - Highlight 2-3 most relevant experiences that directly relate to job requirements
           - Quantify achievements where possible
           - Show how your skills solve problems this company faces
           - Demonstrate potential impact you could make

        4. **Personal Touch:**
           - Share a brief, relevant personal story or motivation
           - Show personality while maintaining professionalism
           - Explain what draws you to this company's culture or mission

        5. **Structure & Style:**
           - Opening: Hook with company-specific insight and role interest
           - Body (2 paragraphs): Relevant experience + why this company appeals to you
           - Closing: Strong call to action and enthusiasm
           - Tone: Professional but conversational, confident but humble
           - Length: 250-350 words (3-4 paragraphs)

        **AVOID:**
        - Generic templates or clichéd phrases
        - Repeating resume content verbatim
        - Overly formal or stiff language
        - Focusing solely on what you want rather than what you can offer
        - Making claims you can't support

        Write a cover letter that would make {job_posting.company} excited to meet this candidate.
        """
    
    def format_company_cover_letter(self, content: str, personal_info: Dict, job_posting: JobPosting) -> str:
        """Format cover letter with proper business letter structure"""
        
        from datetime import datetime
        
        # Create professional header
        header = f"""
{personal_info.get('name', '')}
{personal_info.get('email', '')}
{personal_info.get('phone', '')}
{personal_info.get('portfolio', '') or personal_info.get('linkedin', '')}

{datetime.now().strftime('%B %d, %Y')}

Hiring Team
{job_posting.company}
{job_posting.department + ' Department' if job_posting.department else ''}

Dear {job_posting.company} Hiring Team,

{content}

Best regards,
{personal_info.get('name', '')}
        """.strip()
        
        return header
    
    def create_fallback_company_cover_letter(self, personal_info: Dict, job_posting: JobPosting) -> str:
        """Create a thoughtful fallback cover letter when AI generation fails"""
        
        from datetime import datetime
        
        return f"""
{personal_info.get('name', '')}
{personal_info.get('email', '')}
{personal_info.get('phone', '')}

{datetime.now().strftime('%B %d, %Y')}

Dear {job_posting.company} Hiring Team,

I am excited to apply for the {job_posting.title} position at {job_posting.company}. Your company's reputation for innovation and commitment to excellence aligns perfectly with my professional values and career aspirations.

In my previous roles, I have developed strong technical skills and a passion for solving complex problems through collaborative teamwork. I am particularly drawn to {job_posting.company} because of your focus on creating meaningful impact in the industry. The {job_posting.title} role represents an ideal opportunity for me to contribute to your team's success while continuing to grow professionally.

I am impressed by {job_posting.company}'s approach to technology and would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's continued success. Thank you for considering my application.

I look forward to hearing from you.

Sincerely,
{personal_info.get('name', '')}
        """
    
    def generate_company_specific_opener(self, company_name: str, role: str, job_description: str) -> str:
        """Generate a compelling opening line specific to the company and role"""
        
        prompt = f"""
        Write a compelling opening sentence for a cover letter applying to {company_name} for a {role} position.

        Job context: {job_description[:300]}

        Requirements:
        - Show specific knowledge about {company_name}
        - Demonstrate genuine interest in this particular role
        - Avoid generic phrases like "I am writing to apply"
        - Make it engaging and personal
        - Keep it to 1-2 sentences maximum

        Examples of good openers:
        - "When I read about [Company's] innovative approach to [specific area], I knew I had to be part of the team revolutionizing [industry]."
        - "Having followed [Company's] journey from [early stage] to [current achievement], I'm excited to contribute to your mission as a [Role]."
        - "[Specific company achievement or product] perfectly embodies why I'm passionate about [relevant field], and I'd love to help [Company] continue this impact as your next [Role]."
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for this simpler task
                messages=[
                    {"role": "system", "content": "You are an expert at writing compelling, company-specific cover letter openers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate opener: {e}")
            return f"I am excited to apply for the {role} position at {company_name}, where I can contribute to your innovative team and mission."