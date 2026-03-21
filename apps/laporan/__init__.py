"""
==========================================================================
 LAPORAN APP - Modul Laporan / Reporting (Read-Only)
==========================================================================
 Package ini menampilkan laporan bisnis dari berbagai modul.
 Semua data bersifat READ-ONLY (hanya ditampilkan, tidak diubah).

 Berisi:
 - views.py → Views untuk 5 jenis laporan:
   1. Laporan Produk → Daftar produk + nilai aset
   2. Laporan Stok → Stok per gudang + riwayat pergerakan
   3. Laporan Penjualan → Sales Order + POS transaksi
   4. Laporan Pembelian → Purchase Order
   5. Laporan Keuangan → Ringkasan laba/rugi (pendapatan - pengeluaran - HPP)
 - urls.py → Routing URL modul laporan

 Fitur: Filter tanggal, export Excel/PDF, kalkulasi keuntungan

 Terhubung dengan SEMUA modul bisnis (query data dari models lain).
==========================================================================
"""
from django.apps import AppConfig


class LaporanConfig(AppConfig):
    """
    Konfigurasi aplikasi Laporan.

    Atribut:
    - default_auto_field: Tipe ID default (BigAutoField = 64-bit integer)
    - name: Path lengkap app (harus sesuai folder structure)
    - verbose_name: Nama tampilan di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.laporan'
    verbose_name = 'Laporan'
