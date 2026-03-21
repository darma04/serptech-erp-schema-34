"""
==========================================================================
 LAPORAN VIEWS - Views Halaman Laporan / Report (Read-Only)
==========================================================================
 File ini berisi views untuk menampilkan laporan bisnis.
 Semua views bersifat READ-ONLY (hanya menampilkan, tidak mengubah data).

 Daftar View:
 ┌─────────────────────────────┬───────────────────────────────────────┐
 │ View                        │ Penjelasan                            │
 ├─────────────────────────────┼───────────────────────────────────────┤
 │ LaporanProdukView           │ Laporan produk + nilai aset           │
 │ LaporanProdukDetailView     │ Detail produk + riwayat stok          │
 │ LaporanStokView             │ Ringkasan stok per gudang             │
 │ LaporanStokDetailView       │ Detail stok + riwayat transfer/adj    │
 │ LaporanPenjualanView        │ Laporan penjualan (SO + POS)          │
 │ LaporanPenjualanDetailView  │ Detail Sales Order                    │
 │ LaporanPembelianView        │ Laporan pembelian (PO)                │
 │ LaporanPembelianDetailView  │ Detail Purchase Order                 │
 │ LaporanKeuanganView         │ Ringkasan keuangan (laba/rugi)        │
 └─────────────────────────────┴───────────────────────────────────────┘

 Fitur umum semua view:
 - ReadPermissionMixin → Cek permission SubCRUD laporan_produk/stok/dll
 - Filter tanggal (start_date, end_date) via GET parameter
 - Kalkulasi keuntungan (harga_jual - harga_beli) per transaksi
 - Activity Log integration untuk riwayat perubahan

 Terhubung dengan:
 - apps/produk/models.py → Produk, Kategori, Stok, Gudang
 - apps/penjualan/models.py → SalesOrder, SalesOrderItem, Customer
 - apps/pembelian/models.py → PurchaseOrder, PurchaseOrderItem, Supplier
 - apps/biaya/models.py → TransaksiBiaya, KategoriBiaya
 - apps/pos/models.py → POSTransaction, POSTransactionItem
 - apps/activity_log/models.py → UserActivity (riwayat perubahan)
==========================================================================
"""
from django.shortcuts import render, get_object_or_404
# Import dari framework Django
from django.contrib.auth.decorators import login_required
# Import dari framework Django
from django.views.generic import TemplateView, ListView, DetailView
# Import dari framework Django
from django.utils.decorators import method_decorator
# Import dari framework Django
from django.db.models import Count, Sum, Q
from web_project import TemplateLayout
# Import dari modul internal proyek
from apps.produk.models import Produk, Kategori, Stok, Gudang
# Import dari modul internal proyek
from apps.penjualan.models import SalesOrder, SalesOrderItem, Customer
# Import dari modul internal proyek
from apps.pembelian.models import PurchaseOrder, PurchaseOrderItem, Supplier
# Import dari modul internal proyek
from apps.biaya.models import TransaksiBiaya, KategoriBiaya
# Import dari modul internal proyek
from apps.activity_log.models import UserActivity
# Import dari modul internal proyek
from apps.core.mixins import ReadPermissionMixin


