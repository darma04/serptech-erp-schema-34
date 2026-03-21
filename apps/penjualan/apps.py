"""
==========================================================================
 PENJUALAN APPS - Konfigurasi aplikasi Django untuk modul Penjualan
==========================================================================
"""
from django.apps import AppConfig

class PenjualanConfig(AppConfig):
    """Konfigurasi aplikasi Penjualan (Sales Module)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.penjualan'
    verbose_name = 'Penjualan'
