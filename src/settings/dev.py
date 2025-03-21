import os
import stat
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ig%^xfx+y+bwo*6fs3wzgd&lteu9meb02_h#c=-)b$gi&bs5d*"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOCS_ROOT = BASE_DIR.parent / "docs" / "build" / "html"
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
WIALON_ADMIN_ID = os.getenv("WIALON_ADMIN_ID")

ALLOWED_HOSTS = []
ADMINS = [
    ("Blake", "blake@terminusgps.com"),
    ("Peter", "peter@terminusgps.com"),
    ("Lili", "lili@terminusgps.com"),
]

FIELD_ENCRYPTION_KEY = "A77vVn8KpLMjLMkEptaAV232jd-TPS0ahX51aPuT8pc="
TIMEKEEPER_REPO_URL = "https://github.com/terminusgps/terminusgps-timekeeper/"
FILE_UPLOAD_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
SILENCED_SYSTEM_CHECKS = ["staticfiles.W004"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "encrypted_model_fields",
    "django_browser_reload",
    "terminusgps_timekeeper.apps.TerminusgpsTimekeeperConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "src.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_DIRS.append(BASE_DIR / "src" / "static")
MEDIA_URL = os.path.join(BASE_DIR, "media/")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
