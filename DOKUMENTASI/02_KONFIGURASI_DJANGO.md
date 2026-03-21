# ⚙️ 02 — Konfigurasi Django — Penjelasan Detail

## A. Settings (`config/settings.py`) — Otak Konfigurasi Django

File `settings.py` adalah file **PALING PENTING** di Django. Setiap kali Django dijalankan, file ini yang PERTAMA dibaca. Semua konfigurasi ada di sini.

---

### 1. BASE_DIR — Di Mana Project Berada?

```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
```

**Apa artinya baris per baris:**
- `from pathlib import Path` → Import class `Path` dari modul `pathlib` bawaan Python. `Path` mempermudah manipulasi path file/folder.
- `Path(__file__)` → `__file__` = path file ini sendiri (config/settings.py). Hasilnya: `D:\starter-kit\config\settings.py`
- `.resolve()` → Ubah ke absolute path (bukan relative). Hasilnya: `D:\starter-kit\config\settings.py`
- `.parent` → Naik 1 level ke folder induk. Hasilnya: `D:\starter-kit\config\`
- `.parent` → Naik 1 level lagi. Hasilnya: `D:\starter-kit\`

**Jadi `BASE_DIR` = `D:\starter-kit\`** — folder root project.

**Kenapa perlu?** Agar kita bisa mereferensikan file lain secara relative:
```python
DATABASES = {"default": {"NAME": BASE_DIR / "db.sqlite3"}}
#                                  ↑ = D:\starter-kit\db.sqlite3
```

---

### 2. INSTALLED_APPS — Modul Apa Saja yang Aktif?

```python
INSTALLED_APPS = [
    # ══════════════════════════════════════════════
    # MODUL BAWAAN DJANGO — jangan dihapus!
    # ══════════════════════════════════════════════
    "django.contrib.admin",        
    # Django Admin Panel — halaman admin di /admin/
    # Menyediakan antarmuka web untuk mengelola data di database
    # Tanpa ini: tidak bisa akses /admin/
    
    "django.contrib.auth",         
    # Sistem Otentikasi Django — model User, Group, Permission
    # Menyediakan: login, logout, password hashing, session
    # Tanpa ini: tidak bisa login sama sekali
    
    "django.contrib.contenttypes", 
    # Content Type Framework — metadata tentang semua model
    # Dibutuhkan oleh auth (untuk generic permissions)
    # Tanpa ini: auth tidak bisa bekerja
    
    "django.contrib.sessions",     
    # Session Framework — menyimpan data per-user di server
    # Contoh: setelah login, session menyimpan "user ini sudah login"
    # Data session disimpan di database (tabel django_session)
    # Tanpa ini: user harus login ulang setiap kali buka halaman
    
    "django.contrib.messages",     
    # Message Framework — pesan flash yang muncul 1x
    # Contoh: "Produk berhasil ditambahkan!" (muncul sekali lalu hilang)
    # Tanpa ini: tidak bisa menampilkan notifikasi sukses/error
    
    "django.contrib.staticfiles",  
    # Static Files Framework — serving CSS, JS, gambar
    # Menghandle {% static 'css/style.css' %} di template
    # Tanpa ini: CSS/JS tidak bisa diload di browser
    
    # ══════════════════════════════════════════════
    # MODUL CUSTOM PROJECT
    # ══════════════════════════════════════════════
    "auth.apps.AuthConfig",        
    # App otentikasi custom kita — model Profile, view Login/Register
    # Kenapa nama "auth.apps.AuthConfig"?
    # → auth/ adalah folder, apps.py berisi class AuthConfig
    # → Django perlu tahu nama lengkap class konfigurasi app
    
    "apps.core.apps.CoreConfig",   
    # Core: RBAC Permission, Mixins, Template Filters
    # Ini "jantung" sistem keamanan — mengontrol siapa bisa akses apa
    
    # ══════════════════════════════════════════════
    # MODUL-MODUL ERP
    # ══════════════════════════════════════════════
    "apps.dashboard",              # Dashboard — halaman utama setelah login
    "apps.produk",                 # Produk, Kategori, Satuan
    "apps.inventory",              # Gudang, Stok, Transfer, Adjustment
    "apps.pembelian",              # Supplier, Purchase Order (PO)
    "apps.penjualan",              # Customer, Sales Order (SO)
    "apps.pos",                    # POS / Kasir — antarmuka penjualan
    "apps.biaya",                  # Biaya / Pengeluaran operasional
    "apps.laporan",                # Laporan: Produk, Stok, Penjualan, Pembelian
    "apps.hr",                     # HR: Karyawan, Departemen, Absensi, Gaji
    "apps.automation",             # Automasi Telegram — notifikasi otomatis
    "apps.activity_log",           # Log Aktivitas — riwayat semua aksi user
    "apps.pengaturan",             # Pengaturan: Perusahaan, Template Cetak
    "apps.permission_management",  # Manajemen Role & Permission (UI)
    "apps.user_management",        # Manajemen User (tambah/edit/hapus akun)
]
```

**PENTING:** Untuk menambah modul baru:
1. Buat app: `python manage.py startapp nama_modul apps/nama_modul`
2. Tambahkan ke `INSTALLED_APPS`
3. Jika tidak ditambahkan → Django TIDAK akan mengenali model & migrasi modul tersebut

---

### 3. MIDDLEWARE — Pipeline Pemrosesan Request

**Apa itu Middleware?**
Middleware = fungsi yang dijalankan di **SETIAP** request/response. Bayangkan seperti "pos pemeriksaan" di jalan tol — setiap kendaraan (request) harus melewati semua pos secara berurutan.

```
Request masuk → Pos 1 → Pos 2 → Pos 3 → ... → VIEW → ... → Pos 3 → Pos 2 → Pos 1 → Response keluar
```

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # POS 1: Keamanan HTTPS
    # Apa: Redirect HTTP ke HTTPS, tambah header keamanan (X-Content-Type-Options, dll)
    # Kenapa: Mencegah serangan man-in-the-middle
    # Output: Header response: X-Content-Type-Options: nosniff
    
    "django.middleware.gzip.GZipMiddleware",
    # POS 2: Kompresi Response
    # Apa: Kompresi HTML/CSS/JS sebelum dikirim ke browser (gzip)
    # Kenapa: Halaman 500KB dikompresi jadi 50KB → loading lebih cepat
    # Output: Header response: Content-Encoding: gzip
    
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # POS 3: Serving File Statis
    # Apa: Menyajikan file CSS, JS, gambar langsung dari Django
    # Kenapa: Di production, biasanya file statis disajikan by Nginx
    #         WhiteNoise memungkinkan Django handle sendiri (lebih simple)
    # Darimana: Library whitenoise (pip install whitenoise)
    
    "django.contrib.sessions.middleware.SessionMiddleware",
    # POS 4: Session Management
    # Apa: Baca cookie "sessionid" dari browser → load data session dari DB
    # Kenapa: Agar Django tahu siapa user yang sedang mengakses
    # Contoh: Cookie "sessionid=abc123" → DB: {user_id: 5, last_login: ...}
    
    "django.middleware.locale.LocaleMiddleware",
    # POS 5: Deteksi Bahasa
    # Apa: Deteksi bahasa dari URL, cookie, atau header Accept-Language
    # Kenapa: Agar Django bisa menyajikan konten dalam bahasa yang tepat
    
    "web_project.language_middleware.DefaultLanguageMiddleware",
    # POS 6: Bahasa Default Indonesia
    # Apa: Middleware CUSTOM kita — set bahasa default ke id-ID
    # Kenapa: Agar format tanggal, angka menggunakan format Indonesia
    # Darimana: File web_project/language_middleware.py (kode kita sendiri)
    
    "django.middleware.common.CommonMiddleware",
    # POS 7: Pemrosesan Umum
    # Apa: Tambah trailing slash ke URL, cek DISALLOWED_USER_AGENTS
    # Contoh: /produk/list → redirect ke /produk/list/ (tambah /)
    
    "django.middleware.csrf.CsrfViewMiddleware",
    # POS 8: Proteksi CSRF
    # Apa: Cross-Site Request Forgery protection
    # Kenapa: Mencegah website jahat mengirim form ke website kita
    # Cara kerja: Setiap form punya token rahasia {% csrf_token %}
    #             Django cek token ini saat form di-submit
    
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # POS 9: Otentikasi User
    # Apa: Load user dari session → set request.user
    # Kenapa: Agar di view bisa akses request.user (siapa yang login)
    # Sebelum middleware ini: request.user = AnonymousUser
    # Setelah middleware ini: request.user = <User: admin>
    
    "django.contrib.messages.middleware.MessageMiddleware",
    # POS 10: Flash Messages
    # Apa: Mengaktifkan framework pesan (success, error, warning)
    # Contoh: messages.success(request, "Data berhasil disimpan!")
    
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # POS 11: Anti-Clickjacking
    # Apa: Tambah header X-Frame-Options: DENY
    # Kenapa: Mencegah website kita di-embed dalam iframe website lain
    
    "apps.activity_log.middleware.ActivityLogMiddleware",
    # POS 12: Log Aktivitas (CUSTOM)
    # Apa: Mencatat setiap request ke database (siapa, kapan, URL apa)
    # Kenapa: Audit trail — bisa tahu siapa melakukan apa
    # Darimana: apps/activity_log/middleware.py (kode kita sendiri)
]
```

