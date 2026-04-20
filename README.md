# Job Application Dashboard

A Flask web application for tracking job applications and monitoring email replies from Gmail.

## Features

✅ **Job Tracking**
- Scans job application files from `C:\Users\johnj\OneDrive\Documents\Job hunt`
- Supports JSON, TXT, and Markdown file formats
- Displays company, position, application date, status, and notes

✅ **Gmail Integration**
- Integrates with Gmail API to fetch job-related emails
- Monitors your **"JobHunt"** folder in Gmail
- Automatically matches emails to job applications by company name or contact email

✅ **Web Dashboard**
- Real-time statistics (total applications, replies, pending)
- Comprehensive job table with application status
- Job detail modals with email reply information
- Responsive Bootstrap 5 design
- Refresh button for manual data sync

## Status

✅ **Setup Complete**
- Flask application running at `http://localhost:5000`
- Job folder scanning working
- Gmail API credentials configured
- OAuth authentication set up

## Running the Application

```bash
cd C:\Users\johnj\OneDrive\Documents\VS_projects\dashboard
python main.py
```

Visit: **http://localhost:5000**

## Setup Instructions (Already Completed)

### Installation

1. Navigate to project folder
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

### Gmail API Setup

1. **Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Project: **jobhunt-490713**
   - Gmail API is enabled

2. **OAuth 2.0 Credentials:** ✅
   - Credentials file: `credentials.json` (in project root)
   - Type: Desktop Application
   - Ready for authentication

3. **First-Time Authentication:**
   - When running the app, you'll see an authentication prompt
   - Sign in with your Google account
   - Grant permission for Gmail access
   - A `token.json` file will be created automatically
   - **If you see "Access blocked" error:**
     - Go to [OAuth consent screen](https://console.cloud.google.com/apis/consent)
     - Add your email as a Test User
     - Try again

4. **Gmail Label:** ✅
   - Label name: **"JobHunt"**
   - Move job-related emails (replies, offers, etc.) to this label
   - Dashboard will scan this folder for responses

### Job File Format

Create job files in `C:\Users\johnj\OneDrive\Documents\Job hunt` folder:

**JSON Format:**
```json
{
  "company": "Company Name",
  "position": "Job Title",
  "applied_date": "2025-03-19",
  "url": "https://job.posting.url",
  "status": "applied",
  "contact_email": "recruiter@company.com",
  "notes": "Referral from John Doe"
}
```

**Text Format:**
```
Company: Company Name
Position: Job Title
Applied: 2025-03-19
URL: https://job.posting.url
Status: applied
Email: recruiter@company.com
Notes: Referral from John Doe
```

**Markdown Format:**
```markdown
# Company Name - Job Title

Company: Company Name
Position: Job Title
Applied: 2025-03-19
URL: https://job.posting.url
Status: applied
Email: recruiter@company.com
```

## Dashboard Features

- **Statistics Cards**: Total applications, replied count, pending count, total emails
- **Job Table**: All applications with dates, status, reply indicators
- **Job Details**: Click "View" to see full details and matched emails
- **Reply Matching**: Automatically matches emails by company name or contact email
- **Refresh Button**: Manually trigger data sync from job files and Gmail
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Days Waiting**: Shows how many days since each application

## File Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Dashboard routes
│   ├── job_scanner.py       # Job file scanner
│   ├── gmail_service.py     # Gmail API integration
│   ├── models.py            # Data models
│   └── utils.py             # Utility functions
├── static/
│   ├── css/style.css        # Custom styles
│   └── js/dashboard.js      # Client-side scripts
├── templates/
│   ├── base.html            # Base template
│   └── dashboard.html       # Dashboard template
├── config.py                # Configuration
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── credentials.json         # Gmail OAuth credentials
└── README.md               # This file
```

## Configuration

Edit `config.py` to customize:
- `JOBS_FOLDER`: Path to your job files (default: `C:\Users\johnj\OneDrive\Documents\Job hunt`)
- `GMAIL_FOLDER`: Gmail label name (default: `JobHunt`)
- `DEBUG`: Debug mode (false for production)

## Troubleshooting

**No job files found:**
- Verify folder path: `C:\Users\johnj\OneDrive\Documents\Job hunt`
- Ensure files have `.json`, `.txt`, or `.md` extension
- Check file content format matches expected structure

**Gmail API not working:**
- Verify `credentials.json` is in project root
- Check Gmail API is enabled in Cloud Console (project: jobhunt-490713)
- Ensure "JobHunt" label exists in Gmail with emails in it
- If "Access blocked" error: add your email as Test User in OAuth consent screen

**No emails showing:**
- Verify "JobHunt" label exists in Gmail and has emails
- Check email subjects contain company names or sender is contact email
- Try clicking Refresh button in dashboard

**Port already in use:**
- Modify `main.py` to use different port:
  ```python
  app.run(port=5001)
  ```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/jobs` - JSON list of all jobs
- `GET /api/stats` - Statistics summary
- `GET /api/refresh` - Manually refresh data

## Dependencies

- Flask 2.3.3
- google-auth-oauthlib 1.1.0
- google-api-python-client 2.101.0
- requests 2.31.0
- python-dotenv 1.0.0

## License

MIT License

