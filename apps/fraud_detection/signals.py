"""
==========================================================================
 FRAUD DETECTION SIGNALS — Deteksi Anomali Otomatis via Django Signals
==========================================================================
 File ini berisi signal handlers yang berjalan OTOMATIS saat event tertentu
 terjadi di database (create, update, delete). Setiap signal mendeteksi
 potensi kecurangan dan otomatis membuat FraudAlert.

 Signal yang terdaftar:
 ┌────────────────────────────────────────────────────────────────────┐
 │ No │ Nama                        │ Trigger     │ Anomali          │
 ├────┼─────────────────────────────┼─────────────┼──────────────────┤
 │ 1  │ detect_hapus_lunas          │ pre_delete  │ Hapus Data Lunas │
 │ 2  │ detect_transaksi_diluar_jam │ post_save   │ Diluar Jam       │
 │ 3  │ detect_diskon_berlebihan    │ post_save   │ Diskon Besar     │
 │ 4  │ detect_adjustment_besar     │ post_save   │ Adj Stok Besar   │
 │ 5  │ blokir_stok_minus_pos       │ pre_save    │ Stok Minus       │
 └────────────────────────────────────────────────────────────────────┘

 Cara kerja signal di Django:
 - pre_delete  → Berjalan SEBELUM record dihapus (bisa cancel delete)
 - post_save   → Berjalan SETELAH record disimpan (hanya logging)
 - pre_save    → Berjalan SEBELUM record disimpan (bisa cancel save)

 Terhubung dengan:
 → models.py   — FraudRule.load() untuk cek aturan, FraudAlert.objects.create()
 → apps.py     — Signal diimport di AppConfig.ready() agar aktif saat startup
 → pos/models  — Signal mendeteksi POSTransaction, POSItem
 → penjualan   — Signal mendeteksi SalesOrder
 → pembelian   — Signal mendeteksi PurchaseOrder
 → inventory   — Signal mendeteksi AdjustmentStok

 Catatan penting:
 - Signal ini GLOBAL — berlaku untuk semua save/delete di semua app
 - Kita filter berdasarkan sender.__name__ agar hanya model tertentu yang didengar
 - Untuk menghindari circular import, model di-import secara lazy di dalam function
==========================================================================
"""

# Import standar Python
import logging          # Logging error ke file/console
import traceback        # Stack trace untuk debugging
from decimal import Decimal  # Aritmatika presisi untuk uang

# Import Django signals framework
from django.db.models.signals import pre_delete, post_save, pre_save  # 3 jenis event
from django.dispatch import receiver  # Decorator untuk mendaftarkan signal handler
from django.utils import timezone     # Timezone-aware datetime

# Import model Fraud Detection
from apps.fraud_detection.models import FraudRule, FraudAlert

# Logger — semua error signal masuk ke log 'apps.fraud_detection.signals'
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#  FLAG BYPASS — Untuk menonaktifkan signal saat reset/restore
# ═══════════════════════════════════════════════════════════════
# Flag global yang diset True oleh fungsi reset_data() dan restore_data()
# di pengaturan/views.py SEBELUM melakukan bulk delete.
# Saat True, semua signal handler langsung return tanpa melakukan apapun.
# Ini mencegah FRAUD_BLOCK exception saat menghapus data secara massal.
#
# Penggunaan:
#   from apps.fraud_detection import signals as fraud_signals
#   fraud_signals._BYPASS_FRAUD_SIGNALS = True   # matikan signal
#   ... lakukan bulk delete ...
#   fraud_signals._BYPASS_FRAUD_SIGNALS = False  # nyalakan kembali
_BYPASS_FRAUD_SIGNALS = False


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS — Fungsi pendukung yang dipakai oleh signals
# ═══════════════════════════════════════════════════════════════

# Lazy import model dari app lain agar tidak circular import.
# Kenapa lazy? Karena saat signals.py di-load di AppConfig.ready(),
# belum tentu semua model dari app lain sudah terdaftar.
# Dengan lazy import (di dalam fungsi), model baru diakses saat
# signal benar-benar dipanggil (runtime), bukan saat import time.
def _get_model(app_label, model_name):
    """
    Lazy import model dari app lain menggunakan django.apps.
    ──────────────────────────────────────────────────────────
    Contoh: _get_model('pos', 'POSTransaction')
    Return: model class atau None jika tidak ditemukan
    """
    from django.apps import apps
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def check_operasional_time():
    """
    Cek apakah waktu saat ini DILUAR jam operasional toko.
    ────────────────────────────────────────────────────────
    Membaca FraudRule.load() untuk mendapat jam_operasional_mulai
    dan jam_operasional_selesai, lalu bandingkan dengan waktu sekarang.

    Return:
    → (True, rule)  → Saat ini di LUAR jam operasional (anomali)
    → (False, None)  → Saat ini di DALAM jam operasional (normal)

    Digunakan oleh: detect_transaksi_diluar_jam()
    """
    try:
        rule = FraudRule.load()
        now_time = timezone.localtime().time()  # Waktu lokal saat ini (hanya jam:menit)
        # Jika sekarang SEBELUM jam buka ATAU SESUDAH jam tutup → diluar jam
        if now_time < rule.jam_operasional_mulai or now_time > rule.jam_operasional_selesai:
            return True, rule
    except Exception:
        pass
    return False, None