---

### 4. DATABASE — Koneksi Database

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # ENGINE = "mesin" database yang digunakan
        # sqlite3 = Database file tunggal (tanpa perlu install server)
        # Alternatif: django.db.backends.postgresql, mysql, oracle
        
        "NAME": BASE_DIR / "db.sqlite3",
        # NAME = Path ke file database
        # BASE_DIR / "db.sqlite3" = D:\starter-kit\db.sqlite3
        # File ini AUTO-GENERATED saat pertama kali migrate
    }
}
```

**Kenapa SQLite untuk development?**
- Tidak perlu install MySQL/PostgreSQL
- Database = 1 file (mudah di-backup, di-copy)
- Cocok untuk development dan small-medium traffic

**Untuk production?** Ganti ke PostgreSQL:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "erp_db",
        "USER": "erp_user", 
        "PASSWORD": "password_rahasia",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

---

## B. Context Processors — Penyuntik Data Global

### Apa itu Context Processor?
Context processor = **fungsi Python** yang dipanggil OTOMATIS di **SETIAP** request, dan hasilnya (dictionary) di-merge ke template context.

**Analogi:** Bayangkan setiap halaman web seperti surat. Context processor seperti **kop surat** — otomatis ditambahkan ke SEMUA surat tanpa perlu ditulis ulang.

### Contoh cara kerjanya:

**File `config/context_processors.py`:**
```python
def pengaturan_perusahaan(request):
    """
    Menyuntikkan data perusahaan ke SEMUA template.
    
    Dipanggil otomatis di setiap request oleh Django.
    Return dictionary yang bisa diakses di template.
    """
    from apps.pengaturan.models import PengaturanPerusahaan
    try:
        pengaturan = PengaturanPerusahaan.objects.first()
        return {
            'system_title': pengaturan.nama if pengaturan else 'ERP System',
            'system_logo_url': pengaturan.logo.url if pengaturan and pengaturan.logo else '/static/img/logo.png',
        }
    except:
        return {
            'system_title': 'ERP System',
            'system_logo_url': '/static/img/logo.png',
        }
