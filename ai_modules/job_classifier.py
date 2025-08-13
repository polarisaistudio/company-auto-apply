# ai_modules/job_classifier.py
import openai
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

from scrapers.company_scraper import JobPosting

class JobRole(Enum):
    AI_ENGINEER = "ai_engineer"
    CLOUD_ENGINEER = "cloud_engineer" 
    DATA_SCIENTIST = "data_scientist"
    SECURITY_ANALYST = "security_analyst"
    OTHER = "other"

class JobClassifier:
    """Intelligent job role classification and matching system"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Role-specific keywords and patterns
        self.role_patterns = {
            JobRole.AI_ENGINEER: {
                "primary_keywords": [
                    "ai engineer", "artificial intelligence", "machine learning engineer",
                    "ml engineer", "deep learning", "neural networks", "llm", "nlp",
                    "computer vision", "pytorch", "tensorflow", "transformers",
                    "ai research", "applied scientist", "ml platform", "mlops"
                ],
                "secondary_keywords": [
                    "python", "keras", "scikit-learn", "pandas", "numpy",
                    "model deployment", "model training", "feature engineering",
                    "recommender systems", "reinforcement learning", "gpt", "bert"
                ],
                "anti_keywords": [
                    "purely frontend", "marketing", "sales", "business development"
                ]
            },
            JobRole.CLOUD_ENGINEER: {
                "primary_keywords": [
                    "cloud engineer", "devops", "sre", "site reliability",
                    "infrastructure", "kubernetes", "docker", "aws", "gcp", "azure",
                    "terraform", "ansible", "jenkins", "ci/cd", "platform engineer"
                ],
                "secondary_keywords": [
                    "monitoring", "prometheus", "grafana", "microservices",
                    "containerization", "orchestration", "automation", "scaling",
                    "load balancing", "networking", "security", "compliance"
                ],
                "anti_keywords": [
                    "frontend only", "marketing", "sales", "business development"
                ]
            },
            JobRole.DATA_SCIENTIST: {
                "primary_keywords": [
                    "data scientist", "data science", "analytics", "statistical analysis",
                    "predictive modeling", "data mining", "business intelligence",
                    "data analyst", "quantitative analyst", "research scientist"
                ],
                "secondary_keywords": [
                    "python", "r", "sql", "tableau", "pandas", "numpy", "scipy",
                    "statistics", "hypothesis testing", "a/b testing", "visualization",
                    "reporting", "dashboard", "insights", "experimentation"
                ],
                "anti_keywords": [
                    "purely engineering", "infrastructure only", "marketing", "sales"
                ]
            },
            JobRole.SECURITY_ANALYST: {
                "primary_keywords": [
                    "security analyst", "cybersecurity analyst", "soc analyst", 
                    "information security", "cyber security", "security engineer",
                    "incident response", "threat analysis", "vulnerability assessment",
                    "security operations", "infosec", "cybersecurity specialist"
                ],
                "secondary_keywords": [
                    "siem", "splunk", "wireshark", "nessus", "metasploit", "burp suite",
                    "penetration testing", "ethical hacking", "malware analysis",
                    "forensics", "compliance", "risk assessment", "firewall", "ids",
                    "ips", "threat hunting", "security monitoring", "cissp", "ceh",
                    "sans", "nist", "iso 27001", "pci dss", "gdpr", "hipaa"
                ],
                "anti_keywords": [
                    "purely sales", "marketing only", "business development only"
                ]
            }
        }
    
    def classify_job(self, job: JobPosting) -> Tuple[JobRole, float, Dict]:
        """
        Classify job posting and return role, confidence score, and detailed analysis
        
        Returns:
            Tuple[JobRole, float, Dict]: (role, confidence_score, analysis_details)
        """
        
        # First, try rule-based classification for speed
        rule_based_result = self._rule_based_classification(job)
        
        # If confidence is high enough, return rule-based result
        if rule_based_result[1] > 0.8:
            return rule_based_result
        
        # Otherwise, use AI-powered classification for more nuanced analysis
        ai_result = self._ai_powered_classification(job)
        
        # Combine results for final decision
        final_result = self._combine_classification_results(rule_based_result, ai_result)
        
        self.logger.info(f"Classified job '{job.title}' as {final_result[0].value} with {final_result[1]:.2f} confidence")
        
        return final_result
    
    def _rule_based_classification(self, job: JobPosting) -> Tuple[JobRole, float, Dict]:
        """Fast rule-based classification using keyword matching"""
        
        job_text = (job.title + " " + job.description + " " + job.requirements).lower()
        
        role_scores = {}
        
        for role, patterns in self.role_patterns.items():
            score = 0
            matched_keywords = []
            
            # Primary keywords (higher weight)
            for keyword in patterns["primary_keywords"]:
                if keyword in job_text:
                    score += 2
                    matched_keywords.append(keyword)
            
            # Secondary keywords (lower weight)  
            for keyword in patterns["secondary_keywords"]:
                if keyword in job_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Anti-keywords (negative weight)
            for anti_keyword in patterns["anti_keywords"]:
                if anti_keyword in job_text:
                    score -= 3
            
            # Normalize score by total possible score
            max_possible_score = len(patterns["primary_keywords"]) * 2 + len(patterns["secondary_keywords"])
            normalized_score = max(0, score / max_possible_score) if max_possible_score > 0 else 0
            
            role_scores[role] = {
                "score": normalized_score,
                "matched_keywords": matched_keywords,
                "raw_score": score
            }
        
        # Find best matching role
        best_role = max(role_scores.keys(), key=lambda r: role_scores[r]["score"])
        confidence = role_scores[best_role]["score"]
        
        # If no role has decent confidence, classify as OTHER
        if confidence < 0.3:
            best_role = JobRole.OTHER
            confidence = 0.9  # High confidence that it's OTHER
        
        # Handle reasoning for different roles
        if best_role == JobRole.OTHER:
            reasoning = "No strong keyword matches found, classified as OTHER"
            matched_keywords_count = 0
        else:
            matched_keywords_count = len(role_scores[best_role]['matched_keywords'])
            reasoning = f"Matched {matched_keywords_count} keywords for {best_role.value}"
        
        analysis = {
            "method": "rule_based",
            "all_scores": role_scores,
            "reasoning": reasoning
        }
        
        return best_role, confidence, analysis
    
    def _ai_powered_classification(self, job: JobPosting) -> Tuple[JobRole, float, Dict]:
        """AI-powered classification for nuanced understanding"""
        
        prompt = self._create_classification_prompt(job)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert job classification system. Analyze job postings and classify them into specific technical roles based on requirements, responsibilities, and skills. Be precise and consider the primary focus of the role."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse AI response
            role_mapping = {
                "ai_engineer": JobRole.AI_ENGINEER,
                "cloud_engineer": JobRole.CLOUD_ENGINEER,
                "data_scientist": JobRole.DATA_SCIENTIST,
                "security_analyst": JobRole.SECURITY_ANALYST,
                "other": JobRole.OTHER
            }
            
            classified_role = role_mapping.get(result.get("role", "other"), JobRole.OTHER)
            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "AI classification")
            
            analysis = {
                "method": "ai_powered",
                "reasoning": reasoning,
                "key_factors": result.get("key_factors", [])
            }
            
            return classified_role, confidence, analysis
            
        except Exception as e:
            self.logger.error(f"AI classification failed: {e}")
            # Fallback to OTHER with low confidence
            return JobRole.OTHER, 0.3, {"method": "ai_powered", "error": str(e)}
    
    def _create_classification_prompt(self, job: JobPosting) -> str:
        """Create prompt for AI-powered job classification"""
        
        return f"""
        Analyze this job posting and classify it into one of these roles:

        **ROLE DEFINITIONS:**
        1. **ai_engineer**: Roles focused on building AI/ML systems, training models, deploying ML applications, working with LLMs, computer vision, NLP, or AI research
        2. **cloud_engineer**: Roles focused on cloud infrastructure, DevOps, SRE, platform engineering, containerization, CI/CD, monitoring, or infrastructure automation
        3. **data_scientist**: Roles focused on data analysis, statistical modeling, business intelligence, analytics, experimentation, or extracting insights from data
        4. **security_analyst**: Roles focused on cybersecurity, threat analysis, security monitoring, incident response, vulnerability assessment, or information security
        5. **other**: Roles that don't primarily fit the above categories

        **JOB POSTING:**
        Title: {job.title}
        Company: {job.company}
        Location: {job.location}
        
        Description: {job.description[:1000]}
        
        Requirements: {job.requirements[:800]}

        **ANALYSIS REQUIREMENTS:**
        1. Consider the PRIMARY focus and responsibilities of the role
        2. Look at required skills, tools, and technologies
        3. Consider the job title but prioritize actual responsibilities
        4. Account for hybrid roles but classify based on the main focus

        **OUTPUT FORMAT (JSON only):**
        {{
            "role": "ai_engineer|cloud_engineer|data_scientist|security_analyst|other",
            "confidence": 0.85,
            "reasoning": "Brief explanation of why this role fits the category",
            "key_factors": ["factor1", "factor2", "factor3"]
        }}
        """
    
    def _combine_classification_results(self, rule_result: Tuple, ai_result: Tuple) -> Tuple[JobRole, float, Dict]:
        """Combine rule-based and AI classification results"""
        
        rule_role, rule_confidence, rule_analysis = rule_result
        ai_role, ai_confidence, ai_analysis = ai_result
        
        # If both agree and have reasonable confidence, use that
        if rule_role == ai_role and rule_confidence > 0.5 and ai_confidence > 0.5:
            combined_confidence = (rule_confidence + ai_confidence) / 2
            analysis = {
                "method": "combined",
                "agreement": True,
                "rule_analysis": rule_analysis,
                "ai_analysis": ai_analysis
            }
            return rule_role, combined_confidence, analysis
        
        # If they disagree, prefer the one with higher confidence
        if rule_confidence > ai_confidence:
            final_role, final_confidence, final_analysis = rule_result
        else:
            final_role, final_confidence, final_analysis = ai_result
        
        analysis = {
            "method": "combined",
            "agreement": False,
            "chosen": "rule_based" if rule_confidence > ai_confidence else "ai_powered",
            "rule_result": (rule_role.value, rule_confidence),
            "ai_result": (ai_role.value, ai_confidence),
            "final_analysis": final_analysis
        }
        
        return final_role, final_confidence, analysis
    
    def get_matching_resume_template(self, role: JobRole) -> str:
        """Get the appropriate resume template for the classified role"""
        
        template_mapping = {
            JobRole.AI_ENGINEER: "templates/ai_engineer_resume.json",
            JobRole.CLOUD_ENGINEER: "templates/cloud_engineer_resume.json", 
            JobRole.DATA_SCIENTIST: "templates/data_scientist_resume.json",
            JobRole.SECURITY_ANALYST: "templates/security_analyst_resume.json",
            JobRole.OTHER: "templates/base_resume.json"  # Default fallback
        }
        
        return template_mapping[role]
    
    def should_apply_to_job(self, job: JobPosting, min_confidence: float = 0.6) -> Tuple[bool, JobRole, float]:
        """
        Determine if we should apply to this job based on role matching
        
        Returns:
            Tuple[bool, JobRole, float]: (should_apply, classified_role, confidence)
        """
        
        role, confidence, analysis = self.classify_job(job)
        
        # Don't apply to OTHER roles or low-confidence matches
        if role == JobRole.OTHER or confidence < min_confidence:
            return False, role, confidence
        
        return True, role, confidence
    
    def get_role_specific_keywords(self, role: JobRole) -> List[str]:
        """Get keywords for a specific role for targeting"""
        
        if role in self.role_patterns:
            return self.role_patterns[role]["primary_keywords"] + self.role_patterns[role]["secondary_keywords"]
        
        return []
    
    def analyze_job_market_fit(self, jobs: List[JobPosting]) -> Dict:
        """Analyze a list of jobs to understand market fit for each role"""
        
        role_counts = {role: 0 for role in JobRole}
        role_companies = {role: set() for role in JobRole}
        
        for job in jobs:
            role, confidence, _ = self.classify_job(job)
            if confidence > 0.6:
                role_counts[role] += 1
                role_companies[role].add(job.company)
        
        return {
            "total_jobs": len(jobs),
            "role_distribution": {role.value: count for role, count in role_counts.items()},
            "companies_by_role": {role.value: list(companies) for role, companies in role_companies.items()},
            "market_insights": self._generate_market_insights(role_counts, role_companies)
        }
    
    def _generate_market_insights(self, role_counts: Dict, role_companies: Dict) -> Dict:
        """Generate insights about job market trends"""
        
        total_relevant_jobs = sum(count for role, count in role_counts.items() if role != JobRole.OTHER)
        
        if total_relevant_jobs == 0:
            return {"message": "No relevant jobs found in current market scan"}
        
        most_available_role = max(
            [role for role in role_counts.keys() if role != JobRole.OTHER],
            key=lambda r: role_counts[r]
        )
        
        return {
            "most_available_role": most_available_role.value,
            "most_available_count": role_counts[most_available_role],
            "total_relevant_jobs": total_relevant_jobs,
            "recommendation": f"Focus on {most_available_role.value} roles - {role_counts[most_available_role]} opportunities found"
        }