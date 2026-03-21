"""
==========================================================================
 ACTIVITY LOG ADMIN - Konfigurasi Django Admin
==========================================================================
 Modul activity_log tidak mendaftarkan model di Django Admin karena:
 - UserActivity hanya diakses via halaman log aktivitas di frontend
 - Data bersifat read-only (tidak perlu CRUD via admin)
 - Volume data sangat besar — lebih baik dilihat via halaman khusus
==========================================================================
"""
from django.contrib import admin

# Tidak ada model yang didaftarkan ke Django Admin untuk modul ini