```

**Di template (HALAMAN MANA SAJA):**
```html
<title>{{ system_title }}</title>
<!-- Output: <title>PT Serptech Indonesia</title> -->

<img src="{{ system_logo_url }}" alt="Logo">
<!-- Output: <img src="/media/perusahaan/logo.png" alt="Logo"> -->
```

**Tanpa context processor:** Kita harus menambahkan `system_title` di SETIAP view:
```python
# TANPA context processor (REPOT — harus di setiap view!)
class ProdukListView(ListView):
    def get_context_data(self, **kwargs):
        context['system_title'] = 'PT Serptech'  # Harus ditulis di setiap view!
        return context
```

**Dengan context processor:** Otomatis tersedia di semua template. Cukup didefinisikan 1 kali.

---

### Daftar Semua Context Processors

| Processor | Data Output | Contoh di Template | Kenapa Ada |
|-----------|------------|-------------------|------------|
| `my_setting` | Object settings Django | `{{ MY_SETTING.DEBUG }}` → `True` | Agar template bisa cek mode debug |
| `language_code` | Kode bahasa aktif | `{{ LANGUAGE_CODE }}` → `id` | Untuk filter konten multi-bahasa |
| `get_cookie` | Semua cookie request | `{{ COOKIES.dark_mode }}` | Untuk baca preferensi user |
| `export_templates` | Template cetak PDF/Excel | `{{ export_pdf_template.header_nama }}` | Data template cetak di semua halaman |
| `pengaturan_perusahaan` | Nama, logo, favicon | `{{ system_title }}` | Branding di semua halaman |
| `user_permissions` | Permission user login | `{{ can_view.produk }}` | Kontrol akses di template |

---

## C. URL Routing (`config/urls.py`) — Peta Jalan

### Bagaimana Django Mencocokkan URL?

```python
# config/urls.py — URL MASTER (root)
from django.urls import path, include

