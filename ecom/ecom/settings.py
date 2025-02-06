"""
Django settings for ecom project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
 
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/


SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth

    #custom apps
    'store',
    'store_manager',

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    #provides
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
        
     'whitenoise',  # Keep this for serving static files

   
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware'
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
  
]



if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'ecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count', 
                
            ],
        },
    },
]

WSGI_APPLICATION = 'ecom.wsgi.application'


 
 


# Initialize environment variables
  # Should print your RDS endpoint
 
 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),  # e.g., 'ecom'
        'USER': os.getenv('DB_USER'),  # e.g., 'mysuperuser'
        'PASSWORD': os.getenv('DB_PASSWORD'),  # e.g., 'mysuperuser'
        'HOST': os.getenv('DB_HOST'),  # e.g., 'ecom.cvuym2wqodkj.eu-north-1.rds.amazonaws.com'
        'PORT': os.getenv('DB_PORT', default='5432'),  # default is '5432'
    }
}


# Password validation

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
TIME_ZONE = 'Asia/Kolkata'  # Adjust to your local time zone
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'

# Specify the directories where static files are located
STATICFILES_DIRS = [
    BASE_DIR / "static",  # This tells Django to look for a static folder at the project level
]

STATIC_ROOT = BASE_DIR / "staticfiles"  # This will create a staticfiles directory in the root of your project


MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'store.CustomUser'



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'default_email@example.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'default_password')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False 

SITE_ID = 1  # Ensure this matches the ID in the Sites framework
 
 
 
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth backend
]

LOGIN_URL = 'login'  # This will redirect to your custom login view at /login/
LOGIN_REDIRECT_URL = 'home'  # Redirect to home or your desired page after login


 
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')


 
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

SOCIALACCOUNT_QUERY_EMAIL =True


SOCIALACCOUNT_ADAPTER = 'store.adapters.CustomSocialAccountAdapter'


SOCIALACCOUNT_LOGIN_ON_GET = True


#facebook

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',  # Set to 'js_sdk' to use the Facebook connect SDK
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name',
            'email'
        ],
        'EXCHANGE_TOKEN': True,
        # 'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': True,
        'VERSION': 'v13.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    }
}


SOCIALACCOUNT_SIGNUP_REDIRECT_URL = '/'

 

INTERNAL_IPS = [
    "127.0.0.1",  # Localhost
    # Add any additional IPs here if needed
]


 

 

# Razorpay API keys
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
 


#AWS bucket
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
