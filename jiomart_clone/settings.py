"""
Django settings for jiomart_clone project.
"""

from pathlib import Path
import os
import environ
from decouple import config
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Initialize environ AFTER BASE_DIR is defined
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jiomart_clone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jiomart_clone.wsgi.application'


# PostgreSQL Neon Database
ENVIRONMENT = config("ENVIRONMENT", default="development")

if ENVIRONMENT == "production":
    # ✅ PRODUCTION → POSTGRES (Neon)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
            "OPTIONS": {
                "sslmode": "require",
            },
            "CONN_MAX_AGE": 60,  # important for Neon
        }
    }
    print('Connecting to Neon Postgres database...')

else:
    # ✅ DEVELOPMENT → SQLITE (FAST)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print('Connecting to SQLite3 database...')



# Password Validation
AUTH_PASSWORD_VALIDATORS = []


# Language and Time
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



# 🚀 Session Settings
# 🚀 Session Settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True

# ✅ User stays logged in until manual logout
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ✅ Session valid for 30 days
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days

# ✅ Extend session on every request
SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False




# 📩 Email OTP Settings (Gmail SMTP)
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')

# ⚠️ Update your Gmail and App Password
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')