urlpatterns = [
    path("", include("apps.dashboard.urls")),
    # "" = URL kosong (root: /)
    # include("apps.dashboard.urls") = "cari sisa URL di file apps/dashboard/urls.py"
    
    path("produk/", include("apps.produk.urls")),
    # "produk/" = URL yang dimulai dengan /produk/
    # Django akan "memotong" bagian "produk/" lalu meneruskan sisanya
    # Contoh: /produk/list/ → potong "produk/" → sisa "list/" → cari di apps/produk/urls.py
    
    path("inventory/", include("apps.inventory.urls")),
    path("pembelian/", include("apps.pembelian.urls")),
    # ... dan seterusnya untuk semua modul ...
    
    path("api/search/", global_search, name="global_search"),
    # URL untuk API pencarian global (diakses via AJAX dari navbar)
    # global_search = function-based view (bukan class)
]
```

### Proses Pencocokan Step-by-Step

**User mengakses: `http://127.0.0.1:8000/produk/kategori/5/edit/`**

```
LANGKAH 1: Django baca config/urls.py
   path("produk/", include("apps.produk.urls"))
   → Cocok! "produk/" cocok dengan awal URL
   → Sisa URL: "kategori/5/edit/"

LANGKAH 2: Django baca apps/produk/urls.py
   path('kategori/<int:pk>/edit/', KategoriUpdateView.as_view(), name='kategori_edit')
   → Cocok! "kategori/<int:pk>/edit/" cocok
   → <int:pk> = 5 (integer, primary key)
   → Jalankan KategoriUpdateView dengan pk=5

LANGKAH 3: KategoriUpdateView dijalankan
   → Query: Kategori.objects.get(pk=5)
   → Render form edit dengan data kategori id=5
```

---

