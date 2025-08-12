# Role-Based Job Search Usage Guide

## 🎯 Overview

Your job search system now supports **role-based separation** with specialized workflows for each career path:

- **🤖 AI Engineer** - ML, Deep Learning, LLMs, Computer Vision
- **☁️ Cloud Engineer** - DevOps, SRE, Platform Engineering, Infrastructure  
- **📊 Data Scientist** - Analytics, Business Intelligence, Statistics

## 🚀 Quick Start

### Option 1: Use the Unified Launcher (Recommended)
```bash
python run_job_search.py
```

This interactive launcher lets you:
- Choose specific roles to run
- Run all roles sequentially 
- View configuration and reports
- Monitor previous applications

### Option 2: Run Individual Roles Directly
```bash
# AI Engineer job search
python run_ai_engineer.py

# Cloud Engineer job search  
python run_cloud_engineer.py

# Data Scientist job search
python run_data_scientist.py
```

## 📝 How It Works

### 1. **Role-Specific Targeting**
Each role targets companies that frequently hire for that specific position:

- **AI Engineer**: OpenAI, Anthropic, Hugging Face, Microsoft, Meta
- **Cloud Engineer**: AWS, HashiCorp, GitLab, Vercel, Cloudflare  
- **Data Scientist**: Databricks, Snowflake, Stripe, Goldman Sachs

### 2. **Specialized Resumes**
Each role uses its own optimized resume template:

- `templates/ai_engineer_resume.json` - PyTorch, TensorFlow, LLMs focus
- `templates/cloud_engineer_resume.json` - AWS, Kubernetes, Terraform focus
- `templates/data_scientist_resume.json` - Python, R, SQL, Tableau focus

### 3. **Separate Application Tracking**
Each role maintains separate logs and resume outputs:

```
├── ai_engineer_applications.log           # AI Engineer applications log
├── cloud_engineer_applications.log        # Cloud Engineer applications log  
├── data_scientist_applications.log        # Data Scientist applications log
├── resumes/
│   ├── ai_engineer/                       # AI Engineer customized resumes
│   ├── cloud_engineer/                    # Cloud Engineer customized resumes
│   └── data_scientist/                    # Data Scientist customized resumes
```

## ⚙️ Configuration

### Daily Limits (Per Role)
- **AI Engineer**: 25 applications/day
- **Cloud Engineer**: 25 applications/day  
- **Data Scientist**: 25 applications/day
- **Total Maximum**: 75 applications/day (if running all roles)

### Role-Specific Keywords
Each role searches for specific keywords in job descriptions:

**AI Engineer**: `ai engineer`, `machine learning`, `pytorch`, `tensorflow`, `llm`, `nlp`, `computer vision`

**Cloud Engineer**: `devops`, `kubernetes`, `aws`, `terraform`, `ci/cd`, `monitoring`, `sre`

**Data Scientist**: `data scientist`, `analytics`, `python`, `r`, `sql`, `tableau`, `statistics`

## 📊 Benefits of Role-Based Search

### ✅ **Targeted Applications**
- Each application uses the most relevant resume
- Companies are prioritized by role relevance
- Higher success rates with specialized targeting

### ✅ **Better Organization** 
- Separate logs for each career path
- Easy to track which roles are performing best
- Clear organization of customized resumes

### ✅ **Flexible Execution**
- Run individual roles when needed
- Focus on one career path at a time
- Or run all roles for maximum coverage

### ✅ **Role-Specific Optimization**
- AI Engineer: Emphasizes ML frameworks and model deployment
- Cloud Engineer: Highlights infrastructure and DevOps experience
- Data Scientist: Focuses on analytics and statistical methods

## 🎯 Usage Recommendations

### 1. **Start with One Role**
Begin with your strongest/preferred role to get familiar with the system:
```bash
python run_ai_engineer.py        # If you're strongest in ML/AI
python run_cloud_engineer.py     # If you're strongest in DevOps/Infrastructure  
python run_data_scientist.py     # If you're strongest in Analytics/Data
```

### 2. **Use Sequential Mode for Maximum Coverage**
Run all roles in one session for comprehensive coverage:
```bash
python run_job_search.py
# Select option 4: "Run All Roles (Sequential)"
```

### 3. **Monitor Role Performance**
Check which role gets the best response rates:
```bash
# View logs for each role
tail -n 20 ai_engineer_applications.log
tail -n 20 cloud_engineer_applications.log  
tail -n 20 data_scientist_applications.log
```

### 4. **Customize Per Role**
Update your resume templates based on feedback:
- Edit `templates/ai_engineer_resume.json` for AI roles
- Edit `templates/cloud_engineer_resume.json` for Cloud roles  
- Edit `templates/data_scientist_resume.json` for Data roles

## 🔧 Advanced Configuration

### Company Prioritization
Each role has a prioritized list of companies. You can modify these in `config/role_settings.py`:

```python
# Example: Add more AI-focused companies
company_priorities=[
    "OpenAI", "Anthropic", "Hugging Face", 
    "YourFavoriteAICompany"  # Add here
]
```

### Daily Limits
Adjust daily limits per role in `config/role_settings.py`:

```python
daily_limit=15  # Increase from 10 to 15
```

## 📈 Success Tips

1. **Quality Over Quantity**: Each role applies to maximum 40 companies/day for broader coverage while maintaining quality
2. **Role Relevance**: The system automatically prioritizes companies that hire for each specific role
3. **Resume Optimization**: Each application uses AI to customize the role-specific resume for the company
4. **Manual Review**: Keep manual review enabled to ensure quality applications
5. **Staggered Execution**: Space out role executions throughout the day/week

## 🎉 Example Workflow

```bash
# Monday: Focus on AI Engineer roles
python run_ai_engineer.py

# Tuesday: Focus on Cloud Engineer roles  
python run_cloud_engineer.py

# Wednesday: Focus on Data Scientist roles
python run_data_scientist.py

# Thursday: Run all roles for maximum coverage
python run_job_search.py  # Select option 4
```

This role-based approach ensures you're applying with the most relevant resume and targeting the most appropriate companies for each career path!