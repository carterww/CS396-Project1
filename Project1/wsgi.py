"""
WSGI config for Project1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import schedule
from assetman.schedule import update_stock_data

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')

schedule.every().friday.at("23:59").do(update_stock_data)

application = get_wsgi_application()
