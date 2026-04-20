"""Utility functions for the dashboard"""

from difflib import SequenceMatcher

def match_emails_to_jobs(jobs, emails):
    """Match emails to job applications"""
    matched_jobs = []
    
    for job in jobs:
        job_copy = job.copy()
        job_copy['has_reply'] = False
        job_copy['reply_email'] = None
        job_copy['reply_date'] = None
        
        # Try to match email to job
        company = job.get('company', '').lower()
        contact_email = job.get('contact_email', '').lower()
        
        for email in emails:
            sender = email.get('from', '').lower()
            subject = email.get('subject', '').lower()
            
            # Match by contact email or company name in sender
            if contact_email and contact_email in sender:
                job_copy['has_reply'] = True
                job_copy['reply_email'] = email
                job_copy['reply_date'] = email.get('date')
                break
            elif company and company in sender:
                job_copy['has_reply'] = True
                job_copy['reply_email'] = email
                job_copy['reply_date'] = email.get('date')
                break
            elif company and company in subject:
                job_copy['has_reply'] = True
                job_copy['reply_email'] = email
                job_copy['reply_date'] = email.get('date')
                break
        
        matched_jobs.append(job_copy)
    
    return matched_jobs

def calculate_days_since(date_string):
    """Calculate days since a date"""
    from datetime import datetime
    try:
        # Parse various date formats
        date_obj = datetime.fromisoformat(str(date_string).replace('Z', '+00:00'))
        delta = datetime.now(date_obj.tzinfo) - date_obj if date_obj.tzinfo else datetime.now() - date_obj
        return delta.days
    except:
        return None
