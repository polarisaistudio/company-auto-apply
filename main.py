# main.py - Company Website Auto-Apply System
import asyncio
import logging
import time
import random
from datetime import datetime
import json
import os
from typing import List, Dict

from config.settings import config
from companies.company_manager import CompanyManager
from scrapers.company_scraper import CompanyScraper, JobPosting
from ai_modules.resume_generator import AIResumeGenerator
from ai_modules.cover_letter_generator import CoverLetterGenerator
from ai_modules.job_classifier import JobClassifier, JobRole
from automation.company_applier import CompanyApplier
from tracking.application_tracker import ApplicationTracker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('company_applications.log'),
        logging.StreamHandler()
    ]
)

class CompanyJobAutomationSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_components()
        
    def setup_components(self):
        """Initialize system components"""
        
        # Core components
        self.company_manager = CompanyManager()
        self.tracker = ApplicationTracker()
        
        # AI components
        self.resume_generator = AIResumeGenerator(
            api_key=config.openai_api_key,
            model=config.model_name
        )
        
        self.cover_letter_generator = CoverLetterGenerator(
            api_key=config.openai_api_key,
            model=config.model_name
        )
        
        # Job classification system
        self.job_classifier = JobClassifier(
            api_key=config.openai_api_key,
            model=config.model_name
        )
        
        # Load all resume templates
        self.resume_templates = self._load_resume_templates()
            
        self.logger.info("Enhanced company automation system initialized successfully")
    
    def _load_resume_templates(self) -> Dict:
        """Load all resume templates for different roles"""
        
        templates = {}
        template_files = {
            JobRole.AI_ENGINEER: "templates/ai_engineer_resume.json",
            JobRole.CLOUD_ENGINEER: "templates/cloud_engineer_resume.json",
            JobRole.DATA_SCIENTIST: "templates/data_scientist_resume.json",
            JobRole.SECURITY_ANALYST: "templates/security_analyst_resume.json",
            JobRole.OTHER: "templates/base_resume.json"
        }
        
        for role, file_path in template_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    templates[role] = json.load(f)
                self.logger.info(f"Loaded resume template for {role.value}")
            except FileNotFoundError:
                self.logger.warning(f"Resume template not found: {file_path}")
                # Use base template as fallback
                try:
                    with open("templates/base_resume.json", 'r', encoding='utf-8') as f:
                        templates[role] = json.load(f)
                except FileNotFoundError:
                    self.logger.error("No resume templates found!")
                    templates[role] = {}
        
        return templates
    
    async def run_company_applications(self):
        """Run company-focused job application process"""
        
        self.logger.info("Starting company website application process")
        
        applications_today = 0
        target_companies = self.company_manager.get_target_companies()
        
        for company_config in target_companies:
            if applications_today >= config.max_applications_per_day:
                self.logger.info(f"Daily application limit reached ({config.max_applications_per_day})")
                break
                
            self.logger.info(f"Processing company: {company_config['name']}")
            
            try:
                # Initialize company-specific scraper
                scraper = CompanyScraper(
                    company_config=company_config,
                    headless=config.headless_browser
                )
                
                # Discover jobs at this company
                jobs = await scraper.discover_jobs()
                
                if not jobs:
                    self.logger.info(f"No jobs found at {company_config['name']}")
                    continue
                
                # Intelligent job filtering and classification
                relevant_jobs = self.classify_and_filter_jobs(jobs, company_config)
                
                # Process each relevant job
                for job_info in relevant_jobs:
                    if applications_today >= config.max_applications_per_day:
                        break
                    
                    job, role, confidence = job_info["job"], job_info["role"], job_info["confidence"]
                        
                    # Check if already applied
                    if self.is_already_applied(job):
                        self.logger.info(f"Already applied to {job.title} at {job.company}")
                        continue
                    
                    # Manual review step (for ethical compliance)
                    if config.require_manual_review:
                        if not self.manual_job_review(job, role, confidence):
                            continue
                    
                    success = await self.process_company_application(job, scraper, role)
                    
                    if success:
                        applications_today += 1
                        
                    # Respectful delay between applications
                    delay = random.uniform(
                        config.delay_between_applications,
                        config.delay_between_applications * 1.5
                    )
                    
                    self.logger.info(f"Waiting {delay:.1f} seconds before next application")
                    time.sleep(delay)
                
                scraper.close()
                
                # Delay between companies
                company_delay = random.uniform(60, 120)  # 1-2 minutes between companies
                self.logger.info(f"Waiting {company_delay:.1f} seconds before next company")
                time.sleep(company_delay)
                
            except Exception as e:
                self.logger.error(f"Error processing {company_config['name']}: {e}")
                continue
        
        self.logger.info(f"Company applications completed, total: {applications_today} applications")
        self.generate_daily_report()
    
    def classify_and_filter_jobs(self, jobs: List[JobPosting], company_config: dict) -> List[Dict]:
        """Classify jobs and filter for relevant roles with confidence scoring"""
        
        relevant_jobs = []
        
        for job in jobs:
            # Use intelligent classification to determine if we should apply
            should_apply, role, confidence = self.job_classifier.should_apply_to_job(job)
            
            if not should_apply:
                self.logger.debug(f"Skipping job '{job.title}' - classified as {role.value} with {confidence:.2f} confidence")
                continue
            
            # Additional filtering based on company preferences
            if not self._passes_company_filters(job, company_config):
                continue
            
            relevant_jobs.append({
                "job": job,
                "role": role,
                "confidence": confidence
            })
            
            self.logger.info(f"✅ Relevant job found: {job.title} (classified as {role.value}, {confidence:.2f} confidence)")
        
        self.logger.info(f"Found {len(relevant_jobs)} relevant jobs out of {len(jobs)} total jobs")
        
        # Sort by confidence score (highest first)
        relevant_jobs.sort(key=lambda x: x["confidence"], reverse=True)
        
        return relevant_jobs
    
    def _passes_company_filters(self, job: JobPosting, company_config: dict) -> bool:
        """Additional company-specific filtering"""
        
        # Salary filter
        if job.salary and self.extract_salary(job.salary) < config.salary_min:
            self.logger.debug(f"Job '{job.title}' filtered out due to salary")
            return False
        
        # Location preference (if specified)
        if company_config.get('preferred_locations'):
            if job.location and not any(loc.lower() in job.location.lower() 
                                      for loc in company_config['preferred_locations']):
                self.logger.debug(f"Job '{job.title}' filtered out due to location")
                return False
        
        # Experience level filter (avoid overly senior roles)
        if self.is_too_senior(job):
            self.logger.debug(f"Job '{job.title}' filtered out as too senior")
            return False
        
        return True
    
    def filter_jobs(self, jobs: List[JobPosting], company_config: dict) -> List[JobPosting]:
        """Filter jobs based on preferences and company-specific criteria"""
        
        filtered = []
        
        for job in jobs:
            # Salary filter
            if job.salary and self.extract_salary(job.salary) < config.salary_min:
                continue
                
            # Role matching
            if not self.matches_target_roles(job, company_config):
                continue
                
            # Experience level filter
            if self.is_too_senior(job):
                continue
                
            # Location filter (if specified)
            if company_config.get('preferred_locations') and job.location:
                if not any(loc.lower() in job.location.lower() 
                          for loc in company_config['preferred_locations']):
                    continue
                    
            filtered.append(job)
            
        self.logger.info(f"Filtered to {len(filtered)} jobs at {company_config['name']}")
        return filtered
    
    def matches_target_roles(self, job: JobPosting, company_config: dict) -> bool:
        """Check if job matches target roles"""
        
        target_roles = company_config.get('target_roles', config.target_roles)
        job_title_lower = job.title.lower()
        
        return any(role.lower() in job_title_lower for role in target_roles)
    
    def is_too_senior(self, job: JobPosting) -> bool:
        """Check if job is too senior level"""
        
        senior_keywords = [
            "senior", "sr.", "principal", "staff", "lead", "manager",
            "director", "architect", "head of", "vp", "vice president",
            "10+ years", "15+ years", "phd required"
        ]
        
        job_text = (job.title + " " + job.description).lower()
        return any(keyword in job_text for keyword in senior_keywords)
    
    def extract_salary(self, salary_str: str) -> int:
        """Extract salary number from string"""
        import re
        
        numbers = re.findall(r'\d+', salary_str.replace(',', ''))
        if numbers:
            return max(int(num) for num in numbers)
        return 0
    
    def is_already_applied(self, job: JobPosting) -> bool:
        """Check if already applied to this job"""
        return self.tracker.has_applied_to_job(job.url)
    
    def manual_job_review(self, job: JobPosting, role: JobRole, confidence: float) -> bool:
        """Enhanced manual review step with AI classification insights"""
        
        print("\n" + "="*80)
        print("🎯 INTELLIGENT JOB REVIEW")
        print("="*80)
        print(f"Company: {job.company}")
        print(f"Position: {job.title}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary or 'Not specified'}")
        print(f"URL: {job.url}")
        print("\n🤖 AI CLASSIFICATION:")
        print(f"Role Match: {role.value.replace('_', ' ').title()}")
        print(f"Confidence: {confidence:.1%}")
        print(f"Resume Template: {role.value.replace('_', ' ').title()} Resume")
        print("\n📋 Job Description Preview:")
        print(job.description[:500] + "..." if len(job.description) > 500 else job.description)
        print("="*80)
        
        while True:
            response = input("Apply to this job? (y/n/s=skip all): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 's':
                # Skip all remaining jobs for this session
                config.require_manual_review = False
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 's' to skip all remaining")
    
    async def process_company_application(self, job: JobPosting, scraper: CompanyScraper, role: JobRole) -> bool:
        """Process individual company application with role-specific resume"""
        
        self.logger.info(f"Processing application: {job.title} at {job.company} (using {role.value} template)")
        
        try:
            # 1. Select appropriate resume template based on role classification
            base_resume = self.resume_templates.get(role, self.resume_templates[JobRole.OTHER])
            
            # 2. Customize resume for this specific job and role
            customized_resume = self.resume_generator.customize_resume(
                base_resume, job
            )
            
            # 3. Generate targeted cover letter
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                customized_resume, job, config.personal_info
            )
            
            # 4. Save customized files with role information
            resume_path = self.save_customized_resume(customized_resume, job, role)
            
            # 5. Apply through company website
            applier = CompanyApplier(scraper.driver, job.company)
            success = applier.apply_to_job(job, resume_path, cover_letter)
            
            # 6. Record application with role information
            self.tracker.add_application(job, resume_path, cover_letter, success)
            
            if success:
                self.logger.info(f"✅ Successfully applied: {job.title} at {job.company} (as {role.value})")
            else:
                self.logger.warning(f"❌ Application failed: {job.title} at {job.company}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing application: {e}")
            return False
    
    def save_customized_resume(self, resume: dict, job: JobPosting, role: JobRole) -> str:
        """Save customized resume with role and company-specific filename"""
        
        safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        role_name = role.value
        
        filename = f"resumes/{role_name}/{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
            
        return filename
    
    def generate_daily_report(self):
        """Generate daily application report"""
        
        stats = self.tracker.get_application_stats()
        
        report = f"""
        📊 Company Applications Report - {datetime.now().strftime('%Y-%m-%d')}
        
        Today's Applications: {stats['recent_applications']}
        Total Applications: {stats['total_applications']}
        Success Rate: {stats['success_rate']:.2%}
        
        Top Companies Applied To: {', '.join(stats.get('top_companies', [])[:5])}
        
        Status Breakdown:
        """
        
        for status_info in stats['status_breakdown']:
            report += f"  {status_info['status']}: {status_info['count']}\n"
        
        self.logger.info(report)
        return report

