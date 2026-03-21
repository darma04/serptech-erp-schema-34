"""
==========================================================================
 BIAYA APPS - Konfigurasi aplikasi Django untuk modul Biaya
==========================================================================
"""
from django.apps import AppConfig

class BiayaConfig(AppConfig):
    """Konfigurasi aplikasi Biaya (Expense Management)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.biaya'
    verbose_name = 'Biaya'