class LaporanProdukView(ReadPermissionMixin, ListView):
    paginate_by = 50
    """
    Laporan Produk — daftar produk + kalkulasi nilai aset.
    URL: /laporan/produk/
    Filter: start_date, end_date (mempengaruhi qty terjual)
    Cards: total aset, harga beli ready, harga jual ready, estimasi keuntungan
    """
    model = Produk
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/produk.html'
    context_object_name = 'produk_list'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_produk'  # SubCRUD permission
    
    # Override queryset — filter atau optimasi query data
    def get_queryset(self):
        # Prefetch stok dengan gudang untuk efisiensi query
        """Override queryset — filter atau optimasi query data."""
        return Produk.objects.prefetch_related(
            'stok_set', 
            'stok_set__gudang'
        ).select_related('kategori', 'satuan', 'cabang')
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Query database — ambil semua data context['kategori_list']
        # Data konteks: kategori_list — untuk ditampilkan di template
        context['kategori_list'] = Kategori.objects.all()
        
        # Tambah daftar gudang untuk referensi dan filter
        context['gudang_list'] = Gudang.objects.filter(aktif=True)
        
        from decimal import Decimal
        from datetime import datetime
        # Import dari framework Django
        from django.db.models import Sum, Q
        # Import dari modul internal proyek
        from apps.penjualan.models import SalesOrderItem
        # Import dari modul internal proyek
        from apps.pos.models import POSTransactionItem
        
        # Parse filter params for date filtering
        start_date_str = self.request.GET.get('start_date', '')
        end_date_str = self.request.GET.get('end_date', '')
        # Data konteks: filter_start_date — untuk ditampilkan di template
        context['filter_start_date'] = start_date_str
        # Data konteks: filter_end_date — untuk ditampilkan di template
        context['filter_end_date'] = end_date_str
        
        filter_start = None
        filter_end = None
        if start_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        if end_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        
        # ===== Hitung qty terjual per produk =====
        # Dari Sales Order items (status bukan cancelled)
        so_sold_filter = Q(sales_order__status__in=['confirmed', 'delivered', 'completed'])
        if filter_start:
            so_sold_filter &= Q(sales_order__tanggal__date__gte=filter_start)
        if filter_end:
            so_sold_filter &= Q(sales_order__tanggal__date__lte=filter_end)
        
        so_sold_by_produk = {}
        # Query database — ambil data for item in SalesOrderItem.objects.filter(so_sold_filter).values('produk_id').annotate(total_qty yang sesuai filter
        for item in SalesOrderItem.objects.filter(so_sold_filter).values('produk_id').annotate(total_qty=Sum('jumlah')):
            so_sold_by_produk[item['produk_id']] = item['total_qty']
        
        # Dari POS Transaction items (status paid)
        pos_sold_filter = Q(transaction__status='paid')
        if filter_start:
            pos_sold_filter &= Q(transaction__tanggal__date__gte=filter_start)
        if filter_end:
            pos_sold_filter &= Q(transaction__tanggal__date__lte=filter_end)
        
        pos_sold_by_produk = {}
        # Query database — ambil data for item in POSTransactionItem.objects.filter(pos_sold_filter).values('produk_id').annotate(total_qty yang sesuai filter
        for item in POSTransactionItem.objects.filter(pos_sold_filter).values('produk_id').annotate(total_qty=Sum('jumlah')):
            pos_sold_by_produk[item['produk_id']] = item['total_qty']
        
        # ===== Hitung semua cards =====
        total_keseluruhan_aset = Decimal('0')
        total_harga_beli_ready = Decimal('0')
        total_harga_jual_ready = Decimal('0')
        total_stok = Decimal('0')
        total_nilai_beli = Decimal('0')
        total_nilai_jual = Decimal('0')
        produk_count = 0
        
        for produk in Produk.objects.prefetch_related('stok_set').all():
            stok_saat_ini = sum(s.jumlah for s in produk.stok_set.all())
            
            # Qty yang sudah terjual (SO + POS)
            qty_sold_so = so_sold_by_produk.get(produk.pk, Decimal('0'))
            qty_sold_pos = pos_sold_by_produk.get(produk.pk, Decimal('0'))
            qty_total_pernah_masuk = stok_saat_ini + qty_sold_so + qty_sold_pos
            
            # Card 1: Total Keseluruhan Aset = harga_beli × total stok pernah masuk
            total_keseluruhan_aset += produk.harga_beli * qty_total_pernah_masuk
            
            # Untuk ringkasan tfoot
            total_stok += stok_saat_ini
            total_nilai_beli += produk.harga_beli * stok_saat_ini
            total_nilai_jual += produk.harga_jual * stok_saat_ini
            produk_count += 1
            
            # Cards 2,3,4: Hanya produk ready (stok > 0)
            if stok_saat_ini > 0:
                total_harga_beli_ready += produk.harga_beli * stok_saat_ini
                total_harga_jual_ready += produk.harga_jual * stok_saat_ini
        
        estimasi_keuntungan = total_harga_jual_ready - total_harga_beli_ready
        
        # Data konteks: total_keseluruhan_aset — untuk ditampilkan di template
        context['total_keseluruhan_aset'] = total_keseluruhan_aset
        # Data konteks: total_harga_beli_ready — untuk ditampilkan di template
        context['total_harga_beli_ready'] = total_harga_beli_ready
        # Data konteks: total_harga_jual_ready — untuk ditampilkan di template
        context['total_harga_jual_ready'] = total_harga_jual_ready
        # Data konteks: estimasi_keuntungan — untuk ditampilkan di template
        context['estimasi_keuntungan'] = estimasi_keuntungan
        
        # Untuk ringkasan tfoot / backward compat
        context['total_produk'] = produk_count
        # Data konteks: total_nilai_beli — untuk ditampilkan di template
        context['total_nilai_beli'] = total_nilai_beli
        # Data konteks: total_nilai_jual — untuk ditampilkan di template
        context['total_nilai_jual'] = total_nilai_jual
        # Data konteks: total_stok — untuk ditampilkan di template
        context['total_stok'] = int(total_stok)
        
        return context


