from cryptography.fernet import Fernet
from datetime import timedelta
import secrets, os




class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_SECRET_KEY = secrets.token_hex(32)
    ENCRYPTION_KEY = Fernet.generate_key()
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)