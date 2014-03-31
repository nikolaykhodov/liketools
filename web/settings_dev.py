# Django settings for s project.
import os
DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': os.path.join(os.path.dirname(__file__), 'liketools_debug.sqlite'),  # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'liketools',  # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '1',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

APP_ID = 3063501
APP_KEY = '9N78cOIOTO3S8RJ8Zsdw'
SOCIAL_AUTH_HOST = 'http://local-lt.yaboltun.ru:8000'
