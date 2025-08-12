# run_cloud_engineer.py - Cloud Engineer Job Search
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
        logging.FileHandler('cloud_engineer_applications.log'),
        logging.StreamHandler()
    ]
)

class CloudEngineerJobSearch(CompanyJobAutomationSystem):
    def __init__(self):
        super().__init__()
        self.target_role = JobRole.CLOUD_ENGINEER
        self.logger.info(f"☁️ Cloud Engineer Job Search System initialized")
    
    def get_role_specific_companies(self):
        """Get companies that frequently hire Cloud Engineers"""
        all_companies = self.company_manager.get_target_companies()
        cloud_friendly_companies = []
        
        for company in all_companies:
            target_roles = company.get('target_roles', [])
            # Prioritize companies that specifically target Cloud Engineers
            if any('Cloud Engineer' in role or 'DevOps' in role or 'SRE' in role for role in target_roles):
                cloud_friendly_companies.append(company)
        
        self.logger.info(f"Found {len(cloud_friendly_companies)} companies targeting Cloud Engineers")
        return cloud_friendly_companies
    
    async def run_cloud_engineer_search(self):
        """Run Cloud Engineer specific job search"""
        self.logger.info("🚀 Starting Cloud Engineer job search...")
        self.logger.info("🎯 Target Role: Cloud Engineer, DevOps Engineer, SRE, Platform Engineer")
        
        applications_today = 0
        target_companies = self.get_role_specific_companies()
        
        for company_config in target_companies[:40]:  # Process up to 40 companies for broader coverage
            if applications_today >= 25:  # Cloud Engineer specific daily limit
                self.logger.info(f"Daily application limit reached for Cloud Engineer roles (25)")
                break
            
            self.logger.info(f"🏢 Processing company: {company_config['name']} (Cloud/DevOps focus)")
            
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
                
                # Filter for Cloud Engineer roles specifically
                cloud_jobs = []
                for job in jobs:
                    should_apply, role, confidence = self.job_classifier.should_apply_to_job(job)
                    
                    if should_apply and role == JobRole.CLOUD_ENGINEER:
                        cloud_jobs.append({
                            "job": job,
                            "role": role,
                            "confidence": confidence
                        })
                
                self.logger.info(f"Found {len(cloud_jobs)} Cloud Engineer roles at {company_config['name']}")
                
                # Process Cloud Engineer applications
                for job_info in cloud_jobs:
                    if applications_today >= 25:
                        break
                        
                    job, role, confidence = job_info["job"], job_info["role"], job_info["confidence"]
                    
                    # Check if already applied
                    if self.is_already_applied(job):
                        self.logger.info(f"Already applied to {job.title} at {job.company}")
                        continue
                    
                    # Manual review with Cloud Engineer context
                    if hasattr(self.config, 'require_manual_review') and self.config.require_manual_review:
                        if not self.manual_cloud_engineer_review(job, confidence):
                            continue
                    
                    success = await self.process_cloud_engineer_application(job, scraper, role)
                    
                    if success:
                        applications_today += 1
                        self.logger.info(f"✅ Cloud Engineer application #{applications_today} submitted")
                    
                    # Respectful delay
                    import time, random
                    delay = random.uniform(90, 150)
                    time.sleep(delay)
                
                scraper.close()
                
            except Exception as e:
                self.logger.error(f"Error processing {company_config['name']}: {e}")
                continue
        
        self.logger.info(f"🎉 Cloud Engineer job search completed: {applications_today} applications submitted")
        self.generate_cloud_engineer_report(applications_today)
    
    def manual_cloud_engineer_review(self, job, confidence):
        """Cloud Engineer specific manual review"""
        print("\n" + "="*80)
        print("☁️ CLOUD ENGINEER JOB REVIEW")
        print("="*80)
        print(f"Company: {job.company}")
        print(f"Position: {job.title}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary or 'Not specified'}")
        print(f"Cloud/DevOps Confidence: {confidence:.1%}")
        print("\n📋 Job Description Preview:")
        print(job.description[:500] + "..." if len(job.description) > 500 else job.description)
        print("\n🎯 Cloud/DevOps Keywords Found:")
        # Extract Cloud-related keywords from description
        cloud_keywords = ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins', 'devops', 'sre', 'monitoring', 'ci/cd']
        found_keywords = [kw for kw in cloud_keywords if kw.lower() in job.description.lower()]
        print(f"   {', '.join(found_keywords[:10])}")
        print("="*80)
        
        while True:
            response = input("Apply for this Cloud Engineer role? (y/n/s=skip all): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 's':
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 's' to skip all remaining")
    
    async def process_cloud_engineer_application(self, job, scraper, role):
        """Process Cloud Engineer application with specialized resume"""
        
        self.logger.info(f"📝 Processing Cloud Engineer application: {job.title} at {job.company}")
        
        try:
            # Use Cloud Engineer specific resume
            base_resume = self.resume_templates.get(JobRole.CLOUD_ENGINEER)
            
            if not base_resume:
                self.logger.error("Cloud Engineer resume template not found!")
                return False
            
            # Customize for this specific Cloud Engineer role
            customized_resume = self.resume_generator.customize_resume(base_resume, job)
            
            # Generate Cloud Engineer focused cover letter
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                customized_resume, job, self.config.personal_info if hasattr(self.config, 'personal_info') else {}
            )
            
            # Save with Cloud Engineer specific path
            resume_path = self.save_cloud_engineer_resume(customized_resume, job)
            
            # Apply through company website
            from automation.company_applier import CompanyApplier
            applier = CompanyApplier(scraper.driver, job.company)
            success = applier.apply_to_job(job, resume_path, cover_letter)
            
            # Track application
            self.tracker.add_application(job, resume_path, cover_letter, success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing Cloud Engineer application: {e}")
            return False
    
    def save_cloud_engineer_resume(self, resume, job):
        """Save Cloud Engineer specific resume"""
        import os, json
        
        safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        filename = f"resumes/cloud_engineer/{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
            
        return filename
    
    def generate_cloud_engineer_report(self, applications_count):
        """Generate Cloud Engineer specific report"""
        
        report = f"""
        ☁️ CLOUD ENGINEER JOB SEARCH REPORT - {datetime.now().strftime('%Y-%m-%d')}
        
        Applications Submitted: {applications_count}
        Target Role: Cloud Engineer, DevOps Engineer, SRE, Platform Engineer
        Resume Used: Cloud Engineer Template (AWS, Kubernetes, Terraform focus)
        
        🎯 Cloud/DevOps Focus Areas Targeted:
        • Cloud Infrastructure (AWS, GCP, Azure)
        • Container Orchestration (Kubernetes, Docker)
        • Infrastructure as Code (Terraform, Ansible)
        • CI/CD Pipelines (Jenkins, GitHub Actions)
        • Monitoring & Observability (Prometheus, Grafana)
        • Site Reliability Engineering (SRE)
        • DevOps & Platform Engineering
        
        📊 Next Steps:
        • Monitor responses for Cloud Engineer roles
        • Follow up on applications after 1-2 weeks
        • Update Cloud Engineer resume based on feedback
        """
        
        self.logger.info(report)
        return report

async def main():
    """Main entry point for Cloud Engineer job search"""
    
    print("☁️" + "="*79)
    print("CLOUD ENGINEER JOB SEARCH SYSTEM")
    print("="*80)
    print("🎯 Specialized search for Cloud/DevOps Engineer positions")
    print("🔍 Targeting: AWS, Kubernetes, Terraform, Docker, CI/CD")
    print("📝 Using: Cloud Engineer optimized resume template")
    print("="*80)
    
    response = input("Start Cloud Engineer job search? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Cloud Engineer job search cancelled.")
        return
    
    try:
        # Initialize Cloud Engineer job search system
        cloud_search = CloudEngineerJobSearch()
        
        print(f"\n🚀 Cloud Engineer Search Configuration:")
        print(f"• Daily limit: 25 Cloud Engineer applications")
        print(f"• Target companies: Cloud/DevOps focused companies")
        print(f"• Resume template: Cloud Engineer specialized")
        print(f"• Focus: AWS, Kubernetes, Terraform, DevOps")
        
        # Run the Cloud Engineer search
        await cloud_search.run_cloud_engineer_search()
        
    except Exception as e:
        print(f"Cloud Engineer search error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())