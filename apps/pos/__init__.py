"""
==========================================================================
 POS APP - Modul Point of Sale / Kasir
==========================================================================
 Package ini menangani penjualan langsung ke konsumen (retail).

 Berisi:
 - models.py → MetodePembayaran, POSTransaction, POSTransactionItem
 - views.py  → Halaman POS (kasir) + API endpoint transaksi
 - urls.py   → Routing URL modul POS

 Perbedaan POS vs Sales Order:
 - POS: Penjualan retail langsung, tanpa workflow approval
 - SO: Penjualan B2B, ada approval (draft → confirmed → delivered)

 Model MetodePembayaran juga digunakan oleh modul lain:
 - apps/pembelian/ → Cara bayar Purchase Order
 - apps/penjualan/ → Cara bayar Sales Order

 Terhubung dengan:
 - apps/produk/ → Produk, Stok (cek ketersediaan & update stok)
 - apps/automation/ → Notifikasi Telegram saat transaksi POS selesai
 - apps/activity_log/ → Log perubahan stok
 - apps/dashboard/ → Statistik penjualan POS
 - apps/laporan/ → Laporan penjualan
==========================================================================
"""
from django.apps import AppConfig


class PosConfig(AppConfig):
    """
    Konfigurasi aplikasi POS (Point of Sale).

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app
    - verbose_name: Nama tampilan di Django Admin dan sidebar
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pos'
    verbose_name = 'POS/Kasir'
