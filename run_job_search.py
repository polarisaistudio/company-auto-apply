# run_job_search.py - Unified Role-Based Job Search Launcher
import asyncio
import sys
import os
from datetime import datetime

def print_header():
    """Print the main header"""
    print("\n" + "🎯" + "="*78)
    print("MULTI-ROLE INTELLIGENT JOB APPLICATION SYSTEM")
    print("="*80)
    print("🤖 AI-powered job search with role-specific optimization")
    print("📊 149+ Remote-friendly companies • 3 Specialized resumes")
    print("☁️ Separate workflows for targeted applications")
    print("="*80)

def print_role_options():
    """Print role selection options"""
    print("\n🎯 SELECT YOUR TARGET ROLE:")
    print("="*50)
    print("1. 🤖 AI Engineer")
    print("   • Machine Learning Engineer")
    print("   • Applied Scientist")
    print("   • ML Platform Engineer")
    print("   • Deep Learning Engineer")
    print("   Focus: PyTorch, TensorFlow, LLMs, Computer Vision")
    print()
    print("2. ☁️ Cloud Engineer")
    print("   • DevOps Engineer")
    print("   • Site Reliability Engineer (SRE)")
    print("   • Platform Engineer")
    print("   • Infrastructure Engineer")
    print("   Focus: AWS, Kubernetes, Terraform, Docker")
    print()
    print("3. 📊 Data Scientist")
    print("   • Analytics Engineer")
    print("   • Business Intelligence Analyst")
    print("   • Data Analyst")
    print("   • Quantitative Analyst")
    print("   Focus: Python, R, SQL, Tableau, Statistics")
    print()
    print("4. 🔄 Run All Roles (Sequential)")
    print("   • AI Engineer → Cloud Engineer → Data Scientist")
    print("   • Complete coverage with role-specific resumes")
    print()
    print("5. ⚙️ Configuration & Settings")
    print("6. 📊 View Previous Reports")
    print("7. ❌ Exit")
    print("="*50)

async def run_ai_engineer():
    """Run AI Engineer job search"""
    print("\n🤖 Launching AI Engineer job search...")
    from run_ai_engineer import AIEngineerJobSearch
    
    ai_search = AIEngineerJobSearch()
    await ai_search.run_ai_engineer_search()

async def run_cloud_engineer():
    """Run Cloud Engineer job search"""
    print("\n☁️ Launching Cloud Engineer job search...")
    from run_cloud_engineer import CloudEngineerJobSearch
    
    cloud_search = CloudEngineerJobSearch()
    await cloud_search.run_cloud_engineer_search()

async def run_data_scientist():
    """Run Data Scientist job search"""
    print("\n📊 Launching Data Scientist job search...")
    from run_data_scientist import DataScientistJobSearch
    
    data_search = DataScientistJobSearch()
    await data_search.run_data_scientist_search()

