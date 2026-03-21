"""
==========================================================================
 AUTOMATION SIGNALS - Helper Notifikasi Telegram per Jenis Transaksi
==========================================================================
 File ini berisi fungsi-fungsi helper yang menyiapkan data notifikasi
 dan mengirimnya ke Telegram. Disebut "signals" karena awalnya dirancang
 sebagai signal handler, tapi sekarang DIPANGGIL LANGSUNG dari views.

 Alasan dipanggil dari views, bukan dari post_save signal:
 - Saat post_save terpicu, items transaksi belum tersimpan
 - Kita butuh data lengkap (items + total) sebelum kirim notifikasi
 - Jadi fungsi ini dipanggil SETELAH semua items disimpan di views

 Fungsi yang tersedia:
 ┌───────────────────────────────┬──────────────────────────────────────┐
 │ Fungsi                        │ Dipanggil dari                       │
 ├───────────────────────────────┼──────────────────────────────────────┤
 │ kirim_notifikasi_pos()        │ pos/views.py setelah transaksi POS   │
 │ kirim_notifikasi_sales_order()│ penjualan/views.py setelah SO dibuat │
 │ kirim_notifikasi_purchase_order()│ pembelian/views.py setelah PO dibuat│
 │ kirim_notifikasi_biaya()      │ biaya/views.py setelah biaya dibuat  │
 └───────────────────────────────┴──────────────────────────────────────┘

 Setiap fungsi mengikuti pola yang sama:
 1. refresh_from_db() → Ambil data terbaru dari database
 2. Format detail items menjadi string untuk pesan
 3. Siapkan dict data sesuai placeholder template
 4. Panggil kirim_notifikasi_async() → kirim di background thread

 Terhubung dengan:
 - telegram_service.py → kirim_notifikasi_async(), format_angka()
 - views.py (pos, penjualan, pembelian, biaya) → Memanggil fungsi di sini
 - models.py → TemplatePesan (template pesan diambil dari database)
==========================================================================
"""

# Import fungsi dari telegram_service.py:
# - kirim_notifikasi_async: mengirim notifikasi di background thread
# - format_angka: format angka menjadi "1,000,000" (dengan pemisah ribuan)
from .telegram_service import kirim_notifikasi_async, format_angka


def kirim_notifikasi_pos(instance):
    """
    Kirim notifikasi Telegram untuk transaksi POS yang baru selesai.

    Parameter:
        instance: Object POSTransaction yang sudah memiliki items lengkap

    Dipanggil dari:
        pos/views.py → setelah checkout berhasil dan semua POSTransactionItem tersimpan

    Alur data:
    1. Refresh data dari DB → pastikan subtotal/total terbaru
    2. Loop semua items → format menjadi string list
    3. Siapkan dict data → sesuai placeholder di template POS
    4. Kirim via kirim_notifikasi_async('pos', ...) → background thread

    Data yang dikirim ke template:
    - nomor_transaksi, tanggal, kasir, gudang
    - detail_items (daftar produk x qty = subtotal)
    - subtotal, diskon, pajak, total
    - metode_pembayaran, status, customer
    """
    # Refresh data dari database agar subtotal/total terbaru
    # Kenapa? Karena setelah items disimpan, total mungkin berubah
    instance.refresh_from_db()

    # ═══ Format detail items ═══
    # Loop semua POSTransactionItem yang terkait
    # Format: "  1. Beras Premium x2 = Rp 30,000"
    items = instance.items.all()  # QuerySet: semua item transaksi ini
    detail_items = ""
    for i, item in enumerate(items, 1):  # enumerate mulai dari 1 (bukan 0)
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"

    # Jika tidak ada items (seharusnya tidak terjadi, tapi jaga-jaga)
    if not detail_items:
        detail_items = "  (Belum ada item)"

    # ═══ Siapkan data untuk template ═══
    # Key di dict ini HARUS sesuai dengan placeholder {{key}} di TemplatePesan
    data = {
        # Identitas transaksi
        'nomor_transaksi': instance.nomor_transaksi,          # Contoh: TRX-20260306-001
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',

        # Pelaku transaksi
        'kasir': instance.kasir.get_full_name() or instance.kasir.username if instance.kasir else '-',
        'gudang': str(instance.gudang) if instance.gudang else '-',  # Nama gudang/cabang

        # Detail item (string multi-line)
        'detail_items': detail_items.strip(),

        # Nominal
        'subtotal': format_angka(instance.subtotal),          # Sebelum diskon & pajak
        'diskon': format_angka(instance.diskon),              # Total diskon
        'pajak': format_angka(instance.pajak),                # Total pajak (PPN)
        'total': format_angka(instance.total_harga),          # Grand total

        # Info pembayaran
        'metode_pembayaran': str(instance.metode_pembayaran) if instance.metode_pembayaran else '-',
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'customer': instance.nama_customer or 'Walk-in',      # Default: Walk-in (tanpa nama)
    }

    # Kirim notifikasi di background thread (tidak blocking view)
    # Parameter: jenis_transaksi, nomor_referensi, data_dict
    kirim_notifikasi_async('pos', instance.nomor_transaksi, data)