# ═══════════════════════════════════════════════════════════════
#  SIGNAL 1: HAPUS DATA LUNAS (pre_delete)
# ═══════════════════════════════════════════════════════════════
# Trigger: Setiap kali user mencoba menghapus record dari database
# Target model: POSTransaction, SalesOrder, PurchaseOrder
# Aksi:
#   1. Cek apakah status record = lunas/confirmed/completed
#   2. Jika ya → buat FraudAlert jenis 'hapus_lunas' severity 'high'
#   3. Jika FraudRule.block_delete_paid = True → BLOKIR DELETE (raise Exception)
#
# Kenapa penting?
# → Kasir nakal bisa menghapus transaksi yang sudah lunas setelah menerima
#   uang dari customer. Uang masuk kantong, record transaksi hilang.
#   Signal ini mendeteksi dan bisa memblokir aksi tersebut.

@receiver(pre_delete)
def detect_hapus_lunas(sender, instance, **kwargs):
    """
    Deteksi dan blokir penghapusan data transaksi lunas.
    ─────────────────────────────────────────────────────
    sender   = Model class yang dihapus (POSTransaction, SalesOrder, dll)
    instance = Record spesifik yang akan dihapus
    """
    model_name = sender.__name__
    # BYPASS: Jika flag bypass aktif (saat reset/restore data), skip semua pengecekan
    if _BYPASS_FRAUD_SIGNALS:
        return
    # Hanya pantau 3 model transaksi utama
    if model_name in ['POSTransaction', 'SalesOrder', 'PurchaseOrder']:
        try:
            status = getattr(instance, 'status', '')
            # Hanya cek jika status = lunas/dikonfirmasi/selesai
            if status in ['paid', 'confirmed', 'delivered', 'completed']:
                rule = FraudRule.load()

                # Ambil user pelaku (kasir/pembuat) — berbeda field per model
                user = getattr(instance, 'kasir',
                    getattr(instance, 'created_by',
                        getattr(instance, 'dibuat_oleh', None)))
                # Ambil nominal transaksi
                nominal = getattr(instance, 'total_harga',
                    getattr(instance, 'grand_total', 0))

                # BUAT FRAUD ALERT — record anomali di database
                FraudAlert.objects.create(
                    jenis='hapus_lunas',
                    severity='high',
                    deskripsi=f"Percobaan menghapus data lunas: {model_name} ID {instance.pk}",
                    user_terkait=user,
                    nominal=nominal,
                    model_name=model_name,
                    object_id=str(instance.pk)
                )

                # BLOKIR DELETE jika pengaturan aktif
                # raise Exception akan membatalkan proses delete
                if rule.block_delete_paid:
                    raise Exception("FRAUD_BLOCK: Penghapusan transaksi lunas diblokir oleh sistem keamanan Fraud Rule.")

        except Exception as e:
            # Jika exception berasal dari FRAUD_BLOCK → lempar kembali
            # agar delete benar-benar gagal (ini yang memblokir)
            if "FRAUD_BLOCK" in str(e):
                raise  # Re-raise agar delete dibatalkan
            # Jika error lain (database error, dll) → hanya log, jangan crash
            logger.error(f"Error in detect_hapus_lunas: {e}")


# ═══════════════════════════════════════════════════════════════
#  SIGNAL 2: TRANSAKSI DILUAR JAM OPERASIONAL (post_save)
# ═══════════════════════════════════════════════════════════════
# Trigger: Setiap kali record BARU disimpan (created=True)
# Target model: POSTransaction, SalesOrder, PurchaseOrder
# Aksi: Buat FraudAlert jenis 'diluar_jam' severity 'medium'
#
# Kenapa penting?
# → Transaksi yang dibuat di luar jam operasional bisa mengindikasikan
#   akses tidak sah atau karyawan yang bekerja tanpa izin.
#   Contoh: transaksi jam 2 pagi → sangat mencurigakan.

