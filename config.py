import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # Database - PostgreSQL for Render, SQLite for local development
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///markets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}
    
    # Cloudinary upload settings
    CLOUDINARY_CONFIG = {
        'cloud_name': CLOUDINARY_CLOUD_NAME,
        'api_key': CLOUDINARY_API_KEY,
        'api_secret': CLOUDINARY_API_SECRET,
        'secure': True
    }
    
    # ===== EMAIL CONFIGURATION =====
    # Email server settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    
    # Email authentication
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Email settings
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False').lower() == 'true'
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    MAIL_ASCII_ATTACHMENTS = os.environ.get('MAIL_ASCII_ATTACHMENTS', 'False').lower() == 'true'