class LaporanStokView(ReadPermissionMixin, ListView):
    """
    Laporan Stok — ringkasan stok per produk per gudang.
    URL: /laporan/stok/
    Cards: total produk, total gudang, stok habis, stok rendah
    """
    model = Stok
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/stok.html'
    context_object_name = 'stok_list'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_stok'  # SubCRUD permission
    
    def get_queryset(self):
        """Override queryset — filter atau optimasi query data."""
        return Stok.objects.select_related('produk', 'gudang').all()
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Query database — ambil semua data context['gudang_list']
        # Data konteks: gudang_list — untuk ditampilkan di template
        context['gudang_list'] = Gudang.objects.all()
        # Summary stats
        context['total_produk'] = Produk.objects.count()
        # Hitung jumlah data yang cocok
        # Data konteks: total_gudang — untuk ditampilkan di template
        context['total_gudang'] = Gudang.objects.count()
        # Query database — ambil data context['stok_habis'] yang sesuai filter
        # Data konteks: stok_habis — untuk ditampilkan di template
        context['stok_habis'] = Stok.objects.filter(jumlah=0).count()
        # Query database — ambil data context['stok_rendah'] yang sesuai filter
        # Data konteks: stok_rendah — untuk ditampilkan di template
        context['stok_rendah'] = Stok.objects.filter(jumlah__gt=0, jumlah__lte=10).count()
        
        # Aggregated total for summary row
        total_stok_aggregate = Stok.objects.aggregate(total_stok=Sum('jumlah'))
        # Data konteks: total_stok — untuk ditampilkan di template
        context['total_stok'] = int(total_stok_aggregate['total_stok'] or 0)
        
        return context


class LaporanPenjualanView(ReadPermissionMixin, ListView):
    """
    Laporan Penjualan — gabungan Sales Order + POS Transaction.
    URL: /laporan/penjualan/
    Filter: start_date, end_date
    Cards: total penjualan, total keuntungan, rata-rata order
    Menghitung harga_beli dan keuntungan per order.
    """
    model = SalesOrder
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/penjualan.html'
    context_object_name = 'sales_order_list'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_penjualan'  # SubCRUD permission
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Query database — ambil semua data context['customer_list']
        # Data konteks: customer_list — untuk ditampilkan di template
        context['customer_list'] = Customer.objects.all()
        
        # Import POS model
        from apps.pos.models import POSTransaction, POSTransactionItem
        from decimal import Decimal
        from datetime import datetime
        
        # Parse filter params
        start_date_str = self.request.GET.get('start_date', '')
        end_date_str = self.request.GET.get('end_date', '')
        # Data konteks: filter_start_date — untuk ditampilkan di template
        context['filter_start_date'] = start_date_str
        # Data konteks: filter_end_date — untuk ditampilkan di template
        context['filter_end_date'] = end_date_str
        
        filter_start = None
        filter_end = None
        if start_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        if end_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        
        # ===== Build filter kwargs =====
        so_filter = {'status__in': ['draft', 'confirmed', 'delivered', 'completed']}
        pos_filter = {'status__in': ['draft', 'unpaid', 'paid']}
        if filter_start:
            so_filter['tanggal__date__gte'] = filter_start
            pos_filter['tanggal__date__gte'] = filter_start
        if filter_end:
            so_filter['tanggal__date__lte'] = filter_end
            pos_filter['tanggal__date__lte'] = filter_end
        
        # ===== Sales Order: hitung harga_beli dan keuntungan per SO =====
        so_qs = SalesOrder.objects.filter(**so_filter).prefetch_related('items__produk')
        so_list_annotated = []
        so_total = Decimal('0')
        so_harga_beli_total = Decimal('0')
        so_keuntungan_total = Decimal('0')
        
        for so in so_qs:
            harga_beli_so = Decimal('0')
            for item in so.items.all():
                harga_beli_so += item.produk.harga_beli * item.jumlah
            keuntungan_so = so.total_harga - harga_beli_so
            so.harga_beli_calc = harga_beli_so
            so.keuntungan_calc = keuntungan_so
            so_list_annotated.append(so)
            so_total += so.total_harga
            so_harga_beli_total += harga_beli_so
            so_keuntungan_total += keuntungan_so
        
        so_count = len(so_list_annotated)
        
        # ===== POS Transaction: hitung harga_beli dan keuntungan per POS =====
        # CATATAN (Fix Maret 2026 — K8): Sebelumnya query ini dibatasi [:50] transaksi,
        # yang menyebabkan laporan penjualan POS tidak lengkap. Limit dihapus.
        pos_qs = POSTransaction.objects.filter(**pos_filter).prefetch_related('items__produk').order_by('-tanggal')
        pos_list_annotated = []
        pos_total = Decimal('0')
        pos_harga_beli_total = Decimal('0')
        pos_keuntungan_total = Decimal('0')
        
        for pos in pos_qs:
            harga_beli_pos = Decimal('0')
            for item in pos.items.all():
                harga_beli_pos += item.produk.harga_beli * item.jumlah
            keuntungan_pos = pos.total_harga - harga_beli_pos
            pos.harga_beli_calc = harga_beli_pos
            pos.keuntungan_calc = keuntungan_pos
            pos_list_annotated.append(pos)
            pos_total += pos.total_harga
            pos_harga_beli_total += harga_beli_pos
            pos_keuntungan_total += keuntungan_pos
        
        pos_count = len(pos_list_annotated)
        
        # ===== Combined stats =====
        total_penjualan = so_total + pos_total
        total_harga_beli = so_harga_beli_total + pos_harga_beli_total
        total_keuntungan = so_keuntungan_total + pos_keuntungan_total
        total_order = so_count + pos_count
        
        # Summary cards
        context['total_penjualan'] = total_penjualan
        # Data konteks: total_keuntungan — untuk ditampilkan di template
        context['total_keuntungan'] = total_keuntungan
        # Data konteks: total_harga_beli — untuk ditampilkan di template
        context['total_harga_beli'] = total_harga_beli
        # Data konteks: rata_rata_order — untuk ditampilkan di template
        context['rata_rata_order'] = int(total_penjualan / total_order) if total_order > 0 else 0
        
        # SO breakdown
        context['so_total'] = so_total
        # Data konteks: so_count — untuk ditampilkan di template
        context['so_count'] = so_count
        # Data konteks: so_harga_beli_total — untuk ditampilkan di template
        context['so_harga_beli_total'] = so_harga_beli_total
        # Data konteks: so_keuntungan_total — untuk ditampilkan di template
        context['so_keuntungan_total'] = so_keuntungan_total
        
        # POS breakdown
        context['pos_total'] = pos_total
        # Data konteks: pos_count — untuk ditampilkan di template
        context['pos_count'] = pos_count
        # Data konteks: pos_harga_beli_total — untuk ditampilkan di template
        context['pos_harga_beli_total'] = pos_harga_beli_total
        # Data konteks: pos_keuntungan_total — untuk ditampilkan di template
        context['pos_keuntungan_total'] = pos_keuntungan_total
        
        # Override queryset & POS list with annotated versions
        context['sales_order_list'] = so_list_annotated
        # Data konteks: pos_transaction_list — untuk ditampilkan di template
        context['pos_transaction_list'] = pos_list_annotated
        
        return context


