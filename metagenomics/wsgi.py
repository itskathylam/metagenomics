"""
WSGI config for metagenomics project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/home/kathy/metagenomics/metagenomics/metagenomics')
sys.path.append('/home/kathy/metagenomics/metagenomics')
sys.path.append('/home/kathy/metagenomics')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metagenomics.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
