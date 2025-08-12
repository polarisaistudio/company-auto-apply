# run_ai_engineer.py - AI Engineer Job Search
import asyncio
import logging
from datetime import datetime
from ai_modules.job_classifier import JobRole
from main import CompanyJobAutomationSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_engineer_applications.log'),
        logging.StreamHandler()
    ]
)

class AIEngineerJobSearch(CompanyJobAutomationSystem):
    def __init__(self):
        super().__init__()
        self.target_role = JobRole.AI_ENGINEER
        self.logger.info(f"🤖 AI Engineer Job Search System initialized")
    
    def get_role_specific_companies(self):
        """Get companies that frequently hire AI Engineers"""
        all_companies = self.company_manager.get_target_companies()
        ai_friendly_companies = []
        
        for company in all_companies:
            target_roles = company.get('target_roles', [])
            # Prioritize companies that specifically target AI Engineers
            if any('AI Engineer' in role or 'Machine Learning' in role or 'ML Engineer' in role for role in target_roles):
                ai_friendly_companies.append(company)
        
        self.logger.info(f"Found {len(ai_friendly_companies)} companies targeting AI Engineers")
        return ai_friendly_companies
    
    async def run_ai_engineer_search(self):
        """Run AI Engineer specific job search"""
        self.logger.info("🚀 Starting AI Engineer job search...")
        self.logger.info("🎯 Target Role: AI Engineer, Machine Learning Engineer, Applied Scientist")
        
        applications_today = 0
        target_companies = self.get_role_specific_companies()
        
        for company_config in target_companies[:40]:  # Process up to 40 companies for broader coverage
            if applications_today >= 25:  # AI Engineer specific daily limit
                self.logger.info(f"Daily application limit reached for AI Engineer roles (25)")
                break
            
            self.logger.info(f"🏢 Processing company: {company_config['name']} (AI/ML focus)")
            
            try:
                from scrapers.company_scraper import CompanyScraper
                scraper = CompanyScraper(
                    company_config=company_config,
                    headless=True
                )
                
                # Discover jobs at this company
                jobs = await scraper.discover_jobs()
                
                if not jobs:
                    self.logger.info(f"No jobs found at {company_config['name']}")
                    continue
                
                # Filter for AI Engineer roles specifically
                ai_jobs = []
                for job in jobs:
                    should_apply, role, confidence = self.job_classifier.should_apply_to_job(job)
                    
                    if should_apply and role == JobRole.AI_ENGINEER:
                        ai_jobs.append({
                            "job": job,
                            "role": role,
                            "confidence": confidence
                        })
                
                self.logger.info(f"Found {len(ai_jobs)} AI Engineer roles at {company_config['name']}")
                
                # Process AI Engineer applications
                for job_info in ai_jobs:
                    if applications_today >= 25:
                        break
                        
                    job, role, confidence = job_info["job"], job_info["role"], job_info["confidence"]
                    
                    # Check if already applied
                    if self.is_already_applied(job):
                        self.logger.info(f"Already applied to {job.title} at {job.company}")
                        continue
                    
                    # Manual review with AI Engineer context
                    if hasattr(self.config, 'require_manual_review') and self.config.require_manual_review:
                        if not self.manual_ai_engineer_review(job, confidence):
                            continue
                    
                    success = await self.process_ai_engineer_application(job, scraper, role)
                    
                    if success:
                        applications_today += 1
                        self.logger.info(f"✅ AI Engineer application #{applications_today} submitted")
                    
                    # Respectful delay
                    import time, random
                    delay = random.uniform(90, 150)
                    time.sleep(delay)
                
                scraper.close()
                
            except Exception as e:
                self.logger.error(f"Error processing {company_config['name']}: {e}")
                continue
        
        self.logger.info(f"🎉 AI Engineer job search completed: {applications_today} applications submitted")
        self.generate_ai_engineer_report(applications_today)
    
    def manual_ai_engineer_review(self, job, confidence):
        """AI Engineer specific manual review"""
        print("\n" + "="*80)
        print("🤖 AI ENGINEER JOB REVIEW")
        print("="*80)
        print(f"Company: {job.company}")
        print(f"Position: {job.title}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary or 'Not specified'}")
        print(f"AI/ML Confidence: {confidence:.1%}")
        print("\n📋 Job Description Preview:")
        print(job.description[:500] + "..." if len(job.description) > 500 else job.description)
        print("\n🎯 AI/ML Keywords Found:")
        # Extract AI-related keywords from description
        ai_keywords = ['ai', 'machine learning', 'deep learning', 'neural network', 'pytorch', 'tensorflow', 'nlp', 'computer vision', 'llm', 'gpt']
        found_keywords = [kw for kw in ai_keywords if kw.lower() in job.description.lower()]
        print(f"   {', '.join(found_keywords[:10])}")
        print("="*80)
        
        while True:
            response = input("Apply for this AI Engineer role? (y/n/s=skip all): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 's':
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 's' to skip all remaining")
    
    async def process_ai_engineer_application(self, job, scraper, role):
        """Process AI Engineer application with specialized resume"""
        
        self.logger.info(f"📝 Processing AI Engineer application: {job.title} at {job.company}")
        
        try:
            # Use AI Engineer specific resume
            base_resume = self.resume_templates.get(JobRole.AI_ENGINEER)
            
            if not base_resume:
                self.logger.error("AI Engineer resume template not found!")
                return False
            
            # Customize for this specific AI Engineer role
            customized_resume = self.resume_generator.customize_resume(base_resume, job)
            
            # Generate AI Engineer focused cover letter
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                customized_resume, job, self.config.personal_info if hasattr(self.config, 'personal_info') else {}
            )
            
            # Save with AI Engineer specific path
            resume_path = self.save_ai_engineer_resume(customized_resume, job)
            
            # Apply through company website
            from automation.company_applier import CompanyApplier
            applier = CompanyApplier(scraper.driver, job.company)
            success = applier.apply_to_job(job, resume_path, cover_letter)
            
            # Track application
            self.tracker.add_application(job, resume_path, cover_letter, success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing AI Engineer application: {e}")
            return False
    
    def save_ai_engineer_resume(self, resume, job):
        """Save AI Engineer specific resume"""
        import os, json
        
        safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        filename = f"resumes/ai_engineer/{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
            
        return filename
    
    def generate_ai_engineer_report(self, applications_count):
        """Generate AI Engineer specific report"""
        
        report = f"""
        🤖 AI ENGINEER JOB SEARCH REPORT - {datetime.now().strftime('%Y-%m-%d')}
        
        Applications Submitted: {applications_count}
        Target Role: AI Engineer, ML Engineer, Applied Scientist
        Resume Used: AI Engineer Template (PyTorch, TensorFlow, LLMs focus)
        
        🎯 AI/ML Focus Areas Targeted:
        • Machine Learning Engineering
        • Deep Learning & Neural Networks
        • Natural Language Processing (NLP)
        • Computer Vision
        • Large Language Models (LLMs)
        • MLOps and Model Deployment
        • AI Research and Applied Science
        
        📊 Next Steps:
        • Monitor responses for AI Engineer roles
        • Follow up on applications after 1-2 weeks
        • Update AI Engineer resume based on feedback
        """
        
        self.logger.info(report)
        return report

async def main():
    """Main entry point for AI Engineer job search"""
    
    print("🤖" + "="*79)
    print("AI ENGINEER JOB SEARCH SYSTEM")
    print("="*80)
    print("🎯 Specialized search for AI/ML Engineer positions")
    print("🔍 Targeting: PyTorch, TensorFlow, LLMs, Computer Vision, NLP")
    print("📝 Using: AI Engineer optimized resume template")
    print("="*80)
    
    response = input("Start AI Engineer job search? (yes/no): ").lower().strip()
    if response != 'yes':
        print("AI Engineer job search cancelled.")
        return
    
    try:
        # Initialize AI Engineer job search system
        ai_search = AIEngineerJobSearch()
        
        print(f"\n🚀 AI Engineer Search Configuration:")
        print(f"• Daily limit: 25 AI Engineer applications")
        print(f"• Target companies: AI/ML focused companies")
        print(f"• Resume template: AI Engineer specialized")
        print(f"• Focus: PyTorch, TensorFlow, LLMs, Deep Learning")
        
        # Run the AI Engineer search
        await ai_search.run_ai_engineer_search()
        
    except Exception as e:
        print(f"AI Engineer search error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())