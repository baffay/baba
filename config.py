import os
from datetime import timedelta

class Config:
    # أساسيات
    SECRET_KEY = 'your-secret-key-here'  # غير هذا في الإنتاج
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # قاعدة البيانات
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'finance.db')
    
    # التطبيق
    FLASK_APP = 'app.py'
    FLASK_ENV = 'development'  # غير إلى 'production' في الإنتاج