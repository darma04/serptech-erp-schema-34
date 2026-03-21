"""
==========================================================================
 AUTOMATION APP - Automasi Notifikasi Telegram
==========================================================================
 Package ini menangani pengiriman notifikasi otomatis via Telegram Bot.

 Berisi:
 - models.py           → PengaturanTelegram, TemplatePesan, LogNotifikasi
 - signals.py          → Fungsi helper kirim notifikasi (dipanggil dari views)
 - telegram_service.py → Service layer untuk komunikasi dengan Telegram API
 - views.py            → CRUD pengaturan, template pesan, dan log notifikasi

 Alur notifikasi:
 1. User membuat transaksi (POS, biaya, PO, dll)
 2. View memanggil fungsi di signals.py (contoh: kirim_notifikasi_pos)
 3. Fungsi mengambil template pesan dari database
 4. Template di-render dengan data transaksi
 5. Pesan dikirim ke Telegram via Bot API
 6. Hasil pengiriman dicatat di LogNotifikasi

 Terhubung dengan:
 - apps/pos/views.py → Notifikasi saat transaksi POS selesai
 - apps/biaya/views.py → Notifikasi saat biaya baru dicatat
 - apps/pembelian/views.py → Notifikasi saat PO dibuat
==========================================================================
"""
