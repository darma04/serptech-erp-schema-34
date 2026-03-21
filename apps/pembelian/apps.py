"""
==========================================================================
 PEMBELIAN APPS - Konfigurasi aplikasi Django untuk modul Pembelian
==========================================================================
"""

from django.apps import AppConfig


class PembelianConfig(AppConfig):
    """Konfigurasi aplikasi Pembelian (Purchase Module)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pembelian'
    verbose_name = 'Pembelian'
