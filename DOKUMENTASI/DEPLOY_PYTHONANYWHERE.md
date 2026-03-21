# 🚀 Panduan Deploy ERP SINTSTECH ke PythonAnywhere

> **Panduan lengkap langkah demi langkah** untuk men-deploy project ERP Django ini ke PythonAnywhere.
> Ditulis khusus untuk project ini — semua path, config, dan command sudah disesuaikan.

---

## 📋 Daftar Isi

1. [Persiapan Sebelum Deploy](#1-persiapan-sebelum-deploy)
2. [Buat Akun PythonAnywhere](#2-buat-akun-pythonanywhere)
3. [Upload Project ke PythonAnywhere](#3-upload-project-ke-pythonanywhere)
4. [Setup Virtual Environment](#4-setup-virtual-environment)
5. [Konfigurasi File .env (Production)](#5-konfigurasi-file-env-production)
6. [Jalankan Migrasi Database](#6-jalankan-migrasi-database)
7. [Kumpulkan Static Files](#7-kumpulkan-static-files)
8. [Konfigurasi Web App di PythonAnywhere](#8-konfigurasi-web-app-di-pythonanywhere)
9. [Konfigurasi WSGI File](#9-konfigurasi-wsgi-file)
10. [Konfigurasi Static & Media Files](#10-konfigurasi-static--media-files)
11. [Reload & Test](#11-reload--test)
12. [Troubleshooting](#12-troubleshooting)
13. [Maintenance & Update](#13-maintenance--update)
14. [Hal yang Harus Diperhatikan](#14-hal-yang-harus-diperhatikan)

---

## 1. Persiapan Sebelum Deploy

### ✅ Checklist sebelum mulai:

| Item | Keterangan |
|------|------------|
| Akun PythonAnywhere | Daftar gratis di pythonanywhere.com |
| Project ERP | Pastikan berjalan normal di lokal (`python manage.py runserver`) |
| Git (opsional) | Jika project sudah di GitHub/GitLab, deploy lebih mudah |
| File backup | Backup `db.sqlite3` dan folder `media/` sebelum deploy |

### 📦 Dependensi Project Ini

Project ini menggunakan library berikut (dari `requirements.txt`):

```
Django==5.0.6
gunicorn==22.0.0
packaging==24.1
python-dotenv==1.0.1
sqlparse==0.5.0
typing_extensions==4.12.2
whitenoise==6.7.0
openpyxl==3.1.2
python-barcode==0.15.1
Pillow==10.2.0
numpy==1.26.4
```

### 📂 Struktur Penting yang Perlu Diketahui

```
starter-kit/                    ← ROOT PROJECT
├── config/
│   ├── settings.py             ← Pengaturan Django utama
│   ├── urls.py                 ← Routing URL
│   ├── wsgi.py                 ← Entry point WSGI (dipakai PythonAnywhere)
│   └── template.py             ← Konfigurasi template/theme
├── apps/                       ← Semua modul ERP
├── templates/                  ← Template HTML
├── src/assets/                 ← Asset CSS/JS/Gambar (sumber)
├── static/                     ← Static files tambahan
├── staticfiles/                ← Hasil collectstatic (JANGAN edit manual)
├── media/                      ← File upload (produk, avatar, logo)
├── db.sqlite3                  ← Database SQLite
├── manage.py                   ← Command Django
├── requirements.txt            ← Daftar dependensi Python
├── .env                        ← Env development (JANGAN pakai di production)
├── .env.prod                   ← Template env production
└── web_project/                ← Template tags, middleware
```

> ⚠️ **PENTING:** PythonAnywhere akun **gratis** hanya mendukung **1 web app** dan bandwidth terbatas. Untuk production serius, gunakan akun **Hacker** ($5/bulan) atau lebih tinggi.

---

## 2. Buat Akun PythonAnywhere

### Langkah:

1. Buka **https://www.pythonanywhere.com**
2. Klik **"Pricing & signup"**
3. Pilih plan:
   - **Beginner** (gratis) → Untuk testing/demo, domain: `username.pythonanywhere.com`
   - **Hacker** ($5/bulan) → Untuk production, bisa custom domain
4. Isi form registrasi (username, email, password)
5. Verifikasi email

> 💡 **Tips:** Username PythonAnywhere akan menjadi subdomain Anda.
> Contoh: username `sintstech` → URL: `sintstech.pythonanywhere.com`

---

## 3. Upload Project via GitHub (DIREKOMENDASIKAN)

Menggunakan GitHub adalah cara **terbaik** untuk deploy karena:
- ✅ Ukuran upload kecil (hanya kode, bukan file besar)
- ✅ Mudah update kode nanti (`git pull` saja)
- ✅ Ada version control (bisa rollback jika ada masalah)
- ✅ Tidak perlu upload ZIP besar

### 3.1. Install Git di Komputer Lokal (Jika Belum Ada)

Cek apakah Git sudah terinstall:

```bash
git --version
```
> **Arti:** Menampilkan versi Git yang terinstall. Jika muncul `git version 2.x.x`, berarti sudah ada.

Jika belum ada, download di: **https://git-scm.com/downloads**

Setelah install, konfigurasi identitas Anda (hanya 1x pertama kali):

```bash
git config --global user.name "Nama Anda"
git config --global user.email "email@anda.com"
```
> **Arti:**
> - `git config` → Mengatur konfigurasi Git
> - `--global` → Berlaku untuk semua project Git di komputer ini
> - `user.name` → Nama yang muncul di setiap commit (perubahan kode)
> - `user.email` → Email yang dikaitkan dengan setiap commit

---

### 3.2. Buat Akun GitHub (Jika Belum Punya)

1. Buka **https://github.com**
2. Klik **"Sign up"**
3. Isi form: username, email, password
4. Verifikasi email

> 💡 Username GitHub akan menjadi bagian URL repository.
> Contoh: username `sintstech` → `github.com/sintstech/nama-repo`

---

### 3.3. Buat Repository Baru di GitHub

1. Login ke GitHub
2. Klik tombol **"+"** di pojok kanan atas → pilih **"New repository"**
3. Isi form:

| Field | Isi | Keterangan |
|-------|-----|------------|
| Repository name | `erp-sintstech` | Nama bebas, tanpa spasi (gunakan tanda `-`) |
| Description | `ERP System - SINTSTECH` | Opsional, deskripsi singkat project |
| Visibility | **Private** ✅ | WAJIB Private! Jangan Public karena ini kode bisnis |
| Initialize | **JANGAN centang apapun** | Jangan tambah README/gitignore/license |

4. Klik **"Create repository"**

> ⚠️ **KRITIS:** Pilih **Private**! Jika Public, siapapun bisa melihat kode dan data Anda.

Setelah dibuat, GitHub akan menampilkan halaman dengan instruksi. **Jangan ditutup** — kita perlu URL repository ini.

URL repository Anda akan terlihat seperti:
```
https://github.com/USERNAME_GITHUB/erp-sintstech.git
```

---

### 3.4. Persiapan Keamanan: Pastikan .env Tidak Ter-upload

Sebelum push ke GitHub, kita **WAJIB** memastikan file berisi data sensitif **TIDAK** ikut ter-upload.

Buka file `.gitignore` di project dan pastikan baris-baris berikut **ada** (tidak di-comment):

```gitignore
# File sensitif — JANGAN upload ke GitHub!
.env
.env.prod
db.sqlite3
db.sqlite3-journal
```

> ⚠️ **SANGAT PENTING:**
> Di project ini, baris `.env` di `.gitignore` saat ini **di-comment** (ada tanda `#` di depannya).
> Anda **HARUS** menghapus tanda `#` agar `.env` tidak ikut ter-upload ke GitHub!
>
> **Kenapa?** File `.env` berisi `SECRET_KEY` — jika bocor ke publik, orang lain bisa mengambil alih aplikasi Anda.

**Cara edit .gitignore:**

1. Buka file `.gitignore` di text editor
2. Cari baris `# .env` (sekitar baris 135)
3. **Hapus tanda `#`** sehingga menjadi `.env`
4. Simpan file

---

### 3.5. Push Project ke GitHub (Dari Komputer Lokal)

Buka **terminal/command prompt** di folder project (`d:\starter-kit`), lalu jalankan satu per satu:

#### Langkah A: Inisialisasi Git Repository

```bash
git init
```
> **Arti:** Membuat folder ini menjadi Git repository (tempat penyimpanan versi kode).
> Git akan membuat folder tersembunyi `.git/` yang menyimpan semua riwayat perubahan.
> **Hanya perlu dijalankan 1x pertama kali.**

---

#### Langkah B: Tambahkan Semua File ke Staging Area

```bash
git add .
```
> **Arti:**
> - `git add` → Menandai file yang akan disimpan (di-commit)
> - `.` (titik) → Artinya **semua file** di folder ini dan subfolder
> - File yang terdaftar di `.gitignore` **otomatis dilewati** (tidak ikut)
>
> **Analogi:** Seperti memasukkan barang ke dalam kardus sebelum dikirim.
> File yang sudah di-`add` disebut berada di "staging area" (siap dikirim).

Untuk cek file apa saja yang akan di-upload:

```bash
git status
```
> **Arti:** Menampilkan status semua file — mana yang sudah di-add (hijau), mana yang belum (merah), mana yang di-ignore.
>
> **PENTING:** Pastikan `db.sqlite3` dan `.env` **TIDAK** muncul di daftar hijau!
> Jika muncul, berarti `.gitignore` belum benar — kembali ke langkah 3.4.

---

#### Langkah C: Commit (Simpan Versi Pertama)

```bash
git commit -m "Initial commit: ERP SINTSTECH"
```
> **Arti:**
> - `git commit` → Menyimpan snapshot semua file yang sudah di-add sebagai satu "versi"
> - `-m` → Flag untuk menambahkan pesan commit langsung (tanpa membuka text editor)
> - `"Initial commit: ERP SINTSTECH"` → Pesan deskriptif tentang apa yang disimpan
>
> **Analogi:** Seperti menulis label pada kardus: "Isi: Semua kode ERP versi pertama"
>
> Setiap commit memiliki ID unik (contoh: `a1b2c3d`). Ini berguna untuk rollback nanti.

---

#### Langkah D: Hubungkan ke GitHub

```bash
git remote add origin https://github.com/USERNAME_GITHUB/erp-sintstech.git
```
> **Arti:**
> - `git remote add` → Menambahkan alamat server Git jarak jauh (remote)
> - `origin` → Nama alias untuk alamat remote ini (standar/konvensi)
> - `https://github.com/...` → URL repository GitHub yang tadi dibuat
>
> **Analogi:** Seperti menyimpan nomor telepon teman. `origin` = nama kontak, URL = nomor telepon.
>
> ⚠️ **Ganti `USERNAME_GITHUB`** dengan username GitHub Anda yang sebenarnya!
> ⚠️ **Ganti `erp-sintstech`** dengan nama repository yang Anda buat di langkah 3.3!

---

#### Langkah E: Ganti Nama Branch ke `main`

```bash
git branch -M main
```
> **Arti:**
> - `git branch` → Perintah tentang branch (cabang kode)
> - `-M` → Rename branch saat ini (paksa/force)
> - `main` → Nama branch utama (standar GitHub modern)
>
> Secara default, Git membuat branch bernama `master`. GitHub sekarang menggunakan `main`.
> Command ini mengganti nama agar sesuai standar GitHub.

---

#### Langkah F: Push (Upload ke GitHub)

```bash
git push -u origin main
```
> **Arti:**
> - `git push` → Mengirim semua commit lokal ke server remote (GitHub)
> - `-u` → Singkatan dari `--set-upstream`. Menyimpan pengaturan default sehingga push berikutnya cukup `git push` saja (tanpa perlu tulis `origin main` lagi)
> - `origin` → Nama remote yang dituju (yang tadi kita buat di langkah D)
> - `main` → Nama branch yang dikirim
>
> **Analogi:** Seperti mengirim kardus ke gudang (GitHub).

---

### 🔐 Autentikasi Saat Push

Saat pertama kali `git push`, Git akan meminta **username dan password**.

> ⚠️ **PENTING:** Sejak Agustus 2021, GitHub **TIDAK** menerima password biasa untuk push.
> Anda harus menggunakan **Personal Access Token (PAT)** sebagai pengganti password.

#### Cara Membuat Personal Access Token (PAT):

1. Login ke GitHub
2. Klik **foto profil** (pojok kanan atas) → **Settings**
3. Scroll ke bawah, klik **"Developer settings"** (paling bawah sidebar kiri)
4. Klik **"Personal access tokens"** → **"Tokens (classic)"**
5. Klik **"Generate new token"** → **"Generate new token (classic)"**
6. Isi form:

| Field | Isi |
|-------|-----|
| Note | `pythonanywhere-deploy` (label/nama token) |
| Expiration | Pilih **90 days** atau **No expiration** |
| Scopes | Centang **✅ repo** (akses penuh ke repository) |

7. Klik **"Generate token"**
8. **SALIN TOKEN SEKARANG!** Token hanya ditampilkan **1x**. Jika lupa, harus buat ulang.

Token terlihat seperti: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Saat Git Meminta Password:

```
Username: USERNAME_GITHUB
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   ← PASTE TOKEN DI SINI (bukan password)
```

> 💡 **Tips:** Agar tidak diminta token setiap kali push, simpan credential:
> ```bash
> git config --global credential.helper store
> ```
> **Arti:** Menyimpan username dan token ke file di komputer Anda sehingga tidak perlu input ulang.
> ⚠️ Token disimpan dalam teks biasa — hanya gunakan di komputer pribadi.

---

### 3.6. Verifikasi Upload ke GitHub

1. Buka **https://github.com/USERNAME_GITHUB/erp-sintstech**
2. Anda akan melihat semua file project sudah ter-upload
3. Pastikan **TIDAK ADA**:
   - ❌ `db.sqlite3` (database)
   - ❌ `.env` (konfigurasi sensitif)
   - ❌ `env/` (virtual environment)
   - ❌ `staticfiles/` (hasil collectstatic)
4. Pastikan **ADA**:
   - ✅ `apps/` (kode modul ERP)
   - ✅ `config/` (settings, urls, wsgi)
   - ✅ `templates/` (template HTML)
   - ✅ `src/` (assets CSS/JS)
   - ✅ `media/` (file upload gambar produk/logo)
   - ✅ `requirements.txt` (daftar dependensi)
   - ✅ `manage.py` (command Django)

---

### 3.7. Clone Repository di PythonAnywhere

Sekarang project sudah di GitHub. Saatnya download ke PythonAnywhere.

1. Login ke **PythonAnywhere**
2. Buka tab **"Consoles"** → klik **"Bash"**
3. Jalankan:

```bash
cd ~
```
> **Arti:** Pindah ke home directory (`/home/USERNAME/`). Tanda `~` adalah shortcut untuk home directory.

```bash
git clone https://github.com/USERNAME_GITHUB/erp-sintstech.git starter-kit
```
> **Arti:**
> - `git clone` → Download seluruh repository dari GitHub ke komputer/server ini
> - `https://github.com/...` → URL repository sumber
> - `starter-kit` → Nama folder tujuan (opsional — jika tidak ditulis, otomatis pakai nama repo)
>
> Ini akan membuat folder `/home/USERNAME/starter-kit/` berisi semua kode project.

> ⚠️ Karena repository **Private**, Git akan meminta autentikasi:
> ```
> Username: USERNAME_GITHUB
> Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ← Paste PAT di sini
> ```

#### Verifikasi clone berhasil:

```bash
ls ~/starter-kit/
```
> **Arti:** Tampilkan isi folder `starter-kit`. Harus ada `manage.py`, `config/`, `apps/`, dll.

```bash
ls ~/starter-kit/manage.py
```
> **Arti:** Cek apakah file `manage.py` ada. Jika tidak ada, berarti clone gagal atau path salah.

---

### 3.8. Upload Database & Media yang Tidak Ada di GitHub

Karena `db.sqlite3` ada di `.gitignore` (tidak ikut push), kita perlu upload terpisah.

#### Cara Upload db.sqlite3:

**Opsi A: Via PythonAnywhere File Manager (Paling Mudah)**

1. Di PythonAnywhere, buka tab **"Files"**
2. Navigasi ke `/home/USERNAME/starter-kit/`
3. Klik **"Upload a file"**
4. Pilih file `db.sqlite3` dari komputer lokal
5. Tunggu upload selesai

**Opsi B: Via SCP dari terminal lokal (Untuk yang familiar command line)**

```bash
scp d:\starter-kit\db.sqlite3 USERNAME@ssh.pythonanywhere.com:~/starter-kit/
```
> **Arti:**
> - `scp` → Secure Copy — perintah untuk copy file via SSH (aman/terenkripsi)
> - Sumber: `d:\starter-kit\db.sqlite3` (file di komputer lokal)
> - Tujuan: `USERNAME@ssh.pythonanywhere.com:~/starter-kit/` (server PythonAnywhere)
>
> ⚠️ SCP hanya tersedia untuk akun **berbayar** PythonAnywhere.

#### Verifikasi di PythonAnywhere Bash:

```bash
ls -la ~/starter-kit/db.sqlite3
```
> **Arti:** Tampilkan detail file database. Harus menampilkan ukuran file (bukan "No such file").

```bash
ls -la ~/starter-kit/media/
```
> **Arti:** Cek folder media. Jika `media/` ikut terpush ke GitHub (karena tidak di `.gitignore`), folder ini sudah otomatis ada.

#### Set Permission Database:

```bash
chmod 664 ~/starter-kit/db.sqlite3
chmod 775 ~/starter-kit/
```
> **Arti:**
> - `chmod` → Change Mode — mengubah izin akses file
> - `664` → Pemilik bisa baca+tulis, grup bisa baca+tulis, lainnya bisa baca
> - `775` → Pemilik bisa semua, grup bisa semua, lainnya bisa baca+eksekusi
>
> Django **WAJIB** bisa menulis ke `db.sqlite3` dan folder parent-nya.
> Tanpa ini, akan muncul error "OperationalError: unable to open database file".

---

### 📝 Ringkasan Perintah Git yang Dipakai

| Perintah | Arti Singkat | Kapan Dipakai |
|----------|-------------|---------------|
| `git init` | Jadikan folder ini Git repo | 1x pertama kali |
| `git add .` | Tandai semua file untuk disimpan | Setiap ada perubahan |
| `git status` | Lihat status file (sudah di-add atau belum) | Cek sebelum commit |
| `git commit -m "pesan"` | Simpan versi kode dengan label pesan | Setiap ada perubahan |
| `git remote add origin URL` | Hubungkan ke GitHub | 1x pertama kali |
| `git branch -M main` | Rename branch ke `main` | 1x pertama kali |
| `git push -u origin main` | Upload ke GitHub (pertama kali) | 1x pertama kali |
| `git push` | Upload ke GitHub (selanjutnya) | Setiap ada commit baru |
| `git pull origin main` | Download perubahan dari GitHub | Update kode di server |
| `git clone URL` | Download seluruh repo dari GitHub | 1x di PythonAnywhere |
| `git log --oneline -5` | Lihat 5 riwayat commit terakhir | Cek riwayat perubahan |
| `git diff` | Lihat perubahan yang belum di-commit | Cek apa yang berubah |

---

## 4. Setup Virtual Environment

Virtual environment **WAJIB** di PythonAnywhere. Ini mengisolasi dependensi project.

### Langkah:

1. Buka **Bash console** di PythonAnywhere
2. Jalankan perintah berikut satu per satu:

```bash
# 1. Pindah ke home directory
cd ~

# 2. Buat virtual environment dengan Python 3.10
#    (PythonAnywhere mendukung Python 3.8 - 3.12)
#    Gunakan versi yang paling mendekati versi lokal Anda
mkvirtualenv --python=/usr/bin/python3.10 erp-env

# 3. Virtual environment otomatis aktif setelah dibuat
#    Prompt berubah menjadi: (erp-env) $

# 4. Pindah ke folder project
cd ~/starter-kit

# 5. Install semua dependensi
pip install -r requirements.txt
```

### Verifikasi instalasi:

```bash
# Pastikan semua package terinstall
pip list

# Harus ada: Django, whitenoise, Pillow, openpyxl, dll
# Jika ada error, install satu-satu yang gagal:
# pip install Django==5.0.6
# pip install Pillow==10.2.0
# dll
```

> 💡 **Tips:** Jika nanti perlu masuk lagi ke virtual environment:
> ```bash
> workon erp-env
> ```
> PythonAnywhere menyimpan virtualenv di `/home/USERNAME/.virtualenvs/erp-env/`

---

## 5. Konfigurasi File .env (Production)

Project ini membaca konfigurasi dari file `.env`. Untuk production, kita perlu membuat `.env` khusus.

### Langkah:

1. Masih di Bash console, buat/edit file `.env`:

```bash
cd ~/starter-kit
nano .env
```

2. Isi dengan konfigurasi production berikut:

```env
# ═══════════════════════════════════════════════════════
# PRODUCTION ENV — PythonAnywhere
# ═══════════════════════════════════════════════════════

# WAJIB: Set False untuk production!
DEBUG=False

# Environment identifier
DJANGO_ENVIRONMENT=production

# WAJIB: Ganti dengan secret key yang BARU dan UNIK!
# Generate di: https://djecrety.ir/
SECRET_KEY=GANTI_DENGAN_SECRET_KEY_BARU_YANG_PANJANG_DAN_RANDOM

# WAJIB: Ganti USERNAME dengan username PythonAnywhere Anda
ALLOWED_HOSTS=USERNAME.pythonanywhere.com,localhost,127.0.0.1

# WAJIB: CSRF trusted origins (dengan https://)
CSRF_TRUSTED_ORIGINS=https://USERNAME.pythonanywhere.com

# Base URL aplikasi
BASE_URL=https://USERNAME.pythonanywhere.com
```

3. Tekan **Ctrl+O** → **Enter** untuk simpan
4. Tekan **Ctrl+X** untuk keluar dari nano

> ⚠️ **SANGAT PENTING:**
> - **GANTI `USERNAME`** dengan username PythonAnywhere Anda yang sebenarnya
> - **GANTI `SECRET_KEY`** dengan key baru! Jangan pakai yang sama dengan development
> - **JANGAN commit** file `.env` ke Git jika berisi data sensitif

### Generate SECRET_KEY baru:

```bash
# Cara cepat generate secret key via Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Salin hasilnya dan paste ke `.env` sebagai nilai `SECRET_KEY`.

---

## 6. Jalankan Migrasi Database

### Langkah:

```bash
# Pastikan virtual environment aktif
workon erp-env

# Pindah ke folder project
cd ~/starter-kit

# Jalankan migrasi
python manage.py migrate

# Verifikasi tidak ada error
python manage.py check
```

### Jika database baru (belum ada data):

```bash
# Buat superuser/admin
python manage.py createsuperuser

# Ikuti prompt:
# Username: admin
# Email: admin@example.com
# Password: (masukkan password yang kuat)
```

### Jika database sudah ada (upload dari lokal):

Tidak perlu `createsuperuser` — data login sudah ada di `db.sqlite3`.

> ⚠️ **PENTING:** Pastikan `db.sqlite3` memiliki permission yang benar:
> ```bash
> chmod 664 ~/starter-kit/db.sqlite3
> chmod 775 ~/starter-kit/
> ```
> Django perlu izin **write** ke file database DAN folder parent-nya (untuk SQLite journal/WAL file).

---

## 7. Kumpulkan Static Files

Django perlu mengumpulkan semua file CSS/JS/Gambar ke satu folder untuk production.

### Langkah:

```bash
# Pastikan virtual environment aktif
workon erp-env
cd ~/starter-kit

# Kumpulkan static files
python manage.py collectstatic --noinput
```

Perintah ini akan:
- Mengumpulkan file dari `src/assets/` dan `static/` → ke folder `staticfiles/`
- Whitenoise (sudah ada di project) akan menyajikan file-file ini secara efisien

### Verifikasi:

```bash
# Pastikan folder staticfiles berisi file
ls ~/starter-kit/staticfiles/
# Harus ada banyak folder: css/, js/, img/, vendor/, dll
```

---

## 8. Konfigurasi Web App di PythonAnywhere

Ini bagian **paling penting** — menghubungkan Django dengan web server PythonAnywhere.

### Langkah:

1. Buka tab **"Web"** di PythonAnywhere dashboard
2. Klik **"Add a new web app"**
3. Klik **"Next"** (terima domain `USERNAME.pythonanywhere.com`)
4. Pilih **"Manual configuration"** (⚠️ JANGAN pilih "Django"!)
5. Pilih versi Python yang **sama** dengan virtual environment (contoh: **Python 3.10**)
6. Klik **"Next"** sampai selesai

### Setelah web app dibuat, isi konfigurasi berikut:

#### A. Source Code

Di bagian **"Code"**, isi:

| Field | Nilai |
|-------|-------|
| Source code | `/home/USERNAME/starter-kit` |
| Working directory | `/home/USERNAME/starter-kit` |

#### B. Virtual Environment

Di bagian **"Virtualenv"**, isi:

| Field | Nilai |
|-------|-------|
| Virtualenv | `/home/USERNAME/.virtualenvs/erp-env` |

> 💡 Ganti `USERNAME` dengan username PythonAnywhere Anda.

---

## 9. Konfigurasi WSGI File

Ini file yang menghubungkan web server PythonAnywhere dengan aplikasi Django.

### Langkah:

1. Di halaman **"Web"**, cari bagian **"Code"**
2. Klik link **WSGI configuration file** (biasanya: `/var/www/USERNAME_pythonanywhere_com_wsgi.py`)
3. **HAPUS SEMUA** isi file tersebut
4. **Ganti** dengan kode berikut:

```python
"""
==========================================================================
 WSGI Configuration untuk PythonAnywhere
==========================================================================
 File ini menghubungkan web server PythonAnywhere dengan aplikasi
 Django ERP SINTSTECH.

 PENTING: Ganti 'USERNAME' dengan username PythonAnywhere Anda!
==========================================================================
"""
import os
import sys

# ═══ PATH PROJECT ═══
# Tambahkan folder project ke Python path agar Django bisa menemukan modul
# Ganti 'USERNAME' dengan username PythonAnywhere Anda
path = '/home/USERNAME/starter-kit'

if path not in sys.path:
    sys.path.append(path)

# ═══ ENVIRONMENT VARIABLES ═══
# Load file .env secara manual (karena PythonAnywhere tidak otomatis load .env)
from dotenv import load_dotenv
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# ═══ DJANGO SETTINGS ═══
# Beritahu Django mana file settings yang dipakai
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ═══ WSGI APPLICATION ═══
# Buat WSGI application object — ini yang dipanggil web server untuk setiap request
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **GANTI `USERNAME`** dengan username PythonAnywhere Anda (ada di 1 tempat: variabel `path`)
6. Klik **"Save"**

> ⚠️ **KRITIS:** Pastikan path `/home/USERNAME/starter-kit` benar-benar sesuai dengan lokasi project Anda. Cek via Bash:
> ```bash
> ls /home/USERNAME/starter-kit/manage.py
> # Harus menampilkan path manage.py tanpa error
> ```

---

## 10. Konfigurasi Static & Media Files

PythonAnywhere perlu tahu di mana file CSS/JS/gambar dan file upload disimpan.

### Langkah:

1. Di halaman **"Web"**, scroll ke bagian **"Static files"**
2. Tambahkan 2 mapping berikut:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/USERNAME/starter-kit/staticfiles` |
| `/media/` | `/home/USERNAME/starter-kit/media` |

### Cara menambahkan:
- Klik **"Enter URL"** → ketik `/static/`
- Klik **"Enter path"** → ketik `/home/USERNAME/starter-kit/staticfiles`
- Klik centang (✓) untuk simpan
- Ulangi untuk `/media/`

> 💡 **Catatan tentang Whitenoise:**
> Project ini sudah menggunakan Whitenoise di `settings.py` (middleware). Whitenoise bisa melayani static files **tanpa** konfigurasi di atas. Tapi menambahkan mapping static files di PythonAnywhere **lebih efisien** karena web server (Nginx) langsung menyajikan file tanpa melewati Python.

---

## 11. Reload & Test

### Langkah:

1. Di halaman **"Web"**, klik tombol hijau besar **"Reload USERNAME.pythonanywhere.com"**
2. Tunggu beberapa detik
3. Buka browser dan akses: **https://USERNAME.pythonanywhere.com**
4. Anda akan melihat halaman **login**

### Checklist Test:

| No | Test | Yang Diharapkan |
|----|------|-----------------|
| 1 | Buka URL utama | Halaman login muncul dengan styling lengkap |
| 2 | Login | Bisa login dengan akun admin |
| 3 | Dashboard | Chart, statistik, dan data muncul |
| 4 | Static files | CSS/JS/gambar tampil (tidak broken) |
| 5 | Media files | Logo, foto produk, avatar tampil |
| 6 | Tambah data | CRUD produk/kategori berfungsi |
| 7 | Upload file | Upload gambar produk/logo berfungsi |
| 8 | POS | Halaman kasir berfungsi |
| 9 | Export | Export Excel/PDF berfungsi |
| 10 | Backup/Restore | Backup data bisa di-download |

### Jika ada error:

Cek **error log** di PythonAnywhere:
1. Buka tab **"Web"**
2. Scroll ke bagian **"Log files"**
3. Klik **"Error log"** — ini tempat Django error muncul
4. Klik **"Server log"** — untuk error web server

---

## 12. Troubleshooting

### ❌ Error: "Something went wrong" / halaman putih

**Penyebab umum:** Error di konfigurasi.

**Solusi:**
1. Cek **Error log** di tab Web
2. Biasanya masalah di WSGI file atau `.env`

```bash
# Test Django bisa jalan:
workon erp-env
cd ~/starter-kit
python manage.py check
```

---

### ❌ Error: "DisallowedHost"

**Penyebab:** Domain belum ditambahkan ke `ALLOWED_HOSTS`.

**Solusi:** Edit `.env`:
```env
ALLOWED_HOSTS=USERNAME.pythonanywhere.com,localhost,127.0.0.1
```

Lalu reload web app.

---

### ❌ Error: "CSRF verification failed"

**Penyebab:** Domain belum ditambahkan ke `CSRF_TRUSTED_ORIGINS`.

**Solusi:** Edit `.env` dan pastikan ada:
```env
CSRF_TRUSTED_ORIGINS=https://USERNAME.pythonanywhere.com
```

> ⚠️ Harus pakai `https://` (dengan protokol!)

---

### ❌ CSS/JS tidak tampil (halaman polos tanpa styling)

**Penyebab:** Static files belum dikumpulkan atau mapping salah.

**Solusi:**
```bash
workon erp-env
cd ~/starter-kit
python manage.py collectstatic --noinput
```

Lalu verifikasi mapping static files di tab Web:
- URL: `/static/` → Path: `/home/USERNAME/starter-kit/staticfiles`

---

### ❌ Error: "ModuleNotFoundError"

**Penyebab:** Virtual environment belum aktif atau path salah.

**Solusi:**
1. Pastikan path virtualenv di tab Web sudah benar:
   `/home/USERNAME/.virtualenvs/erp-env`
2. Install ulang requirements:
```bash
workon erp-env
cd ~/starter-kit
pip install -r requirements.txt
```

---

### ❌ Error: "OperationalError: database is locked"

**Penyebab:** SQLite kurang cocok untuk traffic tinggi.

**Solusi temporer:**
```bash
# Pastikan permission benar
chmod 664 ~/starter-kit/db.sqlite3
chmod 775 ~/starter-kit/
```

**Solusi permanen:** Untuk traffic tinggi, pertimbangkan upgrade ke MySQL (tersedia di PythonAnywhere):

```python
# Di settings.py, ganti konfigurasi database:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'USERNAME$erp',
        'USER': 'USERNAME',
        'PASSWORD': 'password_mysql_anda',
        'HOST': 'USERNAME.mysql.pythonanywhere-services.com',
    }
}
```

---

### ❌ Gambar produk/logo tidak tampil

**Penyebab:** Mapping media files belum dikonfigurasi.

**Solusi:**
1. Pastikan di tab Web ada mapping:
   - URL: `/media/` → Path: `/home/USERNAME/starter-kit/media`
2. Pastikan folder `media/` sudah ter-upload dengan isinya

---

### ❌ Error saat upload gambar: "Permission denied"

**Penyebab:** Folder media tidak writable.

**Solusi:**
```bash
chmod -R 775 ~/starter-kit/media/
```

---

## 13. Maintenance & Update

### 🔄 Update Code (jika project di Git)

```bash
# 1. Buka Bash console
workon erp-env
cd ~/starter-kit

# 2. Pull perubahan terbaru
git pull origin main

# 3. Install dependensi baru (jika requirements.txt berubah)
pip install -r requirements.txt

# 4. Jalankan migrasi (jika ada model baru)
python manage.py migrate

# 5. Kumpulkan static files (jika ada CSS/JS baru)
python manage.py collectstatic --noinput

# 6. Reload web app
# Buka tab Web → klik "Reload"
```

### 🔄 Update Code (jika tanpa Git)

1. Upload file yang berubah via tab **"Files"**
2. Atau upload ZIP baru dan extract (hati-hati jangan timpa `db.sqlite3` dan `media/`!)

### 💾 Backup Database

```bash
# Backup database
cp ~/starter-kit/db.sqlite3 ~/starter-kit/db_backup_$(date +%Y%m%d).sqlite3

# Atau gunakan fitur backup di menu Pengaturan → Manajemen Data → Backup
```

### 📅 Akun Gratis: Perpanjang Setiap 3 Bulan

PythonAnywhere akun gratis **menonaktifkan** web app setiap 3 bulan. Anda harus login dan klik **"Run until 3 months from today"** di tab Web untuk memperpanjang.

---

## 14. Hal yang Harus Diperhatikan

### 🔴 KRITIS — Wajib Diperhatikan

| No | Item | Detail |
|----|------|--------|
| 1 | **SECRET_KEY** | WAJIB ganti dengan key baru! Jangan pakai key development |
| 2 | **DEBUG=False** | WAJIB False di production. Jika True, informasi sensitif bisa bocor |
| 3 | **ALLOWED_HOSTS** | WAJIB isi dengan domain PythonAnywhere Anda |
| 4 | **CSRF_TRUSTED_ORIGINS** | WAJIB isi dengan `https://` + domain Anda |
| 5 | **File .env** | JANGAN pernah commit ke Git jika berisi SECRET_KEY production |
| 6 | **db.sqlite3** | JANGAN lupa backup rutin! Ini semua data bisnis Anda |

### 🟡 PENTING — Perlu Diketahui

| No | Item | Detail |
|----|------|--------|
| 1 | **SQLite** | Cukup untuk 1-5 user bersamaan. Untuk traffic lebih tinggi, gunakan MySQL |
| 2 | **Akun Gratis** | Bandwidth terbatas, 1 web app, harus diperpanjang tiap 3 bulan |
| 3 | **Static files** | Jalankan `collectstatic` setiap ada perubahan CSS/JS |
| 4 | **Media files** | Pastikan folder `media/` writable (`chmod 775`) |
| 5 | **Whitenoise** | Sudah terinstall di project — bisa menyajikan static files |
| 6 | **Time Zone** | Default UTC di settings.py. Ubah ke `Asia/Jakarta` jika perlu |

### 🟢 OPSIONAL — Bisa Dilakukan Nanti

| No | Item | Detail |
|----|------|--------|
| 1 | **Custom Domain** | Perlu akun berbayar ($5+/bulan) |
| 2 | **HTTPS** | Sudah otomatis di PythonAnywhere (Let's Encrypt) |
| 3 | **MySQL** | Tersedia gratis, tapi migrasi dari SQLite perlu effort |
| 4 | **Scheduled Tasks** | Untuk auto-backup, bisa pakai PythonAnywhere Task Scheduler |
| 5 | **Email** | Akun gratis TIDAK bisa kirim email. Perlu akun berbayar |

---

## 📝 Ringkasan Cepat (Quick Reference)

```
Semua path di bawah — ganti USERNAME dengan username PythonAnywhere Anda:

Project path    : /home/USERNAME/starter-kit
Virtualenv path : /home/USERNAME/.virtualenvs/erp-env
WSGI file       : /var/www/USERNAME_pythonanywhere_com_wsgi.py
Static URL      : /static/  →  /home/USERNAME/starter-kit/staticfiles
Media URL       : /media/   →  /home/USERNAME/starter-kit/media
Settings module : config.settings
WSGI module     : config.wsgi

Perintah penting:
  workon erp-env                            # Aktifkan virtualenv
  cd ~/starter-kit                          # Masuk folder project
  python manage.py migrate                  # Jalankan migrasi
  python manage.py collectstatic --noinput  # Kumpulkan static files
  python manage.py check                    # Cek konfigurasi
  python manage.py createsuperuser          # Buat admin baru
```

---

> 📌 **Panduan ini dibuat khusus untuk project ERP SINTSTECH** dengan konfigurasi Django 5.0.6,
> SQLite, Whitenoise, dan python-dotenv. Terakhir diperbarui: Februari 2026.
