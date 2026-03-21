# 📂 01 — Struktur Project & File Penting (Detail)

## A. Kenapa Perlu Memahami Struktur Folder?

Sebelum menulis kode, kita HARUS tahu di mana menaruh file. Django punya konvensi (aturan) penamaan dan lokasi file. Jika salah menaruh, Django tidak akan menemukannya.

---

## B. Struktur Folder Utama — Penjelasan Detail

```
starter-kit/                    ← ROOT PROJECT (folder utama)
│
├── manage.py                   ← ★ Entry point Django (jalankan perintah dari sini)
├── .env                        ← ★ Variabel rahasia (SECRET_KEY, DEBUG)
├── requirements.txt            ← ★ Daftar library Python yang dibutuhkan
├── db.sqlite3                  ← Database SQLite (file tunggal, auto-generated)
│
├── config/                     ← ★ KONFIGURASI UTAMA DJANGO
│   ├── __init__.py             ← Menandai ini package Python (wajib ada, biasanya kosong)
│   ├── settings.py             ← ★★★ OTAK konfigurasi (DB, Apps, Middleware, Security)
│   ├── urls.py                 ← ★★ Peta URL master (mendaftarkan semua modul)
│   ├── template.py             ← Konfigurasi tema & layout visual (dark mode, sidebar, dll)
│   ├── context_processors.py   ← Fungsi yang menyuntikkan data ke SEMUA template
│   ├── wsgi.py                 ← Entry point production (Gunicorn membaca file ini)
│   └── asgi.py                 ← Entry point async (untuk WebSocket — belum dipakai)
│
├── apps/                       ← ★ MODUL-MODUL ERP (semua logika bisnis di sini)
│   ├── core/                   ← Inti: RBAC Permission, Mixins, Template Filters
│   ├── dashboard/              ← Halaman dashboard utama
│   ├── produk/                 ← Produk, Kategori, Satuan
│   ├── inventory/              ← Gudang, Stok, Transfer, Adjustment
│   ├── pembelian/              ← Supplier, Purchase Order
│   ├── penjualan/              ← Customer, Sales Order
│   ├── pos/                    ← Point of Sale (Kasir)
│   ├── biaya/                  ← Pengeluaran / Biaya Operasional
│   ├── laporan/                ← Laporan (Produk, Stok, Penjualan, Pembelian)
│   ├── hr/                     ← Karyawan, Departemen, Absensi, Penggajian
│   ├── automation/             ← Notifikasi Telegram
│   ├── user_management/        ← Manajemen User
│   ├── permission_management/  ← Manajemen Role & Permission
│   ├── pengaturan/             ← Pengaturan Perusahaan & Template Cetak
│   ├── ai_assistant/           ← AI Dashboard & AI Chat Assistant
│   ├── activity_log/           ← Log Aktivitas Pengguna
│   ├── fraud_detection/        ← Deteksi Kecurangan & Rekonsiliasi Kas
│   ├── pages/                  ← Halaman error (404, 403, 500)
│   └── sample/                 ← Contoh layout halaman
│
├── auth/                       ← ★ OTENTIKASI (Login, Register, Profile)
│   ├── models.py               ← Model Profile (extend User bawaan Django)
│   ├── views.py                ← View Login, Register, Forgot Password
│   ├── urls.py                 ← URL routing halaman auth
│   └── admin.py                ← Registrasi Profile di Django Admin panel
│
├── templates/                  ← ★ FILE HTML TEMPLATE (tampilan halaman)
│   ├── layout/                 ← Layout utama (kerangka halaman)
│   │   ├── master.html         ← Base template (HTML head, body, scripts global)
│   │   ├── layout_vertical.html ← Layout sidebar vertikal (PALING SERING DIPAKAI)
│   │   ├── layout_horizontal.html ← Layout menu horizontal (jarang dipakai)
│   │   └── partials/           ← Bagian-bagian layout:
│   │       ├── menu/           ←   Sidebar menu (vertical_menu.html, horizontal_menu.html)
│   │       ├── navbar/         ←   Navbar atas (search, user dropdown, notifikasi)
│   │       ├── footer/         ←   Footer bawah
│   │       ├── styles.html     ←   CSS global (semua halaman pakai ini)
│   │       └── scripts.html    ←   JS global (jQuery, Bootstrap, dll)
│   ├── produk/                 ← Template halaman produk
│   │   ├── produk_list.html    ←   Daftar produk
│   │   ├── produk_form.html    ←   Form tambah/edit produk
│   │   ├── kategori_list.html  ←   Daftar kategori
│   │   └── ...
│   ├── inventory/              ← Template halaman inventory
│   ├── pembelian/              ← Template halaman pembelian
│   └── ...                     ← Template modul lainnya
│
├── src/assets/                 ← ★ FILE STATIS (CSS, JS, Gambar vendor)
│   ├── vendor/                 ← Library pihak ke-3:
│   │   ├── libs/               ←   DataTables, Select2, Flatpickr, ApexCharts
│   │   ├── js/                 ←   Bootstrap bundle JS, jQuery
│   │   └── css/                ←   Bootstrap CSS, Sneat theme CSS
│   ├── css/                    ← Custom CSS (styling tambahan kita)
│   ├── js/                     ← Custom JS (JavaScript tambahan kita)
│   └── img/                    ← Gambar, favicon, logo default
│
├── static/                     ← File statis tambahan (favicon, dll)
├── staticfiles/                ← Hasil collectstatic (untuk production)
├── media/                      ← File upload user (gambar produk, avatar)
│   ├── produk/                 ←   Foto produk
│   └── avatars/                ←   Foto profil user
│
└── web_project/                ← Helper & Middleware kustom
    ├── __init__.py             ← TemplateLayout class (inisialisasi layout)
    ├── template_helpers/       ← TemplateHelper (theme_variables, layout config)
    ├── template_tags/          ← Custom template tags (filter)
    └── language_middleware.py   ← Middleware bahasa default (id-ID)
```