class LaporanPembelianView(ReadPermissionMixin, ListView):
    """
    Laporan Pembelian — daftar Purchase Order + statistik.
    URL: /laporan/pembelian/
    Filter: start_date, end_date
    Cards: total pembelian, total PO, total pajak, total stok masuk
    """
    model = PurchaseOrder
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/pembelian.html'
    context_object_name = 'purchase_order_list'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_pembelian'  # SubCRUD permission
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Query database — ambil semua data context['supplier_list']
        # Data konteks: supplier_list — untuk ditampilkan di template
        context['supplier_list'] = Supplier.objects.all()
        
        from datetime import datetime
        from decimal import Decimal
        
        # Parse filter params
        start_date_str = self.request.GET.get('start_date', '')
        end_date_str = self.request.GET.get('end_date', '')
        # Data konteks: filter_start_date — untuk ditampilkan di template
        context['filter_start_date'] = start_date_str
        # Data konteks: filter_end_date — untuk ditampilkan di template
        context['filter_end_date'] = end_date_str
        
        filter_start = None
        filter_end = None
        if start_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        if end_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        
        # Bangun filter kwargs
        po_filter = {}
        if filter_start:
            po_filter['tanggal__date__gte'] = filter_start
        if filter_end:
            po_filter['tanggal__date__lte'] = filter_end
        
        # Query database — ambil data po_qs yang sesuai filter
        po_qs = PurchaseOrder.objects.filter(**po_filter).prefetch_related('items__produk').order_by('-tanggal')
        
        # Annotate each PO with product names, total stok, pajak
        po_list_annotated = []
        total_pembelian = Decimal('0')
        total_pajak = Decimal('0')
        total_stok = Decimal('0')
        
        for po in po_qs:
            produk_names = []
            stok_total = Decimal('0')
            for item in po.items.all():
                produk_names.append(item.produk.nama)
                stok_total += item.jumlah
            po.produk_list = ', '.join(produk_names) if produk_names else '-'
            po.stok_total = stok_total
            po.pajak_display = po.pajak
            po_list_annotated.append(po)
            total_pembelian += po.total_harga
            total_pajak += po.pajak
            total_stok += stok_total
        
        total_po = len(po_list_annotated)
        
        # Summary stats with filter
        context['total_pembelian'] = total_pembelian
        # Data konteks: total_po — untuk ditampilkan di template
        context['total_po'] = total_po
        # Data konteks: total_pajak — untuk ditampilkan di template
        context['total_pajak'] = total_pajak
        # Data konteks: total_stok — untuk ditampilkan di template
        context['total_stok'] = total_stok
        # Hitung jumlah data yang cocok
        # Data konteks: total_supplier — untuk ditampilkan di template
        context['total_supplier'] = Supplier.objects.count()
        # Data konteks: rata_rata_po — untuk ditampilkan di template
        context['rata_rata_po'] = int(total_pembelian / total_po) if total_po > 0 else 0
        
        # Override queryset with annotated version
        context['purchase_order_list'] = po_list_annotated
        
        return context


