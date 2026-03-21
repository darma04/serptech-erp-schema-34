"""
==========================================================================
 PRODUK ADMIN - Registrasi Model Produk ke Django Admin
==========================================================================
 File ini mendaftarkan model Produk ke halaman admin Django (/admin/).

 Django Admin:
 - Panel admin bawaan Django untuk mengelola data database
 - Otomatis menyediakan CRUD (Create, Read, Update, Delete)
 - Dikustomisasi via ModelAdmin class

 Kustomisasi:
 - list_display: Kolom yang ditampilkan di tabel list
 - list_filter: Filter di sidebar kanan
 - search_fields: Field yang bisa dicari via search box

 Koneksi:
 - apps/produk/models.py → Model yang didaftarkan
 - django.contrib.admin → Framework admin bawaan Django
==========================================================================
"""

from django.contrib import admin              # Framework admin Django
from .models import Kategori, Satuan, Produk, Gudang, Stok  # Model dari file yang sama


# Decorator @admin.register(Kategori):
# - Mendaftarkan model Kategori ke panel admin Django
# - Menghubungkan model dengan class KategoriAdmin di bawahnya
# - Alternatif dari: admin.site.register(Kategori, KategoriAdmin)
@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    """Konfigurasi admin untuk model Kategori produk."""
    # list_display: Kolom-kolom yang ditampilkan di halaman daftar
    # Contoh tampilan: | nama          | dibuat_pada      |
    #                  | Elektronik    | 2024-01-15 10:30 |
    list_display = ['nama', 'dibuat_pada']
    # search_fields: Field yang bisa dicari via search box di atas tabel
    search_fields = ['nama']


@admin.register(Satuan)
class SatuanAdmin(admin.ModelAdmin):
    """Konfigurasi admin untuk model Satuan (unit pengukuran)."""
    # Menampilkan nama lengkap dan singkatan di tabel
    # Contoh: | nama      | singkatan |
    #         | Kilogram  | kg        |
    list_display = ['nama', 'singkatan']
    search_fields = ['nama']


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    """Konfigurasi admin untuk model Produk (master produk)."""
    # Kolom yang ditampilkan di tabel list
    # Contoh: | sku       | nama         | kategori   | harga_jual | aktif |
    #         | ELK-00001 | Laptop Asus  | Elektronik | 8,500,000  | ✓     |
    list_display = ['sku', 'nama', 'kategori', 'harga_jual', 'aktif']

    # list_filter: Filter sidebar di sebelah kanan halaman
    # User bisa filter berdasarkan kategori dan status aktif
    list_filter = ['kategori', 'aktif']

    # search_fields: User bisa mencari berdasarkan SKU atau nama produk
    search_fields = ['sku', 'nama']


@admin.register(Gudang)
class GudangAdmin(admin.ModelAdmin):
    """Konfigurasi admin untuk model Gudang (warehouse)."""
    # Kolom: kode gudang, nama gudang, status aktif
    list_display = ['kode', 'nama', 'aktif']
    search_fields = ['kode', 'nama']


@admin.register(Stok)
class StokAdmin(admin.ModelAdmin):
    """
    Konfigurasi admin untuk model Stok (jumlah barang per gudang).

    Catatan penting:
    - search_fields menggunakan 'produk__nama' (double underscore)
    - Ini memungkinkan pencarian via FK (ForeignKey) relation
    - Contoh: User ketik 'Laptop' di search box → tampilkan stok Laptop di semua gudang
    """
    # Kolom: nama produk (via FK), gudang, dan jumlah stok
    list_display = ['produk', 'gudang', 'jumlah']

    # Filter berdasarkan gudang — user bisa lihat stok per gudang
    list_filter = ['gudang']

    # Search via relasi FK: produk__nama = nama produk (bukan ID)
    # Double underscore (__) untuk mengakses field di model terkait
    search_fields = ['produk__nama']
