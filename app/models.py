"""Data models for the application"""

from datetime import datetime

class JobApplication:
    """Represents a job application"""
    
    def __init__(self, company, position, applied_date, url='', status='applied', notes='', contact_email=''):
        self.company = company
        self.position = position
        self.applied_date = applied_date
        self.url = url
        self.status = status
        self.notes = notes
        self.contact_email = contact_email
        self.reply_date = None
        self.reply_subject = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'company': self.company,
            'position': self.position,
            'applied_date': self.applied_date,
            'url': self.url,
            'status': self.status,
            'notes': self.notes,
            'contact_email': self.contact_email,
            'reply_date': self.reply_date,
            'reply_subject': self.reply_subject
        }

class Email:
    """Represents an email message"""
    
    def __init__(self, id, subject, sender, date, body=''):
        self.id = id
        self.subject = subject
        self.sender = sender
        self.date = date
        self.body = body
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'subject': self.subject,
            'sender': self.sender,
            'date': self.date,
            'body': self.body
        }
