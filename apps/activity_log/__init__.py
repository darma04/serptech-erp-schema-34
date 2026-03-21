"""
==========================================================================
 ACTIVITY LOG APP - Sistem Audit Trail & Logging Aktivitas
==========================================================================
 Package ini mencatat SEMUA aktivitas user di sistem sebagai audit trail.

 Berisi:
 - models.py        → Model UserActivity (record log aktivitas)
 - middleware.py    → Middleware untuk meng-capture request aktif
 - signals.py       → Auto-logging via Django signals (create/update/delete)
 - stock_signals.py → Logging khusus perubahan stok (lebih detail)
 - views.py         → Halaman daftar log aktivitas
 - apps.py          → Konfigurasi app + pendaftaran signals saat startup

 Cara kerja:
 1. Middleware menyimpan request aktif di thread-local storage
 2. Signals mendeteksi perubahan model (pre_save, post_save, post_delete)
 3. Setiap perubahan dicatat ke tabel UserActivity dengan detail:
    - Siapa (user), Apa (action), Kapan (timestamp)
    - Model apa yang berubah, field mana yang berubah (delta tracking)
    - IP address dan user agent untuk keamanan
==========================================================================
"""
