"""
==========================================================================
 SAMPLE APPS - Konfigurasi Aplikasi Contoh Starter Kit
==========================================================================
 Modul sample bawaan starter kit. Tidak memiliki models atau signals.
 Digunakan sebagai contoh/referensi untuk memahami struktur app Django.
==========================================================================
"""
from django.apps import AppConfig


class SampleConfig(AppConfig):
    """Konfigurasi aplikasi Sample — template contoh modul."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sample"  # Path app (harus sesuai INSTALLED_APPS)
