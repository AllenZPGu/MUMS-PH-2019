import os
import django_heroku
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ag9d18mr6#u@^00@_xs$mnpw6)mf%cdsa&2hs7#wfq0--%-$t&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'PHapp',
    'crispy_forms',
    'django_extensions',
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


# #deployment checks
# SECURE_SSL_REDIRECT = True

# SESSION_COOKIE_SECURE = True

# SECURE_BROWSER_XSS_FILTER = True

# SECURE_CONTENT_TYPE_NOSNIFF = True

# X_FRAME_OPTIONS = 'DENY'

# SECURE_HSTS_SECONDS = 10  

# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURE_HSTS_PRELOAD = True


ROOT_URLCONF = 'PH_backend.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'PH_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    #development server
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd8na88rhs2t5r4',
        'USER': 'ttmvgtyolplhwc',
        'PASSWORD': 'f9ce4469fd0ea78794ad32d909285180e91e929044510f2742d5e9d0fc7b5184',
        'HOST': 'ec2-50-19-249-121.compute-1.amazonaws.com',
        'PORT': '5432',
    },

    #live server
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'd5ifh5ejt8k1ua',
    #     'USER': 'wrzxfbzdnebchw',
    #     'PASSWORD': 'f97d2a161123c415c5eef52c1a76009c7584847a3d80cb4efb0558de71f94ffa',
    #     'HOST': 'ec2-75-101-147-226.compute-1.amazonaws.com',
    #     'PORT': '5432',
    # },

    'development': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd8na88rhs2t5r4',
        'USER': 'ttmvgtyolplhwc',
        'PASSWORD': 'f9ce4469fd0ea78794ad32d909285180e91e929044510f2742d5e9d0fc7b5184',
        'HOST': 'ec2-50-19-249-121.compute-1.amazonaws.com',
        'PORT': '5432',
    },

    #live server
    'live': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd5ifh5ejt8k1ua',
        'USER': 'wrzxfbzdnebchw',
        'PASSWORD': 'f97d2a161123c415c5eef52c1a76009c7584847a3d80cb4efb0558de71f94ffa',
        'HOST': 'ec2-75-101-147-226.compute-1.amazonaws.com',
        'PORT': '5432',
    },
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# Activate Django-Heroku.
django_heroku.settings(locals())

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    #os.path.join(BASE_DIR, 'PHapp/puzzleFiles'),
]

CSRF_USE_SESSIONS = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'

#auto email stuff
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = 'mumspuzzlehunt2019@gmail.com'
EMAIL_HOST_PASSWORD = '420blazer'