@receiver(post_save)
def detect_transaksi_diluar_jam(sender, instance, created, **kwargs):
    """
    Deteksi transaksi yang dibuat di luar jam operasional.
    ─────────────────────────────────────────────────────
    Hanya berjalan saat record BARU dibuat (created=True),
    agar tidak trigger saat update data lama.
    """
    # Hanya untuk record BARU dari 3 model transaksi utama
    if created and sender.__name__ in ['POSTransaction', 'SalesOrder', 'PurchaseOrder']:
        try:
            is_outside, rule = check_operasional_time()
            if is_outside:
                now_time = timezone.localtime().time().strftime('%H:%M')
                user = getattr(instance, 'kasir',
                    getattr(instance, 'created_by',
                        getattr(instance, 'dibuat_oleh', None)))
                nominal = getattr(instance, 'total_harga',
                    getattr(instance, 'grand_total', 0))

                FraudAlert.objects.create(
                    jenis='diluar_jam',
                    severity='medium',
                    deskripsi=f"Transaksi dibuat diluar jam operasional ({now_time}): {sender.__name__} ID {instance.pk}",
                    user_terkait=user,
                    nominal=nominal,
                    model_name=sender.__name__,
                    object_id=str(instance.pk)
                )
        except Exception as e:
            logger.error(f"Error in detect_transaksi_diluar_jam: {e}")


# ═══════════════════════════════════════════════════════════════
#  SIGNAL 3: DISKON BERLEBIHAN (post_save)
# ═══════════════════════════════════════════════════════════════
# Trigger: Setiap kali POSTransaction disimpan (create atau update)
# Target model: POSTransaction
# Aksi: Buat FraudAlert jenis 'diskon_besar' severity 'high'
#
# Kenapa penting?
# → Kasir bisa memberikan diskon berlebihan untuk teman/keluarga,
#   atau memberikan diskon lalu mengantongi selisihnya.
#   Contoh: Barang Rp 1.000.000 di-diskon 80% → kasir bayar sendiri Rp 200.000.

@receiver(post_save)
def detect_diskon_berlebihan(sender, instance, created, **kwargs):
    """
    Deteksi diskon yang melebihi batas FraudRule.max_discount_percent.
    ──────────────────────────────────────────────────────────────────
    Berlaku untuk create DAN update (bukan hanya created=True),
    karena kasir bisa edit diskon setelah transaksi dibuat.
    """
    if sender.__name__ == 'POSTransaction':
        try:
            rule = FraudRule.load()
            # Ambil subtotal (sebelum diskon)
            subtotal = getattr(instance, 'subtotal', 0)
            if not subtotal and hasattr(instance, 'get_subtotal'):
                subtotal = instance.get_subtotal()

            # Ambil nominal diskon (bisa field 'diskon' atau 'potongan')
            diskon_nominal = getattr(instance, 'diskon', getattr(instance, 'potongan', 0))

            # Hitung persentase diskon
            if subtotal and subtotal > 0 and diskon_nominal > 0:
                diskon_percent = (Decimal(str(diskon_nominal)) / Decimal(str(subtotal))) * Decimal('100.0')

                # Bandingkan dengan batas dari FraudRule
                if diskon_percent > rule.max_discount_percent:
                    user = getattr(instance, 'kasir', getattr(instance, 'created_by', None))

                    # Cegah duplikat alert untuk transaksi yang sama
                    alert_exists = FraudAlert.objects.filter(
                        jenis='diskon_besar',
                        model_name=sender.__name__,
                        object_id=str(instance.pk)
                    ).exists()

                    if not alert_exists:
                        FraudAlert.objects.create(
                            jenis='diskon_besar',
                            severity='high',
                            deskripsi=f"Diskon {diskon_percent:.2f}% melebihi batas {rule.max_discount_percent:.2f}% pada POS ID {instance.pk}",
                            user_terkait=user,
                            nominal=diskon_nominal,
                            model_name=sender.__name__,
                            object_id=str(instance.pk)
                        )
        except Exception as e:
            logger.error(f"Error in detect_diskon_berlebihan: {e}")


# ═══════════════════════════════════════════════════════════════
#  SIGNAL 4: ADJUSTMENT STOK BESAR (post_save)
# ═══════════════════════════════════════════════════════════════
# Trigger: Setiap kali AdjustmentStok BARU dibuat (created=True)
# Target model: AdjustmentStok
# Threshold: qty > 50 unit ATAU nominal > Rp 1.000.000
# Aksi: Buat FraudAlert jenis 'adjustment_besar' severity 'high'
#
# Kenapa penting?
# → Adjustment stok adalah celah kecurangan klasik.
#   Karyawan gudang bisa menambah/mengurangi stok di sistem
#   tanpa perpindahan fisik barang → barang hilang secara diam-diam.
#   Threshold 50 pcs / Rp 1 juta untuk menangkap adjustment abnormal.

