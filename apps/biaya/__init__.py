"""
==========================================================================
 BIAYA APP - Modul Manajemen Biaya / Pengeluaran
==========================================================================
 Package ini menangani pencatatan biaya operasional perusahaan.

 Berisi:
 - models.py → KategoriBiaya (kategori pengeluaran) & TransaksiBiaya (pencatatan)
 - views.py  → CRUD kategori biaya & transaksi biaya
 - forms.py  → Form Django untuk input data biaya
 - urls.py   → Routing URL modul biaya

 Terhubung dengan:
 - apps/automation/ → Notifikasi Telegram saat biaya baru dicatat
 - apps/activity_log/ → Audit trail setiap perubahan data biaya
 - apps/dashboard/ → Statistik biaya di halaman dashboard
 - apps/laporan/ → Laporan keuangan (pengeluaran)
==========================================================================
"""
