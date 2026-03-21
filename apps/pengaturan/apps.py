"""
==========================================================================
 PENGATURAN APPS - Konfigurasi aplikasi Django untuk Pengaturan
==========================================================================
"""
from django.apps import AppConfig

class PengaturanConfig(AppConfig):
    """Konfigurasi aplikasi Pengaturan (Settings/Konfigurasi Sistem)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pengaturan'
    verbose_name = 'Pengaturan'