---

## C. Apa Fungsi Setiap File dalam App Django?

Setiap modul di `apps/` mengikuti pola yang KONSISTEN. Ini adalah kekuatan Django — **konvensi** yang seragam.

```
apps/produk/                    ← Contoh: Modul Produk
├── __init__.py                 ← File kosong (WAJIB ada — menandai ini Python package)
├── apps.py                     ← Konfigurasi app (nama, label)
├── models.py                   ← ★★★ DEFINISI DATABASE — tabel, kolom, relasi
├── views.py                    ← ★★★ LOGIKA BISNIS — proses request, query DB, render
├── urls.py                     ← ★★ ROUTING URL — URL mana → view mana
├── forms.py                    ← ★ FORM INPUT — definisi field form, widget, validasi
├── admin.py                    ← Registrasi model di Django Admin panel (opsional)
├── migrations/                 ← ★ File migrasi database (AUTO-GENERATED!)
│   ├── __init__.py
│   ├── 0001_initial.py         ← Migrasi pertama (buat tabel awal)
│   ├── 0002_gudang.py          ← Migrasi ke-2 (tambah tabel gudang)
│   └── 0003_produk_berat.py    ← Migrasi ke-3 (tambah field berat)
└── tests.py                    ← Unit test (opsional, untuk automated testing)
```

### Penjelasan Detail Setiap File:

#### 1. `models.py` — JANTUNG Data
**Apa:** Mendefinisikan struktur tabel database menggunakan class Python.
**Kenapa:** Agar kita bisa bekerja dengan database menggunakan Python (bukan SQL mentah).
**Kapan diedit:** Saat ingin menambah tabel baru atau menambah kolom ke tabel yang ada.
**Contoh isi:**
```python
class Produk(models.Model):
    nama = models.CharField(max_length=200)  # → kolom VARCHAR(200) di database
    harga = models.DecimalField(max_digits=15, decimal_places=2)  # → kolom DECIMAL
```
**Setelah edit:** WAJIB jalankan `makemigrations` + `migrate`

#### 2. `views.py` — OTAK Logika
**Apa:** Fungsi/class yang memproses HTTP request dan mengembalikan response.
**Kenapa:** Ini yang menghubungkan URL → data → tampilan.
**Kapan diedit:** Saat ingin menambah/mengubah halaman web.
**Contoh isi:**
```python
class ProdukListView(ListView):
    model = Produk  # "Ambil semua data dari tabel Produk"
    template_name = 'produk/produk_list.html'  # "Tampilkan menggunakan template ini"
```

#### 3. `urls.py` — PETA URL
**Apa:** Mendaftarkan URL pattern dan menghubungkannya ke view.
**Kenapa:** Agar Django tahu URL `/produk/list/` harus menjalankan `ProdukListView`.
**Kapan diedit:** Saat menambah URL baru.
```python
path('list/', ProdukListView.as_view(), name='list')
# Artinya: URL 'list/' → jalankan ProdukListView
# name='list' → bisa dipanggil di template: {% url 'produk:list' %}
```

