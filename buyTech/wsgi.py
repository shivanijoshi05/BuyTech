"""
WSGI config for buyTech project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from decouple import config

# Load environment variables from .env file
DJANGO_ENV = config('DJANGO_ENV', default='development')

# Rest of the wsgi.py code...

# Set the Django settings module based on environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buyTech.' + DJANGO_ENV)


application = get_wsgi_application()
