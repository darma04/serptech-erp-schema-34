"""
Script test regenerasi debug PDF untuk verifikasi template fix.
Jalankan dari folder: SERPTECH-Software-39
  python test_pdf_debug.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

django.setup()

from django.template.loader import render_to_string
from apps.automation.pdf_generator import _html_to_pdf, _get_template_cetak
from apps.pengaturan.models import PengaturanPerusahaan

try:
    perusahaan = PengaturanPerusahaan.load()
except Exception:
    perusahaan = None

# ── Test Slip Gaji ────────────────────────────────────────────────────────────
print(">>> Mencari data slip gaji untuk test...")
from apps.hr.models import SlipGaji
slip = SlipGaji.objects.first()
if slip:
    template = _get_template_cetak('slip_gaji')
    context = {'slip': slip, 'perusahaan': perusahaan, 'template': template}

    # Render HTML debug
    html = render_to_string('hr/penggajian_print.html', context)
    debug_path = os.path.join(BASE_DIR, 'media', 'temp_pdf', 'debug_gaji_fix.html')
    os.makedirs(os.path.dirname(debug_path), exist_ok=True)
    with open(debug_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  HTML debug: {debug_path}")

    # Generate PDF
    pdf_path = _html_to_pdf(html, "TEST_GAJI_FIX")
    if pdf_path:
        print(f"  PDF OK: {pdf_path}")
    else:
        print("  PDF GAGAL!")
else:
    print("  Tidak ada data slip gaji.")

# ── Test Biaya ────────────────────────────────────────────────────────────────
print(">>> Mencari data biaya untuk test...")
from apps.biaya.models import TransaksiBiaya
biaya = TransaksiBiaya.objects.first()
if biaya:
    template_b = _get_template_cetak('expense')
    context_b = {'transaksi': biaya, 'perusahaan': perusahaan, 'template': template_b}

    html_b = render_to_string('biaya/transaksi_biaya_print.html', context_b)
    debug_path_b = os.path.join(BASE_DIR, 'media', 'temp_pdf', 'debug_biaya_fix.html')
    with open(debug_path_b, 'w', encoding='utf-8') as f:
        f.write(html_b)
    print(f"  HTML debug: {debug_path_b}")

    pdf_path_b = _html_to_pdf(html_b, "TEST_BIAYA_FIX")
    if pdf_path_b:
        print(f"  PDF OK: {pdf_path_b}")
    else:
        print("  PDF GAGAL!")
else:
    print("  Tidak ada data biaya.")

print("\n=== SELESAI ===")
print("Buka file debug di browser untuk verifikasi tampilan:")
print("  http://127.0.0.1:8001/media/temp_pdf/debug_gaji_fix.html")
print("  http://127.0.0.1:8001/media/temp_pdf/debug_biaya_fix.html")
