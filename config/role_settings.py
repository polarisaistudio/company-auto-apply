# config/role_settings.py - Role-specific configuration settings
from dataclasses import dataclass
from typing import List, Dict
from ai_modules.job_classifier import JobRole

@dataclass
class RoleConfig:
    """Configuration for a specific job role"""
    role: JobRole
    daily_limit: int
    resume_template: str
    target_keywords: List[str]
    company_priorities: List[str]
    focus_areas: List[str]
    log_file: str
    resume_output_dir: str

class RoleBasedSettings:
    """Manage role-specific settings and configurations"""
    
    def __init__(self):
        self.role_configs = {
            JobRole.AI_ENGINEER: RoleConfig(
                role=JobRole.AI_ENGINEER,
                daily_limit=25,
                resume_template="templates/ai_engineer_resume.json",
                target_keywords=[
                    "ai engineer", "machine learning engineer", "ml engineer",
                    "applied scientist", "deep learning", "neural networks",
                    "pytorch", "tensorflow", "transformers", "llm", "nlp",
                    "computer vision", "mlops", "model deployment"
                ],
                company_priorities=[
                    # AI-first companies
                    "OpenAI", "Anthropic", "Hugging Face", "Cohere", "Replicate",
                    "Weights & Biases", "AssemblyAI", "Determined AI", "RunPod",
                    # Tech giants with strong AI focus
                    "Microsoft", "Google", "Meta", "Amazon", "Apple",
                    # Companies with ML infrastructure
                    "Databricks", "Snowflake", "Palantir", "Stripe"
                ],
                focus_areas=[
                    "Machine Learning Engineering",
                    "Deep Learning & Neural Networks", 
                    "Natural Language Processing (NLP)",
                    "Computer Vision",
                    "Large Language Models (LLMs)",
                    "MLOps and Model Deployment",
                    "AI Research and Applied Science"
                ],
                log_file="ai_engineer_applications.log",
                resume_output_dir="resumes/ai_engineer"
            ),
            
            JobRole.CLOUD_ENGINEER: RoleConfig(
                role=JobRole.CLOUD_ENGINEER,
                daily_limit=25,
                resume_template="templates/cloud_engineer_resume.json",
                target_keywords=[
                    "cloud engineer", "devops engineer", "sre", "site reliability",
                    "platform engineer", "infrastructure engineer", "aws", "azure",
                    "gcp", "kubernetes", "docker", "terraform", "ansible",
                    "jenkins", "ci/cd", "monitoring", "prometheus", "grafana"
                ],
                company_priorities=[
                    # Cloud-native companies
                    "Vercel", "Netlify", "Cloudflare", "DigitalOcean", "Linode",
                    "HashiCorp", "Docker", "CircleCI", "GitLab",
                    # Cloud providers and infrastructure
                    "Amazon", "Microsoft", "Google", "Oracle",
                    # Companies with heavy cloud infrastructure
                    "Stripe", "Shopify", "GitHub", "Atlassian"
                ],
                focus_areas=[
                    "Cloud Infrastructure (AWS, GCP, Azure)",
                    "Container Orchestration (Kubernetes, Docker)",
                    "Infrastructure as Code (Terraform, Ansible)",
                    "CI/CD Pipelines (Jenkins, GitHub Actions)",
                    "Monitoring & Observability (Prometheus, Grafana)",
                    "Site Reliability Engineering (SRE)",
                    "DevOps & Platform Engineering"
                ],
                log_file="cloud_engineer_applications.log",
                resume_output_dir="resumes/cloud_engineer"
            ),
            
            JobRole.DATA_SCIENTIST: RoleConfig(
                role=JobRole.DATA_SCIENTIST,
                daily_limit=25,
                resume_template="templates/data_scientist_resume.json",
                target_keywords=[
                    "data scientist", "analytics engineer", "business intelligence",
                    "data analyst", "quantitative analyst", "python", "r",
                    "sql", "tableau", "power bi", "statistics", "regression",
                    "clustering", "pandas", "numpy", "scikit-learn", "jupyter"
                ],
                company_priorities=[
                    # Data-focused companies
                    "Databricks", "Snowflake", "Palantir", "Tableau", "Looker",
                    "dbt Labs", "Fivetran", "Airbnb", "Segment", "Mixpanel",
                    # Financial services (heavy data users)
                    "Goldman Sachs", "JPMorgan Chase", "Stripe", "Robinhood",
                    # Tech companies with data products
                    "Meta", "Google", "Microsoft", "Amazon", "Netflix"
                ],
                focus_areas=[
                    "Statistical Analysis & Modeling",
                    "Business Intelligence & Analytics", 
                    "Data Visualization (Tableau, Power BI)",
                    "Python/R Programming & Libraries",
                    "SQL & Database Management",
                    "Machine Learning for Business",
                    "A/B Testing & Experimentation",
                    "Predictive Analytics"
                ],
                log_file="data_scientist_applications.log",
                resume_output_dir="resumes/data_scientist"
            )
        }
    
    def get_role_config(self, role: JobRole) -> RoleConfig:
        """Get configuration for a specific role"""
        return self.role_configs.get(role)
    
    def get_prioritized_companies_for_role(self, role: JobRole, all_companies: List[Dict]) -> List[Dict]:
        """Get companies prioritized for a specific role"""
        role_config = self.get_role_config(role)
        if not role_config:
            return all_companies
        
        prioritized = []
        remaining = []
        
        # First, add companies that are in the priority list
        priority_names = role_config.company_priorities
        for company in all_companies:
            company_name = company.get('name', '')
            if company_name in priority_names:
                prioritized.append(company)
            else:
                remaining.append(company)
        
        # Then add companies that target this specific role
        for company in remaining[:]:
            target_roles = company.get('target_roles', [])
            role_matches = []
            
            if role == JobRole.AI_ENGINEER:
                role_matches = ['AI Engineer', 'Machine Learning', 'ML Engineer', 'Applied Scientist']
            elif role == JobRole.CLOUD_ENGINEER:
                role_matches = ['Cloud Engineer', 'DevOps', 'SRE', 'Platform Engineer']
            elif role == JobRole.DATA_SCIENTIST:
                role_matches = ['Data Scientist', 'Analytics', 'Business Intelligence']
            
            if any(match in str(target_roles) for match in role_matches):
                prioritized.append(company)
                remaining.remove(company)
        
        # Return prioritized companies first, then remaining
        return prioritized + remaining
    
    def get_daily_limits_summary(self) -> Dict[str, int]:
        """Get summary of daily limits for all roles"""
        return {
            "AI Engineer": self.role_configs[JobRole.AI_ENGINEER].daily_limit,
            "Cloud Engineer": self.role_configs[JobRole.CLOUD_ENGINEER].daily_limit,
            "Data Scientist": self.role_configs[JobRole.DATA_SCIENTIST].daily_limit,
            "Total Possible": sum(config.daily_limit for config in self.role_configs.values())
        }
    
    def get_all_target_keywords(self) -> Dict[str, List[str]]:
        """Get all target keywords organized by role"""
        return {
            role.value: config.target_keywords 
            for role, config in self.role_configs.items()
        }
    
    def get_role_focus_areas(self, role: JobRole) -> List[str]:
        """Get focus areas for a specific role"""
        config = self.get_role_config(role)
        return config.focus_areas if config else []

# Global role-based settings instance
role_settings = RoleBasedSettings()