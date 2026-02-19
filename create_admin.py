import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smm_audit.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'Abdulvosit'
password = '20020722'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser created: {username} / {password}")
else:
    print(f"Superuser {username} already exists.")
