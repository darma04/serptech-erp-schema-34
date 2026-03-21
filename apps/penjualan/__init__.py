"""
==========================================================================
 PENJUALAN APP - Modul Sales Order (SO) & Customer
==========================================================================
 Package ini menangani penjualan barang ke customer.

 Berisi:
 - models.py → Customer, SalesOrder, SalesOrderItem
 - views.py  → CRUD customer & sales order
 - forms.py  → Form Django + formset untuk input SO
 - urls.py   → Routing URL modul penjualan

 Alur SO: Draft → Confirmed → Delivered → Completed
                                  ↓
                            Stok berkurang

 Perbedaan SO vs POS:
 - SO: Penjualan B2B (antar bisnis), ada approval workflow
 - POS: Penjualan langsung ke konsumen, tanpa approval

 Terhubung dengan:
 - apps/produk/ → Produk, Stok (cek ketersediaan & update stok)
 - apps/pos/ → MetodePembayaran
 - apps/activity_log/ → Log perubahan stok saat delivery
 - apps/dashboard/ → Statistik penjualan
 - apps/laporan/ → Laporan penjualan
==========================================================================
"""
from django.apps import AppConfig


class PenjualanConfig(AppConfig):
    """
    Konfigurasi aplikasi Penjualan.

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app (harus sesuai folder structure)
    - verbose_name: Nama tampilan di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.penjualan'
    verbose_name = 'Penjualan'
