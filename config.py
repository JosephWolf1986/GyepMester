import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gyepmester-titkos-kulcs-2024'
    
    # Adatbázis kapcsolat (Supabase / PostgreSQL vagy SQLite fallback)
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = raw_db_url or \
        'sqlite:///' + os.path.join(basedir, 'gyepmester.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Képfeltöltés
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or ''
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
