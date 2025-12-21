"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# 스토리지 백엔드 확인 로그
try:
    from django.core.files.storage import default_storage
    print(f"[WSGI Debug] default_storage backend: {default_storage.__class__.__name__}")
    print(f"[WSGI Debug] default_storage location: {getattr(default_storage, 'location', 'N/A')}")
    print(f"[WSGI Debug] default_storage base_url: {getattr(default_storage, 'base_url', 'N/A')}")
except Exception as e:
    print(f"[WSGI Debug] Error checking storage: {e}")