class LaporanKeuanganView(ReadPermissionMixin, TemplateView):
    """
    Laporan Keuangan — ringkasan laba/rugi + pengeluaran.
    URL: /laporan/keuangan/
    Filter: start_date, end_date
    Hitung: pendapatan (SO+POS), pengeluaran (PO+Biaya), laba bersih
    """
    template_name = 'laporan/keuangan.html'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_keuangan'  # SubCRUD permission
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Import dari modul internal proyek
        from apps.pos.models import POSTransaction, MetodePembayaran
        from datetime import datetime
        
        # Parse filter params
        start_date_str = self.request.GET.get('start_date', '')
        end_date_str = self.request.GET.get('end_date', '')
        cabang_id = self.request.GET.get('cabang', '')
        metode_id = self.request.GET.get('metode_pembayaran', '')
        
        filter_start = None
        filter_end = None
        if start_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        if end_date_str:
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                filter_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Tangkap error ValueError — lanjutkan tanpa crash
            except ValueError:
                pass
        
        # Data konteks: filter_start_date — untuk ditampilkan di template
        context['filter_start_date'] = start_date_str
        # Data konteks: filter_end_date — untuk ditampilkan di template
        context['filter_end_date'] = end_date_str
        # Data konteks: filter_cabang — untuk ditampilkan di template
        context['filter_cabang'] = cabang_id
        # Data konteks: filter_metode — untuk ditampilkan di template
        context['filter_metode'] = metode_id
        
        # Kirim data filter ke template
        context['gudang_list'] = Gudang.objects.filter(aktif=True)
        # Query database — ambil data context['metode_pembayaran_list'] yang sesuai filter
        # Data konteks: metode_pembayaran_list — untuk ditampilkan di template
        context['metode_pembayaran_list'] = MetodePembayaran.objects.filter(aktif=True)
        
        # Bangun filter kwargs berdasarkan tanggal + cabang + metode
        so_filter = {'status__in': ['confirmed', 'delivered', 'completed']}
        pos_filter = {'status': 'paid'}
        # Filter status PO menggunakan 'approved' dan 'received' (bukan 'confirmed')
        # CATATAN (Fix Maret 2026 — K7): Sebelumnya menggunakan ['confirmed', 'received', 'completed']
        # yang salah karena PO tidak memiliki status 'confirmed' maupun 'completed'.
        # Status alur PO yang benar: draft → approved → received
        po_filter = {'status__in': ['approved', 'received']}
        biaya_filter = {'status': 'approved'}  # Hanya biaya yang disetujui = pengeluaran nyata
        
        if filter_start:
            so_filter['tanggal__date__gte'] = filter_start
            pos_filter['tanggal__date__gte'] = filter_start
            po_filter['tanggal__date__gte'] = filter_start
            biaya_filter['tanggal__gte'] = filter_start
        if filter_end:
            so_filter['tanggal__date__lte'] = filter_end
            pos_filter['tanggal__date__lte'] = filter_end
            po_filter['tanggal__date__lte'] = filter_end
            biaya_filter['tanggal__lte'] = filter_end
        
        # Filter cabang (gudang)
        if cabang_id:
            so_filter['gudang_id'] = cabang_id
            pos_filter['gudang_id'] = cabang_id
            po_filter['gudang_id'] = cabang_id
            biaya_filter['cabang_id'] = cabang_id
        
        # Filter metode pembayaran
        if metode_id:
            so_filter['metode_pembayaran_id'] = metode_id
            pos_filter['metode_pembayaran_id'] = metode_id
            po_filter['metode_pembayaran_id'] = metode_id
            biaya_filter['metode_pembayaran_id'] = metode_id
        
        # Pemasukan dari penjualan (Sales Order + POS)
        total_sales_order = SalesOrder.objects.filter(
            **so_filter
        ).aggregate(Sum('total_harga'))['total_harga__sum'] or 0
        
        # Query database — ambil data total_pos yang sesuai filter
        total_pos = POSTransaction.objects.filter(
            **pos_filter
        ).aggregate(Sum('total_harga'))['total_harga__sum'] or 0
        
        total_pemasukan = total_sales_order + total_pos
        
        # Pengeluaran dari pembelian + biaya
        total_pembelian = PurchaseOrder.objects.filter(
            **po_filter
        ).aggregate(Sum('total_harga'))['total_harga__sum'] or 0
        # Query database — ambil data total_biaya yang sesuai filter
        total_biaya = TransaksiBiaya.objects.filter(
            **biaya_filter
        ).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        total_pengeluaran = total_pembelian + total_biaya
        
        # Laba/rugi
        laba_rugi = total_pemasukan - total_pengeluaran
        
        # ===== Total Aset — Formula Inventori Historis (SINKRON dengan Dashboard) =====
        # Total Aset = harga_beli × semua qty yang pernah masuk (stok + terjual + adj_out)
        # Tidak dipengaruhi filter tanggal — bersifat kumulatif historis
        # Menjadi patokan untuk deteksi kecurangan/selisih
        from apps.produk.models import Produk, Stok
        from apps.penjualan.models import SalesOrderItem
        from apps.pos.models import POSTransactionItem
        from apps.inventory.models import AdjustmentStok
        from decimal import Decimal
        
        total_aset = Decimal('0')
        total_harga_beli_ready = Decimal('0')
        total_harga_jual_ready = Decimal('0')
        
        try:
            # Qty terjual per produk dari SO (kumulatif historis)
            so_sold_by_produk = {}
            for item in SalesOrderItem.objects.filter(
                sales_order__status__in=['confirmed', 'delivered', 'completed']
            ).values('produk_id').annotate(total_qty=Sum('jumlah')):
                so_sold_by_produk[item['produk_id']] = item['total_qty']
            
            # Qty terjual per produk dari POS (kumulatif historis)
            pos_sold_by_produk = {}
            for item in POSTransactionItem.objects.filter(
                transaction__status='paid'
            ).values('produk_id').annotate(total_qty=Sum('jumlah')):
                pos_sold_by_produk[item['produk_id']] = item['total_qty']
            
            # Qty adjustment out per produk (kumulatif historis)
            adj_out_by_produk = {}
            for item in AdjustmentStok.objects.filter(
                tipe='out'
            ).values('produk_id').annotate(total_qty=Sum('jumlah')):
                adj_out_by_produk[item['produk_id']] = item['total_qty']
            
            # Hitung per produk
            for produk in Produk.objects.prefetch_related('stok_set').all():
                stok_saat_ini = sum(s.jumlah for s in produk.stok_set.all())
                qty_sold_so = so_sold_by_produk.get(produk.pk, Decimal('0'))
                qty_sold_pos = pos_sold_by_produk.get(produk.pk, Decimal('0'))
                qty_adj_out = adj_out_by_produk.get(produk.pk, Decimal('0'))
                qty_total_pernah_masuk = stok_saat_ini + qty_sold_so + qty_sold_pos + qty_adj_out
                
                total_aset += produk.harga_beli * qty_total_pernah_masuk
                
                if stok_saat_ini > 0:
                    total_harga_beli_ready += produk.harga_beli * stok_saat_ini
                    total_harga_jual_ready += produk.harga_jual * stok_saat_ini
        except Exception:
            pass
        
        estimasi_keuntungan = total_harga_jual_ready - total_harga_beli_ready
        
        # ===== Keuntungan Kotor dari penjualan (margin per item terjual) =====
        # Sinkron dengan Dashboard profit_data.gross_profit
        keuntungan_kotor = Decimal('0')
        try:
            from django.db.models import F, DecimalField, ExpressionWrapper
            
            # Keuntungan dari SO
            ke_so_filter = {'sales_order__status__in': ['confirmed', 'delivered', 'completed']}
            if filter_start:
                ke_so_filter['sales_order__tanggal__date__gte'] = filter_start
            if filter_end:
                ke_so_filter['sales_order__tanggal__date__lte'] = filter_end
            if cabang_id:
                ke_so_filter['sales_order__gudang_id'] = cabang_id
            
            keuntungan_so = SalesOrderItem.objects.filter(
                **ke_so_filter
            ).annotate(
                margin=ExpressionWrapper(
                    (F('harga_satuan') - F('produk__harga_beli')) * F('jumlah'),
                    output_field=DecimalField()
                )
            ).aggregate(total=Sum('margin'))['total'] or Decimal('0')
            
            # Keuntungan dari POS
            ke_pos_filter = {'transaction__status': 'paid'}
            if filter_start:
                ke_pos_filter['transaction__tanggal__date__gte'] = filter_start
            if filter_end:
                ke_pos_filter['transaction__tanggal__date__lte'] = filter_end
            if cabang_id:
                ke_pos_filter['transaction__gudang_id'] = cabang_id
            
            keuntungan_pos = POSTransactionItem.objects.filter(
                **ke_pos_filter
            ).annotate(
                margin=ExpressionWrapper(
                    (F('harga_satuan') - F('produk__harga_beli')) * F('jumlah'),
                    output_field=DecimalField()
                )
            ).aggregate(total=Sum('margin'))['total'] or Decimal('0')
            
            keuntungan_kotor = keuntungan_so + keuntungan_pos
        except Exception:
            pass
        
        # Data konteks: total_pemasukan — untuk ditampilkan di template
        context['total_pemasukan'] = total_pemasukan
        # Data konteks: total_sales_order — untuk ditampilkan di template
        context['total_sales_order'] = total_sales_order
        # Data konteks: total_pos — untuk ditampilkan di template
        context['total_pos'] = total_pos
        # Data konteks: total_pengeluaran — untuk ditampilkan di template
        context['total_pengeluaran'] = total_pengeluaran
        # Data konteks: total_pembelian — untuk ditampilkan di template
        context['total_pembelian'] = total_pembelian
        # Data konteks: total_biaya — untuk ditampilkan di template
        context['total_biaya'] = total_biaya
        # Data konteks: laba_rugi — untuk ditampilkan di template
        context['laba_rugi'] = laba_rugi
        # Data konteks: total_aset — Nilai inventori historis (sinkron Dashboard)
        context['total_aset'] = total_aset
        # Data konteks tambahan — sinkron dengan Dashboard
        context['total_harga_beli_ready'] = total_harga_beli_ready
        context['total_harga_jual_ready'] = total_harga_jual_ready
        context['estimasi_keuntungan'] = estimasi_keuntungan
        context['keuntungan_kotor'] = keuntungan_kotor
        
        # List data — with all filters applied + select_related for new columns
        # DIPERBAIKI: Tambahkan filter status agar list konsisten dengan summary cards
        so_list_filter = {'status__in': ['confirmed', 'delivered', 'completed']}
        pos_list_filter = {'status': 'paid'}
        po_list_filter = {'status__in': ['approved', 'received']}
        biaya_list_filter = {'status': 'approved'}  # Hanya tampilkan biaya yang disetujui
        if filter_start:
            so_list_filter['tanggal__date__gte'] = filter_start
            pos_list_filter['tanggal__date__gte'] = filter_start
            po_list_filter['tanggal__date__gte'] = filter_start
            biaya_list_filter['tanggal__gte'] = filter_start
        if filter_end:
            so_list_filter['tanggal__date__lte'] = filter_end
            pos_list_filter['tanggal__date__lte'] = filter_end
            po_list_filter['tanggal__date__lte'] = filter_end
            biaya_list_filter['tanggal__lte'] = filter_end
        if cabang_id:
            so_list_filter['gudang_id'] = cabang_id
            pos_list_filter['gudang_id'] = cabang_id
            po_list_filter['gudang_id'] = cabang_id
            biaya_list_filter['cabang_id'] = cabang_id
        if metode_id:
            so_list_filter['metode_pembayaran_id'] = metode_id
            pos_list_filter['metode_pembayaran_id'] = metode_id
            po_list_filter['metode_pembayaran_id'] = metode_id
            biaya_list_filter['metode_pembayaran_id'] = metode_id
        
        # Query database — ambil data context['sales_order_list'] yang sesuai filter
        # Data konteks: sales_order_list — untuk ditampilkan di template
        context['sales_order_list'] = SalesOrder.objects.filter(
            **so_list_filter
        ).select_related('gudang', 'metode_pembayaran', 'customer').order_by('-tanggal')[:100]
        
        # Query database — ambil data context['pos_transaction_list'] yang sesuai filter
        # Data konteks: pos_transaction_list — untuk ditampilkan di template
        context['pos_transaction_list'] = POSTransaction.objects.filter(
            **pos_list_filter
        ).select_related('gudang', 'metode_pembayaran').order_by('-tanggal')[:100]
        
        # Query database — ambil data context['purchase_order_list'] yang sesuai filter
        # Data konteks: purchase_order_list — untuk ditampilkan di template
        context['purchase_order_list'] = PurchaseOrder.objects.filter(
            **po_list_filter
        ).select_related('gudang', 'metode_pembayaran', 'supplier').order_by('-tanggal')[:100]
        
        # Query database — ambil data context['transaksi_biaya_list'] yang sesuai filter
        # Data konteks: transaksi_biaya_list — untuk ditampilkan di template
        context['transaksi_biaya_list'] = TransaksiBiaya.objects.filter(
            **biaya_list_filter
        ).select_related('cabang', 'metode_pembayaran', 'kategori').order_by('-tanggal')[:100]
        
        return context



