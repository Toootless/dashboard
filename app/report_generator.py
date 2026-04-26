"""Report generation functionality for the dashboard"""

from datetime import datetime
import json


# Company career page URLs
COMPANY_CAREER_PAGES = {
    'GM': 'https://careers.gm.com',
    'General Motors': 'https://careers.gm.com',
    'HLMando': 'https://www.hlmando.com/careers',
    'H.L. Mando': 'https://www.hlmando.com/careers',
    'LUX': 'https://www.lux.com/careers',
    'Magna': 'https://www.magna.com/careers',
    'Slate': 'https://slate.com/careers',
    'Ford': 'https://corporate.ford.com/careers',
    'Tesla': 'https://www.tesla.com/careers',
    'Rivian': 'https://www.rivian.com/careers',
    'Apple': 'https://www.apple.com/careers',
    'Google': 'https://careers.google.com',
    'Amazon': 'https://www.amazon.jobs',
    'Microsoft': 'https://careers.microsoft.com',
    'Boeing': 'https://www.boeing.com/careers',
    'Lockheed Martin': 'https://www.lockheedmartin.com/en-us/careers',
    'Raytheon': 'https://www.rtx.com/careers',
    'Qualcomm': 'https://www.qualcomm.com/careers',
    'Intel': 'https://www.intel.com/content/www/us/en/jobs/jobs-at-intel.html',
    'NVIDIA': 'https://www.nvidia.com/en-us/about-nvidia/careers',
    'Texas Instruments': 'https://careers.ti.com',
    'Analog Devices': 'https://www.analog.com/en/careers.html',
    'Microchip': 'https://www.microchip.com/en-us/careers',
    'NXP': 'https://www.nxp.com/company/careers',
    'STMicroelectronics': 'https://www.st.com/content/st_com/en/about/careers.html',
    'ON Semiconductor': 'https://careers.onsemi.com',
}


def parse_job_status(filename):
    """
    Parse the status from a job filename or folder name.
    
    Convention:
        __Rejected_Interview_CompanyName_JobName_JobNumber → rejected_interview
        Rejected_Interview_CompanyName_JobName_JobNumber → rejected_interview
        __Interview_CompanyName_JobName_JobNumber         → interview
        Interview_CompanyName_JobName_JobNumber          → interview
        __Rejected_CompanyName_JobName_JobNumber         → rejected
        Rejected_CompanyName_JobName_JobNumber           → rejected
        CompanyName_JobName_JobNumber                     → applied
    
    Args:
        filename: The filename or folder name to parse
    
    Returns:
        (status, remainder) where remainder is the name with prefix removed
    """
    # Strip leading underscores, dashes, and dots first
    cleaned = filename.lstrip('_-.')
    
    status_prefixes = [
        ('Rejected_Interview_', 'rejected_interview'),
        ('Rejected_',           'rejected'),
        ('Interview_',          'interview'),
    ]
    
    for prefix, status in status_prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            return status, cleaned[len(prefix):]
    
    return 'applied', cleaned


def get_career_url(company_name):
    """
    Get the career page URL for a company.
    
    Args:
        company_name: The company name to look up
    
    Returns:
        Career page URL if found, None otherwise
    """
    if not company_name:
        return None
    
    # Try exact match first
    if company_name in COMPANY_CAREER_PAGES:
        return COMPANY_CAREER_PAGES[company_name]
    
    # Try case-insensitive match
    for company, url in COMPANY_CAREER_PAGES.items():
        if company.lower() == company_name.lower():
            return url
    
    return None


def add_career_urls_to_jobs(jobs):
    """
    Add career page URLs to job dictionaries based on company name.
    
    Args:
        jobs: List of job application dictionaries
    
    Returns:
        List of job dictionaries with career_url field added
    """
    enhanced_jobs = []
    for job in jobs:
        job_copy = job.copy()
        company_name = job_copy.get('company', '')
        job_copy['career_url'] = get_career_url(company_name)
        enhanced_jobs.append(job_copy)
    return enhanced_jobs


