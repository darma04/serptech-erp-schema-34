"""
==========================================================================
 INVENTORY APPS - Konfigurasi aplikasi Django untuk modul Inventory
==========================================================================
 Mendaftarkan modul inventory ke Django dengan nama 'apps.inventory'.
 verbose_name ditampilkan di Django Admin sebagai 'Inventory'.
==========================================================================
"""

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Konfigurasi aplikasi Inventory."""
    default_auto_field = 'django.db.models.BigAutoField'  # Auto-increment BigInt untuk PK
    name = 'apps.inventory'                                # Path modul Python
    verbose_name = 'Inventory'                             # Nama tampilan di Admin
