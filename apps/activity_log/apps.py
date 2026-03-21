"""
==========================================================================
 ACTIVITY LOG APP CONFIG - Konfigurasi Aplikasi Pencatatan Aktivitas
==========================================================================
 File ini mengkonfigurasi modul Activity Log untuk Django.

 Fungsi modul:
 - Mencatat SEMUA aktivitas user di sistem (CRUD operations)
 - Tracking perubahan stok secara detail (before/after)
 - Menyimpan IP address dan user agent untuk audit trail
 - Menyediakan halaman log aktivitas untuk admin

 Terhubung dengan:
 - models.py → UserActivity (model utama pencatatan)
 - signals.py → Auto-log via Django post_save/post_delete signals
 - stock_signals.py → Log perubahan stok detail per transaksi
 - middleware.py → Tracking request info (IP, user agent)
 - views.py → Halaman daftar aktivitas untuk admin
==========================================================================
"""
from django.apps import AppConfig


class ActivityLogConfig(AppConfig):
    """Konfigurasi aplikasi Activity Log — pencatatan aktivitas user."""
    default_auto_field = 'django.db.models.BigAutoField'  # Tipe ID default = BigAutoField (int 64-bit)
    name = 'apps.activity_log'     # Path lengkap app (harus cocok dengan folder structure)
    verbose_name = 'Activity Log'  # Nama tampilan di Django Admin

    def ready(self):
        """
        Dipanggil otomatis SEKALI saat Django startup (runserver, migrate, dll).
        Di sini kita mendaftarkan signal handlers untuk auto-logging
        ke SEMUA model di aplikasi (kecuali yang di-exclude).
        """
        from .signals import register_signals
        register_signals()
