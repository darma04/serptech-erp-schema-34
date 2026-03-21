"""
==========================================================================
 FRAUD DETECTION APP — Modul Deteksi Kecurangan & Rekonsiliasi Kas
==========================================================================
 Aplikasi Django untuk mendeteksi dan mencegah kecurangan dalam sistem ERP.

 Komponen utama:
 - FraudRule (models.py)
   → Singleton pengaturan pencegahan fraud (blokir hapus lunas, batas diskon, dll)
 - FraudAlert (models.py)
   → Log anomali kecurangan yang terdeteksi otomatis oleh sistem
 - CashReconciliation (models.py)
   → Rekonsiliasi kas kasir (blind cash closing) — verifikasi uang fisik vs sistem

 Integrasi dengan modul lain:
 - activity_log → FraudAlert.activity FK ke UserActivity
 - pos          → CashReconciliation mengacu pada transaksi POS per shift
 - produk       → CashReconciliation.gudang FK ke Gudang (cabang)
 - ai_assistant → Intent 'fraud_detection' mengumpulkan data fraud untuk AI Chat
 - pengaturan   → ManajemenData menampilkan statistik fraud, backup/reset/restore
                   mencakup data fraud

 URL namespace: 'fraud_detection'
 URL prefix:    /fraud/
==========================================================================
"""
