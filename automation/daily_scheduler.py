# automation/daily_scheduler.py
import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json

from main import CompanyJobAutomationSystem
from config.settings import config

class DailyJobScheduler:
    """Daily job monitoring and application scheduler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.last_run_date = None
        self.stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "total_applications": 0,
            "companies_processed": 0
        }
    
    def start_daily_automation(self):
        """Start the daily automation scheduler"""
        
        if not config.enable_daily_automation:
            self.logger.info("Daily automation is disabled in configuration")
            return
        
        self.logger.info(f"🚀 Starting daily job automation scheduler")
        self.logger.info(f"⏰ Scheduled to run daily at {config.daily_run_time}")
        self.logger.info(f"🎯 Will apply to max {config.max_applications_per_day} jobs per day")
        self.logger.info(f"🏢 Will process max {config.max_companies_per_day} companies per day")
        
        # Schedule daily run
        schedule.every().day.at(config.daily_run_time).do(self._run_daily_job_search)
        
        # Also allow immediate run for testing
        if input("Run job search now? (y/n): ").lower().strip() == 'y':
            asyncio.run(self._run_daily_job_search())
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def _run_daily_job_search(self):
        """Execute daily job search process"""
        
        if self.is_running:
            self.logger.warning("Daily job search is already running, skipping this execution")
            return
        
        self.is_running = True
        run_start_time = datetime.now()
        
        try:
            self.logger.info("="*80)
            self.logger.info(f"🌅 DAILY JOB SEARCH STARTED - {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("="*80)
            
            # Initialize the job automation system
            system = CompanyJobAutomationSystem()
            
            # Run the job search process
            await system.run_company_applications()
            
            # Update statistics
            self.stats["total_runs"] += 1
            self.stats["successful_runs"] += 1
            self.last_run_date = run_start_time.date()
            
            run_duration = datetime.now() - run_start_time
            
            self.logger.info("="*80)
            self.logger.info(f"✅ DAILY JOB SEARCH COMPLETED")
            self.logger.info(f"⏱️  Duration: {run_duration}")
            self.logger.info(f"📊 Run #{self.stats['total_runs']}")
            self.logger.info("="*80)
            
            # Generate and save daily summary
            await self._generate_daily_summary(system, run_duration)
            
        except Exception as e:
            self.logger.error(f"❌ Daily job search failed: {e}")
            self.stats["total_runs"] += 1
            # Don't increment successful_runs
            
        finally:
            self.is_running = False
    
    async def _generate_daily_summary(self, system: CompanyJobAutomationSystem, duration: timedelta):
        """Generate comprehensive daily summary"""
        
        stats = system.tracker.get_application_stats()
        
        summary = {
            "run_date": datetime.now().isoformat(),
            "duration_minutes": duration.total_seconds() / 60,
            "applications": {
                "today": stats.get("recent_applications", 0),
                "total": stats.get("total_applications", 0),
                "success_rate": stats.get("success_rate", 0)
            },
            "companies_processed": len(system.company_manager.get_target_companies()),
            "scheduler_stats": self.stats.copy()
        }
        
        # Save summary to file
        summary_filename = f"daily_summaries/summary_{datetime.now().strftime('%Y%m%d')}.json"
        
        import os
        os.makedirs(os.path.dirname(summary_filename), exist_ok=True)
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Log summary
        self.logger.info(f"📈 DAILY SUMMARY:")
        self.logger.info(f"   Applications submitted today: {summary['applications']['today']}")
        self.logger.info(f"   Total applications: {summary['applications']['total']}")
        self.logger.info(f"   Success rate: {summary['applications']['success_rate']:.1%}")
        self.logger.info(f"   Companies processed: {summary['companies_processed']}")
        self.logger.info(f"   Duration: {summary['duration_minutes']:.1f} minutes")
        
        # Send notifications if configured
        await self._send_daily_notifications(summary)
    
    async def _send_daily_notifications(self, summary: Dict):
        """Send daily summary notifications (email, Slack, etc.)"""
        
        # This is a placeholder for notification integrations
        # You could add email, Slack, Discord, or other notifications here
        
        self.logger.info("📧 Daily summary saved to daily_summaries/")
        
        # Example: Simple email notification (would need email configuration)
        if hasattr(config, 'notification_email') and config.notification_email:
            try:
                await self._send_email_summary(summary)
            except Exception as e:
                self.logger.error(f"Failed to send email notification: {e}")
    
    async def _send_email_summary(self, summary: Dict):
        """Send email summary (placeholder implementation)"""
        
        # This would require email configuration in settings
        # For now, just log the intent
        self.logger.info(f"Would send email summary to {getattr(config, 'notification_email', 'not configured')}")
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status and statistics"""
        
        return {
            "is_running": self.is_running,
            "last_run_date": self.last_run_date.isoformat() if self.last_run_date else None,
            "next_run": schedule.next_run().isoformat() if schedule.jobs else None,
            "stats": self.stats.copy(),
            "config": {
                "enabled": config.enable_daily_automation,
                "run_time": config.daily_run_time,
                "max_applications_per_day": config.max_applications_per_day,
                "max_companies_per_day": config.max_companies_per_day
            }
        }
    
    def stop_scheduler(self):
        """Stop the daily scheduler"""
        
        schedule.clear()
        self.logger.info("Daily scheduler stopped")
    
    def run_manual_check(self):
        """Run a manual job check without applying"""
        
        self.logger.info("🔍 Running manual job market check...")
        
        # This would run the discovery process without applying
        # Useful for monitoring job market trends
        
        asyncio.run(self._manual_market_check())
    
    async def _manual_market_check(self):
        """Check job market without applying"""
        
        try:
            system = CompanyJobAutomationSystem()
            companies = system.company_manager.get_target_companies()
            
            all_jobs = []
            
            for company_config in companies[:5]:  # Check first 5 companies
                self.logger.info(f"Checking jobs at {company_config['name']}")
                
                scraper = CompanyScraper(company_config, headless=True)
                jobs = await scraper.discover_jobs()
                
                if jobs:
                    classified_jobs = system.classify_and_filter_jobs(jobs, company_config)
                    all_jobs.extend([job_info["job"] for job_info in classified_jobs])
                
                scraper.close()
                time.sleep(30)  # Respectful delay
            
            # Analyze job market
            if all_jobs:
                market_analysis = system.job_classifier.analyze_job_market_fit(all_jobs)
                self.logger.info(f"📊 Market Analysis: {market_analysis}")
            else:
                self.logger.info("No relevant jobs found in market check")
                
        except Exception as e:
            self.logger.error(f"Manual market check failed: {e}")

def main():
    """Main entry point for daily scheduler"""
    
    scheduler = DailyJobScheduler()
    
    print("🤖 Company Auto-Apply Daily Scheduler")
    print("="*50)
    print("1. Start daily automation")
    print("2. Check scheduler status") 
    print("3. Run manual market check")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        scheduler.start_daily_automation()
    elif choice == "2":
        status = scheduler.get_scheduler_status()
        print(json.dumps(status, indent=2, default=str))
    elif choice == "3":
        scheduler.run_manual_check()
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()