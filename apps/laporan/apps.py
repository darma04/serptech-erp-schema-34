"""
==========================================================================
 LAPORAN APPS - Konfigurasi Aplikasi Laporan
==========================================================================
 Modul laporan tidak memiliki models sendiri — semua data diambil dari
 modul lain (produk, penjualan, pembelian, biaya, pos, inventory).
 Tidak ada signal atau ready() khusus.
==========================================================================
"""
from django.apps import AppConfig


class LaporanConfig(AppConfig):
    """Konfigurasi aplikasi Laporan — modul reporting data bisnis."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.laporan'      # Path app (harus sesuai INSTALLED_APPS)
    verbose_name = 'Laporan'   # Nama tampilan di Django Admin
