# Job Application Dashboard

Flask web application for tracking job applications and email replies from Gmail.

## Project Status
✅ **PRODUCTION READY** - All features implemented and tested

## Features
- Scans job files from `C:\Users\johnj\OneDrive\Documents\Job hunt`
- Integrates with Gmail API to track job-related email replies from "JobHunt" label
- Web-based dashboard displaying application metrics and status
- Shows application vs reply statistics, dates, and company information
- Automatic email-to-job matching by company name or contact email
- Responsive Bootstrap 5 design

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Gmail credentials configured: `credentials.json` (in project root)
3. Run: `python main.py`
4. Visit: `http://localhost:5000`

## Configuration
- Jobs folder: `C:\Users\johnj\OneDrive\Documents\Job hunt`
- Gmail label: `JobHunt` (monitored for replies)
- Google Cloud Project: jobhunt-490713
- Dashboard: `http://localhost:5000`

## Key Files
- `config.py` - Configuration settings
- `app/job_scanner.py` - Reads job files (JSON/TXT/Markdown)
- `app/gmail_service.py` - Gmail API integration
- `app/routes.py` - Dashboard routes and API endpoints
- `templates/dashboard.html` - Main UI template
- `static/css/style.css` - Custom styling

## Job File Format
Supported formats in Job Hunt folder:
- **JSON**: Complete structured data
- **TXT**: Key-value format (Company: ..., Position: ...)
- **Markdown**: Formatted text with fields

