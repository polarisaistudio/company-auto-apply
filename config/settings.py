# config/settings.py
import os
from dataclasses import dataclass
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class CompanyJobSearchConfig:
    # Search parameters
    target_roles: List[str] = None
    salary_min: int = 70000
    experience_level: str = "entry-mid"  # More conservative than previous system
    
    # Company-specific settings
    max_companies_per_day: int = 40  # Process more companies for broader coverage
    max_applications_per_day: int = 25  # Higher limit for broader reach while maintaining quality
    max_applications_per_company: int = 1  # 1 job per company per day approach
    delay_between_applications: int = 90  # Longer delays for respectfulness
    delay_between_companies: int = 180  # 3 minutes between companies
    
    # Daily automation settings
    enable_daily_automation: bool = False  # Set to True for daily scheduled runs
    daily_run_time: str = "09:00"  # Time to run daily automation (24hr format)
    job_classification_threshold: float = 0.6  # Minimum confidence for auto-application
    
    # Ethical settings
    require_manual_review: bool = True  # Default to manual review
    respect_robots_txt: bool = True
    max_pages_per_company: int = 3  # Limit scraping depth
    
    # AI configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    model_name: str = "gpt-4"
    
    # Browser settings
    headless_browser: bool = False  # Show browser for transparency
    browser_timeout: int = 30
    
    # File paths
    personal_info: Dict = None
    base_resume_path: str = "templates/base_resume.json"
    companies_config_path: str = "companies/target_companies.json"
    
    def __post_init__(self):
        # Set default target roles
        if self.target_roles is None:
            self.target_roles = [
                "Software Engineer",
                "Frontend Developer", 
                "Backend Developer",
                "Full Stack Developer",
                "Technical Support Engineer",
                "Customer Success Engineer",
                "DevOps Engineer",
                "Cloud Engineer"
            ]
        
        # Load personal info from environment
        if self.personal_info is None:
            self.personal_info = {
                "name": os.getenv("USER_NAME", ""),
                "email": os.getenv("USER_EMAIL", ""),
                "phone": os.getenv("USER_PHONE", ""),
                "linkedin": os.getenv("USER_LINKEDIN", ""),
                "github": os.getenv("USER_GITHUB", ""),
                "portfolio": os.getenv("USER_PORTFOLIO", "")
            }
        
        # Load API keys from environment
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
            
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        errors = []
        
        # Check required API keys
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY environment variable is required")
        
        # Check personal info
        required_fields = ["name", "email"]
        for field in required_fields:
            if not self.personal_info.get(field):
                errors.append(f"USER_{field.upper()} environment variable is required")
        
        # Validate email format
        email = self.personal_info.get("email", "")
        if email and "@" not in email:
            errors.append("Invalid email format")
        
        # Check numeric limits (updated for hybrid approach)
        if self.max_applications_per_day > 50:
            errors.append("max_applications_per_day should not exceed 50 for ethical usage")
        
        if self.max_applications_per_day <= 0:
            errors.append("max_applications_per_day must be positive")
        
        if self.delay_between_applications < 30:
            errors.append("delay_between_applications should be at least 30 seconds")
        
        if self.max_companies_per_day > 100:
            errors.append("max_companies_per_day should not exceed 100 for reasonable processing limits")
        
        # Check file paths
        if not os.path.exists(os.path.dirname(self.base_resume_path)):
            os.makedirs(os.path.dirname(self.base_resume_path), exist_ok=True)
        
        if not os.path.exists(os.path.dirname(self.companies_config_path)):
            os.makedirs(os.path.dirname(self.companies_config_path), exist_ok=True)
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))
    
    def get_user_agent(self) -> str:
        """Get a respectful user agent string"""
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def should_respect_robots_txt(self, company_name: str) -> bool:
        """Check if we should respect robots.txt for this company"""
        # Always respect robots.txt unless explicitly configured otherwise
        return self.respect_robots_txt

# Global configuration instance
config = CompanyJobSearchConfig()