@receiver(post_save)
def detect_adjustment_besar(sender, instance, created, **kwargs):
    """
    Deteksi adjustment stok yang besar (qty > 50 atau nominal > Rp 1 juta).
    ───────────────────────────────────────────────────────────────────────
    Hanya untuk record BARU (created=True) agar tidak trigger saat update.
    """
    if created and sender.__name__ == 'AdjustmentStok':
        try:
            qty = getattr(instance, 'jumlah', 0)
            produk = getattr(instance, 'produk', None)
            harga = getattr(produk, 'harga_beli', 0) if produk else 0
            nominal = Decimal(str(qty)) * Decimal(str(harga))

            # Threshold: qty > 50 unit ATAU nominal > Rp 1.000.000
            if qty > 50 or nominal > Decimal('1000000'):
                user = getattr(instance, 'dibuat_oleh', getattr(instance, 'created_by', None))
                FraudAlert.objects.create(
                    jenis='adjustment_besar',
                    severity='high',
                    deskripsi=f"Adjustment stok besar terpantau pada produk {produk} sejumlah {qty} ({getattr(instance, 'tipe', '')})",
                    user_terkait=user,
                    nominal=nominal,
                    model_name=sender.__name__,
                    object_id=str(instance.pk)
                )
        except Exception as e:
            logger.error(f"Error in detect_adjustment_besar: {e}")


# ═══════════════════════════════════════════════════════════════
#  SIGNAL 5: BLOKIR STOK MINUS — POS ITEM (pre_save)
# ═══════════════════════════════════════════════════════════════
# Trigger: Setiap kali POSItem (item baris POS) AKAN disimpan
# Target model: POSItem (baris item dalam transaksi POS)
# Aksi:
#   1. Cek apakah FraudRule.block_negative_stock = True
#   2. Jika ya, cek stok produk di gudang terkait
#   3. Jika qty > stok tersedia → BLOKIR SAVE (raise Exception)
#   4. Buat FraudAlert jenis 'stok_minus'
#
# Kenapa pre_save (bukan post_save)?
# → Karena kita perlu MENCEGAH save, bukan hanya melaporkan.
#   pre_save berjalan SEBELUM data masuk database.
#   Jika raise Exception di pre_save → record tidak jadi tersimpan.

@receiver(pre_save)
def blokir_stok_minus_pos(sender, instance, **kwargs):
    """
    Blokir item POS jika stok tidak mencukupi.
    ──────────────────────────────────────────────
    Hanya aktif jika FraudRule.block_negative_stock = True.
    Hanya cek untuk record BARU (instance.pk belum ada).
    """
    if sender.__name__ == 'POSItem':
        try:
            rule = FraudRule.load()
            # Hanya berlaku jika flag block_negative_stock aktif
            if rule.block_negative_stock:
                produk = getattr(instance, 'produk', None)
                qty = getattr(instance, 'kuantitas', 0)

                if produk and qty > 0:
                    # Ambil gudang dari transaksi POS parent
                    transaksi = getattr(instance, 'transaksi', None)
                    gudang = getattr(transaksi, 'gudang', None)

                    # Cek stok tersedia di gudang terkait
                    if hasattr(produk, 'get_stok') and gudang:
                        stok_tersedia = produk.get_stok(gudang=gudang)

                        # Jika record BARU dan qty > stok → BLOKIR
                        if not instance.pk and qty > stok_tersedia:
                            # Catat anomali dulu
                            user = getattr(transaksi, 'kasir', None)
                            FraudAlert.objects.create(
                                jenis='stok_minus',
                                severity='medium',
                                deskripsi=f"POS Item diblokir: Kuantitas {qty} melebihi stok tersedia ({stok_tersedia}) untuk produk {produk.nama}",
                                user_terkait=user,
                                nominal=0,
                                model_name='POSItem',
                                object_id=''
                            )
                            # Raise exception → cancel save
                            raise Exception(f"FRAUD_BLOCK: Stok {produk.nama} tidak mencukupi (tersedia: {stok_tersedia}, diminta: {qty}).")
        except Exception as e:
            if "FRAUD_BLOCK" in str(e):
                raise  # Re-raise agar save dibatalkan
            logger.error(f"Error in blokir_stok_minus_pos: {e}")
