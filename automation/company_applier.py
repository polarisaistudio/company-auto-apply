# automation/company_applier.py
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict, Optional

from scrapers.company_scraper import JobPosting
from config.settings import config

class CompanyApplier:
    """Generic form automation for company website applications"""
    
    def __init__(self, driver: webdriver.Chrome, company_name: str):
        self.driver = driver
        self.company_name = company_name
        self.logger = logging.getLogger(__name__)
    
    def apply_to_job(self, job: JobPosting, resume_path: str, cover_letter: str) -> bool:
        """Apply to job on company website"""
        
        self.logger.info(f"Starting application to {job.title} at {job.company}")
        
        try:
            # Navigate to job posting page
            self.driver.get(job.url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Let page fully render
            
            # Find and click apply button
            if not self._find_and_click_apply_button():
                self.logger.warning(f"Could not find apply button for {job.title}")
                return False
            
            # Wait for application form to appear
            time.sleep(5)
            
            # Fill out the application form
            form_filled = self._fill_application_form(job)
            
            if not form_filled:
                self.logger.warning(f"Could not fill application form for {job.title}")
                return False
            
            # Handle file uploads
            files_uploaded = self._handle_file_uploads(resume_path, cover_letter)
            
            # Add cover letter text if there's a text area
            self._add_cover_letter_text(cover_letter)
            
            # Final review before submission
            if config.require_manual_review:
                if not self._manual_submission_review(job):
                    self.logger.info(f"Application cancelled by user for {job.title}")
                    return False
            
            # Submit the application
            submitted = self._submit_application()
            
            if submitted:
                self.logger.info(f"Successfully submitted application for {job.title}")
                return True
            else:
                self.logger.warning(f"Failed to submit application for {job.title}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying to {job.title}: {e}")
            return False
    
    def _find_and_click_apply_button(self) -> bool:
        """Find and click the apply button using various strategies"""
        
        # Try multiple selectors for apply buttons
        apply_selectors = [
            "button:contains('Apply')",
            "a:contains('Apply')",
            "input[value*='Apply']",
            "button[class*='apply']",
            "a[class*='apply']",
            ".apply-button",
            ".apply-btn",
            "#apply-button",
            "#apply-btn"
        ]
        
        # Also try text-based search
        text_searches = [
            "Apply for this job",
            "Apply now",
            "Submit application",
            "Apply"
        ]
        
        # Try CSS selectors first
        for selector in apply_selectors:
            try:
                if ":contains(" in selector:
                    # Handle jQuery-style selectors with XPath
                    text = selector.split("'")[1]
                    xpath = f"//button[contains(text(), '{text}')] | //a[contains(text(), '{text}')] | //input[@value[contains(., '{text}')]]"
                    element = self.driver.find_element(By.XPATH, xpath)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    self.logger.info("Found and clicked apply button")
                    return True
                    
            except (NoSuchElementException, TimeoutException):
                continue
        
        # Try searching by text content
        for text in text_searches:
            try:
                xpath = f"//button[contains(., '{text}')] | //a[contains(., '{text}')] | //input[@value[contains(., '{text}')]]"
                elements = self.driver.find_elements(By.XPATH, xpath)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        self.logger.info(f"Found and clicked apply button with text: {text}")
                        return True
                        
            except Exception:
                continue
        
        # Try looking for buttons in common container classes
        container_selectors = [
            ".job-actions",
            ".job-buttons", 
            ".application-section",
            ".apply-section"
        ]
        
        for container_selector in container_selectors:
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                buttons = container.find_elements(By.TAG_NAME, "button")
                buttons.extend(container.find_elements(By.TAG_NAME, "a"))
                
                for button in buttons:
                    if ("apply" in button.text.lower() or 
                        "apply" in button.get_attribute("class").lower()):
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            self.logger.info("Found apply button in container")
                            return True
                            
            except (NoSuchElementException, TimeoutException):
                continue
        
        return False
    
    def _fill_application_form(self, job: JobPosting) -> bool:
        """Fill out the application form with personal information"""
        
        self.logger.info("Filling application form")
        
        # Common field mappings
        personal_info = config.personal_info
        
        field_mappings = {
            "first_name": personal_info.get("name", "").split()[0] if personal_info.get("name") else "",
            "last_name": personal_info.get("name", "").split()[-1] if personal_info.get("name") else "",
            "full_name": personal_info.get("name", ""),
            "email": personal_info.get("email", ""),
            "phone": personal_info.get("phone", ""),
            "linkedin": personal_info.get("linkedin", ""),
            "github": personal_info.get("github", ""),
            "portfolio": personal_info.get("portfolio", ""),
            "website": personal_info.get("portfolio", "") or personal_info.get("github", "")
        }
        
        fields_filled = 0
        
        # Try to fill each field type
        for field_type, value in field_mappings.items():
            if not value:
                continue
                
            filled = self._fill_field_by_type(field_type, value)
            if filled:
                fields_filled += 1
                time.sleep(random.uniform(0.5, 1.5))  # Human-like delay
        
        self.logger.info(f"Filled {fields_filled} form fields")
        
        # Also try to fill any other visible required fields
        self._fill_additional_required_fields()
        
        return fields_filled > 0
    
    def _fill_field_by_type(self, field_type: str, value: str) -> bool:
        """Fill a specific type of field with various selector strategies"""
        
        # Generate possible selectors for this field type
        selectors = self._generate_field_selectors(field_type)
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Clear and fill the field
                        element.clear()
                        element.send_keys(value)
                        
                        # Verify the value was entered
                        time.sleep(0.5)
                        if element.get_attribute('value') == value:
                            self.logger.debug(f"Successfully filled {field_type} field")
                            return True
                            
            except Exception as e:
                self.logger.debug(f"Error with selector {selector} for {field_type}: {e}")
                continue
        
        return False
    
    def _generate_field_selectors(self, field_type: str) -> List[str]:
        """Generate CSS selectors for different field types"""
        
        base_selectors = [
            f"input[name*='{field_type}']",
            f"input[id*='{field_type}']",
            f"input[placeholder*='{field_type}']",
            f"input[class*='{field_type}']"
        ]
        
        # Add variations and alternatives
        if field_type == "first_name":
            base_selectors.extend([
                "input[name*='first']",
                "input[name*='fname']", 
                "input[placeholder*='First name']",
                "input[placeholder*='First Name']"
            ])
        elif field_type == "last_name":
            base_selectors.extend([
                "input[name*='last']",
                "input[name*='lname']",
                "input[placeholder*='Last name']",
                "input[placeholder*='Last Name']"
            ])
        elif field_type == "full_name":
            base_selectors.extend([
                "input[name*='name']",
                "input[placeholder*='Full name']",
                "input[placeholder*='Your name']"
            ])
        elif field_type == "email":
            base_selectors.extend([
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']"
            ])
        elif field_type == "phone":
            base_selectors.extend([
                "input[type='tel']",
                "input[name*='phone']",
                "input[placeholder*='phone']"
            ])
        
        return base_selectors
    
    def _fill_additional_required_fields(self):
        """Fill any other visible required fields with reasonable defaults"""
        
        try:
            # Find required fields
            required_selectors = [
                "input[required]",
                "input[aria-required='true']",
                "select[required]",
                "textarea[required]"
            ]
            
            for selector in required_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if not element.is_displayed() or not element.is_enabled():
                        continue
                    
                    # Skip if already filled
                    if element.get_attribute('value'):
                        continue
                    
                    element_type = element.tag_name.lower()
                    input_type = element.get_attribute('type')
                    
                    # Handle different field types
                    if element_type == 'select':
                        self._handle_select_field(element)
                    elif input_type == 'checkbox':
                        # Generally don't check checkboxes automatically
                        pass
                    elif input_type == 'radio':
                        # Don't select radio buttons automatically
                        pass
                    else:
                        # For text fields, try to infer what they want
                        placeholder = element.get_attribute('placeholder') or ""
                        name = element.get_attribute('name') or ""
                        
                        default_value = self._get_default_value_for_field(placeholder, name)
                        if default_value:
                            element.send_keys(default_value)
                            time.sleep(0.5)
                            
        except Exception as e:
            self.logger.debug(f"Error filling additional required fields: {e}")
    
    def _handle_select_field(self, select_element):
        """Handle dropdown/select fields"""
        
        try:
            select = Select(select_element)
            options = select.options
            
            # Skip first option if it's a placeholder
            if len(options) > 1:
                first_option_text = options[0].text.lower()
                if any(word in first_option_text for word in ['select', 'choose', 'please', '--']):
                    select.select_by_index(1)
                else:
                    select.select_by_index(0)
                    
        except Exception as e:
            self.logger.debug(f"Error handling select field: {e}")
    
    def _get_default_value_for_field(self, placeholder: str, name: str) -> Optional[str]:
        """Get a reasonable default value for a field based on its context"""
        
        field_context = (placeholder + " " + name).lower()
        
        # Common field patterns and their defaults
        if any(word in field_context for word in ['city', 'location']):
            return "Remote"
        elif any(word in field_context for word in ['country']):
            return "United States"
        elif any(word in field_context for word in ['state', 'province']):
            return "CA"
        elif any(word in field_context for word in ['hear', 'source', 'how did you']):
            return "Company website"
        
        return None
    
    def _handle_file_uploads(self, resume_path: str, cover_letter: str) -> bool:
        """Handle resume and cover letter file uploads"""
        
        self.logger.info("Looking for file upload fields")
        
        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        
        files_uploaded = 0
        
        for file_input in file_inputs:
            if not file_input.is_displayed():
                continue
            
            # Determine what type of file this input expects
            accept_attr = file_input.get_attribute('accept') or ""
            name_attr = file_input.get_attribute('name') or ""
            id_attr = file_input.get_attribute('id') or ""
            
            context = (accept_attr + " " + name_attr + " " + id_attr).lower()
            
            try:
                if any(word in context for word in ['resume', 'cv']):
                    # This is likely for a resume
                    file_input.send_keys(resume_path)
                    files_uploaded += 1
                    self.logger.info("Uploaded resume file")
                    
                elif any(word in context for word in ['cover', 'letter']):
                    # This is likely for a cover letter
                    # We'd need to create a file from the cover letter text
                    cover_letter_path = self._create_cover_letter_file(cover_letter)
                    if cover_letter_path:
                        file_input.send_keys(cover_letter_path)
                        files_uploaded += 1
                        self.logger.info("Uploaded cover letter file")
                        
                else:
                    # Generic file upload - default to resume
                    file_input.send_keys(resume_path)
                    files_uploaded += 1
                    self.logger.info("Uploaded file (defaulted to resume)")
                
                time.sleep(2)  # Wait for upload to process
                
            except Exception as e:
                self.logger.debug(f"Error uploading file: {e}")
                continue
        
        self.logger.info(f"Uploaded {files_uploaded} files")
        return files_uploaded > 0
    
    def _create_cover_letter_file(self, cover_letter: str) -> Optional[str]:
        """Create a temporary cover letter file"""
        
        try:
            import tempfile
            import os
            
            # Create a temporary text file with the cover letter
            temp_dir = tempfile.gettempdir()
            cover_letter_path = os.path.join(temp_dir, f"cover_letter_{int(time.time())}.txt")
            
            with open(cover_letter_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter)
            
            return cover_letter_path
            
        except Exception as e:
            self.logger.error(f"Error creating cover letter file: {e}")
            return None
    
    def _add_cover_letter_text(self, cover_letter: str):
        """Add cover letter text to text areas"""
        
        # Look for text areas that might be for cover letters
        text_areas = self.driver.find_elements(By.TAG_NAME, "textarea")
        
        for textarea in text_areas:
            if not textarea.is_displayed() or not textarea.is_enabled():
                continue
            
            # Check if this textarea is likely for a cover letter
            context = (
                textarea.get_attribute('placeholder') or "" +
                textarea.get_attribute('name') or "" +
                textarea.get_attribute('id') or ""
            ).lower()
            
            if any(word in context for word in ['cover', 'letter', 'message', 'additional', 'why']):
                try:
                    textarea.clear()
                    textarea.send_keys(cover_letter)
                    self.logger.info("Added cover letter text to textarea")
                    break
                except Exception as e:
                    self.logger.debug(f"Error adding cover letter text: {e}")
    
    def _manual_submission_review(self, job: JobPosting) -> bool:
        """Allow manual review before submitting"""
        
        print("\n" + "="*80)
        print("FINAL APPLICATION REVIEW")
        print("="*80)
        print(f"Ready to submit application for:")
        print(f"Position: {job.title}")
        print(f"Company: {job.company}")
        print(f"URL: {job.url}")
        print("\nPlease review the filled form in the browser window.")
        print("="*80)
        
        while True:
            response = input("Submit this application? (y/n/e=edit): ").lower().strip()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 'e':
                input("Make your edits in the browser, then press Enter to continue...")
                continue
            else:
                print("Please enter 'y' to submit, 'n' to skip, or 'e' to edit")
    
    def _submit_application(self) -> bool:
        """Submit the application form"""
        
        self.logger.info("Attempting to submit application")
        
        # Try to find submit button
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Submit')",
            "button:contains('Send')",
            "button:contains('Apply')",
            ".submit-button",
            ".submit-btn",
            "#submit-button",
            "#submit-btn"
        ]
        
        for selector in submit_selectors:
            try:
                if ":contains(" in selector:
                    # Handle jQuery-style selectors
                    text = selector.split("'")[1]
                    xpath = f"//button[contains(text(), '{text}')] | //input[@value[contains(., '{text}')]]"
                    element = self.driver.find_element(By.XPATH, xpath)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    self.logger.info("Clicked submit button")
                    
                    # Wait and check for success indicators
                    time.sleep(3)
                    return self._check_submission_success()
                    
            except (NoSuchElementException, TimeoutException):
                continue
        
        # Try pressing Enter on the last focused element
        try:
            self.driver.switch_to.active_element.send_keys(Keys.RETURN)
            time.sleep(3)
            return self._check_submission_success()
        except:
            pass
        
        return False
    
    def _check_submission_success(self) -> bool:
        """Check if the application was successfully submitted"""
        
        success_indicators = [
            "thank you",
            "application submitted",
            "application received", 
            "successfully submitted",
            "we'll be in touch",
            "confirmation",
            "success"
        ]
        
        try:
            page_text = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    self.logger.info(f"Success indicator found: {indicator}")
                    return True
            
            # Check URL for success indicators
            current_url = self.driver.current_url.lower()
            if any(word in current_url for word in ['success', 'thank', 'confirmation']):
                return True
                
        except Exception as e:
            self.logger.debug(f"Error checking submission success: {e}")
        
        return False