"""Test SERPTECH PDF generation for slip gaji and biaya."""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.automation.pdf_generator import generate_penggajian_pdf, generate_biaya_pdf
from apps.hr.models import Penggajian
from apps.biaya.models import TransaksiBiaya

s = Penggajian.objects.first()
b = TransaksiBiaya.objects.first()

if s:
    p1 = generate_penggajian_pdf(s)
    print('Slip Gaji OK:', os.path.basename(p1))
    print('URL: http://127.0.0.1:8000/media/temp_pdf/' + os.path.basename(p1))
else:
    print('No Penggajian data found')

if b:
    p2 = generate_biaya_pdf(b)
    print('Biaya OK:', os.path.basename(p2))
    print('URL: http://127.0.0.1:8000/media/temp_pdf/' + os.path.basename(p2))
else:
    print('No TransaksiBiaya data found')
