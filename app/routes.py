"""Routes for the dashboard application"""

from flask import Blueprint, render_template, jsonify, current_app, request
from app.job_scanner import JobScanner
from app.gmail_service import GmailService
from app.utils import match_emails_to_jobs
from app.interview_prep import build_interview_prep

main_bp = Blueprint('main', __name__)


def get_services():
    """Get or create cached service instances"""
    if not hasattr(current_app, 'job_scanner'):
        current_app.job_scanner = JobScanner(current_app.config['JOBS_FOLDER'])
    if not hasattr(current_app, 'gmail_service'):
        current_app.gmail_service = GmailService(current_app.config)
    return current_app.job_scanner, current_app.gmail_service


def _build_label_data(jobs):
    """
    Build the label_data dict from already-scanned job records.

    Status is detected from the filename prefix by job_scanner, so no
    extra I/O is needed here — we simply group the jobs by status.

    Returns:
        {
          'Rejected':  {'count': N, 'jobs': [...]},
          'Interview': {'count': N, 'jobs': [...]},
        }
    """
    rejected  = [j for j in jobs if j.get('status') in ('rejected', 'rejected_interview')]
    interview = [j for j in jobs if j.get('status') in ('interview', 'rejected_interview')]
    return {
        'Rejected':  {'count': len(rejected),  'jobs': rejected},
        'Interview': {'count': len(interview), 'jobs': interview},
    }


@main_bp.route('/')
def dashboard():
    """Main dashboard view"""
    job_scanner, gmail_service = get_services()

    # Scan the Job hunt folder — status is derived from filename prefixes
    jobs = job_scanner.scan_jobs()

    # Group into label-based sections (file-name driven, no Gmail call)
    label_data = _build_label_data(jobs)

    # Fetch emails from Gmail for comms-check matching
    try:
        emails = gmail_service.get_job_emails()
    except Exception as e:
        print(f"Gmail error: {e}")
        emails = []

    # Match emails to jobs for the "Comms Check" column
    matched_data = match_emails_to_jobs(jobs, emails)

    # Rebuild label_data on matched_data so status badges stay consistent
    label_data = _build_label_data(matched_data)

    stats = {
        'total_applications': len(jobs),
        'total_replies':      len(emails),
        'replied':            len([j for j in matched_data if j.get('has_reply')]),
        'pending':            len([j for j in matched_data if not j.get('has_reply')
                                   and j.get('status') == 'applied']),
        'rejected':           label_data['Rejected']['count'],
        'interview':          label_data['Interview']['count'],
    }

    return render_template('dashboard.html',
                           jobs=matched_data,
                           stats=stats,
                           emails=emails,
                           label_data=label_data)


@main_bp.route('/api/jobs')
def api_jobs():
    """API endpoint for jobs data"""
    job_scanner, gmail_service = get_services()
    jobs = job_scanner.scan_jobs()
    try:
        emails = gmail_service.get_job_emails()
    except Exception:
        emails = []
    matched_data = match_emails_to_jobs(jobs, emails)
    return jsonify({'success': True, 'jobs': matched_data, 'count': len(matched_data)})


@main_bp.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    job_scanner, gmail_service = get_services()
    jobs = job_scanner.scan_jobs()
    try:
        emails = gmail_service.get_job_emails()
    except Exception:
        emails = []
    matched_data = match_emails_to_jobs(jobs, emails)
    label_data   = _build_label_data(matched_data)
    stats = {
        'total_applications': len(jobs),
        'total_replies':      len(emails),
        'replied':            len([j for j in matched_data if j.get('has_reply')]),
        'pending':            len([j for j in matched_data if not j.get('has_reply')
                                   and j.get('status') == 'applied']),
        'rejected':           label_data['Rejected']['count'],
        'interview':          label_data['Interview']['count'],
        'reply_rate':         round(
            len([j for j in matched_data if j.get('has_reply')]) / len(jobs) * 100, 1
        ) if jobs else 0,
    }
    return jsonify(stats)


@main_bp.route('/api/refresh')
def api_refresh():
    """Refresh data from jobs folder and Gmail"""
    job_scanner, gmail_service = get_services()
    try:
        jobs   = job_scanner.scan_jobs()
        emails = gmail_service.get_job_emails()
        return jsonify({
            'success':      True,
            'jobs_count':   len(jobs),
            'emails_count': len(emails),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/interview-prep')
def api_interview_prep():
    """
    Return interview preparation data for a given company + position.

    Query params:
      ?company=Slate&position=AttributeIntegrationEng
    """
    company  = request.args.get('company',  '').strip()
    position = request.args.get('position', '').strip()

    if not company and not position:
        return jsonify({'error': 'company and/or position are required'}), 400

    try:
        prep = build_interview_prep(company, position)
        return jsonify({'success': True, 'prep': prep})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
