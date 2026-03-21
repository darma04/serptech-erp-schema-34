"""
==========================================================================
 PRODUK APP - Modul Manajemen Produk & Stok
==========================================================================
 Package ini adalah DATA MASTER untuk semua modul bisnis.
 Hampir SEMUA modul lain bergantung pada model di sini.

 Berisi:
 - models.py → Kategori, Satuan, Produk, Gudang, Stok
 - views.py  → CRUD produk, kategori, satuan + API pencarian produk
 - forms.py  → Form Django untuk input data produk
 - urls.py   → Routing URL modul produk

 Relasi antar model:
 - Kategori (1) → (N) Produk (setiap produk punya 1 kategori)
 - Satuan (1) → (N) Produk (setiap produk punya 1 satuan: pcs, kg, liter)
 - Produk (N) ←→ (N) Gudang melalui Stok (stok per produk per gudang)

 Digunakan oleh:
 - apps/pos/ → Mencari & menambah produk ke transaksi POS
 - apps/penjualan/ → Item Sales Order
 - apps/pembelian/ → Item Purchase Order
 - apps/inventory/ → Transfer stok & adjustment stok
 - apps/laporan/ → Laporan produk & stok
 - apps/dashboard/ → Statistik produk
==========================================================================
"""
from django.apps import AppConfig


class ProdukConfig(AppConfig):
    """
    Konfigurasi aplikasi Produk.

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app
    - verbose_name: Nama tampilan di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produk'
    verbose_name = 'Produk'
