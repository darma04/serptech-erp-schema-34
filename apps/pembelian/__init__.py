"""
==========================================================================
 PEMBELIAN APP - Modul Purchase Order (PO) & Supplier
==========================================================================
 Package ini menangani pembelian barang dari supplier.

 Berisi:
 - models.py → Supplier, PurchaseOrder, PurchaseOrderItem
 - views.py  → CRUD supplier & purchase order
 - forms.py  → Form Django + formset untuk input PO
 - urls.py   → Routing URL modul pembelian

 Alur PO: Draft → Submitted → Approved → Received (stok masuk ke gudang)

 Saat status 'received':
 - Stok ditambahkan ke gudang tujuan
 - Log perubahan stok dicatat di activity_log

 Terhubung dengan:
 - apps/produk/ → Produk, Gudang, Stok (data master)
 - apps/pos/ → MetodePembayaran (cara bayar PO)
 - apps/activity_log/ → Log stok masuk
 - apps/dashboard/ → Statistik pembelian
 - apps/laporan/ → Laporan pembelian
==========================================================================
"""
from django.apps import AppConfig


class PembelianConfig(AppConfig):
    """
    Konfigurasi aplikasi Pembelian.

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app (harus sesuai folder structure)
    - verbose_name: Nama tampilan di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pembelian'
    verbose_name = 'Pembelian'
