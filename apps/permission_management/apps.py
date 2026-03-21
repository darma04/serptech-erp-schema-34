"""
==========================================================================
 PERMISSION MANAGEMENT APP CONFIG - Konfigurasi Manajemen Hak Akses
==========================================================================
 File ini mengkonfigurasi modul Permission Management.

 Fungsi modul:
 - Halaman manajemen role (Daftar Role, CRUD Role)
 - Halaman manajemen permission per role per modul
 - Tabel permission matrix (modul × aksi CRUD)
 - SubCRUD management (permission sub-modul)

 Terhubung dengan:
 - views.py → PermissionListView, PermissionUpdateView
 - views_roles.py → RoleListView, RoleCreateView, RoleUpdateView
 - core/models.py → RolePermission model
 - core/permissions.py → Logika pengecekan (dipakai oleh views ini)
==========================================================================
"""
from django.apps import AppConfig


class PermissionManagementConfig(AppConfig):
    """Konfigurasi aplikasi Permission Management — kelola hak akses role."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.permission_management'
    verbose_name = 'Permission Management'