#### 4. `forms.py` — FORMULIR Input
**Apa:** Mendefinisikan form HTML dengan validasi server-side.
**Kenapa:** Validasi di browser (JavaScript) bisa di-bypass. Validasi server TIDAK bisa.
**Kapan diedit:** Saat mengubah form input (tambah field, ubah widget, validasi).

#### 5. `migrations/` — JANGAN EDIT MANUAL!
**Apa:** File Python yang berisi instruksi perubahan database.
**Kenapa:** Agar perubahan database bisa dilacak dan di-rollback.
**PENTING:** File ini AUTO-GENERATED oleh `makemigrations`. Jangan edit manual!

#### 6. `__init__.py` — Kenapa Ada File Kosong?
**Apa:** File yang menandai folder sebagai Python package.
**Kenapa:** Tanpa file ini, Python tidak bisa melakukan `from apps.produk import models`.
**Isi:** Biasanya kosong (0 bytes). Kadang berisi kode inisialisasi.

---

## D. File Konfigurasi Penting

### `manage.py` — Apa yang Terjadi di Balik Layar?

```python
#!/usr/bin/env python
"""Entry point untuk semua perintah Django."""

import os   # Modul akses variabel lingkungan
import sys  # Modul akses argumen command line

def main():
    # LANGKAH 1: Beritahu Django di mana file settings berada
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # setdefault = set nilai HANYA JIKA belum ada
    # "config.settings" = file config/settings.py

    try:
        # LANGKAH 2: Import fungsi Django untuk jalankan perintah
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # LANGKAH 2b: Jika Django belum terinstall → error jelas
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc

    # LANGKAH 3: Jalankan perintah
    # sys.argv contoh: ['manage.py', 'runserver'] 
    # → Django tahu harus menjalankan runserver
    execute_from_command_line(sys.argv)

# Baris ini memastikan main() hanya dijalankan jika file ini 
# dieksekusi langsung (bukan saat diimport oleh file lain)
if __name__ == "__main__":
    main()
```

**Jadi ketika kita mengetik `python manage.py runserver`:**
1. Python menjalankan file `manage.py`
2. `manage.py` set `DJANGO_SETTINGS_MODULE` ke `config.settings`
3. Django membaca `config/settings.py` → tahu database, apps, middleware
4. Django menjalankan perintah `runserver` → server development aktif

---

## E. Semua Perintah `manage.py` yang Sering Dipakai

```bash
# ═══ DEVELOPMENT ═══
python manage.py runserver                      # Jalankan server development (http://127.0.0.1:8000)
python manage.py runserver 0.0.0.0:8000         # Jalankan & bisa diakses dari LAN
python manage.py shell                          # Python shell interaktif + Django ORM
python manage.py dbshell                        # SQL shell langsung ke database

# ═══ DATABASE & MIGRASI ═══
python manage.py makemigrations                 # Detect perubahan model → buat file migrasi
python manage.py makemigrations produk          # Buat migrasi untuk app 'produk' saja
python manage.py migrate                        # Jalankan migrasi ke database
python manage.py migrate produk 0002            # Rollback ke migrasi 0002
python manage.py showmigrations                 # Lihat status migrasi (✓ = sudah, ✗ = belum)
python manage.py sqlmigrate produk 0001         # Preview SQL dari migrasi (tidak eksekusi)

# ═══ USER MANAGEMENT ═══
python manage.py createsuperuser                # Buat akun superadmin
python manage.py changepassword admin           # Ganti password user 'admin'

# ═══ STATIC FILES ═══
python manage.py collectstatic                  # Kumpulkan semua static files → STATIC_ROOT
                                                # Wajib dijalankan saat deployment production

# ═══ DEBUGGING & CHECK ═══
python manage.py check                          # Cek error konfigurasi (0 issues = aman)
python manage.py check --deploy                 # Cek kesiapan deployment production
python manage.py diffsettings                   # Lihat perbedaan settings vs default Django
```

### Perintah yang PALING SERING dipakai (harian):

| Perintah | Kapan | Frekuensi |
|----------|-------|-----------|
| `runserver` | Setiap mulai coding | Setiap hari |
| `makemigrations` + `migrate` | Setelah ubah models.py | Sering |
| `createsuperuser` | Setup awal / reset DB | Jarang |
| `collectstatic` | Deploy ke production | Saat deploy |
| `check` | Sebelum commit | Sebelum push |

