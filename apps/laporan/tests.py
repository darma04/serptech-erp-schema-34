"""
Tests for laporan app — SERPTECH variant (no service/sparepart).
Verifies:
1. All core URL patterns resolve
2. Service/sparepart URLs DO NOT exist
3. All view classes can be imported
4. URLs.syntax is valid
"""
from django.test import SimpleTestCase
from django.urls import reverse, NoReverseMatch, resolve
from django.core.exceptions import ViewDoesNotExist


class LaporanURLTests(SimpleTestCase):
    """Verify URL patterns work correctly."""

    def test_produk_url_resolves(self):
        url = reverse('laporan:produk')
        self.assertEqual(url, '/laporan/produk/')

    def test_stok_url_resolves(self):
        url = reverse('laporan:stok')
        self.assertEqual(url, '/laporan/stok/')

    def test_penjualan_url_resolves(self):
        url = reverse('laporan:penjualan')
        self.assertEqual(url, '/laporan/penjualan/')

    def test_pembelian_url_resolves(self):
        url = reverse('laporan:pembelian')
        self.assertEqual(url, '/laporan/pembelian/')

    def test_keuangan_url_resolves(self):
        url = reverse('laporan:keuangan')
        self.assertEqual(url, '/laporan/keuangan/')

    def test_cabang_url_resolves(self):
        url = reverse('laporan:cabang')
        self.assertEqual(url, '/laporan/cabang/')

    def test_produk_detail_url_resolves(self):
        url = reverse('laporan:produk-detail', args=[1])

    def test_stok_detail_url_resolves(self):
        url = reverse('laporan:stok-detail', args=[1])

    def test_penjualan_detail_url_resolves(self):
        url = reverse('laporan:penjualan-detail', args=[1])

    def test_pembelian_detail_url_resolves(self):
        url = reverse('laporan:pembelian-detail', args=[1])

    # ── Service/sparepart should NOT exist ──

    def test_service_url_does_not_exist(self):
        with self.assertRaises(NoReverseMatch):
            reverse('laporan:service')

    def test_sparepart_url_does_not_exist(self):
        with self.assertRaises(NoReverseMatch):
            reverse('laporan:sparepart')

    def test_service_detail_url_does_not_exist(self):
        with self.assertRaises(NoReverseMatch):
            reverse('laporan:service-detail', args=[1])

    def test_sparepart_detail_url_does_not_exist(self):
        with self.assertRaises(NoReverseMatch):
            reverse('laporan:sparepart-detail', args=[1])


class LaporanViewImportTests(SimpleTestCase):
    """Verify view classes can be imported."""

    def test_core_views_importable(self):
        from apps.laporan import views as v
        # Core views
        self.assertTrue(hasattr(v, 'LaporanProdukView'))
        self.assertTrue(hasattr(v, 'LaporanStokView'))
        self.assertTrue(hasattr(v, 'LaporanPenjualanView'))
        self.assertTrue(hasattr(v, 'LaporanPembelianView'))
        self.assertTrue(hasattr(v, 'LaporanKeuanganView'))
        self.assertTrue(hasattr(v, 'LaporanCabangView'))
        # Detail views
        self.assertTrue(hasattr(v, 'LaporanProdukDetailView'))
        self.assertTrue(hasattr(v, 'LaporanStokDetailView'))
        self.assertTrue(hasattr(v, 'LaporanPenjualanDetailView'))
        self.assertTrue(hasattr(v, 'LaporanPembelianDetailView'))

    def test_service_views_not_importable(self):
        """SERPTECH: service/sparepart views must NOT exist."""
        from apps.laporan import views as v
        self.assertFalse(hasattr(v, 'LaporanServiceView'),
                         'LaporanServiceView should not exist in SERPTECH')
        self.assertFalse(hasattr(v, 'LaporanSparepartView'),
                         'LaporanSparepartView should not exist in SERPTECH')
        self.assertFalse(hasattr(v, 'LaporanServiceDetailView'),
                         'LaporanServiceDetailView should not exist in SERPTECH')
        self.assertFalse(hasattr(v, 'LaporanSparepartDetailView'),
                         'LaporanSparepartDetailView should not exist in SERPTECH')
