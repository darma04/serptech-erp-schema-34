import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = ''akuntansi_akun'')')
print('TABLE EXISTS:', cursor.fetchone()[0])
