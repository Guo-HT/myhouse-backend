"""
WSGI config for MyHouse project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyHouse.settings')

application = get_wsgi_application()

# 开启mqtt监听
# from common import mqtt_sub

#mqtt_sub.connect_mqtt_server()
