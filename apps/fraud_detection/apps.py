"""
==========================================================================
 FRAUD DETECTION APP CONFIG — Konfigurasi Aplikasi Django
==========================================================================
 File ini mendaftarkan app 'fraud_detection' ke Django.
 Fungsi utama: menjalankan import signals di method ready()
 agar semua signal handler aktif saat server Django start.

 Terhubung dengan:
 → settings.py (INSTALLED_APPS) — app terdaftar sebagai 'apps.fraud_detection'
 → signals.py — di-import di ready() agar signal handler aktif
==========================================================================
"""

# Import AppConfig dari Django — base class untuk konfigurasi aplikasi
from django.apps import AppConfig


class FraudDetectionConfig(AppConfig):
    """
    Konfigurasi app Fraud Detection.
    ─────────────────────────────────
    - name:         Path lengkap app (sesuai INSTALLED_APPS di settings.py)
    - verbose_name: Nama yang ditampilkan di Django Admin
    - ready():      Method yang dijalankan saat Django memuat app ini
    """
    # Field ID otomatis menggunakan BigAutoField (integer 64-bit)
    default_auto_field = 'django.db.models.BigAutoField'

    # Path app — harus sesuai dengan entry di INSTALLED_APPS settings.py
    name = 'apps.fraud_detection'

    # Nama tampilan di Django Admin dan sidebar menu
    verbose_name = 'Fraud Detection'

    def ready(self):
        """
        Dipanggil otomatis saat Django selesai memuat app ini.
        ────────────────────────────────────────────────────────
        Import signals.py di sini agar semua signal handler
        (pre_delete, post_save, pre_save) aktif dan bisa mendeteksi anomali.

        Kenapa di ready() dan bukan di __init__.py?
        → Karena ready() dipanggil SETELAH semua model terdaftar,
          sehingga signal bisa mengakses model dari app lain tanpa error.
          Jika import di __init__.py, bisa terjadi circular import.
        """
        import apps.fraud_detection.signals  # noqa: F401 — import untuk side effect
