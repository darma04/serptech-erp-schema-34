"""
==========================================================================
 HR ADMIN - Registrasi model HR di Django Admin
==========================================================================
 Berbeda dari modul lain (yang admin.py kosong), modul HR MENDAFTARKAN
 model-modelnya di Django Admin sebagai alternatif pengelolaan data:
 - DepartemenAdmin: list/filter/search by kode, nama
 - JabatanAdmin: + filter departemen, level
 - KaryawanAdmin: + filter departemen, jabatan, status
 - FotoWajahAdmin: list karyawan + status aktif
 - AbsensiAdmin: + date_hierarchy (navigasi per tanggal)
 - PenggajianAdmin: + filter status, periode
==========================================================================
"""

from django.contrib import admin                        # Framework admin bawaan Django
from apps.hr.models import Departemen, Jabatan, Karyawan, FotoWajah, Absensi, Penggajian  # Semua model HR


@admin.register(Departemen)
class DepartemenAdmin(admin.ModelAdmin):
    """
    Admin untuk model Departemen (divisi/bagian perusahaan).
    Menampilkan kode, nama, kepala departemen, status aktif, dan tanggal dibuat.
    """
    # Kolom yang ditampilkan di tabel list
    list_display = ['kode', 'nama', 'kepala_departemen', 'aktif', 'dibuat_pada']
    # Filter sidebar berdasarkan status aktif
    list_filter = ['aktif']
    # Search box bisa mencari berdasarkan kode atau nama departemen
    search_fields = ['kode', 'nama']


@admin.register(Jabatan)
class JabatanAdmin(admin.ModelAdmin):
    """
    Admin untuk model Jabatan (posisi/role karyawan).
    Filter berdasarkan departemen, level jabatan, dan status aktif.
    """
    # Kolom: kode, nama, departemen (FK), level, gaji pokok, aktif
    list_display = ['kode', 'nama', 'departemen', 'level', 'gaji_pokok', 'aktif']
    # Filter sidebar — bisa filter by departemen, level, atau aktif
    list_filter = ['departemen', 'level', 'aktif']
    search_fields = ['kode', 'nama']


@admin.register(Karyawan)
class KaryawanAdmin(admin.ModelAdmin):
    """
    Admin untuk model Karyawan (data personil).
    Filter lengkap: departemen, jabatan, status kerja, dan status aktif.
    """
    # Kolom: NIK, nama, jabatan (FK), departemen (FK), status kerja, aktif
    list_display = ['nik', 'nama', 'jabatan', 'departemen', 'status', 'aktif']
    # Filter sidebar komprehensif
    list_filter = ['departemen', 'jabatan', 'status', 'aktif']
    # Search bisa via NIK, nama, atau email karyawan
    search_fields = ['nik', 'nama', 'email']


@admin.register(FotoWajah)
class FotoWajahAdmin(admin.ModelAdmin):
    """
    Admin untuk model FotoWajah (foto untuk face recognition).
    Menampilkan karyawan pemilik foto, status aktif, dan tanggal upload.
    """
    list_display = ['karyawan', 'aktif', 'dibuat_pada']
    list_filter = ['aktif']


@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    """
    Admin untuk model Absensi (catatan kehadiran karyawan).

    Fitur khusus:
    - date_hierarchy: Navigasi kalender di atas tabel
      Klik tahun → bulan → tanggal untuk drill-down data absensi
    - search_fields menggunakan double underscore (__) untuk
      mengakses field di model terkait (FK to Karyawan)
    """
    # Kolom: karyawan, tanggal, jam masuk/keluar, status (hadir/sakit/dll)
    list_display = ['karyawan', 'tanggal', 'jam_masuk', 'jam_keluar', 'status']
    list_filter = ['status', 'tanggal']
    # Search via FK: karyawan__nama dan karyawan__nik
    search_fields = ['karyawan__nama', 'karyawan__nik']
    # date_hierarchy: Navigasi drill-down berbasis tanggal (tahun → bulan → hari)
    date_hierarchy = 'tanggal'


@admin.register(Penggajian)
class PenggajianAdmin(admin.ModelAdmin):
    """
    Admin untuk model Penggajian (slip gaji karyawan).
    Filter berdasarkan status gaji, tahun, dan bulan periode.
    """
    # Kolom: karyawan, periode (bulan/tahun), gaji bersih, status
    list_display = ['karyawan', 'periode_bulan', 'periode_tahun', 'gaji_bersih', 'status']
    # Filter berdasarkan status pembayaran dan periode
    list_filter = ['status', 'periode_tahun', 'periode_bulan']
    # Search via FK ke karyawan
    search_fields = ['karyawan__nama', 'karyawan__nik']
