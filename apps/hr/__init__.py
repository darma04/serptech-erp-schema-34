"""
==========================================================================
 HR APP - Modul Human Resources / SDM (Sumber Daya Manusia)
==========================================================================
 Package ini menangani manajemen karyawan, departemen, jabatan,
 absensi (termasuk face recognition), dan penggajian.

 Berisi:
 - models.py     → Departemen, Jabatan, Karyawan, FotoWajah,
                    PengaturanAbsensi, Absensi, Penggajian
 - views.py      → CRUD untuk semua entitas HR + dashboard HR
 - forms.py      → Form Django untuk input data HR
 - face_utils.py → Utilitas face recognition untuk absensi wajah
 - urls.py       → Routing URL modul HR

 Hierarki: Departemen → Jabatan → Karyawan → Absensi → Penggajian

 Terhubung dengan:
 - django.contrib.auth.models.User → Karyawan bisa terhubung ke akun user
 - apps/dashboard/ → Statistik karyawan di halaman dashboard
==========================================================================
"""
