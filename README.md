# Company-Focused Auto-Apply System

🎯 **Ethical job application automation for company websites**

This system focuses on applying directly to companies through their career websites, avoiding the legal and ethical issues associated with platform automation like LinkedIn or Indeed.

## ✅ Why Company Websites Are Better

**Legal Benefits:**
- ✅ No platform Terms of Service violations
- ✅ Direct relationship with employers  
- ✅ Minimal legal risk
- ✅ Respectful of company policies

**Quality Benefits:**
- 🎯 More targeted approach - you choose specific companies
- 🔍 Encourages research before applying
- 💼 Better impression on employers
- 📈 Higher quality applications over quantity

**Technical Benefits:**
- 🛡️ Less sophisticated bot detection
- 🔧 Simpler, more predictable form structures
- 🚀 More reliable automation
- ⚡ Better success rates

## 🏗️ System Architecture

```
company-auto-apply/
├── main.py                    # Main orchestrator with ethical safeguards
├── config/                    
│   └── settings.py           # Conservative, ethical configuration
├── companies/
│   ├── company_manager.py    # Manage target companies
│   └── target_companies.json # Your curated company list
├── scrapers/
│   └── company_scraper.py    # Respectful company website scraping
├── automation/
│   └── company_applier.py    # Generic form automation
├── ai_modules/
│   ├── resume_generator.py   # Company-specific resume optimization
│   └── cover_letter_generator.py # Personalized cover letters
├── tracking/
│   └── application_tracker.py # Enhanced application tracking
└── templates/
    └── base_resume.json      # Your base resume template
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repository-url>
cd company-auto-apply
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
# Edit .env with your information
```

### 2. Configure Your Information

Edit `.env` file:
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
USER_NAME=Your Full Name
USER_EMAIL=your.email@example.com