def extract_job_info(filename):
    """
    Extract company, position, and job number from a job filename.
    
    Examples:
        GM_ElectrificationCalibrationEngJR-202605458
        → company: GM, position: ElectrificationCalibrationEng, job_number: JR-202605458
        
        Rejected_HLMando_SystemsEng
        → status: rejected, company: HLMando, position: SystemsEng
    
    Args:
        filename: The job filename or folder name
    
    Returns:
        Dictionary with parsed information
    """
    status, remainder = parse_job_status(filename)
    
    # Split on underscores
    parts = remainder.split('_')
    
    company = parts[0] if parts else ''
    
    # Join remaining parts as position
    position_parts = parts[1:-1] if len(parts) > 2 else (parts[1:] if len(parts) > 1 else [])
    position = ' '.join(position_parts) if position_parts else ''
    
    # Extract job number (usually hyphenated, last part)
    job_number = parts[-1] if len(parts) > 1 else ''
    
    # Check if the last part looks like a job number (contains numbers)
    if not any(char.isdigit() for char in job_number):
        # If no digits, it's part of the position
        if position:
            position = f"{position} {job_number}"
        else:
            position = job_number
        job_number = ''
    
    return {
        'status': status,
        'company': company,
        'position': position,
        'job_number': job_number,
        'filename': filename,
    }


def generate_report(jobs, emails, start_date=None, end_date=None):
    """
    Generate a comprehensive report for applications and replies within a date range.
    
    Args:
        jobs: List of job application dictionaries
        emails: List of email dictionaries from Gmail
        start_date: Start date string (YYYY-MM-DD) or datetime object
        end_date: End date string (YYYY-MM-DD) or datetime object
    
    Returns:
        Dictionary containing detailed report data with status breakdowns
    """
    # Parse dates if they're strings
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            start_date = None
    
    if isinstance(end_date, str):
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            end_date = None
    
    # Filter jobs by date range
    filtered_jobs = []
    for job in jobs:
        job_date = job.get('applied_date')
        if job_date:
            try:
                if isinstance(job_date, str):
                    job_date = datetime.fromisoformat(str(job_date).replace('Z', '+00:00'))
                    job_date = job_date.replace(tzinfo=None)
                
                if start_date and job_date < start_date:
                    continue
                if end_date and job_date > end_date:
                    continue
            except (ValueError, TypeError):
                pass
        
        filtered_jobs.append(job)
    
    # Filter emails by date range
    filtered_emails = []
    for email in emails:
        email_date = email.get('date')
        if email_date:
            try:
                if isinstance(email_date, str):
                    email_date = datetime.fromisoformat(str(email_date).replace('Z', '+00:00'))
                    email_date = email_date.replace(tzinfo=None)
                
                if start_date and email_date < start_date:
                    continue
                if end_date and email_date > end_date:
                    continue
            except (ValueError, TypeError):
                pass
        
        filtered_emails.append(email)
    
    # Build detailed statistics by status
    status_groups = {
        'applied': [j for j in filtered_jobs if j.get('status') == 'applied'],
        'interview': [j for j in filtered_jobs if j.get('status') == 'interview'],
        'rejected': [j for j in filtered_jobs if j.get('status') == 'rejected'],
        'rejected_interview': [j for j in filtered_jobs if j.get('status') == 'rejected_interview'],
    }
    
    # Count replied vs pending for each status
    replied_by_status = {}
    for status, jobs_with_status in status_groups.items():
        replied_count = len([j for j in jobs_with_status if j.get('has_reply')])
        replied_by_status[status] = replied_count
    
    # Build report statistics
    total_replied = len([j for j in filtered_jobs if j.get('has_reply')])
    total_applications = len(filtered_jobs)
    
    # Add career URLs to jobs
    jobs_with_careers = add_career_urls_to_jobs(filtered_jobs)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d') if start_date else 'All',
            'end': end_date.strftime('%Y-%m-%d') if end_date else 'All',
        },
        'statistics': {
            'total_applications': total_applications,
            'total_replies': len(filtered_emails),
            'total_replied': total_replied,
            'total_pending': total_applications - total_replied,
            'reply_rate': round(total_replied / total_applications * 100, 1) if total_applications > 0 else 0,
            'by_status': {
                'applied': {
                    'total': len(status_groups['applied']),
                    'replied': replied_by_status['applied'],
                    'pending': len(status_groups['applied']) - replied_by_status['applied'],
                },
                'interview': {
                    'total': len(status_groups['interview']),
                    'replied': replied_by_status['interview'],
                    'pending': len(status_groups['interview']) - replied_by_status['interview'],
                },
                'rejected': {
                    'total': len(status_groups['rejected']),
                    'replied': replied_by_status['rejected'],
                    'pending': len(status_groups['rejected']) - replied_by_status['rejected'],
                },
                'rejected_interview': {
                    'total': len(status_groups['rejected_interview']),
                    'replied': replied_by_status['rejected_interview'],
                    'pending': len(status_groups['rejected_interview']) - replied_by_status['rejected_interview'],
                },
            }
        },
        'jobs': jobs_with_careers,
        'emails': filtered_emails,
        'jobs_by_status': status_groups,
    }
    
    return report