class LaporanProdukDetailView(ReadPermissionMixin, DetailView):
    """
    Detail Produk — info lengkap + riwayat stok + activity log.
    URL: /laporan/produk/<pk>/
    Context: margin, activity_logs, stok_list, po_items, so_items
    """
    model = Produk
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/produk_detail.html'
    context_object_name = 'produk'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        produk = self.object
        
        # Hitung margin
        context['margin'] = produk.harga_jual - produk.harga_beli
        
        # Riwayat Activity Log yang KOMPREHENSIF untuk produk ini
        # Mencakup: perubahan langsung pada produk DAN semua perubahan stok terkait
        context['activity_logs'] = UserActivity.objects.filter(
            Q(model_name__icontains='produk', object_id=str(produk.pk)) |  # Perubahan langsung pada produk
            Q(  # Stock-specific actions untuk produk ini di semua gudang  
                action__in=['stock_in', 'stock_out', 'stock_adjustment', 'stock_transfer_in', 'stock_transfer_out'],
                object_repr__icontains=produk.nama
            ) |
            Q(  # Perubahan pada stok produk ini
                model_name__icontains='stok',
                object_repr__icontains=produk.nama
            )
        ).select_related('user').order_by('-timestamp')[:100]
        
        # Related data - Stok di gudang
        context['stok_list'] = Stok.objects.filter(produk=produk).select_related('gudang')
        
        # Related data - Item di Purchase Orders
        context['po_items'] = PurchaseOrderItem.objects.filter(
            produk=produk
        ).select_related('purchase_order', 'purchase_order__supplier').order_by('-purchase_order__tanggal')[:10]
        
        # Related data - Item di Sales Orders
        context['so_items'] = SalesOrderItem.objects.filter(
            produk=produk
        ).select_related('sales_order', 'sales_order__customer').order_by('-sales_order__tanggal')[:10]
        
        return context



