"""Flask application factory"""

from flask import Flask
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

def create_app(config_name='development'):
    """Application factory function"""
    # Point Flask at the project root for templates and static files.
    # Without this, Flask resolves paths relative to the 'app' package
    # folder and cannot find dashboard/templates/ or dashboard/static/.
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, 'templates'),
        static_folder=os.path.join(root_dir, 'static'),
    )
    
    # Load configuration
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
