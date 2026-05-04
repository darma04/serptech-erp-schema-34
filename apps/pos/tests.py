from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.produk.models import Produk, Kategori, Satuan, KonversiSatuan, Gudang, Stok
from apps.pos.models import MetodePembayaran, POSTransaction, POSTransactionItem
from apps.penjualan.models import Customer
from apps.hr.models import Karyawan, Departemen, Jabatan
from django.contrib.auth.models import User

class MetodePembayaranFinancialTest(TestCase):
    """
    Unit Test khusus untuk memastikan kalkulasi pengeluaran modal (Total Aset / Modal Produk)
    bekerja dengan benar menggunakan `jumlah_konversi` pada POS Transaction Item.
    """

    def setUp(self):
        # 1. Setup User
        self.user = User.objects.create_user(username='kasir1', password='password123')
        
        # 2. Setup Kategori & Satuan
        self.kategori = Kategori.objects.create(nama='Elektronik')
        self.satuan_pcs = Satuan.objects.create(nama='Pcs', singkatan='pcs')
        self.satuan_box = Satuan.objects.create(nama='Box', singkatan='box')

        # 3. Setup Metode Pembayaran
        self.metode_modal = MetodePembayaran.objects.create(nama='Tunai', kode='CASH', saldo=Decimal('10000000'))
        
        # 4. Setup Produk (Satu produk dibeli menggunakan metode_modal)
        # Produk dibeli dengan harga_beli 5.000 per Pcs
        self.produk_multi = Produk.objects.create(
            nama='Lampu LED Box', sku='PRD-002', kategori=self.kategori,
            satuan=self.satuan_pcs,
            harga_beli=Decimal('5000'),
            harga_jual=Decimal('80000'),
            metode_pembayaran=self.metode_modal # Produk modalnya dari Tunai
        )

        # 5. Setup Gudang & Stok Awal
        self.gudang = Gudang.objects.create(nama='Gudang Utama', kode='GDG-01')
        Stok.objects.create(produk=self.produk_multi, gudang=self.gudang, jumlah=50) # 50 pcs (Stok Saat Ini)
        
        # 6. Setup Customer
        self.customer = Customer.objects.create(nama='Walk in Customer')

    def test_total_pengeluaran_menggunakan_jumlah_konversi(self):
        """
        Memastikan total pengeluaran untuk pembelian produk dihitung berdasarkan
        qty_historis = stok_saat_ini + qty_terjual_pos_konversi.
        """
        # Sebelum transaksi POS, stok_saat_ini = 50.
        # Pengeluaran = 50 * 5000 = 250.000
        pengeluaran_awal = self.metode_modal.total_pengeluaran
        self.assertEqual(pengeluaran_awal, Decimal('250000'), 
            f"Pengeluaran awal salah. Harapan: 250000, Realita: {pengeluaran_awal}")

        # Lakukan Transaksi POS: Jual 2 Box (dimana 1 Box = 10 Pcs, jadi 20 Pcs yang terkonversi)
        trx = POSTransaction.objects.create(
            nomor_transaksi='POS-001',
            kasir=self.user,
            customer=self.customer,
            metode_pembayaran=self.metode_modal,
            gudang=self.gudang,
            status='paid',
            subtotal=Decimal('160000'), 
            total_harga=Decimal('160000'),
            jumlah_bayar=Decimal('200000'),
            kembalian=Decimal('40000')
        )

        POSTransactionItem.objects.create(
            transaction=trx,
            produk=self.produk_multi,
            satuan_transaksi=self.satuan_box,
            jumlah=Decimal('2'),                     # Kasir input 2 (Box)
            jumlah_konversi=Decimal('20'),           # Konversi ke 20 (Pcs)
            harga_satuan=Decimal('80000'),
            subtotal=Decimal('160000')
        )

        # Setelah item POS tersimpan, qty_historis = stok_saat_ini(50) + qty_terjual_pos_konversi(20) = 70
        # Pengeluaran = 70 * 5000 = 350.000
        # Wait, if we use POS, stok is deducted manually in `update_stock()`. 
        # But even if stok is not deducted yet, stok_saat_ini = 50, terjual = 20, qty_historis = 70.
        
        pengeluaran_akhir = self.metode_modal.total_pengeluaran
        self.assertEqual(pengeluaran_akhir, Decimal('350000'),
            f"Pengeluaran akhir salah! Harapan: 350000 (menggunakan jumlah_konversi 20), Realita: {pengeluaran_akhir}")
