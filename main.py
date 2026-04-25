#!/usr/bin/env python
"""Main entry point for the Job Application Dashboard"""

import os
from app import create_app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=True, host='127.0.0.1', port=5000)
