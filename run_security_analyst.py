# run_security_analyst.py - Security Analyst Job Search
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
        logging.FileHandler('security_analyst_applications.log'),
        logging.StreamHandler()
    ]
)

class SecurityAnalystJobSearch(CompanyJobAutomationSystem):
    def __init__(self):
        super().__init__()
        self.target_role = JobRole.SECURITY_ANALYST
        self.logger.info(f"🛡️ Security Analyst Job Search System initialized")
    
    def get_role_specific_companies(self):
        """Get companies that frequently hire Security Analysts"""
        all_companies = self.company_manager.get_target_companies()
        security_friendly_companies = []
        
        for company in all_companies:
            target_roles = company.get('target_roles', [])
            # Prioritize companies that specifically target Security Analysts
            if any('Security Analyst' in role or 'Cybersecurity' in role or 'SOC Analyst' in role for role in target_roles):
                security_friendly_companies.append(company)
        
        self.logger.info(f"Found {len(security_friendly_companies)} companies targeting Security Analysts")
        return security_friendly_companies
    
    async def run_security_analyst_search(self):
        """Run Security Analyst specific job search"""
        self.logger.info("🚀 Starting Security Analyst job search...")
        self.logger.info("🎯 Target Role: Security Analyst, Cybersecurity Analyst, SOC Analyst")
        
        applications_today = 0
        target_companies = self.get_role_specific_companies()
        
        for company_config in target_companies[:40]:  # Process up to 40 companies for broader coverage
            if applications_today >= 25:  # Security Analyst specific daily limit
                self.logger.info(f"Daily application limit reached for Security Analyst roles (25)")
                break
            
            self.logger.info(f"🏢 Processing company: {company_config['name']} (Cybersecurity focus)")
            
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
                
                # Filter for Security Analyst roles specifically
                security_jobs = []
                for job in jobs:
                    should_apply, role, confidence = self.job_classifier.should_apply_to_job(job)
                    
                    if should_apply and role == JobRole.SECURITY_ANALYST:
                        security_jobs.append({
                            "job": job,
                            "role": role,
                            "confidence": confidence
                        })
                
                self.logger.info(f"Found {len(security_jobs)} Security Analyst roles at {company_config['name']}")
                
                # Process Security Analyst applications
                for job_info in security_jobs:
                    if applications_today >= 25:
                        break
                        
                    job, role, confidence = job_info["job"], job_info["role"], job_info["confidence"]
                    
                    # Check if already applied
                    if self.is_already_applied(job):
                        self.logger.info(f"Already applied to {job.title} at {job.company}")
                        continue
                    
                    # Manual review with Security Analyst context
                    if hasattr(self.config, 'require_manual_review') and self.config.require_manual_review:
                        if not self.manual_security_analyst_review(job, confidence):
                            continue
                    
                    success = await self.process_security_analyst_application(job, scraper, role)
                    
                    if success:
                        applications_today += 1
                        self.logger.info(f"✅ Security Analyst application #{applications_today} submitted")
                    
                    # Respectful delay
                    import time, random
                    delay = random.uniform(90, 150)
                    time.sleep(delay)
                
                scraper.close()
                
            except Exception as e:
                self.logger.error(f"Error processing {company_config['name']}: {e}")
                continue
        
        self.logger.info(f"🎉 Security Analyst job search completed: {applications_today} applications submitted")
        self.generate_security_analyst_report(applications_today)
    
    def manual_security_analyst_review(self, job, confidence):
        """Security Analyst specific manual review"""
        print("\n" + "="*80)
        print("🛡️ SECURITY ANALYST JOB REVIEW")
        print("="*80)
        print(f"Company: {job.company}")
        print(f"Position: {job.title}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary or 'Not specified'}")
        print(f"Security Confidence: {confidence:.1%}")
        print("\n📋 Job Description Preview:")
        print(job.description[:500] + "..." if len(job.description) > 500 else job.description)
        print("\n🎯 Security Keywords Found:")
        # Extract security-related keywords from description
        security_keywords = ['security', 'cybersecurity', 'soc', 'siem', 'incident response', 'threat', 'vulnerability', 'firewall', 'splunk', 'nessus']
        found_keywords = [kw for kw in security_keywords if kw.lower() in job.description.lower()]
        print(f"   {', '.join(found_keywords[:10])}")
        print("="*80)
        
        while True:
            response = input("Apply for this Security Analyst role? (y/n/s=skip all): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 's':
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no, or 's' to skip all remaining")
    
    async def process_security_analyst_application(self, job, scraper, role):
        """Process Security Analyst application with specialized resume"""
        
        self.logger.info(f"📝 Processing Security Analyst application: {job.title} at {job.company}")
        
        try:
            # Use Security Analyst specific resume
            base_resume = self.resume_templates.get(JobRole.SECURITY_ANALYST)
            
            if not base_resume:
                self.logger.error("Security Analyst resume template not found!")
                return False
            
            # Customize for this specific Security Analyst role
            customized_resume = self.resume_generator.customize_resume(base_resume, job)
            
            # Generate Security Analyst focused cover letter
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                customized_resume, job, self.config.personal_info if hasattr(self.config, 'personal_info') else {}
            )
            
            # Save with Security Analyst specific path
            resume_path = self.save_security_analyst_resume(customized_resume, job)
            
            # Apply through company website
            from automation.company_applier import CompanyApplier
            applier = CompanyApplier(scraper.driver, job.company)
            success = applier.apply_to_job(job, resume_path, cover_letter)
            
            # Track application
            self.tracker.add_application(job, resume_path, cover_letter, success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing Security Analyst application: {e}")
            return False
    
    def save_security_analyst_resume(self, resume, job):
        """Save Security Analyst specific resume"""
        import os, json
        
        safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        filename = f"resumes/security_analyst/{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, ensure_ascii=False)
            
        return filename
    
    def generate_security_analyst_report(self, applications_count):
        """Generate Security Analyst specific report"""
        
        report = f"""
        🛡️ SECURITY ANALYST JOB SEARCH REPORT - {datetime.now().strftime('%Y-%m-%d')}
        
        Applications Submitted: {applications_count}
        Target Role: Security Analyst, Cybersecurity Analyst, SOC Analyst
        Resume Used: Security Analyst Template (SIEM, Incident Response, Threat Analysis focus)
        
        🎯 Cybersecurity Focus Areas Targeted:
        • Security Information and Event Management (SIEM)
        • Incident Response & Digital Forensics
        • Vulnerability Assessment & Penetration Testing
        • Threat Intelligence & Analysis
        • Security Monitoring & Operations Center (SOC)
        • Compliance & Risk Management (NIST, ISO 27001)
        • Network Security & Firewalls
        • Malware Analysis & Reverse Engineering
        
        📊 Next Steps:
        • Monitor responses for Security Analyst roles
        • Follow up on applications after 1-2 weeks
        • Update Security Analyst resume based on feedback
        """
        
        self.logger.info(report)
        return report

async def main():
    """Main entry point for Security Analyst job search"""
    
    print("🛡️" + "="*79)
    print("SECURITY ANALYST JOB SEARCH SYSTEM")
    print("="*80)
    print("🎯 Specialized search for Cybersecurity Analyst positions")
    print("🔍 Targeting: SIEM, SOC, Incident Response, Threat Analysis")
    print("📝 Using: Security Analyst optimized resume template")
    print("="*80)
    
    response = input("Start Security Analyst job search? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Security Analyst job search cancelled.")
        return
    
    try:
        # Initialize Security Analyst job search system
        security_search = SecurityAnalystJobSearch()
        
        print(f"\n🚀 Security Analyst Search Configuration:")
        print(f"• Daily limit: 25 Security Analyst applications")
        print(f"• Target companies: Cybersecurity focused companies")
        print(f"• Resume template: Security Analyst specialized")
        print(f"• Focus: SIEM, SOC, Incident Response, Threat Hunting")
        
        # Run the Security Analyst search
        await security_search.run_security_analyst_search()
        
    except Exception as e:
        print(f"Security Analyst search error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())