---

## F. File `.env` — Rahasia Konfigurasi

### Apa itu `.env`?

File `.env` menyimpan **variabel rahasia** yang TIDAK BOLEH masuk ke Git. File ini dibaca oleh Django saat startup.

```bash
# ═══ .env — File rahasia (JANGAN commit ke Git!) ═══

SECRET_KEY=django-insecure-abc123xyz456                 
# ↑ Kunci kriptografi Django — dipakai untuk:
#   - Enkripsi session cookie
#   - CSRF token
#   - Password hashing salt
# ⚠️ WAJIB ganti di production! Jika bocor, session bisa di-forge.

DEBUG=True
# ↑ Mode development:
#   - True  → Tampilkan error detail (stack trace) di browser
#   - False → Tampilkan halaman error generik (untuk production)
# ⚠️ JANGAN True di production! Error detail = informasi untuk hacker.

ENVIRONMENT=development
# ↑ Identifikasi lingkungan:
#   - development → Fitur debug aktif, caching nonaktif
#   - staging     → Testing sebelum production
#   - production  → Live, semua security aktif

ALLOWED_HOSTS=127.0.0.1,localhost
# ↑ Domain yang diizinkan mengakses Django:
#   - Development: 127.0.0.1, localhost
#   - Production:  domain.com, www.domain.com, IP server
```

### Kenapa Pakai `.env` dan Bukan Hardcode di `settings.py`?

```
❌ SALAH — Hardcode di settings.py:
SECRET_KEY = 'abc123'  ← Jika push ke GitHub, SEMUA ORANG bisa lihat!

✅ BENAR — Baca dari .env:
SECRET_KEY = os.environ.get('SECRET_KEY')  ← Rahasia tetap di lokal
```

### File `.env.example` — Template untuk Developer Baru:
```bash
# .env.example — COMMIT ini ke Git (berisi template, bukan rahasia)
SECRET_KEY=ganti-dengan-key-anda
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

## G. File `requirements.txt` — Daftar Library

```
# ═══ requirements.txt — Semua library Python yang dibutuhkan ═══

django==4.2.5          # Framework web utama
python-dotenv==1.0.0   # Membaca file .env
Pillow==10.0.0         # Proses gambar (resize, crop, format)
whitenoise==6.5.0      # Serving static files di production
gunicorn==21.2.0       # HTTP server production (pengganti runserver)
openpyxl==3.1.2        # Baca/tulis file Excel (.xlsx)
```

### Cara Pakai:
```bash
# Install SEMUA library yang terdaftar:
pip install -r requirements.txt

# Tambah library baru:
pip install nama-library
pip freeze > requirements.txt   # ← Update daftar

