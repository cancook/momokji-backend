from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

# WSGI application
WSGI_APPLICATION = 'config.wsgi.deploy.application'

STATIC_ROOT = '/home/ubuntu/code/cancook-backend/'