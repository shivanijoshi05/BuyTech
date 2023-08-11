import os
from decouple import config
# Load environment variables from .env file
DJANGO_ENV = config('DJANGO_ENV', default='development')
print(DJANGO_ENV)
if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *
    
