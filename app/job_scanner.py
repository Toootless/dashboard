"""Scans job application files from the jobs folder"""

import os
import json
from pathlib import Path
from datetime import datetime

class JobScanner:
    """Scans and parses job application files"""
    
    def __init__(self, jobs_folder):
        self.jobs_folder = jobs_folder
    
    def scan_jobs(self):
        """Scan jobs folder and return list of job applications.

        Structure:
          Job hunt/
            CompanyName_JobRole/          <- applied (status from prefix or folder)
            Interview_Company_Role/       <- interview
            ____Rejected____/             <- container: everything inside = rejected
              Company_Role/
              RejectedCompany_Role/
        """
        jobs = []

        if not os.path.exists(self.jobs_folder):
            print(f"Jobs folder not found: {self.jobs_folder}")
            return jobs

        _SKIP_PREFIXES = ('John', 'Resume', 'JobDescription', '2025', '2026',
                          'INCOSE', 'SWBX_JD', 'Electrical Technician')
        _SKIP_EXTS = ('.pdf', '.docx', '.doc', '.xlsx', '.jpg', '.png',
                      '.jpeg', '.gif', '.mp4', '.zip')
        _REJECTED_CONTAINER = '____Rejected____'

        for entry_name in os.listdir(self.jobs_folder):
            entry_path = os.path.join(self.jobs_folder, entry_name)

            # --- Rejected container folder: scan its children as 'rejected' ---
            if entry_name == _REJECTED_CONTAINER and os.path.isdir(entry_path):
                for child_name in os.listdir(entry_path):
                    child_path = os.path.join(entry_path, child_name)
                    _, ext = os.path.splitext(child_name)
                    if ext.lower() in _SKIP_EXTS:
                        continue
                    if os.path.isdir(child_path):
                        job_data = self._parse_job_folder(child_path, child_name,
                                                          force_status='rejected')
                        if job_data:
                            jobs.append(job_data)
                continue  # don't treat the container itself as a job

            _, ext = os.path.splitext(entry_name)
            if ext.lower() in _SKIP_EXTS:
                continue
            if any(entry_name.startswith(p) for p in _SKIP_PREFIXES):
                continue

            if os.path.isdir(entry_path):
                job_data = self._parse_job_folder(entry_path, entry_name)
            elif os.path.isfile(entry_path):
                job_data = self._parse_job_file(entry_path, entry_name)
            else:
                continue

            if job_data:
                jobs.append(job_data)

        jobs.sort(key=lambda x: x.get('applied_date', ''), reverse=True)
        return jobs


    def _parse_job_folder(self, folder_path, folder_name, force_status=None):
        """Parse a job-application directory.

        The folder name encodes status + company/role:
            Interview_Slate_AttributeIntegrationEng  -> interview
            Rejected_Ford_ADAS_56651                 -> rejected
            CompanyName_JobName_JobNumber            -> applied

        force_status: if provided, overrides the filename-based status detection.
        """
        status, remainder = self._parse_filename_prefix(folder_name)
        if force_status:
            status = force_status
            # Also strip any Rejected_ prefix from the company name in the remainder
            _, remainder = self._parse_filename_prefix(folder_name)



        parts = [p.strip() for p in remainder.split('_') if p.strip()]
        company  = parts[0] if parts else folder_name
        position = ' '.join(parts[1:]) if len(parts) > 1 else ''

        try:
            mtime = os.path.getmtime(folder_path)
            applied_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except Exception:
            applied_date = ''

        notes = ''
        try:
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                if os.path.isfile(fpath) and fname.lower().endswith(('.txt', '.md')):
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        notes = f.read(500)
                    break
        except Exception:
            pass

        return {
            'company':       company,
            'position':      position,
            'applied_date':  applied_date,
            'url':           '',
            'status':        status,
            'notes':         notes,
            'filename':      folder_name,
            'contact_email': '',
        }

    
    # ------------------------------------------------------------------
    # Filename prefix → status mapping
    #
    # Convention:
    #   Interview_CompanyName_JobName[_JobNumber]         → status='interview'
    #   Rejected_CompanyName_JobName[_JobNumber]          → status='rejected'
    #   Rejected_Interview_CompanyName_JobName[_JobNumber] → status='rejected_interview'
    #   CompanyName_JobName[_JobNumber]                   → status='applied'
    # ------------------------------------------------------------------

    # Ordered so the longest/most-specific prefix is checked first
    _STATUS_PREFIXES = [
        ('Rejected_Interview_', 'rejected_interview'),
        ('Rejected_',           'rejected'),
        ('Interview_',          'interview'),
    ]

    def _parse_filename_prefix(self, stem):
        """
        Given a filename stem (no extension, no path), return
        (status, remainder) where remainder is the stem with the
        status prefix stripped.
        Handles leading underscores: __Interview_Company_... -> interview
        """
        # Strip leading underscores, dashes, and dots first
        cleaned = stem.lstrip('_-.')
        
        for prefix, status in self._STATUS_PREFIXES:
            if cleaned.lower().startswith(prefix.lower()):
                return status, cleaned[len(prefix):]
        return 'applied', cleaned

    def _parse_job_file(self, filepath, filename):
        """Parse a single job file"""
        try:
            # Try parsing as JSON
            if filename.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._normalize_job_data(data, filename)

            # Parse text/markdown files
            elif filename.endswith(('.txt', '.md')):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return self._parse_text_job(content, filename)

            # Parse CSV files
            elif filename.endswith('.csv'):
                return self._parse_csv_job(filepath, filename)

            # Extension-less files — treat like text, derive info from name only
            else:
                return self._parse_extensionless_job(filepath, filename)

        except Exception as e:
            print(f"Error parsing {filename}: {e}")

        return None

    def _parse_extensionless_job(self, filepath, filename):
        """
        Handle files that have no extension (the common case in this project).
        Status and company/position are derived entirely from the filename.
        The file content is read as notes if it is plain text.
        """
        stem = filename  # no extension to strip
        status, remainder = self._parse_filename_prefix(stem)

        # Split remainder into parts on underscore or space
        parts = [p.strip() for p in remainder.replace('_', ' ').split() if p.strip()]

        # Heuristic: first part = company,  rest = position
        company  = parts[0] if parts else stem
        position = ' '.join(parts[1:]) if len(parts) > 1 else ''

        # Try reading file content as notes (may be binary — skip gracefully)
        notes = ''
        try:
            stat = os.stat(filepath)
            if stat.st_size < 50_000:          # skip large binaries
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = f.read(500)
                if raw.isprintable() or any(c.isalpha() for c in raw[:20]):
                    notes = raw
        except Exception:
            pass

        # Applied date = file modification time as a fallback
        try:
            mtime = os.path.getmtime(filepath)
            applied_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except Exception:
            applied_date = ''

        return {
            'company':       company,
            'position':      position,
            'applied_date':  applied_date,
            'url':           '',
            'status':        status,
            'notes':         notes,
            'filename':      filename,
            'contact_email': '',
        }
    
    def _normalize_job_data(self, data, filename):
        """Normalize job data to standard format (JSON files)"""
        if isinstance(data, dict):
            # JSON files may already have a status field; if not, detect from filename
            stem = Path(filename).stem
            detected_status, _ = self._parse_filename_prefix(stem)
            return {
                'company':       data.get('company') or data.get('name') or '',
                'position':      data.get('position') or data.get('title') or '',
                'applied_date':  str(data.get('applied_date') or data.get('date') or ''),
                'url':           data.get('url') or '',
                'status':        data.get('status') or detected_status,
                'notes':         data.get('notes') or '',
                'filename':      filename,
                'contact_email': data.get('contact_email') or '',
            }
        return None
    
    def _parse_text_job(self, content, filename):
        """Parse text/markdown file"""
        stem = Path(filename).stem
        detected_status, remainder = self._parse_filename_prefix(stem)

        lines = content.split('\n')
        job_data = {
            'company':       '',
            'position':      '',
            'applied_date':  '',
            'url':           '',
            'status':        detected_status,  # from filename prefix
            'notes':         '',
            'filename':      filename,
            'contact_email': '',
        }

        # Extract explicit key: value fields from file content
        for line in lines:
            line = line.strip()
            if line.startswith(('Company:', 'company:')):
                job_data['company'] = line.split(':', 1)[1].strip()
            elif line.startswith(('Position:', 'position:')):
                job_data['position'] = line.split(':', 1)[1].strip()
            elif line.startswith(('Date:', 'Applied:', 'applied:')):
                job_data['applied_date'] = line.split(':', 1)[1].strip()
            elif line.startswith(('URL:', 'url:', 'Link:')):
                job_data['url'] = line.split(':', 1)[1].strip()
            elif line.startswith(('Status:', 'status:')):
                # Explicit status in file overrides filename-detected one
                job_data['status'] = line.split(':', 1)[1].strip().lower()
            elif line.startswith(('Email:', 'Contact:', 'contact:')):
                job_data['contact_email'] = line.split(':', 1)[1].strip()

        # Fall back to deriving company/position from the filename remainder
        if not job_data['company'] or not job_data['position']:
            parts = [p.strip() for p in remainder.replace('_', ' ').split() if p.strip()]
            if not job_data['company']:
                job_data['company'] = parts[0] if parts else remainder
            if not job_data['position']:
                job_data['position'] = ' '.join(parts[1:]) if len(parts) > 1 else ''

        return job_data if job_data['company'] or job_data['position'] else None
    
    def _parse_csv_job(self, filepath, filename):
        """Parse CSV file - placeholder"""
        # TODO: Implement CSV parsing if needed
        return None