class LaporanPenjualanDetailView(ReadPermissionMixin, DetailView):
    """
    Detail Sales Order — info SO + activity log.
    URL: /laporan/penjualan/<pk>/
    Context: activity_logs (riwayat perubahan SO)
    """
    model = SalesOrder
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/penjualan_detail.html'
    context_object_name = 'sales_order'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        sales_order = self.object
        
        # Riwayat Activity Log untuk SO ini
        so = self.object
        
        # Activity Log untuk SO ini
        context['activity_logs'] = UserActivity.objects.filter(
            Q(model_name__icontains='sales order') | Q(model_name__icontains='penjualan'),
            object_id=str(so.pk)
        ).select_related('user').order_by('-timestamp')[:50]
        
        return context



class LaporanPembelianDetailView(ReadPermissionMixin, DetailView):
    """
    Detail Purchase Order — info PO + activity log.
    URL: /laporan/pembelian/<pk>/
    Context: activity_logs (riwayat perubahan PO)
    """
    model = PurchaseOrder
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/pembelian_detail.html'
    context_object_name = 'purchase_order'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        po = self.object
        
        # Activity Log untuk PO ini
        context['activity_logs'] = UserActivity.objects.filter(
            Q(model_name__icontains='purchase order') | Q(model_name__icontains='pembelian'),
            object_id=str(po.pk)
        ).select_related('user').order_by('-timestamp')[:50]
        
        return context