## D. TEMPLATES — Konfigurasi Template Engine

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # ↑ Engine template yang digunakan
        # Django punya engine sendiri (DTL — Django Template Language)
        # Alternatif: Jinja2 (lebih cepat, syntax sedikit beda)

        "DIRS": [BASE_DIR / "templates"],
        # ↑ Folder tempat Django mencari template
        # BASE_DIR / "templates" = d:\starter-kit\templates\
        # Django akan cari file HTML di folder ini PERTAMA

        "APP_DIRS": True,
        # ↑ True = Django juga cari template di folder templates/ tiap app
        # Contoh: apps/produk/templates/produk/list.html
        # Project ini TIDAK pakai pola ini — semua template di folder root templates/

        "OPTIONS": {
            "context_processors": [
                # ═══ BAWAAN DJANGO ═══
                "django.template.context_processors.debug",
                # → Menyuntikkan variabel 'debug' ke template (True/False)

                "django.template.context_processors.request",
                # → Menyuntikkan objek 'request' ke template
                # Agar template bisa akses: request.user, request.path, dll

                "django.contrib.auth.context_processors.auth",
                # → Menyuntikkan 'user' dan 'perms' ke template
                # {{ user.username }}, {{ perms.produk.can_view }}

                "django.contrib.messages.context_processors.messages",
                # → Menyuntikkan flash messages ke template

                # ═══ CUSTOM PROJECT ═══
                "config.context_processors.language_code",
                # → {{ LANGUAGE_CODE }} = "id"

                "config.context_processors.my_setting",
                # → {{ MY_SETTING.DEBUG }} = True/False

                "config.context_processors.get_cookie",
                # → {{ COOKIES.dark_mode }} — baca preferensi user

                "config.context_processors.environment",
                # → {{ ENVIRONMENT }} = "development" / "production"

                "config.context_processors.export_templates",
                # → Template cetak PDF/Excel (header, footer)

                "config.context_processors.pengaturan_perusahaan",
                # → {{ system_title }}, {{ system_logo_url }}, {{ system_favicon_url }}

                "apps.core.context_processors.user_permissions",
                # → {{ can_create.produk }} — RBAC permission check
            ],

            "libraries": {
                "theme": "web_project.template_tags.theme",
                # ↑ Register library 'theme' agar bisa {% load theme %}
            },

            "builtins": [
                "django.templatetags.static",
                "web_project.template_tags.theme",
                # ↑ Builtins = template tags yang OTOMATIS tersedia
                # Tanpa perlu {% load static %} di setiap template
            ],
        },
    },
]
```

### Template Caching (Production Only):

```python
# Di production (DEBUG=False), Django mengaktifkan cached template loader:
if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]
# ↑ Template hanya dicompile 1x, lalu disimpan di memory
# Development: template di-reload setiap request (agar perubahan langsung terlihat)
# Production: template di-cache (lebih cepat, tapi perlu restart jika template berubah)
```

---

## E. Static Files & Media Files — Konfigurasi Lengkap

### Static Files (CSS, JS, Gambar vendor):

```python
# URL untuk akses static files di browser
STATIC_URL = "/static/"
# ↑ Browser akses: http://localhost:8000/static/vendor/css/core.css
# Template akses: {% static 'vendor/css/core.css' %}

# Folder SUMBER static files (development)
STATICFILES_DIRS = [
    BASE_DIR / "src" / "assets",    # → d:\starter-kit\src\assets\
    BASE_DIR / "static",            # → d:\starter-kit\static\
]
# ↑ Django mencari static files di folder-folder ini
# Urutan penting! Folder pertama dicek duluan.

# Folder TUJUAN collectstatic (production)
STATIC_ROOT = BASE_DIR / "staticfiles"
# ↑ Saat deploy: python manage.py collectstatic
# Django mengumpulkan SEMUA static files ke folder ini
# WhiteNoise lalu menyajikan file dari folder ini
```

### Media Files (Upload user):

```python
# URL untuk akses media files di browser
MEDIA_URL = "/media/"
# ↑ Browser akses: http://localhost:8000/media/produk/beras.jpg

