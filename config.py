import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JOBS_FOLDER = r'C:\Users\johnj\OneDrive\Documents\Job hunt'
    GMAIL_FOLDER = 'JobHunt'  # Gmail folder label name
    DEBUG = False
    TESTING = False
    
    # Gmail API config
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'

    # Gmail labels to actively monitor (in addition to the main JobHunt folder)
    MONITORED_LABELS = ['Rejected', 'Interview']
    
    # Cache settings
    CACHE_TIMEOUT = timedelta(hours=1)
    DATABASE = 'app_data.db'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    JOBS_FOLDER = './test_jobs'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
