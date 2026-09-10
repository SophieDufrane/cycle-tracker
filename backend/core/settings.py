import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# ==============================================================================
# 1. PATHS AND ENVIRONMENT LOADING
# ==============================================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a local .env file if present
load_dotenv()

# ==============================================================================
# 2. SECURITY CONFIGURATION
# ==============================================================================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'DEBUG' in os.environ

# Dynamic allowed hosts to prevent Host Header Injection attacks
ALLOWED_HOSTS = [
    os.environ.get('ALLOWED_HOST'),
    'localhost',
    '127.0.0.1',
]

# ==============================================================================
# 3. APPLICATION DEFINITION
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party extensions
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Project Custom Apps
    'cycles'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Handles static files efficiently in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'

# ==============================================================================
# 4. DATABASE CONFIGURATION
# ==============================================================================
# Automatically switches between local SQLite and Production PostgreSQL via environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# 5. PASSWORD VALIDATION & INTERNATIONALIZATION
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# 6. STATIC FILES MANAGEMENT
# ==============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# 7. DJANGO REST FRAMEWORK CONFIGURATION
# ==============================================================================
if DEBUG:
    # LOCAL DEVELOPMENT: Allow public access without tokens for easy browser testing
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny',
        ],
    }
else:
    # PRODUCTION ENVIRONMENT: Enforce strict token authentication for maximum security
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
    }

# ==============================================================================
# 8. CORS (CROSS-ORIGIN RESOURCE SHARING) CONFIGURATION
# ==============================================================================
if DEBUG:
    # Allow all connections for local frontend development flexibility
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Secure setup: block all origins except your verified frontend domains
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000", # Allows local frontend to communicate with production API
        "http://127.0.0.1:3000",
    ]
    
    # Dynamically append your production frontend URL (Vercel, Scaleway, etc.) if provided
    FRONTEND_URL = os.environ.get('FRONTEND_URL')
    if FRONTEND_URL:
        CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)