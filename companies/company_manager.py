# companies/company_manager.py
import json
import os
import logging
from typing import List, Dict, Optional
from urllib.robotparser import RobotFileParser

from config.settings import config

class CompanyManager:
    """Manages target companies and their configurations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.companies_file = config.companies_config_path
        self._ensure_companies_file_exists()
    
    def _ensure_companies_file_exists(self):
        """Create default companies file if it doesn't exist"""
        
        if not os.path.exists(self.companies_file):
            default_companies = self._get_default_companies()
            self.save_companies_config(default_companies)
            self.logger.info(f"Created default companies configuration at {self.companies_file}")
    
    def _get_default_companies(self) -> List[Dict]:
        """Get default company configurations"""
        
        return [
            {
                "name": "Stripe",
                "careers_url": "https://stripe.com/jobs",
                "application_patterns": {
                    "job_links": [
                        "a[href*='/jobs/']",
                        "a[href*='/careers/']"
                    ],
                    "apply_buttons": [
                        "button:contains('Apply')",
                        "a:contains('Apply')",
                        "input[value*='Apply']"
                    ]
                },
                "target_roles": [
                    "Software Engineer",
                    "Frontend Engineer", 
                    "Backend Engineer",
                    "Full Stack Engineer"
                ],
                "preferred_locations": ["Remote", "San Francisco", "New York"],
                "company_values": [
                    "Financial infrastructure",
                    "Developer-first",
                    "Global payments"
                ],
                "notes": "Great engineering culture, remote-friendly"
            },
            {
                "name": "Shopify",
                "careers_url": "https://www.shopify.com/careers",
                "application_patterns": {
                    "job_links": [
                        "a[href*='/careers/']",
                        "a[href*='/jobs/']"
                    ],
                    "apply_buttons": [
                        "button:contains('Apply')",
                        "a.btn:contains('Apply')"
                    ]
                },
                "target_roles": [
                    "Developer",
                    "Software Engineer",
                    "Technical Support"
                ],
                "preferred_locations": ["Remote", "Toronto", "Ottawa"],
                "company_values": [
                    "E-commerce platform",
                    "Entrepreneurship",
                    "Remote-first"
                ],
                "notes": "Strong remote culture, e-commerce focus"
            },
            {
                "name": "Vercel",
                "careers_url": "https://vercel.com/careers",
                "application_patterns": {
                    "job_links": [
                        "a[href*='/careers']",
                        "a[href*='job']"
                    ],
                    "apply_buttons": [
                        "button:contains('Apply')",
                        "a:contains('Apply now')"
                    ]
                },
                "target_roles": [
                    "Frontend Engineer",
                    "Full Stack Engineer",
                    "Developer Experience",
                    "Technical Support"
                ],
                "preferred_locations": ["Remote", "San Francisco"],
                "company_values": [
                    "Frontend infrastructure", 
                    "Developer experience",
                    "Performance"
                ],
                "notes": "Frontend-focused, excellent developer tools"
            },
            {
                "name": "Supabase",
                "careers_url": "https://supabase.com/careers",
                "application_patterns": {
                    "job_links": [
                        "a[href*='careers']",
                        "a[href*='jobs']"
                    ],
                    "apply_buttons": [
                        "button:contains('Apply')",
                        "a:contains('Apply')"
                    ]
                },
                "target_roles": [
                    "Software Engineer",
                    "Developer Advocate",
                    "Technical Support"
                ],
                "preferred_locations": ["Remote"],
                "company_values": [
                    "Open source",
                    "Firebase alternative", 
                    "Developer tools"
                ],
                "notes": "Open source Firebase alternative, remote-first"
            },
            {
                "name": "Railway",
                "careers_url": "https://railway.app/careers",
                "application_patterns": {
                    "job_links": [
                        "a[href*='careers']"
                    ],
                    "apply_buttons": [
                        "button:contains('Apply')",
                        "a:contains('Apply')"
                    ]
                },
                "target_roles": [
                    "Software Engineer",
                    "Frontend Engineer",
                    "Customer Success"
                ],
                "preferred_locations": ["Remote"],
                "company_values": [
                    "Infrastructure",
                    "Developer experience",
                    "Simplicity"
                ],
                "notes": "Infrastructure platform, developer-focused"
            }
        ]
    
    def get_target_companies(self) -> List[Dict]:
        """Load and return target companies configuration"""
        
        try:
            with open(self.companies_file, 'r', encoding='utf-8') as f:
                companies = json.load(f)
            
            # Validate and filter active companies
            active_companies = []
            for company in companies:
                if company.get('active', True):  # Default to active
                    if self._validate_company_config(company):
                        active_companies.append(company)
            
            self.logger.info(f"Loaded {len(active_companies)} active companies")
            return active_companies
            
        except FileNotFoundError:
            self.logger.error(f"Companies file not found: {self.companies_file}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in companies file: {e}")
            return []
    
    def _validate_company_config(self, company: Dict) -> bool:
        """Validate individual company configuration"""
        
        required_fields = ['name', 'careers_url']
        
        for field in required_fields:
            if field not in company:
                self.logger.warning(f"Company config missing required field '{field}': {company.get('name', 'Unknown')}")
                return False
        
        return True
    
    def add_company(self, company_config: Dict):
        """Add a new company to the configuration"""
        
        companies = self.get_target_companies()
        
        # Check if company already exists
        existing_names = [c['name'].lower() for c in companies]
        if company_config['name'].lower() in existing_names:
            self.logger.warning(f"Company {company_config['name']} already exists")
            return False
        
        companies.append(company_config)
        self.save_companies_config(companies)
        
        self.logger.info(f"Added company: {company_config['name']}")
        return True
    
    def update_company(self, company_name: str, updates: Dict):
        """Update an existing company configuration"""
        
        companies = self.get_target_companies()
        
        for i, company in enumerate(companies):
            if company['name'].lower() == company_name.lower():
                companies[i].update(updates)
                self.save_companies_config(companies)
                self.logger.info(f"Updated company: {company_name}")
                return True
        
        self.logger.warning(f"Company not found for update: {company_name}")
        return False
    
    def disable_company(self, company_name: str):
        """Disable a company (set active=False)"""
        
        return self.update_company(company_name, {'active': False})
    
    def save_companies_config(self, companies: List[Dict]):
        """Save companies configuration to file"""
        
        os.makedirs(os.path.dirname(self.companies_file), exist_ok=True)
        
        with open(self.companies_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
    
    def check_robots_txt(self, company_config: Dict) -> bool:
        """Check if robots.txt allows our access"""
        
        if not config.respect_robots_txt:
            return True
        
        try:
            base_url = company_config['careers_url']
            
            # Extract domain
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Check if our user agent can fetch the careers page
            user_agent = config.get_user_agent()
            can_fetch = rp.can_fetch(user_agent, company_config['careers_url'])
            
            if not can_fetch:
                self.logger.warning(f"robots.txt disallows access to {company_config['name']} careers page")
            
            return can_fetch
            
        except Exception as e:
            self.logger.debug(f"Could not check robots.txt for {company_config['name']}: {e}")
            # If we can't check, err on the side of being respectful
            return True
    
    def get_company_by_name(self, name: str) -> Optional[Dict]:
        """Get specific company configuration by name"""
        
        companies = self.get_target_companies()
        
        for company in companies:
            if company['name'].lower() == name.lower():
                return company
        
        return None
    
    def list_companies(self) -> List[str]:
        """Get list of all company names"""
        
        companies = self.get_target_companies()
        return [company['name'] for company in companies]