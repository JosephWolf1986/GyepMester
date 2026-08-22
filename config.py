import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gyepmester-titkos-kulcs-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'gyepmester.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Képfeltöltés
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or ''
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