async def main():
    """Main entry point"""
    
    print("="*80)
    print("🏢 COMPANY WEBSITE AUTO-APPLY SYSTEM")
    print("="*80)
    print("This system applies to jobs directly on company websites.")
    print("Benefits:")
    print("• No platform Terms of Service violations")
    print("• Direct relationship with employers")
    print("• More targeted and ethical approach")
    print("• Better success rates with manual review")
    print()
    print("🔍 ETHICAL GUIDELINES:")
    print("• Only targets companies you've researched and want to work for")
    print("• Includes manual review of each job (recommended)")
    print("• Respectful delays between applications")
    print("• Focuses on quality over quantity")
    print("="*80)
    
    response = input("Continue with company applications? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Exiting. Consider manually applying to companies you're interested in.")
        return
    
    try:
        # Initialize system
        system = CompanyJobAutomationSystem()
        
        print(f"\nSystem Configuration:")
        print(f"• Max applications per day: {config.max_applications_per_day}")
        print(f"• Delay between applications: {config.delay_between_applications}s")
        print(f"• Manual review enabled: {config.require_manual_review}")
        print(f"• Target companies: {len(system.company_manager.get_target_companies())}")
        
        # Run the application process
        await system.run_company_applications()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease check your environment variables and company configurations.")
        return
    except Exception as e:
        print(f"System Error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())