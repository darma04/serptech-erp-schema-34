"""
==========================================================================
 PENGATURAN APP - Modul Pengaturan / Settings Sistem
==========================================================================
 Package ini menangani konfigurasi dan pengaturan sistem ERP.

 Berisi:
 - models.py → PengaturanPerusahaan (singleton), TemplateCetak, BackupHistory
 - views.py  → Halaman pengaturan profil, perusahaan, template cetak, backup
 - forms.py  → Form untuk edit pengaturan
 - urls.py   → Routing URL modul pengaturan

 Model utama:
 - PengaturanPerusahaan: Data perusahaan (nama, alamat, logo, config)
   → Singleton pattern: hanya 1 record, diakses via .load()
 - TemplateCetak: Template untuk cetak struk, invoice, receipt
   → Digunakan di halaman print POS, SO, PO, biaya
 - BackupHistory: Riwayat backup database

 Terhubung dengan:
 - Semua halaman print → Mengambil data perusahaan & template cetak
 - Auth login/register → Mengambil nama & logo perusahaan
 - apps/dashboard/ → Menampilkan info perusahaan
==========================================================================
"""
from django.apps import AppConfig


class PengaturanConfig(AppConfig):
    """
    Konfigurasi aplikasi Pengaturan.

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app
    - verbose_name: Nama tampilan di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pengaturan'
    verbose_name = 'Pengaturan'