# Folder penyimpanan upload
MEDIA_ROOT = BASE_DIR / "media"
# ↑ Upload dilakukan via model ImageField/FileField:
# class Produk(models.Model):
#     gambar = models.ImageField(upload_to='produk/')
# → File disimpan di: media/produk/nama_file.jpg
```

### WhiteNoise — Serving Static Files:

```python
MIDDLEWARE = [
    # ...
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ↑ WhiteNoise menyajikan static files langsung dari Django
    # Tanpa WhiteNoise: perlu Nginx/Apache terpisah untuk serve static
    # Dengan WhiteNoise: Django handle sendiri (lebih simpel)
]
```

---

## F. Authentication & Login — Konfigurasi

```python
# ═══ URL REDIRECT ═══
LOGIN_URL = "/login/"
# ↑ Jika user BELUM login dan akses halaman protected
# → Redirect ke URL ini
# Contoh: @login_required me-redirect ke /login/?next=/produk/list/

LOGOUT_REDIRECT_URL = "/login/"
# ↑ Setelah logout → redirect ke halaman login

LOGIN_REDIRECT_URL = "/"
# ↑ Setelah login berhasil → redirect ke halaman utama (dashboard)
```

### Password Validators:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        # ↑ Password TIDAK BOLEH mirip dengan username/email
        # Contoh: username="admin" → password="admin123" ❌ DITOLAK
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        # ↑ Password minimal 8 karakter
        # "abc" ❌ DITOLAK (terlalu pendek)
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        # ↑ Password TIDAK BOLEH terlalu umum
        # "password" ❌ DITOLAK (ada di daftar 20.000 password umum)
        # "123456" ❌ DITOLAK
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        # ↑ Password TIDAK BOLEH hanya angka
        # "12345678" ❌ DITOLAK (hanya angka)
        # "abc12345" ✅ OK (campuran)
    },
]
```

---

## G. Session — Konfigurasi Sesi User

```python
# Mesin penyimpanan session
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# ↑ Session disimpan di DATABASE (tabel django_session)
# Alternatif:
#   - "django.contrib.sessions.backends.cache" → di memory cache (cepat)
#   - "django.contrib.sessions.backends.file" → di file system
#   - "django.contrib.sessions.backends.cached_db" → cache + DB (hybrid)

# Keamanan cookie session
SESSION_COOKIE_HTTPONLY = True
# ↑ Cookie session TIDAK bisa diakses oleh JavaScript
# Mencegah serangan XSS mencuri session cookie
# document.cookie TIDAK akan menampilkan session cookie

SESSION_COOKIE_SAMESITE = "Lax"
# ↑ Cookie hanya dikirim untuk request dari situs yang SAMA
# "Lax" = aman untuk navigasi normal, block cross-site POST
# "Strict" = lebih ketat, bisa mengganggu login dari link eksternal
# "None" = paling longgar (butuh Secure=True)

SESSION_COOKIE_AGE = 86400  # 24 jam dalam detik
# ↑ Session expired setelah 24 jam
# User harus login ulang setelah 24 jam
# 86400 = 60 detik × 60 menit × 24 jam
```

---

## H. Security Hardening — Perlindungan dari Serangan

### Selalu Aktif (Development & Production):

```python
X_FRAME_OPTIONS = "DENY"
# ↑ Halaman TIDAK bisa di-embed dalam iframe
# Mencegah serangan clickjacking:
# → Penyerang membuat iframe dengan halaman kita
# → User klik tombol di iframe tanpa sadar

SECURE_CONTENT_TYPE_NOSNIFF = True
# ↑ Browser TIDAK boleh menebak tipe file (MIME sniffing)
# Tanpa ini: browser bisa salah menjalankan file text sebagai JavaScript
```

### Khusus Production (DEBUG=False):