# Recommended for better applications
USER_PHONE=+1-555-123-4567
USER_LINKEDIN=linkedin.com/in/your-profile
USER_GITHUB=github.com/your-username
USER_PORTFOLIO=https://your-portfolio.com
```

### 3. Setup Your Resume

Edit `templates/base_resume.json` with your actual experience, skills, and achievements.

### 4. Choose Target Companies

The system comes with curated company examples (Stripe, Shopify, Vercel, etc.). 

Edit `companies/target_companies.json` to:
- ✅ Keep companies you're genuinely interested in
- ❌ Remove companies that don't align with your goals
- ➕ Add companies you've researched and want to target

### 5. Run the System

```bash
python main.py
```

The system will:
1. 🚨 Show ethical warnings and guidelines
2. 🎯 Process your target companies one by one
3. 🔍 Discover relevant job openings
4. 📝 Generate customized resumes and cover letters
5. 🤔 Ask for manual review (highly recommended)
6. 📤 Submit applications respectfully
7. 📊 Track everything in a database

## ⚖️ Ethical Guidelines

This system is designed with ethics as a priority:

### Built-in Safeguards

- **Manual Review**: Each application can be reviewed before submission
- **Conservative Limits**: Max 15 applications/day, 5 companies/day
- **Respectful Delays**: 90+ seconds between applications, 3+ minutes between companies
- **robots.txt Compliance**: Respects website policies
- **Quality over Quantity**: Focus on companies you actually want to work for

### Best Practices

1. **Research First**: Only target companies you've researched and genuinely want to work for
2. **Start Small**: Begin with 5-10 applications per day maximum
3. **Manual Review**: Always review applications before submitting
4. **Follow Up**: Use the tracking system to manage follow-ups professionally
5. **Be Honest**: Never let AI generate false information in your applications

## 🎯 Target Company Management

### Default Companies Included

The system includes examples of developer-friendly companies:
- **Stripe**: Financial infrastructure, great engineering culture
- **Shopify**: E-commerce platform, remote-friendly
- **Vercel**: Frontend infrastructure, excellent developer tools
- **Supabase**: Open source Firebase alternative
- **Railway**: Infrastructure platform, developer-focused

### Adding Your Own Companies

```json
{
  "name": "Company Name",
  "careers_url": "https://company.com/careers",
  "target_roles": ["Software Engineer", "Frontend Developer"],
  "preferred_locations": ["Remote", "San Francisco"],
  "company_values": ["Innovation", "Remote work", "Open source"],
  "notes": "Why you want to work here"
}
```

## 🤖 AI-Powered Customization

### Resume Optimization
- **Company-specific**: Tailors your resume for each company's values and needs
- **Role-focused**: Emphasizes relevant experience for specific positions  
- **Truthful**: Never invents experience or skills you don't have
- **Professional**: Maintains your authentic professional brand

### Cover Letter Generation
- **Personalized**: Shows genuine interest in the specific company
- **Research-based**: Incorporates company knowledge and values
- **Role-relevant**: Connects your background to the specific position
- **Compelling**: Engaging tone that stands out from generic applications

## 📊 Advanced Tracking

### Application Management
- **Timeline Tracking**: Complete history of each application
- **Company Insights**: Success rates by company
- **Follow-up Management**: Automated reminders for follow-ups
- **Analytics**: Detailed statistics on your job search

### Export Options
- **CSV Reports**: Export data for external analysis
- **Company Research**: Track what you learn about each company
- **Success Metrics**: Monitor response rates and improvements

## 🛡️ Safety and Compliance

### Technical Safety
- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Error Handling**: Robust recovery from failures
- **robots.txt Respect**: Always checks and respects website policies
- **User Agent**: Uses respectful, realistic browser identification

### Legal Compliance
- **No Platform Violations**: Avoids third-party platform restrictions
- **Direct Relationships**: Works directly with company websites
- **Transparent Operation**: Clear logging of all actions
- **User Control**: Manual override options for all automation

## 🔧 Configuration Options

### Application Limits (Conservative Defaults)
```python
max_applications_per_day = 15    # Total applications per day
max_companies_per_day = 5        # Companies to target per day
delay_between_applications = 90   # Seconds between applications
delay_between_companies = 180     # Seconds between companies
```

### Quality Controls
```python
require_manual_review = True      # Review each application
respect_robots_txt = True         # Always respect robots.txt
max_pages_per_company = 3         # Limit scraping depth
```

## 📈 Success Tips

### Research Strategy
1. **Quality over Quantity**: Target 20-30 companies you genuinely want to work for
2. **Company Research**: Understand each company's mission, values, and challenges
3. **Role Alignment**: Only apply to roles that genuinely fit your skills and interests
4. **Network Building**: Use the system to identify companies, then build relationships

### Application Strategy  
1. **Batch Processing**: Process 3-5 companies per session
2. **Peak Hours**: Apply during business hours for better visibility
3. **Follow-up Cadence**: Follow up 2 weeks after application
4. **Continuous Improvement**: Analyze response rates and adjust approach

### Technical Strategy
1. **Resume Optimization**: Keep your base resume updated and comprehensive
2. **Cover Letter Quality**: Review AI-generated cover letters for authenticity
3. **Portfolio Updates**: Ensure your portfolio showcases relevant work
4. **Skills Development**: Continuously learn skills that target companies value

## 🆘 Troubleshooting

### Common Issues

**ChromeDriver Errors**
```bash
# Download matching ChromeDriver version
# https://chromedriver.chromium.org/
# Place in PATH or project directory
```

**Form Recognition Issues**
```bash
# Companies use different form structures
# The system includes adaptive form detection
# Manual review helps catch edge cases
```

**API Rate Limits**
```bash
# OpenAI rate limits
# System includes retry logic
# Consider upgrading API plan for heavy usage
```

### Getting Help

1. **Check Logs**: Review `company_applications.log` for detailed error information
2. **Validate Config**: Ensure all required environment variables are set  
3. **Test Companies**: Start with 1-2 companies to verify setup
4. **Manual Mode**: Use manual review to understand any form issues

## 📞 Support and Contributing

### Getting Support
- **Documentation**: Check this README and code comments
- **Logs**: Always check `company_applications.log` first
- **Issues**: Report bugs with detailed error logs
- **Community**: Share experiences and best practices

### Contributing
- **Bug Reports**: Include steps to reproduce and error logs
- **Company Configs**: Share working configurations for new companies
- **Feature Requests**: Suggest improvements that maintain ethical standards
- **Code Contributions**: Follow existing patterns and include tests

## ⚖️ Legal Notice

This software is provided "as is" for educational purposes. Users are responsible for:
- ✅ Complying with website terms of service
- ✅ Ensuring truthful application information  
- ✅ Following respectful automation practices
- ✅ Maintaining professional conduct

The authors assume no liability for consequences of using this tool. Always prioritize ethical job searching practices.