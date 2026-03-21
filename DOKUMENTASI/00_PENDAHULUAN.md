# 📘 00 — Pendahuluan: Mengenal Sistem ERP Ini dari NOL

## DAFTAR ISI
- [A. Apa itu ERP?](#a-apa-itu-erp)
- [B. Asal-Usul Project: Materialize / Sneat Starter Kit](#b-asal-usul-project)
- [C. Teknologi yang Digunakan (dan KENAPA)](#c-teknologi-yang-digunakan)
- [D. Persiapan & Instalasi dari Awal](#d-persiapan--instalasi)
- [E. Cara Menjalankan Project](#e-cara-menjalankan-project)
- [F. Arsitektur & Alur Kerja Django](#f-arsitektur--alur-kerja-django)
- [G. Peta Modul ERP](#g-peta-modul-erp)

---

## A. Apa itu ERP?

**ERP (Enterprise Resource Planning)** = sistem informasi terintegrasi yang mengelola SEMUA proses bisnis perusahaan dalam SATU platform.

### Tanpa ERP vs Dengan ERP:
```
TANPA ERP:                                   DENGAN ERP:
┌─────────────┐                              ┌───────────────────────────┐
│ Stok: Excel │  ← tidak sinkron →           │                           │
├─────────────┤                              │    SATU SISTEM TERPADU    │
│ Penjualan:  │  ← data beda →               │                           │
│ Buku tulis  │                              │   Produk ↔ Stok ↔ POS     │
├─────────────┤                              │   PO ↔ SO ↔ Invoice       │
│ Keuangan:   │  ← salah hitung →            │   HR ↔ Biaya ↔ Laporan    │
│ Kalkulator  │                              │                           │
└─────────────┘                              │  Semua TERHUBUNG otomatis │
Hasil: Data tidak akurat,                    └───────────────────────────┘
       duplikasi, lambat                     Hasil: Real-time, akurat, efisien
```

### Modul ERP yang Kita Bangun:
| No | Modul | Fungsi | Contoh Penggunaan |
|----|-------|--------|-------------------|
| 1 | Dashboard | Ringkasan bisnis real-time | Total penjualan hari ini |
| 2 | Produk | Kelola master data produk | Tambah produk "Beras 5kg" |
| 3 | Kategori | Pengelompokan produk | Kategori "Sembako" |
| 4 | Satuan | Unit pengukuran | Kg, Pcs, Karton |
| 5 | Inventory | Kelola gudang & stok | Transfer stok antar gudang |
| 6 | Pembelian | Purchase Order dari supplier | Beli 100 karton dari Indofood |
| 7 | Penjualan | Sales Order ke customer | Jual 50 karton ke Toko Makmur |
| 8 | POS | Point of Sale (kasir) | Bayar di kasir, cetak struk |
| 9 | Invoice | Faktur penjualan | Cetak invoice customer |
| 10 | Biaya | Catatan pengeluaran | Bayar listrik, gaji, dll |
| 11 | HR | Manajemen SDM | Data karyawan, absensi |
| 12 | Laporan | Analisis bisnis | Laporan penjualan bulanan |
| 13 | User Management | Kelola user sistem | Tambah user, atur role |
| 14 | Permission/RBAC | Hak akses berbasis role | Admin bisa semua, Kasir hanya POS |
| 15 | Pengaturan | Konfigurasi perusahaan | Logo, nama, alamat |
| 16 | Automation | Notifikasi otomatis | Kirim alert ke Telegram |

---

## B. Asal-Usul Project: Materialize / Sneat Starter Kit

### Latar Belakang

Project ERP ini dibangun di atas **Sneat Bootstrap 5 Admin Template** dari **Pixinvent** — sebuah template admin dashboard premium yang dibeli dari ThemeForest/website resmi Pixinvent.

```
Pixinvent membuat 2 versi:
┌─────────────────────────────────────────────────┐
│  1. FULL VERSION (berbayar premium)             │
│     - Semua halaman demo sudah jadi             │
│     - Charts, forms, tables, apps lengkap       │
│     - Ratusan file template                     │
│                                                 │
│  2. STARTER KIT (versi dasar) ← KITA PAKAI INI │
│     - Template KOSONG siap diisi                │
│     - Layout system (master, vertical, blank)   │
│     - Sidebar, navbar, footer sudah ada         │
│     - Theme engine (dark/light, RTL, colors)    │
│     - TIDAK ada halaman konten apapun           │
└─────────────────────────────────────────────────┘

Kenapa kita pilih STARTER KIT?
→ Karena kita MEMBANGUN SENDIRI semua fitur dari nol!
→ Full version = contoh demo, BUKAN aplikasi jadi
→ Starter kit = fondasi yang benar untuk custom app
```

### Apa yang Sudah Ada dari Starter Kit (Bawaan Pixinvent):

| Komponen | File | Fungsi |
|----------|------|--------|
| Master Layout | `templates/layout/master.html` | Template induk (DOCTYPE, head, body) |
| Layout Vertical | `templates/layout/layout_vertical.html` | Layout sidebar kiri |
| Layout Horizontal | `templates/layout/layout_horizontal.html` | Layout menu atas |
| Layout Blank | `templates/layout/layout_blank.html` | Layout tanpa menu (login) |
| Sidebar Menu | `templates/layout/partials/menu/` | Komponen sidebar |
| Navbar | `templates/layout/partials/navbar/` | Komponen navigation bar |
| Footer | `templates/layout/partials/footer/` | Komponen footer |
| Styles Partial | `templates/layout/partials/styles.html` | CSS global |
| Scripts Partial | `templates/layout/partials/scripts.html` | JS global |
| Theme Engine | `web_project/template_helpers/theme.py` | Class TemplateHelper |
| Layout Engine | `web_project/__init__.py` | Class TemplateLayout |
| Config | `config/template.py` | TEMPLATE_CONFIG (pengaturan tema) |
| Static Assets | `static/` | CSS, JS, fonts, icons vendor |

### Apa yang KITA Bangun Sendiri (Dari NOL):

| Komponen | File/Folder | Jumlah |
|----------|-------------|--------|
| Apps Django | `apps/` | 15 modul (produk, inventory, dll) |
| Models | `apps/*/models.py` | 30+ model database |
| Views | `apps/*/views.py` | 100+ view class (CBV) |
| Forms | `apps/*/forms.py` | 25+ form class |
| URLs | `apps/*/urls.py` | 15 file routing |
| Templates HTML | `templates/*/` | 80+ template halaman |
| Permission System | `apps/core/` | RBAC lengkap + caching 30 detik |
| Auth System | `auth/` | Login, register, forgot password (Bahasa Indonesia) |
| JavaScript Logic | Di dalam template | Export PDF/Excel, AJAX delete, POS, Select2 AJAX |
| Dashboard Charts | `templates/dashboard/` | Grafik penjualan, stok, dll (Chart.js) |
| Dokumentasi | `DOKUMENTASI/` | 18 file markdown penjelasan lengkap |

### Evolusi Project:

```
TAHAP 1: Starter Kit (Bawaan Pixinvent)
├── Layout system sudah jadi
├── Theme engine (dark/light mode)
├── Static assets (Bootstrap 5, jQuery, icons)
└── KOSONG — tidak ada halaman/fitur apapun

    ↓ (Kita kembangkan dengan bertahap)

TAHAP 2: Fondasi Django
├── Setup config/settings.py
├── Buat apps/ dengan 14 modul
├── Buat models.py (database schema)
├── Buat views.py (CBV untuk CRUD)
└── Konfigurasi URL routing

    ↓

TAHAP 3: Template & UI
├── Buat 80+ template HTML
├── Integrasi Sneat component (card, table, modal)
├── DataTables untuk semua list view
├── Export Excel & PDF
└── AJAX delete + toast notification

    ↓

TAHAP 4: Sistem Lanjutan
├── RBAC (Role-Based Access Control) lengkap
├── POS (Point of Sale) dengan printer
├── Dashboard dengan grafik Chart.js
├── HR Management
├── Automation (Telegram notification)
└── SEO & branding dinamis

    ↓

TAHAP 5: Optimasi & Polish (Terbaru)
├── Permission caching (1 query/role vs 20-40 query/page)
├── PO/SO auto-product-creation (SKU auto-generate, markup 20%)
├── Transfer Stock Select2 AJAX searchable
├── Roles Table filtering & actions column
├── Auth localization (semua pesan Bahasa Indonesia)
├── Back navigation fix (history.back())
├── Export Excel/PDF standarisasi 14+ halaman
├── Dark mode perbaikan kontras & sidebar
├── Komentar lengkap di SEMUA file (Python, HTML, JS, CSS)
└── Dokumentasi 18 file markdown
```

---

## C. Teknologi yang Digunakan (dan KENAPA)

### Backend — Django (Python)

```python
# Django = web framework Python tingkat tinggi
# Versi yang digunakan: Django 5.x

# KENAPA Django?
# 1. "Batteries included" — ORM, auth, admin, forms SUDAH ADA
# 2. Python — bahasa paling mudah dipelajari
# 3. Keamanan — CSRF, XSS, SQL injection protection OTOMATIS
# 4. Django Admin — panel admin gratis
# 5. Community — dokumentasi lengkap, banyak library
```

### Frontend — Sneat Bootstrap 5 (Materialize Design)

```
Sneat Bootstrap 5 Admin Template (oleh Pixinvent)
├── Bootstrap 5     → Framework CSS responsif
├── jQuery           → Library JavaScript (DOM manipulation)
├── Popper.js        → Library untuk dropdown/tooltip positioning
├── Perfect Scrollbar → Scrollbar custom yang elegan
├── Node Waves       → Efek ripple saat klik (efek material design)
├── Hammer.js        → Touch gesture support (mobile)
├── TypeaheadJS      → Autocomplete search di navbar
├── Remix Icon       → 2000+ icon gratis (ri-* class)
├── Inter Font       → Google Font utama (modern, readable)
└── Template Customizer → Toggle dark/light, RTL, sidebar style
```

### Library Tambahan (Kita Pasang Sendiri):

```
DataTables           → Tabel interaktif (search, sort, pagination)
pdfMake              → Generate PDF di browser (client-side)
Chart.js             → Grafik/chart di dashboard
Select2              → Dropdown searchable untuk form
SweetAlert2          → Alert/confirm dialog yang cantik
```

### Database — SQLite (Development) / PostgreSQL (Production)

```
SQLite (default Django):
- File: db.sqlite3 di root project
- Tidak perlu install server database
- Cocok untuk development & testing
- TIDAK cocok untuk production (tidak bisa concurrent write)

PostgreSQL (rekomendasi production):
- Database server terpisah
- Support concurrent users
- Full-text search
- Lebih aman dan scalable
```

### Hubungan Setiap Teknologi:

```
┌──────────── BROWSER (User) ────────────┐
│                                         │
│  HTML + CSS (Bootstrap 5 + Sneat)      │  ← Tampilan
│  JavaScript (jQuery + DataTables + dll) │  ← Interaksi
│  Remix Icon (ri-* class)               │  ← Ikon
│                                         │
└──────────────── HTTP ──────────────────┘
                    │
                    ▼
┌──────────── SERVER (Django) ───────────┐
│                                         │
│  URL Routing → Views → Templates       │  ← Alur utama
│  Models ←→ ORM ←→ Database             │  ← Data
│  Forms → Validasi → Save               │  ← Input
│  Middleware → CSRF, Session, Auth      │  ← Keamanan
│                                         │
└──────────────── ORM ───────────────────┘
                    │
                    ▼
┌──────────── DATABASE (SQLite) ─────────┐
│                                         │
│  Tabel: produk, kategori, stok, dll    │
│  Relasi: ForeignKey, ManyToMany        │
│                                         │
└─────────────────────────────────────────┘
```

---

## D. Persiapan & Instalasi dari Awal

### Langkah 1: Install Python

```bash
# Download Python 3.10+ dari https://www.python.org/downloads/
# PENTING: Centang "Add Python to PATH" saat install!

# Verifikasi instalasi:
python --version
# Output yang diharapkan: Python 3.13.1 (atau versi 3.10+)

pip --version
# Output: pip 24.x from ...
```

### Langkah 2: Clone / Download Project

```bash
# Jika dari Git:
git clone <url_repository> starter-kit
cd starter-kit

# Jika dari file ZIP:
# Extract ke folder yang diinginkan
# Buka terminal di folder tersebut
```

### Langkah 3: Buat Virtual Environment

```bash
# Apa itu Virtual Environment?
# = Folder terisolasi khusus untuk 1 project
# Kenapa? Agar library project A tidak bentrok dengan project B

python -m venv env
# python         = interpreter Python
# -m venv        = module venv (virtual environment maker)
# env            = nama folder venv (bisa apa saja, konvensi: env/venv/.venv)

# Aktifkan venv:
# Windows CMD:
env\Scripts\activate
# Windows PowerShell:
env\Scripts\Activate.ps1
# Linux/Mac:
source env/bin/activate

# Tanda berhasil: ada (env) di awal prompt terminal
# (env) PS D:\starter-kit>
```

### Langkah 4: Install Dependencies

```bash
pip install -r requirements.txt
# Membaca file requirements.txt → install semua library yang tercantum

# Isi requirements.txt biasanya:
# Django==5.1.4
# Pillow==11.0.0       → Untuk handle gambar (ImageField)
# beautifulsoup4       → Parsing HTML (import Excel/CSV lama)
# python-dotenv        → Load .env file
# ... dll
```

### Langkah 5: Migrasi Database

```bash
python manage.py migrate
# Apa yang terjadi:
# 1. Django baca semua file apps/*/migrations/*.py
# 2. Execute SQL: CREATE TABLE untuk setiap model
# 3. Buat tabel built-in Django: auth_user, django_session, dll
# 4. Catat migrasi yang sudah jalan di django_migrations

# Output yang diharapkan:
# Operations to perform:
#   Apply all migrations: admin, auth, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

### Langkah 6: Buat Superuser (Admin Pertama)

```bash
python manage.py createsuperuser
# Ikuti prompt:
# Username: admin
# Email: admin@example.com
# Password: admin123 (atau password pilihan kamu)
# Password (again): admin123

# Superuser = user dengan SEMUA permission, bypass RBAC
```

### Langkah 7: Jalankan Server

```bash
python manage.py runserver
# Output:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.

# Buka browser → http://127.0.0.1:8000/
# → Redirect ke halaman login
# → Masukkan username & password superuser
# → Masuk ke Dashboard
```

---

## E. Cara Menjalankan Project

### Perintah `manage.py` yang PENTING:

```bash
# ═══ MENJALANKAN SERVER ═══
python manage.py runserver
# Start server development di http://127.0.0.1:8000

python manage.py runserver 0.0.0.0:8080
# Start di port 8080, accessible dari network lain

# ═══ DATABASE ═══
python manage.py makemigrations
# Deteksi perubahan di models.py → buat file migrasi baru

python manage.py migrate
# Jalankan migrasi → buat/ubah tabel database

python manage.py showmigrations
# Tampilkan status migrasi (✓ = sudah, ✗ = belum)

python manage.py dbshell
# Buka shell database langsung (SQL)

# ═══ USER ═══
python manage.py createsuperuser
# Buat user superuser baru

python manage.py changepassword admin
# Ganti password user 'admin'

# ═══ DEBUGGING ═══
python manage.py shell
# Buka Python shell dengan Django loaded
# Bisa query database langsung:
#   >>> from apps.produk.models import Produk
#   >>> Produk.objects.count()
#   50

python manage.py check
# Cek apakah ada error konfigurasi
# Output ideal: System check identified no issues (0 silenced).

# ═══ STATIC FILES ═══
python manage.py collectstatic
# Kumpulkan semua static files ke STATIC_ROOT
# Diperlukan HANYA untuk production deployment
```

---

## F. Arsitektur & Alur Kerja Django

### Alur Request-Response (10 Langkah):

```
                                                    ┌────────────────┐
PENGGUNA                                            │  config/       │
types URL ──────► Browser sends ──────────────────► │  urls.py       │
                  HTTP Request                      │  (URL Router)  │
                  GET /produk/list/                  └───────┬────────┘
                                                            │
              ┌─────────────────────────────────────────┐   │
              │ LANGKAH 1-3: URL MATCHING               │   │
              │                                         │   │
              │ 1. Django terima request                │   │
              │ 2. Cari match di config/urls.py         │   │
              │    → path("produk/", include(produk)) → │   │
              │ 3. Lanjut ke apps/produk/urls.py         │   │
              │    → path('list/', ProdukListView)      │   │
              └─────────────────────────────────────────┘   │
                                                            ▼
                                                    ┌────────────────┐
              ┌─────────────────────────────────────│  apps/produk/  │
              │ LANGKAH 4-6: PERMISSION + VIEW      │  views.py      │
              │                                     │  (View/CBV)    │
              │ 4. Mixin cek permission             └───────┬────────┘
              │    → has_permission(user, 'read', 'produk') │
              │ 5. View get_queryset() → query DB           │
              │ 6. View get_context_data() → siapkan data   │
              └─────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                     ┌────────────────┐
              ┌──────────────────────────────────────│  apps/produk/  │
              │ LANGKAH 5 (detail): DATABASE QUERY   │  models.py     │
              │                                      │  (Model/ORM)   │
              │ Produk.objects.all()                 └───────┬────────┘
              │ → Django ORM translate ke SQL:               │
              │   SELECT * FROM produk_produk                │
              │ → Return: QuerySet [<Produk>, <Produk>, ...] │
              └─────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                     ┌────────────────┐
              ┌──────────────────────────────────────│  templates/    │
              │ LANGKAH 7-8: TEMPLATE RENDERING      │  produk/       │
              │                                      │  produk_list   │
              │ 7. Template engine gabungkan         │  .html         │
              │    HTML + data context               └───────┬────────┘
              │ 8. Render {% for p in produk_list %}         │
              │    → Generate HTML lengkap                   │
              └──────────────────────────────────────────────┘
                                                            │
                                                            ▼
              ┌───────────────────────────────────────────────────────┐
              │ LANGKAH 9-10: RESPONSE                                │
              │                                                       │
              │ 9. View return HttpResponse(HTML)                     │
              │ 10. Django kirim response ke browser                  │
              │     → Browser render HTML → user lihat halaman        │
              └───────────────────────────────────────────────────────┘
```

### Pattern MVT (Model-View-Template):

```
Django TIDAK menggunakan MVC tradisional.
Django menggunakan MVT:

┌──────────┐     ┌──────────┐     ┌──────────┐
│  MODEL   │ ←→  │   VIEW   │ ←→  │ TEMPLATE │
│          │     │          │     │          │
│ Data &   │     │ Logika   │     │ Tampilan │
│ Database │     │ Bisnis   │     │ HTML     │
│          │     │ + Routing│     │          │
│ models.py│     │ views.py │     │ *.html   │
└──────────┘     └──────────┘     └──────────┘

Perbandingan:
MVC (Ruby, PHP)     MVT (Django)
Model       ←→      Model
View        ←→      Template
Controller  ←→      View
```

---

## G. Peta Modul ERP

### Struktur Folder Utama:

```
d:\starter-kit\                    ← ROOT PROJECT
├── config/                        ← Konfigurasi Django
│   ├── settings.py               ← Pengaturan utama
│   ├── urls.py                   ← URL router utama
│   ├── template.py               ← Konfigurasi tema Sneat
│   └── wsgi.py / asgi.py        ← Entry point production
│
├── apps/                          ← 14 MODUL ERP (yang kita buat)
│   ├── core/                     ← Permission system (mixin, helper)
│   ├── dashboard/                ← Halaman dashboard
│   ├── produk/                   ← Master data produk
│   ├── inventory/                ← Gudang, stok, transfer
│   ├── pembelian/                ← Supplier, purchase order
│   ├── penjualan/                ← Customer, sales order
│   ├── pos/                      ← Point of Sale (kasir)
│   ├── biaya/                    ← Biaya operasional
│   ├── laporan/                  ← Laporan bisnis
│   ├── hr/                       ← HR management
│   ├── user_management/          ← Kelola user
│   ├── permission_management/    ← Kelola role & permission
│   ├── pengaturan/               ← Pengaturan perusahaan
│   ├── automation/               ← Notifikasi Telegram
│   ├── activity_log/             ← Log aktivitas
│   └── pages/                    ← Halaman statis
│
├── auth/                          ← Autentikasi (login, register)
├── web_project/                   ← Template engine (Sneat)
│   ├── __init__.py               ← TemplateLayout class
│   └── template_helpers/         ← TemplateHelper class
│
├── templates/                     ← 80+ template HTML
│   ├── layout/                   ← Layout system (Sneat bawaan)
│   │   ├── master.html           ← Template PALING INDUK
│   │   ├── layout_vertical.html  ← Layout sidebar (utama)
│   │   ├── layout_blank.html     ← Layout empty (login)
│   │   └── partials/             ← Komponen (sidebar, navbar, footer)
│   ├── produk/                   ← Template modul produk
│   ├── penjualan/                ← Template modul penjualan
│   └── ...                       ← Template modul lainnya
│
├── static/                        ← Asset statis (CSS, JS, gambar)
│   ├── vendor/                   ← Library pihak ke-3 (Sneat bawaan)
│   │   ├── css/                  ← Bootstrap CSS, theme CSS
│   │   ├── js/                   ← Bootstrap JS, helpers JS
│   │   ├── libs/                 ← jQuery, DataTables, Select2, dll
│   │   └── fonts/                ← Remix Icon, Flag Icons
│   ├── css/                      ← Custom CSS (demo.css)
│   ├── js/                       ← Custom JS (config.js, main.js)
│   └── img/                      ← Gambar (logo, favicon, dll)
│
├── media/                         ← File upload user (gambar produk)
├── db.sqlite3                     ← Database SQLite
├── manage.py                      ← CLI Django
├── requirements.txt               ← Daftar library Python
└── DOKUMENTASI/                   ← File-file ini!
```

### Hubungan Antar Modul:

```
                    ┌──────────────────┐
                    │    DASHBOARD     │
                    │  Ringkasan semua │
                    └────────┬─────────┘
                             │ ambil data dari:
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │  PRODUK  │       │  POS     │       │ PENJUALAN│
   │  + Stok  │◄──────│ (Kasir)  │───────│   + SO   │
   │  + Kate- │       └──────────┘       └──────────┘
   │  gori    │              │                  │
   └────┬─────┘              │                  │
        │                    ▼                  ▼
        │            ┌──────────┐       ┌──────────┐
        │            │ INVOICE  │       │ CUSTOMER │
        │            │ (Faktur) │       │ (Pelang- │
        │            └──────────┘       │  gan)    │
        │                               └──────────┘
        ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │INVENTORY │       │PEMBELIAN │       │  BIAYA   │
   │ Gudang + │◄──────│  + PO    │       │ Operasi  │
   │ Transfer │       │+ Supplier│       │  onal    │
   └──────────┘       └──────────┘       └──────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    ┌──────────────┐
                    │   LAPORAN    │
                    │ Analisis     │
                    │ semua data   │
                    └──────────────┘
```

---

**Dokumen Selanjutnya:** Untuk penjelasan detail setiap komponen, baca file dokumentasi berikut secara urut:

1. [01_STRUKTUR_PROJECT.md](01_STRUKTUR_PROJECT.md) — Struktur folder & file
2. [02_KONFIGURASI_DJANGO.md](02_KONFIGURASI_DJANGO.md) — Settings, middleware, URL
3. [03_MODEL_DATABASE.md](03_MODEL_DATABASE.md) — Model, field, relasi, ORM
4. [04_VIEWS_DAN_URL.md](04_VIEWS_DAN_URL.md) — CBV/FBV, mixin, routing
5. [05_TEMPLATE_DAN_LAYOUT.md](05_TEMPLATE_DAN_LAYOUT.md) — Template, layout Sneat
6. [06_FORM_DAN_VALIDASI.md](06_FORM_DAN_VALIDASI.md) — Form, validasi
7. [07_SISTEM_PERMISSION_RBAC.md](07_SISTEM_PERMISSION_RBAC.md) — RBAC, permission, caching
8. [08_FITUR_MODUL_ERP.md](08_FITUR_MODUL_ERP.md) — Detail setiap modul
9. [09_TIPS_DAN_BEST_PRACTICE.md](09_TIPS_DAN_BEST_PRACTICE.md) — Tips & debugging
10. [10_KOMPONEN_UI_SNEAT.md](10_KOMPONEN_UI_SNEAT.md) — Komponen UI lengkap
11. [11_PANDUAN_MEMBUAT_MODUL_BARU.md](11_PANDUAN_MEMBUAT_MODUL_BARU.md) — Tutorial step-by-step
12. [12_JAVASCRIPT_DAN_AJAX.md](12_JAVASCRIPT_DAN_AJAX.md) — JS, AJAX, DOM manipulation
13. [13_KEAMANAN_SISTEM.md](13_KEAMANAN_SISTEM.md) — Keamanan & proteksi
14. [14_DEPLOYMENT_DAN_HOSTING.md](14_DEPLOYMENT_DAN_HOSTING.md) — Deploy ke production
15. [15_API_DAN_INTEGRASI.md](15_API_DAN_INTEGRASI.md) — REST API & integrasi
16. [16_PERBAIKAN_DAN_PENINGKATAN.md](16_PERBAIKAN_DAN_PENINGKATAN.md) — Perbaikan UI/UX terbaru
17. [17_KOMENTAR_KODE.md](17_KOMENTAR_KODE.md) — Standar komentar kode
18. [18_KEAMANAN_LANJUTAN.md](18_KEAMANAN_LANJUTAN.md) — Keamanan lanjutan & best practice