```python
if not DEBUG:
    # HTTPS wajib — semua HTTP di-redirect ke HTTPS
    SECURE_SSL_REDIRECT = True

    # HSTS — browser WAJIB pakai HTTPS selama 1 tahun
    SECURE_HSTS_SECONDS = 31536000       # 1 tahun
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookie hanya via HTTPS
    SESSION_COOKIE_SECURE = True     # Session cookie
    CSRF_COOKIE_SECURE = True        # CSRF cookie

    # Proxy header (PythonAnywhere/Nginx)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # ↑ Beritahu Django bahwa request aslinya HTTPS
    # (karena reverse proxy menangani SSL termination)

    # Referrer Policy
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    # ↑ Jangan kirim URL lengkap ke situs eksternal

else:
    # Development: cookie tanpa HTTPS (karena pakai http://localhost)
    SESSION_COOKIE_SECURE = False
```

### Perbandingan Development vs Production:

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `SECURE_SSL_REDIRECT` | Tidak aktif | `True` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | Tidak diset | `True` |
| `HSTS` | Tidak aktif | 1 tahun |
| Error page | Stack trace detail | Halaman error generik |

---

## I. Caching — Konfigurasi Cache

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # ↑ Local Memory Cache — cache di RAM proses Django
        # Cepat tapi hilang saat server restart
        # Cocok untuk development dan single-server production

        'LOCATION': 'erp-cache',
        # ↑ Identifier unik untuk cache instance

        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            # ↑ Maksimal 1000 item di cache
            
            'CULL_FREQUENCY': 3,
            # ↑ Saat MAX_ENTRIES tercapai, hapus 1/3 entri tertua
        }
    }
}
```

### Backend Cache yang Tersedia:

| Backend | Keterangan | Cocok Untuk |
|---------|-----------|-------------|
| `locmem.LocMemCache` | Cache di RAM (default project) | Development, single server |
| `db.DatabaseCache` | Cache di tabel database | Multi-server tanpa Redis |
| `filebased.FileBasedCache` | Cache di file system | Jarang dipakai |
| `memcached.PyMemcacheCache` | Cache di server Memcached | Production besar |
| `django_redis.cache.RedisCache` | Cache di server Redis | Production (recommended) |

### Cara Pakai Cache di Kode:

```python
from django.core.cache import cache

# Set cache
cache.set('total_produk', 150, timeout=300)  # Simpan 5 menit

# Get cache
total = cache.get('total_produk')  # 150 (dari cache, bukan DB!)

# Delete cache  
cache.delete('total_produk')

# Contoh caching di view:
def produk_dashboard(request):
    cache_key = f'dashboard_stats_{request.user.id}'
    stats = cache.get(cache_key)
    if stats is None:
        stats = hitung_statistik()
        cache.set(cache_key, stats, 300)  # Cache 5 menit
    return render(request, 'dashboard.html', stats)
```

---

## J. Email & Internationalization

### Email Settings:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# ↑ Kirim email via SMTP (server email)

EMAIL_HOST = "smtp.gmail.com"      # Server SMTP Gmail
EMAIL_PORT = 587                    # Port TLS
EMAIL_USE_TLS = True                # Enkripsi TLS aktif
EMAIL_HOST_USER = ""                # Alamat email pengirim
EMAIL_HOST_PASSWORD = ""            # Password atau App Password
```

### Cara Kirim Email:

```python
from django.core.mail import send_mail

send_mail(
    subject='Notifikasi ERP',
    message='Purchase Order PO-2026-0042 telah disetujui.',
    from_email='erp@perusahaan.com',
    recipient_list=['manager@perusahaan.com'],
)
```

### Internationalization (i18n):

```python
LANGUAGE_CODE = "en"         # Bahasa default
TIME_ZONE = "UTC"            # Zona waktu server
USE_I18N = True              # Aktifkan internasionalisasi
USE_TZ = True                # Gunakan timezone-aware datetime

LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
    ("ar", "Arabic"),
    ("de", "German"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",     # Folder file terjemahan (.po/.mo)
]
```

---

*Lanjut ke [03_MODEL_DATABASE.md](03_MODEL_DATABASE.md) →*