# Buat virtual environment (isolasi library per project):
python -m venv env              # Buat folder env/
env\Scripts\activate            # Aktifkan (Windows)
pip install -r requirements.txt # Install di environment ini
```

---

## H. Anatomi Folder `templates/` — Detail

### Struktur Lengkap:

```
templates/                          ← SEMUA file HTML (19 subfolder)
│
├── layout/                         ← ★ KERANGKA HALAMAN (33 file)
│   ├── master.html                 ← Base template (HTML skeleton)
│   ├── layout_vertical.html        ← Layout sidebar kiri (UTAMA)
│   ├── layout_horizontal.html      ← Layout menu atas (alternatif)
│   ├── layout_without_menu.html    ← Layout tanpa menu (auth pages)
│   ├── layout_blank.html           ← Layout kosong (error pages)
│   └── partials/                   ← Bagian-bagian layout:
│       ├── menu/
│       │   ├── vertical_menu.html  ← Sidebar menu — render dari sidebar_items
│       │   └── horizontal_menu.html
│       ├── navbar/
│       │   └── navbar.html         ← Navbar atas (search, notif, user menu)
│       ├── footer/
│       │   └── footer.html         ← Footer bawah
│       ├── styles.html             ← CSS global (642 baris responsive + dark)
│       └── scripts.html            ← JS global (jQuery, Bootstrap)
│
├── produk/                         ← ★ Template modul Produk (10 file)
│   ├── produk_list.html            ← Daftar produk (tabel + filter)
│   ├── produk_form.html            ← Form tambah/edit produk
│   ├── produk_detail.html          ← Detail produk
│   ├── produk_import.html          ← Import produk dari Excel
│   ├── kategori_list.html          ← Daftar kategori
│   ├── kategori_form.html          ← Form kategori
│   ├── satuan_list.html            ← Daftar satuan
│   ├── satuan_form.html            ← Form satuan
│   ├── produk_confirm_delete.html  ← Konfirmasi hapus
│   └── laporan_produk.html         ← Laporan produk
│
├── inventory/                      ← Template Inventory (9 file)
├── pembelian/                      ← Template Purchase Order (7 file)
├── penjualan/                      ← Template Sales Order (9 file)
├── pos/                            ← Template POS/Kasir (4 file)
├── biaya/                          ← Template Biaya/Expenses (6 file)
├── laporan/                        ← Template Laporan (10 file)
├── hr/                             ← Template HR/Karyawan (18 file)
├── pengaturan/                     ← Template Pengaturan (8 file)
├── permission_management/          ← Template Role & Permission (9 file)
├── user_management/                ← Template User Management (4 file)
├── activity_log/                   ← Template Log Aktivitas (1 file)
├── automation/                     ← Template Automasi Telegram (4 file)
├── ai_assistant/                   ← Template AI Dashboard & AI Chat (3 file)
├── fraud_detection/                ← Template Fraud Detection (6 file)
├── dashboard/                      ← Template Dashboard (1 file)
├── auth/                           ← Template Login/Register (5 file)
├── partials/                       ← Komponen reusable (20 file)
│   ├── _delete_modal.html          ← Modal hapus (dipakai semua modul)
│   ├── _messages.html              ← Flash messages
│   └── ...
└── shared/                         ← Template shared (1 file)
```

### Konvensi Penamaan Template:

| Pattern | Contoh | Fungsi |
|---------|--------|--------|
| `{model}_list.html` | `produk_list.html` | Halaman daftar (tabel) |
| `{model}_form.html` | `produk_form.html` | Form tambah DAN edit |
| `{model}_detail.html` | `produk_detail.html` | Halaman detail/view |
| `{model}_confirm_delete.html` | `produk_confirm_delete.html` | Konfirmasi hapus |
| `{model}_import.html` | `produk_import.html` | Import data dari file |
| `laporan_{nama}.html` | `laporan_produk.html` | Halaman laporan |
| `_partial.html` | `_delete_modal.html` | Komponen reusable (prefix `_`) |

### Hierarki Template Inheritance:

```
master.html                         ← Level 0: HTML skeleton
  └── layout_vertical.html          ← Level 1: + Sidebar + Navbar + Footer
       └── produk_list.html         ← Level 2: + Konten spesifik halaman
```

---

## I. Folder `static/` vs `src/` vs `media/` — Apa Bedanya?

```
┌────────────────────────────────────────────────────────────────────┐
│                     FILE STATIS DI PROJECT                        │
├────────────────┬───────────────────┬───────────────────────────────┤
│ src/assets/    │ static/           │ media/                        │
│ (Development)  │ (Deploy tambahan) │ (User Upload)                 │
├────────────────┼───────────────────┼───────────────────────────────┤
│ CSS vendor     │ favicon.ico       │ Foto produk                   │
│ JS vendor      │ robots.txt        │ Avatar user                   │
│ Library:       │                   │ Logo perusahaan               │
│  - Bootstrap   │                   │                               │
│  - jQuery      │                   │                               │
│  - DataTables  │                   │                               │
│  - Select2     │                   │                               │
│  - ApexCharts  │                   │                               │
│  - Flatpickr   │                   │                               │
│  - Remix Icons │                   │                               │
├────────────────┼───────────────────┼───────────────────────────────┤
│ Di-serve oleh  │ Di-serve oleh     │ Di-serve oleh                 │
│ WhiteNoise     │ WhiteNoise        │ Django (dev) / Nginx (prod)   │
├────────────────┼───────────────────┼───────────────────────────────┤
│ Commit ke Git  │ Commit ke Git     │ JANGAN commit ke Git          │
│ (vendor code)  │ (kecil)           │ (file user, berubah terus)    │
└────────────────┴───────────────────┴───────────────────────────────┘
```

### Konfigurasi di `settings.py`:

```python
# URL untuk akses static files di browser
STATIC_URL = '/static/'

# Folder sumber static files (development)
STATICFILES_DIRS = [
    BASE_DIR / 'src' / 'assets',    # → d:\starter-kit\src\assets\
    BASE_DIR / 'static',            # → d:\starter-kit\static\
]

