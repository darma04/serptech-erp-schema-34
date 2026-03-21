"""
==========================================================================
 PENGATURAN ADMIN - Registrasi model Pengaturan di Django Admin
==========================================================================
 PengaturanPerusahaanAdmin: fieldset (Informasi Perusahaan + Pengaturan)
 TemplateCetakAdmin: fieldset (Info, Header, Footer, Tanda Tangan)
   + filter jenis/aktif + search nama/header
==========================================================================
"""

from django.contrib import admin              # Framework admin bawaan Django
from .models import PengaturanPerusahaan, TemplateCetak  # Model dari file yang sama


@admin.register(PengaturanPerusahaan)
class PengaturanPerusahaanAdmin(admin.ModelAdmin):
    """
    Admin untuk model PengaturanPerusahaan (profil perusahaan).

    Hanya ada 1 record (singleton pattern) di database yang menyimpan
    informasi global perusahaan: nama, logo, alamat, telepon, dll.
    """
    # Kolom yang ditampilkan di tabel list
    list_display = ['nama_perusahaan', 'email', 'telepon', 'diupdate_pada']

    # Fieldsets: Mengelompokkan field dalam form edit
    fieldsets = (
        # Bagian 1: Data identitas perusahaan
        ('Informasi Perusahaan', {
            'fields': ('nama_perusahaan', 'logo', 'alamat', 'telepon', 'email', 'website')
        }),
        # Bagian 2: Pengaturan global (pajak default PPN)
        ('Pengaturan', {
            'fields': ('pajak_default',)
            # Koma setelah 'pajak_default' WAJIB karena ini tuple 1 elemen
        }),
    )


@admin.register(TemplateCetak)
class TemplateCetakAdmin(admin.ModelAdmin):
    """
    Admin untuk model TemplateCetak (template cetak nota/invoice).

    Template digunakan untuk mencetak dokumen seperti:
    - Invoice penjualan
    - Purchase order
    - Nota POS

    Fieldsets membagi form menjadi 4 bagian:
    Info Template, Header, Footer, dan Tanda Tangan.
    """
    # Kolom di tabel list
    list_display = ['nama', 'jenis', 'aktif', 'diupdate_pada']

    # Filter berdasarkan jenis template dan status aktif
    list_filter = ['jenis', 'aktif']

    # Search by nama template atau nama perusahaan di header
    search_fields = ['nama', 'header_nama_perusahaan']

    # Fieldsets: Form edit terstruktur menjadi 4 bagian
    fieldsets = (
        # Bagian 1: Identitas template
        ('Informasi Template', {
            'fields': ('nama', 'jenis', 'aktif')
        }),
        # Bagian 2: Konfigurasi header dokumen (paling atas)
        ('Header', {
            'fields': ('header_nama_perusahaan', 'header_alamat', 'header_telepon',
                       'header_email', 'header_website', 'tampilkan_logo', 'tampilkan_website')
        }),
        # Bagian 3: Konfigurasi footer dokumen (paling bawah)
        ('Footer', {
            'fields': ('footer_ucapan', 'footer_keterangan')
        }),
        # Bagian 4: Label tanda tangan kiri dan kanan
        ('Tanda Tangan', {
            'fields': ('signature_kiri_label', 'signature_kanan_label')
        }),
    )
