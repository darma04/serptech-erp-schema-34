"""
==========================================================================
 LAPORAN MODELS - Tidak Ada Model (Query-Only Module)
==========================================================================
 Modul laporan tidak memerlukan models sendiri karena:
 - Semua laporan menggunakan query langsung ke models modul lain
 - Data diambil dari: Produk, Stok, SalesOrder, PurchaseOrder, TransaksiBiaya
 - Tidak perlu menyimpan data tambahan — hanya menampilkan aggregasi

 Modul yang datanya digunakan:
 - apps/produk → Produk, Kategori, Stok, Gudang
 - apps/penjualan → SalesOrder, SalesOrderItem, Customer
 - apps/pembelian → PurchaseOrder, PurchaseOrderItem, Supplier
 - apps/biaya → TransaksiBiaya, KategoriBiaya
 - apps/pos → POSTransaction, POSTransactionItem
 - apps/activity_log → UserActivity (riwayat perubahan)
==========================================================================
"""