class LaporanStokDetailView(ReadPermissionMixin, DetailView):
    """
    Detail Stok — info stok produk + riwayat perubahan komprehensif.
    URL: /laporan/stok/<pk>/
    Context: activity_logs, po_items, so_items, adjustment_list, transfer_list
    """
    model = Stok
    # Template HTML yang digunakan untuk render halaman
    template_name = 'laporan/stok_detail.html'
    context_object_name = 'stok'
    # Modul permission yang dicek: 'laporan'
    permission_module = 'laporan'
    
    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        stok = self.object
        
        # Query untuk activity logs yang lebih komprehensif
        # Mencakup: stock-specific actions DAN update pada model stok ini
        activity_logs = UserActivity.objects.filter(
            Q(model_name__icontains='stok', object_id=str(stok.pk)) |  # Perubahan langsung pada stok
            Q(  # Stock-specific actions untuk produk+gudang ini
                action__in=['stock_in', 'stock_out', 'stock_adjustment', 'stock_transfer_in', 'stock_transfer_out'],
                gudang_id=str(stok.gudang.pk),
                object_repr__icontains=stok.produk.nama
            )
        ).select_related('user').order_by('-timestamp')[:100]
        
        # Data konteks: activity_logs — untuk ditampilkan di template
        context['activity_logs'] = activity_logs
        
        # Related - PO items yang mempengaruhi stok produk ini (di gudang ini)
        context['po_items'] = PurchaseOrderItem.objects.filter(
            produk=stok.produk,
            purchase_order__gudang=stok.gudang
        ).select_related('purchase_order', 'purchase_order__supplier').order_by('-purchase_order__tanggal')[:20]
        
        # Related - SO items yang mempengaruhi stok produk ini (di gudang ini)
        context['so_items'] = SalesOrderItem.objects.filter(
            produk=stok.produk,
            sales_order__gudang=stok.gudang
        ).select_related('sales_order', 'sales_order__customer').order_by('-sales_order__tanggal')[:20]
        
        # Related - Adjustment pada produk+gudang ini
        from apps.inventory.models import AdjustmentStok, TransferStok
        # Query database — ambil data context['adjustment_list'] yang sesuai filter
        # Data konteks: adjustment_list — untuk ditampilkan di template
        context['adjustment_list'] = AdjustmentStok.objects.filter(
            produk=stok.produk,
            gudang=stok.gudang
        ).order_by('-dibuat_pada')[:20]
        
        # Related - Transfer yang melibatkan gudang ini
        context['transfer_list'] = TransferStok.objects.filter(
            Q(gudang_asal=stok.gudang) | Q(gudang_tujuan=stok.gudang),
            items__produk=stok.produk
        ).distinct().order_by('-dibuat_pada')[:20]
        
        return context
