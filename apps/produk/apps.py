"""
==========================================================================
 PRODUK APPS - Konfigurasi Aplikasi Produk
==========================================================================
 Mendaftarkan 'apps.produk' sebagai Django App.

 Koneksi:
 - config/settings.py → INSTALLED_APPS: "apps.produk"
==========================================================================
"""

from django.apps import AppConfig


class ProdukConfig(AppConfig):
    """Konfigurasi aplikasi Produk."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produk'       # Path modul Python
    verbose_name = 'Produk'    # Nama di admin panel