def kirim_notifikasi_sales_order(instance):
    """
    Kirim notifikasi Telegram untuk Sales Order yang baru dibuat.

    Parameter:
        instance: Object SalesOrder yang sudah memiliki items lengkap

    Dipanggil dari:
        penjualan/views.py → setelah SO dan semua SalesOrderItem tersimpan

    Perbedaan dengan POS:
    - POS = penjualan langsung di kasir (Walk-in customer)
    - SO = penjualan via order (customer terdaftar + alamat pengiriman)
    - POS pakai 'kasir', SO pakai 'customer' dan 'dibuat_oleh'
    """
    # Refresh data dari DB → pastikan total terbaru setelah items disimpan
    instance.refresh_from_db()

    # ═══ Format detail items SO ═══
    items = instance.items.all()  # QuerySet: semua SalesOrderItem
    detail_items = ""
    for i, item in enumerate(items, 1):
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"

    if not detail_items:
        detail_items = "  (Belum ada item)"

    # ═══ Data untuk template Sales Order ═══
    data = {
        'nomor_so': instance.nomor_so,                        # Contoh: SO/2026/03/0015
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',
        'customer': str(instance.customer) if instance.customer else '-',  # Nama customer terdaftar
        'gudang': str(instance.gudang) if instance.gudang else '-',
        'detail_items': detail_items.strip(),
        'subtotal': format_angka(instance.subtotal),
        'diskon': format_angka(instance.diskon),
        'pajak': format_angka(instance.pajak),
        'total': format_angka(instance.total_harga),
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        # Siapa yang membuat SO (bukan kasir, tapi user yang login)
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
    }

    kirim_notifikasi_async('sales_order', instance.nomor_so, data)


def kirim_notifikasi_purchase_order(instance):
    """
    Kirim notifikasi Telegram untuk Purchase Order yang baru dibuat.

    Parameter:
        instance: Object PurchaseOrder yang sudah memiliki items lengkap

    Dipanggil dari:
        pembelian/views.py → setelah PO dan semua PurchaseOrderItem tersimpan

    Perbedaan dengan SO:
    - SO = penjualan ke customer (uang masuk)
    - PO = pembelian dari supplier (uang keluar)
    - PO pakai 'supplier' bukan 'customer'
    - PO tidak punya field 'diskon' (hanya subtotal + pajak)
    """
    # Refresh data dari DB
    instance.refresh_from_db()

    # ═══ Format detail items PO ═══
    items = instance.items.all()  # QuerySet: semua PurchaseOrderItem
    detail_items = ""
    for i, item in enumerate(items, 1):
        detail_items += f"  {i}. {item.produk.nama} x{item.jumlah} = Rp {format_angka(item.subtotal)}\n"

    if not detail_items:
        detail_items = "  (Belum ada item)"

    # ═══ Data untuk template Purchase Order ═══
    data = {
        'nomor_po': instance.nomor_po,                        # Contoh: PO/2026/03/0008
        'tanggal': instance.tanggal.strftime('%d/%m/%Y %H:%M') if instance.tanggal else '-',
        'supplier': str(instance.supplier) if instance.supplier else '-',  # Nama supplier
        'gudang': str(instance.gudang) if instance.gudang else '-',        # Gudang tujuan
        'detail_items': detail_items.strip(),
        'subtotal': format_angka(instance.subtotal),
        'pajak': format_angka(instance.pajak),
        'total': format_angka(instance.total_harga),
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
    }

    kirim_notifikasi_async('purchase_order', instance.nomor_po, data)


def kirim_notifikasi_biaya(instance):
    """
    Kirim notifikasi Telegram untuk Transaksi Biaya yang baru dibuat.

    Parameter:
        instance: Object TransaksiBiaya yang baru tersimpan

    Dipanggil dari:
        biaya/views.py → setelah TransaksiBiaya berhasil disimpan

    Perbedaan dengan POS/SO/PO:
    - Biaya TIDAK punya items (single line item)
    - Hanya ada jumlah sekali, bukan subtotal dari banyak item
    - Ada field kategori biaya (Listrik, Gaji, Sewa, dll)
    """
    # Refresh data dari DB
    instance.refresh_from_db()

    # ═══ Data untuk template Biaya ═══
    # Biaya lebih sederhana: tidak ada items, hanya 1 jumlah
    data = {
        'nomor_transaksi': instance.nomor_transaksi,          # Contoh: EXP/2026/03/0001
        'tanggal': instance.tanggal.strftime('%d/%m/%Y') if instance.tanggal else '-',  # Hanya tanggal (bukan datetime)
        'kategori': str(instance.kategori) if instance.kategori else '-',  # Nama kategori biaya
        'jumlah': format_angka(instance.jumlah),              # Nominal pengeluaran
        'deskripsi': instance.deskripsi or '-',               # Penjelasan biaya
        'status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
        'dibuat_oleh': instance.dibuat_oleh.get_full_name() or instance.dibuat_oleh.username if instance.dibuat_oleh else '-',
        'metode_pembayaran': str(instance.metode_pembayaran) if instance.metode_pembayaran else '-',
    }

    kirim_notifikasi_async('biaya', instance.nomor_transaksi, data)