async def run_all_roles():
    """Run all roles sequentially"""
    print("\n🔄 RUNNING ALL ROLES SEQUENTIALLY")
    print("="*50)
    print("This will run AI Engineer → Cloud Engineer → Data Scientist")
    print("Each role will use its specialized resume and targeting")
    
    confirm = input("\nProceed with all roles? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("All roles search cancelled.")
        return
    
    try:
        # AI Engineer
        print(f"\n{'='*20} PHASE 1: AI ENGINEER {'='*20}")
        await run_ai_engineer()
        
        # Wait between roles
        print("\n⏳ Waiting 5 minutes between role searches...")
        await asyncio.sleep(300)  # 5 minutes
        
        # Cloud Engineer
        print(f"\n{'='*20} PHASE 2: CLOUD ENGINEER {'='*20}")
        await run_cloud_engineer()
        
        # Wait between roles
        print("\n⏳ Waiting 5 minutes between role searches...")
        await asyncio.sleep(300)  # 5 minutes
        
        # Data Scientist
        print(f"\n{'='*20} PHASE 3: DATA SCIENTIST {'='*20}")
        await run_data_scientist()
        
        print("\n🎉 ALL ROLES COMPLETED!")
        print("="*50)
        print("✅ AI Engineer applications submitted")
        print("✅ Cloud Engineer applications submitted") 
        print("✅ Data Scientist applications submitted")
        print("\n📊 Check individual role log files for detailed results:")
        print("   • ai_engineer_applications.log")
        print("   • cloud_engineer_applications.log")
        print("   • data_scientist_applications.log")
        
    except Exception as e:
        print(f"❌ Error during all roles execution: {e}")

def show_configuration():
    """Show current configuration"""
    print("\n⚙️ CURRENT CONFIGURATION")
    print("="*50)
    
    try:
        from config.settings import config
        print(f"Daily Application Limits:")
        print(f"  • AI Engineer: 25 applications")
        print(f"  • Cloud Engineer: 25 applications")
        print(f"  • Data Scientist: 25 applications")
        print(f"  • Total possible: 75 applications/day")
        print()
        print(f"Application Settings:")
        print(f"  • Manual Review: {getattr(config, 'require_manual_review', 'True')}")
        print(f"  • Delay Between Apps: {getattr(config, 'delay_between_applications', 90)}-150 seconds")
        print(f"  • Headless Browser: {getattr(config, 'headless_browser', True)}")
        print()
        print(f"Resume Templates:")
        if os.path.exists("templates/ai_engineer_resume.json"):
            print("  ✅ AI Engineer resume template")
        else:
            print("  ❌ AI Engineer resume template missing")
        if os.path.exists("templates/cloud_engineer_resume.json"):
            print("  ✅ Cloud Engineer resume template")
        else:
            print("  ❌ Cloud Engineer resume template missing")
        if os.path.exists("templates/data_scientist_resume.json"):
            print("  ✅ Data Scientist resume template")
        else:
            print("  ❌ Data Scientist resume template missing")
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
    
    input("\nPress Enter to continue...")

def view_reports():
    """View previous application reports"""
    print("\n📊 PREVIOUS APPLICATION REPORTS")
    print("="*50)
    
    log_files = [
        ("ai_engineer_applications.log", "🤖 AI Engineer"),
        ("cloud_engineer_applications.log", "☁️ Cloud Engineer"),
        ("data_scientist_applications.log", "📊 Data Scientist"),
        ("company_applications.log", "📋 General")
    ]
    
    for log_file, label in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"\n{label} - Last 3 entries:")
                        for line in lines[-3:]:
                            print(f"   {line.strip()}")
                    else:
                        print(f"\n{label} - No entries yet")
            except Exception as e:
                print(f"\n{label} - Error reading log: {e}")
        else:
            print(f"\n{label} - No log file found")
    
    print("\n📁 Resume Output Directories:")
    resume_dirs = ["resumes/ai_engineer", "resumes/cloud_engineer", "resumes/data_scientist"]
    for dir_path in resume_dirs:
        if os.path.exists(dir_path):
            count = len([f for f in os.listdir(dir_path) if f.endswith('.json')])
            print(f"  • {dir_path}: {count} resumes generated")
        else:
            print(f"  • {dir_path}: Not created yet")
    
    input("\nPress Enter to continue...")

async def main():
    """Main launcher function"""
    
    while True:
        try:
            print_header()
            print_role_options()
            
            choice = input("Select option (1-7): ").strip()
            
            if choice == "1":
                await run_ai_engineer()
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                await run_cloud_engineer()
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                await run_data_scientist()
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                await run_all_roles()
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                show_configuration()
                
            elif choice == "6":
                view_reports()
                
            elif choice == "7":
                print("\n👋 Goodbye! Good luck with your job search!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-7.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Job search interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print("🚀 Starting Multi-Role Job Search System...")
    asyncio.run(main())