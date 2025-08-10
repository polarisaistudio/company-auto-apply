# tracking/application_tracker.py
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from scrapers.company_scraper import JobPosting

class ApplicationTracker:
    """Enhanced tracking system for company applications"""
    
    def __init__(self, db_path: str = "company_applications.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced database schema for company applications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Applications table with company-specific fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            department TEXT,
            location TEXT,
            job_url TEXT UNIQUE,
            application_date DATETIME NOT NULL,
            status TEXT DEFAULT 'Applied',
            salary_range TEXT,
            job_type TEXT,
            notes TEXT,
            resume_version TEXT,
            cover_letter TEXT,
            response_date DATETIME,
            interview_date DATETIME,
            follow_up_date DATETIME,
            rejection_date DATETIME,
            offer_date DATETIME,
            company_rating INTEGER,  -- 1-5 rating of interest in company
            role_fit_score INTEGER,  -- 1-5 rating of how well role fits
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Company research table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            industry TEXT,
            size TEXT,
            culture_notes TEXT,
            values TEXT,
            pros TEXT,
            cons TEXT,
            salary_info TEXT,
            interview_process TEXT,
            contacts TEXT,  -- JSON of contacts at company
            last_researched DATETIME,
            interest_level INTEGER,  -- 1-5 rating
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Application events for detailed tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS application_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            event_type TEXT NOT NULL,  -- applied, viewed, responded, interviewed, etc.
            event_date DATETIME NOT NULL,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_date ON applications(application_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_url ON applications(job_url)")
        
        conn.commit()
        conn.close()
    
    def add_application(self, job_posting: JobPosting, resume_path: str, cover_letter: str, success: bool):
        """Record a new application with enhanced tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        status = "Applied" if success else "Failed"
        
        try:
            cursor.execute("""
            INSERT INTO applications 
            (job_title, company, department, location, job_url, application_date, 
             status, salary_range, job_type, resume_version, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_posting.title,
                job_posting.company,
                job_posting.department,
                job_posting.location,
                job_posting.url,
                datetime.now(),
                status,
                job_posting.salary,
                job_posting.job_type,
                resume_path,
                cover_letter[:1000] if cover_letter else None  # Truncate for storage
            ))
            
            application_id = cursor.lastrowid
            
            # Add application event
            cursor.execute("""
            INSERT INTO application_events (application_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
            """, (application_id, "applied" if success else "failed", datetime.now(), 
                  "Automated application" if success else "Application failed"))
            
            conn.commit()
            
        except sqlite3.IntegrityError:
            # Application already exists (duplicate URL)
            pass
        finally:
            conn.close()
    
    def has_applied_to_job(self, job_url: str) -> bool:
        """Check if already applied to this specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE job_url = ?", (job_url,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def update_application_status(self, application_id: int, status: str, notes: str = ""):
        """Update application status and add event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update application
        cursor.execute("""
        UPDATE applications 
        SET status = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """, (status, notes, datetime.now(), application_id))
        
        # Add event
        cursor.execute("""
        INSERT INTO application_events (application_id, event_type, event_date, notes)
        VALUES (?, ?, ?, ?)
        """, (application_id, status.lower(), datetime.now(), notes))
        
        conn.commit()
        conn.close()
    
    def add_company_research(self, company_name: str, research_data: Dict):
        """Add or update company research data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO company_research 
            (company_name, industry, size, culture_notes, values, pros, cons,
             salary_info, interview_process, contacts, interest_level, last_researched)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_name,
                research_data.get('industry', ''),
                research_data.get('size', ''),
                research_data.get('culture_notes', ''),
                research_data.get('values', ''),
                research_data.get('pros', ''),
                research_data.get('cons', ''),
                research_data.get('salary_info', ''),
                research_data.get('interview_process', ''),
                json.dumps(research_data.get('contacts', [])),
                research_data.get('interest_level', 3),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_company_application_history(self, company_name: str) -> List[Dict]:
        """Get all applications to a specific company"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query("""
        SELECT * FROM applications 
        WHERE company = ? 
        ORDER BY application_date DESC
        """, conn, params=(company_name,))
        
        conn.close()
        return df.to_dict('records')
    
    def get_application_stats(self) -> Dict:
        """Get comprehensive application statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Basic stats
        total_applications = pd.read_sql_query("""
        SELECT COUNT(*) as total FROM applications WHERE status != 'Failed'
        """, conn).iloc[0]['total']
        
        recent_applications = pd.read_sql_query("""
        SELECT COUNT(*) as recent 
        FROM applications 
        WHERE application_date >= datetime('now', '-7 days') AND status != 'Failed'
        """, conn).iloc[0]['recent']
        
        # Status breakdown
        status_df = pd.read_sql_query("""
        SELECT status, COUNT(*) as count
        FROM applications 
        GROUP BY status
        ORDER BY count DESC
        """, conn)
        
        # Top companies
        companies_df = pd.read_sql_query("""
        SELECT company, COUNT(*) as applications
        FROM applications 
        WHERE status != 'Failed'
        GROUP BY company 
        ORDER BY applications DESC 
        LIMIT 10
        """, conn)
        
        # Success rate
        success_rate = pd.read_sql_query("""
        SELECT 
            CAST(SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as rate
        FROM applications
        WHERE status != 'Failed'
        """, conn).iloc[0]['rate'] or 0
        
        # Response rate (any status other than 'Applied' or 'Failed')
        response_rate = pd.read_sql_query("""
        SELECT 
            CAST(SUM(CASE WHEN status NOT IN ('Applied', 'Failed') THEN 1 ELSE 0 END) AS FLOAT) / 
            COUNT(*) as rate
        FROM applications
        WHERE status != 'Failed'
        """, conn).iloc[0]['rate'] or 0
        
        # Recent activity (last 30 days)
        activity_df = pd.read_sql_query("""
        SELECT 
            DATE(application_date) as date,
            COUNT(*) as applications
        FROM applications 
        WHERE application_date >= datetime('now', '-30 days') AND status != 'Failed'
        GROUP BY DATE(application_date)
        ORDER BY date DESC
        """, conn)
        
        conn.close()
        
        return {
            "total_applications": int(total_applications),
            "recent_applications": int(recent_applications),
            "success_rate": float(success_rate),
            "response_rate": float(response_rate),
            "status_breakdown": status_df.to_dict('records'),
            "top_companies": companies_df.to_dict('records'),
            "daily_activity": activity_df.to_dict('records')
        }
    
    def get_follow_up_needed(self) -> List[Dict]:
        """Get applications that need follow-up"""
        conn = sqlite3.connect(self.db_path)
        
        # Applications older than 2 weeks with no response
        df = pd.read_sql_query("""
        SELECT * FROM applications 
        WHERE status = 'Applied' 
        AND application_date < datetime('now', '-14 days')
        AND follow_up_date IS NULL
        ORDER BY application_date ASC
        """, conn)
        
        conn.close()
        return df.to_dict('records')
    
    def mark_follow_up_sent(self, application_id: int, notes: str = ""):
        """Mark that follow-up was sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE applications 
        SET follow_up_date = ?, notes = COALESCE(notes || '\n', '') || ?
        WHERE id = ?
        """, (datetime.now(), f"Follow-up sent: {notes}", application_id))
        
        # Add event
        cursor.execute("""
        INSERT INTO application_events (application_id, event_type, event_date, notes)
        VALUES (?, 'follow_up', ?, ?)
        """, (application_id, datetime.now(), notes))
        
        conn.commit()
        conn.close()
    
    def export_applications_csv(self, filename: str = None) -> str:
        """Export applications to CSV with enhanced data"""
        if not filename:
            filename = f"company_applications_{datetime.now().strftime('%Y%m%d')}.csv"
        
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query("""
        SELECT 
            company,
            job_title,
            department,
            location,
            salary_range,
            application_date,
            status,
            response_date,
            interview_date,
            job_url,
            notes
        FROM applications 
        WHERE status != 'Failed'
        ORDER BY application_date DESC
        """, conn)
        
        df.to_csv(filename, index=False)
        conn.close()
        
        return filename
    
    def get_application_timeline(self, application_id: int) -> List[Dict]:
        """Get timeline of events for a specific application"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query("""
        SELECT event_type, event_date, notes
        FROM application_events 
        WHERE application_id = ?
        ORDER BY event_date ASC
        """, conn, params=(application_id,))
        
        conn.close()
        return df.to_dict('records')
    
    def get_company_insights(self) -> Dict:
        """Get insights about company application patterns"""
        conn = sqlite3.connect(self.db_path)
        
        # Companies with best response rates
        response_rates = pd.read_sql_query("""
        SELECT 
            company,
            COUNT(*) as total_applications,
            SUM(CASE WHEN status NOT IN ('Applied', 'Failed') THEN 1 ELSE 0 END) as responses,
            CAST(SUM(CASE WHEN status NOT IN ('Applied', 'Failed') THEN 1 ELSE 0 END) AS FLOAT) / 
            COUNT(*) as response_rate
        FROM applications 
        WHERE status != 'Failed'
        GROUP BY company 
        HAVING COUNT(*) >= 2
        ORDER BY response_rate DESC
        LIMIT 10
        """, conn)
        
        # Most applied to companies
        popular_companies = pd.read_sql_query("""
        SELECT company, COUNT(*) as applications
        FROM applications 
        WHERE status != 'Failed'
        GROUP BY company 
        ORDER BY applications DESC 
        LIMIT 10
        """, conn)
        
        conn.close()
        
        return {
            "best_response_rates": response_rates.to_dict('records'),
            "most_popular_companies": popular_companies.to_dict('records')
        }