# Folder tujuan collectstatic (production)
STATIC_ROOT = BASE_DIR / 'staticfiles'
# python manage.py collectstatic → kumpulkan semua ke staticfiles/

# URL untuk akses media files di browser
MEDIA_URL = '/media/'

# Folder penyimpanan upload user
MEDIA_ROOT = BASE_DIR / 'media'
# Upload produk → media/produk/beras.jpg
# Upload avatar → media/avatars/admin.jpg
```

---

## J. Peta Hubungan Antar File — Bagaimana Semua Terhubung?

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                        ALUR REQUEST → RESPONSE                               │
│                                                                               │
│  Browser                                                                      │
│    │                                                                          │
│    │  GET /produk/list/                                                       │
│    ▼                                                                          │
│  manage.py → config/settings.py                                               │
│    │           │                                                              │
│    │           ├── INSTALLED_APPS → apps/produk/apps.py                       │
│    │           ├── MIDDLEWARE → [Security, Session, Auth, ActivityLog]        │
│    │           ├── DATABASES → db.sqlite3                                     │
│    │           ├── TEMPLATES → templates/                                     │
│    │           └── STATICFILES_DIRS → src/assets/, static/                   │
│    │                                                                          │
│    ▼                                                                          │
│  config/urls.py ──→ path("produk/", include("apps.produk.urls"))             │
│    │                                                                          │
│    ▼                                                                          │
│  apps/produk/urls.py ──→ path('list/', ProdukListView, name='list')          │
│    │                                                                          │
│    ▼                                                                          │
│  apps/produk/views.py ──→ ProdukListView(SubModulePermissionMixin, ListView) │
│    │     │                     │                                              │
│    │     │                     ├── model = Produk (dari models.py)            │
│    │     │                     ├── template_name = 'produk/produk_list.html'  │
│    │     │                     └── get_context_data() → TemplateLayout.init() │
│    │     │                                                                    │
│    │     ▼                                                                    │
│    │  apps/produk/models.py ──→ Produk.objects.all() → SQL → db.sqlite3      │
│    │                                                                          │
│    ▼                                                                          │
│  templates/produk/produk_list.html                                            │
│    │     │                                                                    │
│    │     ├── {% extends 'layout/layout_vertical.html' %}                      │
│    │     │         │                                                          │
│    │     │         └── {% extends layout_path %} (master.html)               │
│    │     │                  ├── partials/styles.html (CSS)                    │
│    │     │                  ├── partials/menu/vertical_menu.html (sidebar)    │
│    │     │                  ├── partials/navbar/navbar.html                   │
│    │     │                  └── partials/scripts.html (JS)                   │
│    │     │                                                                    │
│    │     ├── {% load static %} → src/assets/vendor/...                       │
│    │     ├── {% load currency_filters %} → apps/core/templatetags/           │
│    │     └── {{ produk.harga_jual|rupiah }} → Format ke Rupiah               │
│    │                                                                          │
│    ▼                                                                          │
│  HTML Response → Browser                                                      │
│                                                                               │
│  src/assets/vendor/css/core.css  ← Styling (dimuat via {% static %})         │
│  src/assets/vendor/js/bootstrap.js ← Interaksi (dimuat via {% static %})     │
│  media/produk/beras.jpg          ← Gambar produk (dimuat via {{ .url }})     │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Ringkasan Hubungan:

| File | Terhubung Ke | Cara Terhubung |
|------|-------------|----------------|
| `config/urls.py` | `apps/*/urls.py` | `include()` |
| `apps/*/urls.py` | `apps/*/views.py` | `path()` → `View.as_view()` |
| `apps/*/views.py` | `apps/*/models.py` | `model = Produk` |
| `apps/*/views.py` | `apps/*/forms.py` | `form_class = ProdukForm` |
| `apps/*/views.py` | `templates/*/` | `template_name = '...'` |
| `templates/*.html` | `layout/*.html` | `{% extends %}` |
| `templates/*.html` | `src/assets/` | `{% static %}` |
| `templates/*.html` | `templatetags/` | `{% load %}` |
| `apps/*/models.py` | `migrations/` | `makemigrations` (auto) |
| `config/settings.py` | Seluruh project | Titik konfigurasi pusat |

---

*Lanjut ke [02_KONFIGURASI_DJANGO.md](02_KONFIGURASI_DJANGO.md) →*
