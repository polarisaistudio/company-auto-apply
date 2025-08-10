# scrapers/company_scraper.py
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass
from typing import List, Optional
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from config.settings import config

@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    requirements: str
    url: str
    salary: str = ""
    job_type: str = ""
    posted_date: str = ""
    department: str = ""

class CompanyScraper:
    """Scraper for discovering and extracting jobs from company websites"""
    
    def __init__(self, company_config: dict, headless: bool = False):
        self.company_config = company_config
        self.company_name = company_config['name']
        self.careers_url = company_config['careers_url']
        self.logger = logging.getLogger(__name__)
        
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool):
        """Setup Selenium WebDriver with respectful settings"""
        
        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        # Respectful browser settings
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Use a realistic user agent
        options.add_argument(f"--user-agent={config.get_user_agent()}")
        
        # Don't load images to be more respectful of bandwidth
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(config.browser_timeout)
        
        self.logger.info(f"Initialized browser for {self.company_name}")
    
    async def discover_jobs(self) -> List[JobPosting]:
        """Discover job postings on the company's careers page"""
        
        self.logger.info(f"Discovering jobs at {self.company_name}")
        
        try:
            # Navigate to careers page
            self.driver.get(self.careers_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give the page time to fully render
            time.sleep(3)
            
            # Extract job links
            job_links = self._extract_job_links()
            
            if not job_links:
                self.logger.warning(f"No job links found on {self.company_name} careers page")
                return []
            
            self.logger.info(f"Found {len(job_links)} job links at {self.company_name}")
            
            # Extract detailed job information
            jobs = []
            for link in job_links[:config.max_pages_per_company * 10]:  # Reasonable limit
                try:
                    job = self._extract_job_details(link)
                    if job and self._is_relevant_job(job):
                        jobs.append(job)
                    
                    # Respectful delay between job page visits
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    self.logger.debug(f"Error extracting job details from {link}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(jobs)} relevant jobs from {self.company_name}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error discovering jobs at {self.company_name}: {e}")
            return []
    
    def _extract_job_links(self) -> List[str]:
        """Extract job posting links from careers page"""
        
        job_links = set()
        patterns = self.company_config.get('application_patterns', {}).get('job_links', [])
        
        # Default patterns if none specified
        if not patterns:
            patterns = [
                "a[href*='job']",
                "a[href*='career']", 
                "a[href*='position']",
                "a[href*='opening']"
            ]
        
        for pattern in patterns:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                
                for element in elements:
                    href = element.get_attribute('href')
                    if href:
                        # Convert relative URLs to absolute
                        absolute_url = urljoin(self.careers_url, href)
                        job_links.add(absolute_url)
                        
            except Exception as e:
                self.logger.debug(f"Error with pattern {pattern}: {e}")
                continue
        
        # Also try common job listing containers
        try:
            job_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                ".job, .position, .role, .opening, [class*='job'], [class*='career'], [class*='position']")
            
            for container in job_containers:
                links = container.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute('href')
                    if href and any(keyword in href.lower() for keyword in ['job', 'career', 'position', 'role']):
                        absolute_url = urljoin(self.careers_url, href)
                        job_links.add(absolute_url)
                        
        except Exception as e:
            self.logger.debug(f"Error extracting from job containers: {e}")
        
        return list(job_links)
    
    def _extract_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Extract detailed job information from a job posting page"""
        
        try:
            self.driver.get(job_url)
            
            # Wait for page content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(2)  # Let content load
            
            # Extract job title
            title = self._extract_text_by_selectors([
                "h1",
                ".job-title",
                "[class*='title']",
                "[class*='job-name']",
                "title"
            ], "Job Title Not Found")
            
            # Extract location
            location = self._extract_text_by_selectors([
                "[class*='location']",
                "[class*='city']", 
                "[class*='office']",
                "span:contains('Remote')",
                "span:contains('Location')"
            ], "Location Not Specified")
            
            # Extract salary if available
            salary = self._extract_text_by_selectors([
                "[class*='salary']",
                "[class*='compensation']",
                "[class*='pay']",
                "span:contains('$')"
            ], "")
            
            # Extract department
            department = self._extract_text_by_selectors([
                "[class*='department']",
                "[class*='team']",
                "[class*='division']"
            ], "")
            
            # Extract job description
            description_selectors = [
                ".job-description",
                "[class*='description']",
                "[class*='content']",
                ".job-content",
                "main",
                "article"
            ]
            
            description = ""
            for selector in description_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    description = element.text.strip()
                    if len(description) > 100:  # Make sure we got substantial content
                        break
                except:
                    continue
            
            # Extract requirements from description
            requirements = self._extract_requirements(description)
            
            return JobPosting(
                title=title,
                company=self.company_name,
                location=location,
                description=description,
                requirements=requirements,
                url=job_url,
                salary=salary,
                department=department
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting job details from {job_url}: {e}")
            return None
    
    def _extract_text_by_selectors(self, selectors: List[str], default: str = "") -> str:
        """Try multiple selectors to extract text content"""
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        
        return default
    
    def _extract_requirements(self, description: str) -> str:
        """Extract requirements section from job description"""
        
        requirements_keywords = [
            "requirements", "qualifications", "skills", "experience",
            "required", "must have", "preferred", "desired", "you have"
        ]
        
        lines = description.split('\n')
        requirements_lines = []
        
        in_requirements_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts a requirements section
            if any(keyword in line_lower for keyword in requirements_keywords):
                in_requirements_section = True
                requirements_lines.append(line.strip())
                continue
            
            # If we're in requirements section, continue adding lines
            if in_requirements_section:
                if line.strip():
                    # Stop if we hit a new major section
                    if any(keyword in line_lower for keyword in ['responsibilities', 'benefits', 'about us', 'company']):
                        break
                    requirements_lines.append(line.strip())
                else:
                    # Empty line might indicate end of section
                    if len(requirements_lines) > 3:  # We have some content
                        break
        
        requirements_text = '\n'.join(requirements_lines)
        
        # If we didn't find a clear requirements section, return first part of description
        if not requirements_text or len(requirements_text) < 50:
            return description[:500] + "..." if len(description) > 500 else description
        
        return requirements_text
    
    def _is_relevant_job(self, job: JobPosting) -> bool:
        """Check if job is relevant based on company configuration"""
        
        target_roles = self.company_config.get('target_roles', config.target_roles)
        
        if not target_roles:
            return True  # If no specific roles defined, consider all relevant
        
        job_title_lower = job.title.lower()
        job_desc_lower = job.description.lower()
        
        # Check if job title or description contains target role keywords
        for role in target_roles:
            role_lower = role.lower()
            if (role_lower in job_title_lower or 
                any(word in job_title_lower for word in role_lower.split()) or
                role_lower in job_desc_lower):
                return True
        
        return False
    
    def close(self):
        """Close the browser driver"""
        
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.logger.info(f"Closed browser for {self.company_name}")