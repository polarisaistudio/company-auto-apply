# run_data_scientist.py - Data Scientist Job Search
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
        logging.FileHandler('data_scientist_applications.log'),
        logging.StreamHandler()
    ]
)

class DataScientistJobSearch(CompanyJobAutomationSystem):
    def __init__(self):
        super().__init__()
        self.target_role = JobRole.DATA_SCIENTIST
        self.logger.info(f"📊 Data Scientist Job Search System initialized")
    
    def get_role_specific_companies(self):
        """Get companies that frequently hire Data Scientists"""
        all_companies = self.company_manager.get_target_companies()
        data_friendly_companies = []
        
        for company in all_companies:
            target_roles = company.get('target_roles', [])
            # Prioritize companies that specifically target Data Scientists
            if any('Data Scientist' in role or 'Analytics' in role or 'Business Intelligence' in role for role in target_roles):
                data_friendly_companies.append(company)
        
        self.logger.info(f"Found {len(data_friendly_companies)} companies targeting Data Scientists")
        return data_friendly_companies
    
    async def run_data_scientist_search(self):
        """Run Data Scientist specific job search"""
        self.logger.info("🚀 Starting Data Scientist job search...")
        self.logger.info("🎯 Target Role: Data Scientist, Analytics Engineer, Business Intelligence")
        
        applications_today = 0
        target_companies = self.get_role_specific_companies()
        
        for company_config in target_companies[:40]:  # Process up to 40 companies for broader coverage
            if applications_today >= 25:  # Data Scientist specific daily limit
                self.logger.info(f"Daily application limit reached for Data Scientist roles (25)")
                break
            
            self.logger.info(f"🏢 Processing company: {company_config['name']} (Data/Analytics focus)")
            
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
                
                # Filter for Data Scientist roles specifically
                data_jobs = []
                for job in jobs:
                    should_apply, role, confidence = self.job_classifier.should_apply_to_job(job)
                    
                    if should_apply and role == JobRole.DATA_SCIENTIST:
                        data_jobs.append({
                            "job": job,
                            "role": role,
                            "confidence": confidence
                        })
                
                self.logger.info(f"Found {len(data_jobs)} Data Scientist roles at {company_config['name']}")
                
                # Process Data Scientist applications
                for job_info in data_jobs:
                    if applications_today >= 25:
                        break
                        
                    job, role, confidence = job_info["job"], job_info["role"], job_info["confidence"]
                    
                    # Check if already applied
                    if self.is_already_applied(job):
                        self.logger.info(f"Already applied to {job.title} at {job.company}")
                        continue
                    
                    # Manual review with Data Scientist context
                    if hasattr(self.config, 'require_manual_review') and self.config.require_manual_review:
                        if not self.manual_data_scientist_review(job, confidence):
                            continue
                    
                    success = await self.process_data_scientist_application(job, scraper, role)
                    
                    if success:
                        applications_today += 1
                        self.logger.info(f"✅ Data Scientist application #{applications_today} submitted")
                    
                    # Respectful delay
                    import time, random
                    delay = random.uniform(90, 150)
                    time.sleep(delay)
                
                scraper.close()
                
            except Exception as e:
                self.logger.error(f"Error processing {company_config['name']}: {e}")
                continue
        
        self.logger.info(f"🎉 Data Scientist job search completed: {applications_today} applications submitted")
        self.generate_data_scientist_report(applications_today)
    
    def manual_data_scientist_review(self, job, confidence):
        """Data Scientist specific manual review"""
        print("\n" + "="*80)
        print("📊 DATA SCIENTIST JOB REVIEW")
        print("="*80)
        print(f"Company: {job.company}")
        print(f"Position: {job.title}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary or 'Not specified'}")
        print(f"Data Science Confidence: {confidence:.1%}")
        print("\n📋 Job Description Preview:")
        print(job.description[:500] + "..." if len(job.description) > 500 else job.description)
        print("\n🎯 Data Science Keywords Found:")
        # Extract Data Science-related keywords from description
        data_keywords = ['python', 'r', 'sql', 'tableau', 'power bi', 'statistics', 'regression', 'clustering', 'pandas', 'numpy', 'scikit-learn', 'analytics']
        found_keywords = [kw for kw in data_keywords if kw.lower() in job.description.lower()]
        print(f"   {', '.join(found_keywords[:10])}")
        print("="*80)
        
        while True:
            response = input("Apply for this Data Scientist role? (y/n/s=skip all): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 's':
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 's' to skip all remaining")
    
    async def process_data_scientist_application(self, job, scraper, role):
        """Process Data Scientist application with specialized resume"""
        
        self.logger.info(f"📝 Processing Data Scientist application: {job.title} at {job.company}")
        
        try:
            # Use Data Scientist specific resume
            base_resume = self.resume_templates.get(JobRole.DATA_SCIENTIST)
            
            if not base_resume:
                self.logger.error("Data Scientist resume template not found!")
                return False
            
            # Customize for this specific Data Scientist role
            customized_resume = self.resume_generator.customize_resume(base_resume, job)
            
            # Generate Data Scientist focused cover letter
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                customized_resume, job, self.config.personal_info if hasattr(self.config, 'personal_info') else {}
            )
            
            # Save with Data Scientist specific path
            resume_path = self.save_data_scientist_resume(customized_resume, job)
            
            # Apply through company website
            from automation.company_applier import CompanyApplier
            applier = CompanyApplier(scraper.driver, job.company)
            success = applier.apply_to_job(job, resume_path, cover_letter)
            
            # Track application
            self.tracker.add_application(job, resume_path, cover_letter, success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing Data Scientist application: {e}")
            return False
    
    def save_data_scientist_resume(self, resume, job):
        """Save Data Scientist specific resume"""
        import os, json
        
        safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        filename = f"resumes/data_scientist/{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
            
        return filename
    
    def generate_data_scientist_report(self, applications_count):
        """Generate Data Scientist specific report"""
        
        report = f"""
        📊 DATA SCIENTIST JOB SEARCH REPORT - {datetime.now().strftime('%Y-%m-%d')}
        
        Applications Submitted: {applications_count}
        Target Role: Data Scientist, Analytics Engineer, Business Intelligence
        Resume Used: Data Scientist Template (Python, R, SQL, Tableau focus)
        
        🎯 Data Science Focus Areas Targeted:
        • Statistical Analysis & Modeling
        • Business Intelligence & Analytics
        • Data Visualization (Tableau, Power BI)
        • Python/R Programming & Libraries
        • SQL & Database Management
        • Machine Learning for Business
        • A/B Testing & Experimentation
        • Predictive Analytics
        
        📊 Next Steps:
        • Monitor responses for Data Scientist roles
        • Follow up on applications after 1-2 weeks
        • Update Data Scientist resume based on feedback
        """
        
        self.logger.info(report)
        return report

async def main():
    """Main entry point for Data Scientist job search"""
    
    print("📊" + "="*79)
    print("DATA SCIENTIST JOB SEARCH SYSTEM")
    print("="*80)
    print("🎯 Specialized search for Data Scientist positions")
    print("🔍 Targeting: Python, R, SQL, Tableau, Statistics, Analytics")
    print("📝 Using: Data Scientist optimized resume template")
    print("="*80)
    
    response = input("Start Data Scientist job search? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Data Scientist job search cancelled.")
        return
    
    try:
        # Initialize Data Scientist job search system
        data_search = DataScientistJobSearch()
        
        print(f"\n🚀 Data Scientist Search Configuration:")
        print(f"• Daily limit: 25 Data Scientist applications")
        print(f"• Target companies: Data/Analytics focused companies")
        print(f"• Resume template: Data Scientist specialized")
        print(f"• Focus: Python, R, SQL, Tableau, Statistics")
        
        # Run the Data Scientist search
        await data_search.run_data_scientist_search()
        
    except Exception as e:
        print(f"Data Scientist search error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())