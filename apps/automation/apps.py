"""
==========================================================================
 AUTOMATION APPS - Konfigurasi Aplikasi Automasi (Telegram)
==========================================================================
 Konfigurasi Django app untuk modul automasi.
 Method ready() mengimpor signals.py agar signal handler terdaftar
 saat Django startup. Ini diperlukan agar notifikasi otomatis aktif.
==========================================================================
"""
from django.apps import AppConfig


class AutomationConfig(AppConfig):
    """Konfigurasi aplikasi Automation — integrasi Telegram dan notifikasi otomatis."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.automation'   # Path app (harus sesuai INSTALLED_APPS)
    verbose_name = 'Automasi'  # Nama tampilan di Django Admin

    def ready(self):
        """
        Import signals.py saat startup agar signal handlers aktif.
        noqa: F401 → Abaikan warning "imported but unused" karena
        import ini memang hanya untuk efek samping (mendaftarkan signals).
        """
        import apps.automation.signals  # noqa: F401
