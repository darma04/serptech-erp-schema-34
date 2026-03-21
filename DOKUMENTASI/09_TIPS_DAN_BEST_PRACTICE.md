# 💡 09 — Tips, Debugging & Best Practice — Penjelasan Sangat Detail

## A. Tips Development Harian

### 1. Selalu Cek Virtual Environment Aktif

```bash
# Cek apakah venv sudah aktif:
where python
```
**Output BENAR (venv aktif):**
```
D:\starter-kit\env\Scripts\python.exe
```
**Output SALAH (venv TIDAK aktif):**
```
C:\Python312\python.exe
```
→ **Masalah:** Jika venv tidak aktif, Django mungkin tidak terinstall di Python global.
→ **Solusi:** Aktifkan: `env\Scripts\activate`

### 2. Gunakan `python manage.py check` Sebelum Push Kode

```bash
python manage.py check
```
**Output BAGUS:**
```
System check identified no issues (0 silenced).
```
**Output BERMASALAH:**
```
ERRORS:
apps.produk.Produk.kategori: (fields.E300) Field defines a relation with model 'Kategori', which is either not installed, or is abstract.
```
→ **Arti:** Model `Kategori` tidak ditemukan — mungkin belum didaftarkan di `INSTALLED_APPS`

### 3. Gunakan Django Shell untuk Test Query

```bash
python manage.py shell
```
**Lalu di shell Python:**
```python
>>> from apps.produk.models import Produk, Kategori

# Cek berapa data
>>> Produk.objects.count()
25

# Lihat 5 produk pertama
>>> Produk.objects.all()[:5]
<QuerySet [<Produk: MAK-00001 - Beras>, <Produk: MAK-00002 - Indomie>, ...]>

# Filter produk mahal
>>> Produk.objects.filter(harga_jual__gte=100000).values_list('nama', 'harga_jual')
<QuerySet [('Laptop', Decimal('15000000')), ('TV Samsung', Decimal('5000000'))]>

# Cek relasi
>>> k = Kategori.objects.get(nama="Makanan")
>>> k.produk.all()  # Semua produk di kategori Makanan (via related_name)
<QuerySet [<Produk: Beras>, <Produk: Indomie>]>

# Buat data test
>>> Kategori.objects.create(nama="Test Kategori", deskripsi="Untuk testing")
<Kategori: Test Kategori>

# Keluar shell
>>> exit()
```

---

## B. Debugging — Solusi untuk Error Umum

### Error 1: `TemplateDoesNotExist`
```
django.template.exceptions.TemplateDoesNotExist: produk/produk_list.html
```
**Arti:** Django tidak bisa menemukan file template.

**Penyebab & Solusi:**
1. File belum dibuat → Buat file di `templates/produk/produk_list.html`
2. Nama file salah (typo) → Cek ejaan di view: `template_name = '...'`
3. Folder salah → Template harus di folder `templates/` (bukan `template/`)
4. App belum di INSTALLED_APPS → Tambahkan di `settings.py`

### Error 2: `NoReverseMatch`
```
django.urls.exceptions.NoReverseMatch: Reverse for 'kategori_edit' not found.
```
**Arti:** Django tidak menemukan URL dengan nama tersebut.

**Penyebab & Solusi:**
```python
# 1. Nama URL salah di template
{% url 'produk:kategori_edit' %}    # ← Cek: apakah name='kategori_edit' ada di urls.py?

# 2. Lupa namespace
{% url 'kategori_edit' %}           # ← SALAH — harus 'produk:kategori_edit'

# 3. Lupa kirim parameter yang dibutuhkan
{% url 'produk:kategori_edit' %}    # ← SALAH — URL butuh pk
{% url 'produk:kategori_edit' pk=k.pk %}  # ← BENAR
```

### Error 3: `IntegrityError` (Unique Constraint)
```
django.db.utils.IntegrityError: UNIQUE constraint failed: produk_kategori.nama
```
**Arti:** Mencoba menyimpan data yang sudah ada (melanggar constraint `unique=True`).

**Solusi:**
```python
# Di form: cek duplikat sebelum save
def clean_nama(self):
    nama = self.cleaned_data.get('nama')
    if Kategori.objects.filter(nama__iexact=nama).exclude(pk=self.instance.pk).exists():
        raise forms.ValidationError(f'Kategori "{nama}" sudah ada!')
    return nama
```

### Error 4: `PermissionDenied` (403 Forbidden)
```
django.core.exceptions.PermissionDenied
```
**Arti:** User tidak punya permission untuk akses halaman ini.

**Cara Debug:**
```python
# Buka Django Shell dan cek permission user:
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='budi')
>>> user.profile.role
'KASIR'  # ← Aha! User ini role KASIR

# Cek permission KASIR untuk modul produk:
>>> from apps.core.models import RolePermission
>>> RolePermission.objects.filter(role='KASIR', module='produk')
<QuerySet [<RolePermission: KASIR - produk - daftar_produk - View:True Create:False>]>
# ↑ KASIR hanya bisa VIEW produk, tidak bisa CREATE/EDIT/DELETE
```

**Solusi:** Ubah permission di halaman Permission Management (`/access/roles/`)

### Error 5: `ValueError` pada Form
```
ValueError: invalid literal for int() with base 10: 'abc'
```
**Arti:** Field yang harus angka diisi teks.

**Solusi:**
```python
# Di form: pastikan widget NumberInput digunakan
'harga': forms.NumberInput(attrs={'type': 'number', 'min': '0'})
# Ini akan mencegah user mengetik huruf di browser
# + Django akan validasi di server (double protection)
```

### Error 6: `OperationalError` — Database Locked
```
django.db.utils.OperationalError: database is locked
```
**Arti:** SQLite tidak mendukung banyak penulisan bersamaan (concurrent writes).

**Penyebab:** Multiple proses Django menulis ke database bersamaan.

**Proteksi yang Sudah Diterapkan (Update Maret 2026):**
Semua operasi stok sekarang menggunakan `transaction.atomic()` + `select_for_update()`:
```python
# Pola ini diterapkan di semua operasi stok (PO, SO, POS, Transfer, Adjustment):
with transaction.atomic():
    stok = Stok.objects.select_for_update().get(produk=produk, gudang=gudang)
    stok.jumlah -= qty
    stok.save()
```
→ SQLite menangani ini dengan **file-level lock** (bukan row-level seperti PostgreSQL)
→ Saat 1 user menulis, user lain menunggu (bukan error, hanya delay)

**Solusi jika masih terjadi:**
- **Development:** Restart server (`Ctrl+C` lalu `python manage.py runserver`)
- **Production (direkomendasikan):** Ganti ke PostgreSQL yang mendukung row-level locking
  → Semua `select_for_update()` yang kita pasang akan bekerja LEBIH OPTIMAL di PostgreSQL

### Error 7: Migration Error
```
django.db.utils.OperationalError: no such table: produk_produk
```
**Arti:** Tabel belum dibuat di database.

**Solusi:**
```bash
# Langkah 1: Buat file migrasi
python manage.py makemigrations

# Langkah 2: Jalankan migrasi
python manage.py migrate

# Jika masih error, cek status migrasi:
python manage.py showmigrations produk
# Output:
# produk
#  [X] 0001_initial        ← Sudah dijalankan
#  [ ] 0002_produk_berat   ← BELUM dijalankan (ini masalahnya!)

# Jalankan yang belum:
python manage.py migrate produk
```

---

## C. Best Practice — Pola & Konvensi

### Pola Penamaan (Wajib Diikuti!)

| Jenis | Konvensi | Contoh BENAR | Contoh SALAH |
|-------|----------|-------------|--------------|
| Model | Singular, CamelCase | `PurchaseOrder` | `purchase_orders`, `Po` |
| Field model | snake_case, Indonesia | `harga_beli`, `dibuat_pada` | `HargaBeli`, `createdAt` |
| View Class | CamelCase + View | `ProdukListView` | `produk_list_view` |
| URL name | snake_case | `kategori_add` | `kategoriAdd`, `KategoriAdd` |
| Template file | snake_case.html | `produk_list.html` | `ProdukList.html` |
| CSS class | kebab-case | `btn-primary` | `btnPrimary` |
| JavaScript function | camelCase | `hapusKategori()` | `hapus_kategori()` |

---

### Panduan Langkah Demi Langkah: Menambah Modul Baru

**Contoh: Menambah modul "Proyek" untuk manajemen proyek.**

```bash
# LANGKAH 1: Buat app Django
python manage.py startapp proyek apps/proyek
# Output: Django membuat folder apps/proyek/ dengan:
#   __init__.py, admin.py, apps.py, models.py, views.py, tests.py, migrations/
```

```python
# LANGKAH 2: Edit apps/proyek/apps.py
class ProyekConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.proyek'   # Path lengkap ke app
    verbose_name = 'Proyek' # Nama tampilan di admin
```

```python
# LANGKAH 3: Daftarkan di config/settings.py
INSTALLED_APPS = [
    # ...
    'apps.proyek',  # ← TAMBAHKAN
]
```

```python
# LANGKAH 4: Buat model di apps/proyek/models.py
from django.db import models
from django.contrib.auth.models import User

class Proyek(models.Model):
    nama = models.CharField(max_length=200, verbose_name="Nama Proyek")
    deskripsi = models.TextField(blank=True, null=True)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('PLANNING', 'Planning'),
        ('PROGRESS', 'In Progress'),
        ('DONE', 'Selesai'),
    ], default='PLANNING')
    penanggung_jawab = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Proyek"
        ordering = ['-dibuat_pada']
    
    def __str__(self):
        return self.nama
```

```bash
# LANGKAH 5: Buat dan jalankan migrasi
python manage.py makemigrations proyek
# Output: Migrations for 'proyek': apps/proyek/migrations/0001_initial.py

python manage.py migrate
# Output: Applying proyek.0001_initial... OK
```

```python
# LANGKAH 6: Buat views di apps/proyek/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.core.mixins import SubModulePermissionMixin
from web_project import TemplateLayout
from .models import Proyek

class ProyekListView(SubModulePermissionMixin, ListView):
    model = Proyek
    template_name = 'proyek/proyek_list.html'
    context_object_name = 'proyek_list'
    permission_module = 'proyek'
    permission_action = 'read'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)
        return context
```

```python
# LANGKAH 7: Buat URL di apps/proyek/urls.py
from django.urls import path
from . import views

app_name = 'proyek'
urlpatterns = [
    path('list/', views.ProyekListView.as_view(), name='list'),
    # Tambah URL lainnya (create, edit, delete)
]
```

```python
# LANGKAH 8: Daftarkan URL di config/urls.py
urlpatterns = [
    # ...
    path("proyek/", include("apps.proyek.urls")),  # ← TAMBAHKAN
]
```

```html
<!-- LANGKAH 9: Buat template templates/proyek/proyek_list.html -->
{% extends 'layout/layout_vertical.html' %}
{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <div class="card">
        <div class="card-header"><h5>Daftar Proyek</h5></div>
        <div class="card-body">
            <table class="table">
                <thead><tr><th>Nama</th><th>Status</th><th>PJ</th></tr></thead>
                <tbody>
                    {% for p in proyek_list %}
                    <tr>
                        <td>{{ p.nama }}</td>
                        <td><span class="badge bg-info">{{ p.get_status_display }}</span></td>
                        <td>{{ p.penanggung_jawab.username|default:"-" }}</td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="3">Belum ada proyek</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
```

```
LANGKAH 10: Tambah menu di sidebar
→ Edit web_project/vertical_menu.json
→ Tambah entry baru untuk modul Proyek

LANGKAH 11: Tambah permission
→ Buka /access/roles/
→ Pilih role (ADMIN)
→ Centang modul Proyek: can_view ✅, can_create ✅, can_edit ✅

LANGKAH 12: Test di browser
→ Buka http://127.0.0.1:8000/proyek/list/
→ Halaman Daftar Proyek muncul!
```

---

## D. Deployment Production — Panduan Lengkap dari Nol

### Apa itu Deployment?

**Deployment** = proses membuat aplikasi yang berjalan di komputer lokal Anda menjadi **bisa diakses oleh siapa saja di internet**.

```
Development (lokal):                  Production (server):
┌─────────────────────┐              ┌─────────────────────────────┐
│ Laptop Anda:        │              │ VPS/Cloud Server:           │
│ http://127.0.0.1:   │              │ https://erp.perusahaan.com  │
│   8000              │   DEPLOY →   │                             │
│                     │              │ Diakses oleh:               │
│ Hanya bisa diakses  │              │ - Semua karyawan            │
│ di komputer Anda    │              │ - Dari mana saja            │
│ sendiri             │              │ - 24/7 online               │
└─────────────────────┘              └─────────────────────────────┘
```

### Kenapa Tidak Boleh Pakai `runserver` di Production?

```
python manage.py runserver (DEVELOPMENT ONLY):
├── ❌ Single-threaded → 1 user = 1 orang, lambat jika banyak akses
├── ❌ Tidak aman → DEBUG mode mungkin bocorkan informasi sensitif
├── ❌ Auto-reload → server restart saat file berubah (tidak stabil)
├── ❌ Tidak bisa serve static files secara efisien
└── ❌ Crash = mati, tidak ada auto-restart

Gunicorn / uWSGI (PRODUCTION):
├── ✅ Multi-process → banyak user bersamaan
├── ✅ Dioptimasi untuk performa dan keamanan
├── ✅ Stabil, tidak akan restart sendiri
├── ✅ Bisa di-manage oleh process manager (systemd)
└── ✅ Crash = auto-restart
```

### Pilihan Deployment:

```
┌─────────────────────────────────────────────────────────────┐
│  OPSI 1: VPS (Virtual Private Server) + Manual Setup       │
│  ─────────────────────────────────────────────────────       │
│  Cocok untuk: Belajar, kontrol penuh, biaya terjangkau     │
│  Provider: DigitalOcean, Vultr, Linode, IDCloudHost       │
│  Biaya: ~Rp 50.000 - 200.000/bulan                        │
│                                                             │
│  Stack: Ubuntu + Nginx + Gunicorn + SQLite/PostgreSQL      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  OPSI 2: Docker Container                                  │
│  ─────────────────────────────────────────────────────       │
│  Cocok untuk: Tim, konsistensi environment                 │
│  Perlu: Docker Desktop / Docker Engine                     │
│  Biaya: Sama seperti VPS + Docker overhead minimal         │
│                                                             │
│  Stack: Docker + Docker Compose + Nginx                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  OPSI 3: PaaS (Platform as a Service)                      │
│  ─────────────────────────────────────────────────────       │
│  Cocok untuk: Deploy cepat tanpa kelola server             │
│  Provider: Railway, Render, PythonAnywhere                 │
│  Biaya: Gratis (terbatas) atau ~Rp 70.000/bulan           │
│                                                             │
│  Stack: Otomatis (platform yang atur)                      │
└─────────────────────────────────────────────────────────────┘
```

### OPSI 1 — Deploy ke VPS (Step-by-Step):

```bash
# ═══ LANGKAH 1: Siapkan VPS ═══
# Beli VPS Ubuntu 22.04 dari DigitalOcean/Vultr/IDCloudHost
# SSH ke server:
ssh root@IP_SERVER_ANDA

# ═══ LANGKAH 2: Install dependencies ═══
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx git -y

# ═══ LANGKAH 3: Clone project ═══
cd /var/www
git clone https://github.com/username/starter-kit.git erp
cd erp

# ═══ LANGKAH 4: Setup virtual environment ═══
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# ═══ LANGKAH 5: Setup file .env production ═══
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=ganti-dengan-key-yang-sangat-panjang-dan-acak-min-50-char
ALLOWED_HOSTS=erp.perusahaan.com,IP_SERVER_ANDA
BASE_URL=https://erp.perusahaan.com
DJANGO_ENVIRONMENT=production
EOF
# PENTING:
# - DEBUG=False → WAJIB di production (menyembunyikan error detail)
# - SECRET_KEY → Harus UNIK dan RAHASIA (untuk enkripsi session/csrf)
# - ALLOWED_HOSTS → Domain yang diizinkan mengakses server

# ═══ LANGKAH 6: Jalankan migrasi & collect static ═══
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
# Isi username, email, password untuk akun admin pertama

# ═══ LANGKAH 7: Test Gunicorn ═══
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# Buka http://IP_SERVER:8000 → harus muncul halaman login
# Ctrl+C untuk stop

# ═══ LANGKAH 8: Setup Gunicorn sebagai Service (auto-start) ═══
sudo nano /etc/systemd/system/erp.service
```

**File `/etc/systemd/system/erp.service`:**
```ini
# =========================================
# Systemd Service File untuk ERP Django
# =========================================
# File ini membuat Gunicorn berjalan sebagai service:
# - Auto-start saat server boot
# - Auto-restart jika crash
# - Berjalan sebagai user 'www-data' (keamanan)

[Unit]
Description=ERP Django Gunicorn Service
After=network.target
# ↑ Jalankan service ini SETELAH network tersedia

[Service]
User=www-data
# ↑ Jalankan sebagai user www-data (bukan root, lebih aman)

Group=www-data
WorkingDirectory=/var/www/erp
# ↑ Folder project Django

Environment="PATH=/var/www/erp/env/bin"
# ↑ Gunakan Python dari virtual environment

ExecStart=/var/www/erp/env/bin/gunicorn \
    config.wsgi:application \
    --bind unix:/var/www/erp/erp.sock \
    --workers 3 \
    --timeout 120
# Penjelasan:
# config.wsgi:application → WSGI entry point (file config/wsgi.py)
# --bind unix:erp.sock → Komunikasi via Unix socket (lebih cepat dari TCP)
# --workers 3 → 3 worker proses (rumus: 2 × CPU cores + 1)
# --timeout 120 → Request timeout 2 menit (untuk upload/export besar)

Restart=always
# ↑ Jika crash → restart otomatis

[Install]
WantedBy=multi-user.target
```

```bash
# Aktifkan dan jalankan service:
sudo systemctl daemon-reload
sudo systemctl start erp
sudo systemctl enable erp     # ← Auto-start saat boot
sudo systemctl status erp     # ← Cek apakah running
```

**File `/etc/nginx/sites-available/erp`:**
```nginx
# =========================================
# Nginx Configuration untuk ERP
# =========================================
# Nginx berperan sebagai REVERSE PROXY:
# Browser → Nginx (port 80/443) → Gunicorn (unix socket)
#
# Kenapa pakai Nginx di depan Gunicorn?
# 1. Nginx serve static files JAUH lebih cepat
# 2. Nginx handle SSL/HTTPS
# 3. Nginx bisa buffer request (melindungi Gunicorn)
# 4. Nginx bisa kompresi response (gzip)

server {
    listen 80;
    server_name erp.perusahaan.com;
    # ↑ Domain website Anda

    # Serve static files langsung (CSS, JS, gambar)
    # Nginx serve file statis 10x lebih cepat dari Django
    location /static/ {
        alias /var/www/erp/staticfiles/;
        expires 30d;
        # ↑ Browser cache 30 hari (mengurangi request ke server)
    }

    # Serve media files (upload gambar produk, avatar, dll)
    location /media/ {
        alias /var/www/erp/media/;
        expires 7d;
    }

    # Semua request lain → kirim ke Gunicorn
    location / {
        proxy_pass http://unix:/var/www/erp/erp.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # ↑ Header ini memberi tahu Django:
        # - Host: domain yang diakses
        # - X-Real-IP: IP asli client (bukan IP Nginx)
        # - X-Forwarded-Proto: http atau https
        
        client_max_body_size 10M;
        # ↑ Batas upload file: 10 MB (untuk gambar produk, bukti biaya, dll)
    }
}
```

```bash
# ═══ LANGKAH 9: Aktifkan Nginx ═══
sudo ln -s /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
sudo nginx -t          # ← Test konfigurasi (harus: syntax is ok)
sudo systemctl restart nginx

# ═══ LANGKAH 10: Setup HTTPS (SSL) — GRATIS dengan Let's Encrypt ═══
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d erp.perusahaan.com
# Certbot akan:
# 1. Membuat sertifikat SSL gratis
# 2. Otomatis konfigurasi Nginx untuk HTTPS
# 3. Auto-renew setiap 90 hari

# ═══ SELESAI! ═══
# Buka https://erp.perusahaan.com → ERP sudah online!
```

### OPSI 2 — Deploy dengan Docker:

```dockerfile
# ═══ Dockerfile ═══
# File ini = "resep" untuk membuat container Docker

FROM python:3.13-slim
# ↑ Base image: Python 3.13 versi ringan (tanpa tools development)

WORKDIR /app
# ↑ Semua perintah selanjutnya dijalankan di /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
# ↑ Install semua dependencies Python
# --no-cache-dir = hemat ukuran image

COPY . .
# ↑ Salin seluruh project ke /app di container

RUN python manage.py collectstatic --noinput
# ↑ Kumpulkan file statis saat build (bukan saat runtime)

EXPOSE 8000
# ↑ Container akan listen di port 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
# ↑ Perintah yang dijalankan saat container start
```

```yaml
# ═══ docker-compose.yml ═══
# File ini mengatur SEMUA container yang dibutuhkan

version: '3.8'

services:
  web:
    build: .
    # ↑ Build dari Dockerfile di folder ini
    
    ports:
      - "8000:8000"
    # ↑ Map port 8000 host → 8000 container
    
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - ./media:/app/media
    # ↑ Persist data: database dan file upload
    # Tanpa volume, data HILANG saat container dihapus!
    
    env_file:
      - .env
    # ↑ Load variabel environment dari file .env
    
    restart: unless-stopped
    # ↑ Auto-restart jika crash, kecuali sengaja di-stop
```

```bash
# Jalankan dengan Docker:
docker-compose up -d --build
# -d = detached (background)
# --build = rebuild image (jika ada perubahan kode)

# Jalankan migrasi di dalam container:
docker-compose exec web python manage.py migrate

# Buat superuser:
docker-compose exec web python manage.py createsuperuser

# Lihat log:
docker-compose logs -f web

# Stop:
docker-compose down
```

### Arsitektur Production Lengkap:

```
┌─────────────────────────────────────────────────────────────┐
│                       INTERNET                               │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────┐                           │
│              │   NGINX (port 80) │ ← SSL Termination (443)  │
│              │   Reverse Proxy   │                           │
│              └─────┬────────┬────┘                           │
│                    │        │                                │
│          Static    │        │  Dynamic Requests              │
│          Files     │        │  (API, Views)                  │
│                    ▼        ▼                                │
│              /static/   ┌──────────────────┐                │
│              /media/    │  GUNICORN         │                │
│                         │  (3 workers)      │                │
│                         │  ├── Worker 1     │                │
│                         │  ├── Worker 2     │                │
│                         │  └── Worker 3     │                │
│                         └────────┬─────────┘                │
│                                  │                           │
│                                  ▼                           │
│                         ┌──────────────────┐                │
│                         │  Django App       │                │
│                         │  (config.wsgi)    │                │
│                         └────────┬─────────┘                │
│                                  │                           │
│                         ┌────────▼─────────┐                │
│                         │  SQLite / Postgres│                │
│                         │  Database         │                │
│                         └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### OPSI 3 — Deploy ke PythonAnywhere (Gratis & Mudah):

PythonAnywhere = platform hosting Python yang paling mudah untuk pemula. Tidak perlu install Nginx, Gunicorn, atau konfigurasi server. Cukup upload kode dan klik tombol.

```bash
# ═══ LANGKAH 1: Buat akun di pythonanywhere.com ═══
# Pilih plan "Beginner" (GRATIS) atau "Hacker" (berbayar)
# Akun gratis: username.pythonanywhere.com (1 web app, akses terbatas)

# ═══ LANGKAH 2: Buka Bash console di PythonAnywhere ═══
# Dashboard → Consoles → New console: Bash

# ═══ LANGKAH 3: Clone project ═══
git clone https://github.com/username/starter-kit.git
cd starter-kit

# ═══ LANGKAH 4: Setup virtual environment ═══
python3.13 -m venv env
source env/bin/activate
pip install -r requirements.txt

# ═══ LANGKAH 5: Setup file .env ═══
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=ganti-dengan-key-yang-sangat-panjang-dan-acak
ALLOWED_HOSTS=username.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://username.pythonanywhere.com
BASE_URL=https://username.pythonanywhere.com
DJANGO_ENVIRONMENT=production
EOF

# ═══ LANGKAH 6: Migrasi & collect static ═══
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

**Konfigurasi di Web Tab PythonAnywhere:**

```
Dashboard → Web tab → Add a new web app

1. Domain: username.pythonanywhere.com (otomatis)

2. Python version: Python 3.13

3. Source code: /home/username/starter-kit

4. Working directory: /home/username/starter-kit

5. Virtualenv: /home/username/starter-kit/env

6. Static files mapping:
   URL          | Directory
   /static/     | /home/username/starter-kit/staticfiles/
   /media/      | /home/username/starter-kit/media/
   
   ⚠️ PENTING: Directory HARUS mengarah ke folder `staticfiles/`
   (hasil collectstatic), BUKAN folder `static/` sumber.

7. WSGI configuration file → Klik link → Edit:
```

**File WSGI (`/var/www/username_pythonanywhere_com_wsgi.py`):**

```python
# ═══ WSGI Configuration untuk PythonAnywhere ═══
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Tambahkan path project
path = '/home/username/starter-kit'
if path not in sys.path:
    sys.path.append(path)

# Load .env file
env_path = Path(path) / '.env'
load_dotenv(dotenv_path=env_path)

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

```bash
# ═══ LANGKAH 7: Klik "Reload" di Web tab ═══
# Web app sekarang live di https://username.pythonanywhere.com
```

### ⚠️ Troubleshooting PythonAnywhere — Masalah Umum:

**Masalah 1: JavaScript/CSS 404 Not Found**
```
Gejala: Halaman muncul tapi AJAX/modal tidak bekerja
Console: GET /static/js/nama-file.js → 404

Penyebab: collectstatic belum dijalankan setelah update kode

Solusi:
cd ~/starter-kit
source env/bin/activate
python manage.py collectstatic --noinput
# → Lalu Reload web app di Web tab
```

**Masalah 2: CSRF Verification Failed**
```
Gejala: Form submit gagal, error "CSRF verification failed"

Penyebab: CSRF_TRUSTED_ORIGINS tidak dikonfigurasi
  
Solusi — tambah di .env:
CSRF_TRUSTED_ORIGINS=https://username.pythonanywhere.com
```

**Masalah 3: Static files mapping salah**
```
Gejala: Semua CSS/JS 404, halaman muncul tanpa styling

Cek: Web tab → Static files
  URL: /static/
  Directory: /home/username/starter-kit/staticfiles/
            ↑ HARUS folder staticfiles (hasil collectstatic)
            BUKAN /home/username/starter-kit/static/
```

### Tips Update Kode di PythonAnywhere:

```bash
# Setiap kali push kode baru:
cd ~/starter-kit
git pull origin main                      # 1. Ambil kode terbaru
source env/bin/activate                   # 2. Aktifkan venv
pip install -r requirements.txt           # 3. Install dependency baru (jika ada)
python manage.py migrate                  # 4. Jalankan migrasi
python manage.py collectstatic --noinput  # 5. Update static files ← JANGAN LUPA!
# 6. Klik Reload di Web tab PythonAnywhere
```

---

## E. Testing — Menulis Unit Test & Integration Test

### Kenapa Testing Penting?

```
Tanpa Testing:                          Dengan Testing:
┌─────────────────────────┐            ┌─────────────────────────┐
│ "Saya ubah model Produk"│            │ "Saya ubah model Produk"│
│ "Apakah semua masih     │            │ → Jalankan test         │
│  bekerja?"              │            │ → 45 tests passed ✅    │
│ "Hmm... harus manual    │            │ → 2 tests failed ❌    │
│  cek satu per satu..."  │            │   → Ternyata form       │
│ "Lupa test POS...       │            │     validation rusak!   │
│  ternyata rusak!"       │            │ → Perbaiki sebelum      │
│                         │            │   deploy!               │
└─────────────────────────┘            └─────────────────────────┘
```

### Jenis Test:

```
┌──────────────────────────────────────────────────────────────┐
│  UNIT TEST                                                    │
│  ─────────                                                    │
│  Test SATU komponen secara TERISOLASI.                        │
│  Contoh: Test model Produk, test form validasi                │
│  Cepat: < 1 detik per test                                   │
│                                                               │
│  INTEGRATION TEST                                             │
│  ────────────────                                             │
│  Test BEBERAPA komponen bekerja BERSAMA.                      │
│  Contoh: Test view + template + model + permission            │
│  Lebih lambat: butuh database test                            │
│                                                               │
│  END-TO-END TEST (E2E)                                        │
│  ─────────────────────                                        │
│  Test SELURUH alur dari perspektif user di browser.           │
│  Contoh: Login → buka produk → tambah produk → cek tersimpan │
│  Paling lambat: butuh browser (Selenium)                      │
└──────────────────────────────────────────────────────────────┘
```

### Contoh Test Model:

```python
# File: apps/produk/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from apps.produk.models import Produk, Kategori, Satuan

class ProdukModelTest(TestCase):
    """
    TestCase = class bawaan Django untuk menulis test.
    
    Setiap method yang dimulai 'test_' akan dijalankan sebagai test.
    setUp() dipanggil SEBELUM setiap test method (fresh data).
    Django membuat database KOSONG khusus untuk test (bukan DB asli!)
    → Data test TIDAK akan mengganggu data production.
    """
    
    def setUp(self):
        """
        setUp() = persiapan data sebelum SETIAP test method.
        Dipanggil ulang setiap kali, jadi setiap test mulai fresh.
        """
        # Buat user untuk field 'dibuat_oleh'
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Buat kategori dan satuan
        self.kategori = Kategori.objects.create(
            nama='Makanan',
            dibuat_oleh=self.user
        )
        self.satuan = Satuan.objects.create(
            nama='Kilogram',
            singkatan='kg'
        )
        
        # Buat produk
        self.produk = Produk.objects.create(
            nama='Beras Premium',
            harga_beli=10000,
            harga_jual=15000,
            kategori=self.kategori,
            satuan=self.satuan,
            dibuat_oleh=self.user
        )
    
    def test_produk_str(self):
        """Test: method __str__ mengembalikan format yang benar."""
        # __str__ biasanya return "SKU - Nama"
        self.assertIn('Beras Premium', str(self.produk))
    
    def test_produk_sku_auto_generated(self):
        """Test: SKU otomatis di-generate saat produk dibuat."""
        self.assertIsNotNone(self.produk.sku)
        # SKU format: MAK-00001 (3 huruf kategori + nomor urut)
    
    def test_produk_relasi_kategori(self):
        """Test: produk terhubung ke kategori yang benar."""
        self.assertEqual(self.produk.kategori.nama, 'Makanan')
    
    def test_produk_profit_margin(self):
        """Test: harga jual > harga beli (margin positif)."""
        self.assertGreater(
            self.produk.harga_jual,
            self.produk.harga_beli,
            "Harga jual harus lebih besar dari harga beli!"
        )
    
    def test_produk_default_aktif(self):
        """Test: produk baru default aktif=True."""
        self.assertTrue(self.produk.aktif)
```

### Contoh Test View (Integration):

```python
# File: apps/produk/tests.py (lanjutan)

from django.test import TestCase, Client
from django.urls import reverse

class ProdukViewTest(TestCase):
    """
    Test view menggunakan Django Test Client.
    Client = simulasi browser yang mengirim request HTTP.
    Tidak perlu browser asli — semua di-test di level Python.
    """
    
    def setUp(self):
        # Buat user dan login
        self.client = Client()
        self.user = User.objects.create_user(
            username='admin',
            password='testpass123'
        )
        # Buat profile dengan role SUPERUSER (bypass permission)
        from auth.models import Profile
        Profile.objects.filter(user=self.user).update(role='SUPERUSER')
        
        # Login
        self.client.login(username='admin', password='testpass123')
        
        # Buat data test
        self.kategori = Kategori.objects.create(
            nama='Elektronik',
            dibuat_oleh=self.user
        )
    
    def test_produk_list_view(self):
        """Test: halaman daftar produk bisa diakses (HTTP 200)."""
        url = reverse('produk:list')
        # ↑ reverse() = convert nama URL → path URL
        # 'produk:list' → '/produk/list/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # ↑ HTTP 200 = OK, halaman terbuka dengan benar
    
    def test_produk_list_requires_login(self):
        """Test: user yang belum login di-redirect ke halaman login."""
        self.client.logout()  # Logout dulu
        
        url = reverse('produk:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        # ↑ HTTP 302 = Redirect (ke halaman login)
        self.assertIn('/login/', response.url)
    
    def test_produk_create_view(self):
        """Test: bisa membuat produk baru via form POST."""
        url = reverse('produk:tambah')
        
        data = {
            'nama': 'Laptop Test',
            'harga_beli': '5000000',
            'harga_jual': '7500000',
            'kategori': self.kategori.pk,
            'aktif': True,
        }
        
        response = self.client.post(url, data)
        
        # Cek redirect setelah create berhasil
        self.assertEqual(response.status_code, 302)
        
        # Cek produk tersimpan di database
        self.assertTrue(
            Produk.objects.filter(nama='Laptop Test').exists()
        )
    
    def test_produk_permission_denied(self):
        """Test: user tanpa permission mendapat 403."""
        # Ubah role menjadi USER biasa (tanpa permission)
        from auth.models import Profile
        Profile.objects.filter(user=self.user).update(role='USER')
        
        url = reverse('produk:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)
        # ↑ HTTP 403 = Forbidden (tidak punya akses)
```

### Contoh Test Form (Validasi):

```python
class ProdukFormTest(TestCase):
    """Test form validasi produk."""
    
    def test_form_valid(self):
        """Test: form dengan data lengkap itu valid."""
        from apps.produk.forms import ProdukForm
        
        form_data = {
            'nama': 'Produk Test',
            'harga_beli': '10000',
            'harga_jual': '15000',
        }
        form = ProdukForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_form_invalid_tanpa_nama(self):
        """Test: form tanpa nama itu INVALID."""
        from apps.produk.forms import ProdukForm
        
        form_data = {
            'nama': '',  # ← KOSONG
            'harga_beli': '10000',
        }
        form = ProdukForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nama', form.errors)
        # ↑ Error ada di field 'nama'
```

### Menjalankan Test:

```bash
# ═══ Jalankan SEMUA test ═══
python manage.py test
# Output:
# Creating test database...
# ............................
# Ran 28 tests in 2.341s
# OK

# ═══ Jalankan test untuk 1 app saja ═══
python manage.py test apps.produk
# Hanya jalankan test di apps/produk/tests.py

# ═══ Jalankan 1 test class saja ═══
python manage.py test apps.produk.tests.ProdukModelTest

# ═══ Jalankan 1 test method saja ═══
python manage.py test apps.produk.tests.ProdukModelTest.test_produk_str

# ═══ Verbose output (detail) ═══
python manage.py test -v 2
# Output:
# test_produk_str (apps.produk.tests.ProdukModelTest) ... ok
# test_produk_sku_auto_generated (apps.produk.tests.ProdukModelTest) ... ok
# test_produk_list_view (apps.produk.tests.ProdukViewTest) ... ok
# test_produk_permission_denied (apps.produk.tests.ProdukViewTest) ... ok
```

### Test Database — Aman & Terisolasi:

```
PENTING: Django test TIDAK menggunakan database asli Anda!

Saat 'python manage.py test' dijalankan:
1. Django MEMBUAT database baru: test_db.sqlite3
2. Jalankan semua migrasi di database test
3. Jalankan semua test → data ditulis ke database test
4. Setelah selesai → database test DIHAPUS

Artinya:
✅ Data production Anda 100% AMAN
✅ Setiap test mulai dengan database KOSONG
✅ Test tidak saling mempengaruhi
```

---

## F. Prasyarat Django — Panduan untuk Pemula Absolut

### Apa itu Python?

**Python** = bahasa pemrograman yang digunakan untuk membuat Django & ERP ini.

```
Kenapa Python?
├── Mudah dipelajari (syntax mirip bahasa Inggris)
├── Library sangat banyak (200.000+ package di PyPI)
├── Dipakai oleh: Google, Instagram, Netflix, Spotify
├── Cocok untuk: web, data science, AI, automation
└── GRATIS dan open source
```

### Install Python:

```bash
# ═══ Windows ═══
# 1. Download dari https://www.python.org/downloads/
# 2. Jalankan installer
# 3. PENTING: Centang "Add Python to PATH" ✅
# 4. Klik "Install Now"
# 5. Verifikasi:
python --version
# Output: Python 3.13.2

# ═══ Kenapa harus "Add to PATH"? ═══
# PATH = daftar folder tempat Windows mencari program
# Jika Python TIDAK di PATH:
#   'python' is not recognized as an internal or external command
# Jika Python ADA di PATH:
#   Python 3.13.2  ✅
```

### Apa itu pip?

**pip** = "app store" untuk Python. Digunakan untuk menginstall library/package tambahan.

```bash
# Cek pip sudah terinstall:
pip --version
# Output: pip 24.0 from ...\pip (python 3.13)

# Install package:
pip install django
# ↑ Download Django dari PyPI dan install ke Python

# Install dari requirements.txt:
pip install -r requirements.txt
# ↑ Install SEMUA package yang terdaftar di file requirements.txt
# File ini berisi daftar package yang dibutuhkan project:
# Django==5.0.6
# gunicorn==22.0.0
# openpyxl==3.1.2
# ... dll

# Lihat semua package terinstall:
pip list
# Output:
# Package          Version
# Django           5.0.6
# gunicorn         22.0.0
# ...
```

### Apa itu Virtual Environment (venv)?

**Virtual Environment** = "ruangan terisolasi" untuk setiap project Python.

```
TANPA venv (MASALAH!):              DENGAN venv (BENAR):
┌─────────────────────┐            ┌─────────────────────┐
│ Python Global       │            │ Project ERP          │
│ ├── Django 5.0      │            │ └── env/             │
│ ├── Django 4.2 ← ?  │            │     └── Django 5.0   │
│ ├── numpy 1.26      │            │                      │
│ └── 100 package     │            ├─────────────────────┤
│                     │            │ Project Lain         │
│ Semua project pakai │            │ └── env/             │
│ Python yang SAMA    │            │     └── Django 4.2   │
│ → Konflik versi!    │            │                      │
└─────────────────────┘            │ Setiap project PUNYA │
                                   │ environment SENDIRI  │
                                   │ → Tidak ada konflik! │
                                   └─────────────────────┘
```

```bash
# ═══ Membuat Virtual Environment ═══
python -m venv env
# ↑ Buat folder 'env' berisi Python terisolasi
# 'env' = nama folder (konvensi umum: env, venv, .venv)

# ═══ Mengaktifkan venv ═══
# Windows (PowerShell):
env\Scripts\activate

# Windows (Command Prompt):
env\Scripts\activate.bat

# Linux/Mac:
source env/bin/activate

# ═══ Setelah aktif, prompt berubah: ═══
# (env) D:\starter-kit>
# ↑ "(env)" menandakan venv aktif

# ═══ Menonaktifkan venv ═══
deactivate
```

### Apa itu manage.py?

**manage.py** = "remote control" untuk project Django. Semua perintah penting dijalankan lewat file ini.

```bash
# ═══ Perintah yang PALING SERING dipakai ═══

# 1. Jalankan development server:
python manage.py runserver
# → Buka http://127.0.0.1:8000 di browser

# 2. Buat file migrasi (setelah ubah models.py):
python manage.py makemigrations

# 3. Jalankan migrasi (buat/ubah tabel di database):
python manage.py migrate

# 4. Buat akun superuser:
python manage.py createsuperuser

# 5. Buka Django shell (REPL untuk coba query):
python manage.py shell

# 6. Cek error di project:
python manage.py check

# 7. Kumpulkan file statis untuk production:
python manage.py collectstatic

# 8. Jalankan test:
python manage.py test

# 9. Lihat semua URL yang terdaftar:
python manage.py show_urls  # butuh django-extensions

# 10. Buat app baru:
python manage.py startapp nama_app apps/nama_app
```

### Apa itu Django ORM?

**ORM (Object Relational Mapping)** = cara bicara dengan database menggunakan Python, **TANPA menulis SQL**.

```python
# ═══ TANPA ORM (tulis SQL manual): ═══
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT * FROM produk_produk WHERE aktif=1 AND harga_jual > 10000")
rows = cursor.fetchall()
# ← Ribet, rawan SQL injection, beda syntax tiap database

# ═══ DENGAN Django ORM (Pythonic): ═══
produk = Produk.objects.filter(aktif=True, harga_jual__gt=10000)
# ← Lebih mudah dibaca, aman, dan SAMA untuk semua database!

# ═══ Mapping ORM → SQL ═══
# Python:                          SQL:
# Produk.objects.all()           → SELECT * FROM produk_produk
# Produk.objects.get(pk=1)       → SELECT * FROM produk_produk WHERE id=1
# Produk.objects.filter(aktif=1) → SELECT * FROM produk_produk WHERE aktif=1
# Produk.objects.count()         → SELECT COUNT(*) FROM produk_produk
# Produk.objects.create(nama=..) → INSERT INTO produk_produk (nama) VALUES (...)
# produk.save()                  → UPDATE produk_produk SET ... WHERE id=...
# produk.delete()                → DELETE FROM produk_produk WHERE id=...

# ═══ Lookup yang sering dipakai ═══
# __exact     → WHERE field = value        (default, bisa dihilangkan)
# __iexact    → WHERE LOWER(field) = value (case insensitive)
# __contains  → WHERE field LIKE '%value%'
# __icontains → case insensitive contains
# __gt        → WHERE field > value        (greater than)
# __gte       → WHERE field >= value       (greater than or equal)
# __lt        → WHERE field < value        (less than)
# __lte       → WHERE field <= value
# __in        → WHERE field IN (v1, v2, v3)
# __isnull    → WHERE field IS NULL
# __startswith → WHERE field LIKE 'value%'
# __range     → WHERE field BETWEEN v1 AND v2
```

---

## G. Step-by-Step Project Setup — Dari Nol Sampai Running

```
Persyaratan Minimum:
┌─────────────────────────────────────┐
│ ✅ Python 3.10 atau lebih baru      │
│ ✅ pip (biasanya terinstall bersama)│
│ ✅ Git (untuk clone repository)     │
│ ✅ Text editor (VS Code direkomen) │
│ ✅ Browser modern (Chrome/Firefox)  │
└─────────────────────────────────────┘
```

### Langkah Lengkap:

```bash
# ═══════════════════════════════════════════════════
# LANGKAH 1: Clone Repository
# ═══════════════════════════════════════════════════
git clone https://github.com/username/starter-kit.git
cd starter-kit
# Apa yang terjadi:
# Git mengunduh SEMUA kode project ke folder starter-kit
# cd = masuk ke folder tersebut

# ═══════════════════════════════════════════════════
# LANGKAH 2: Buat Virtual Environment
# ═══════════════════════════════════════════════════
python -m venv env
# Apa yang terjadi:
# Python membuat folder 'env' berisi:
# env/
# ├── Scripts/        ← (Windows) atau bin/ (Linux)
# │   ├── python.exe  ← Python terisolasi
# │   ├── pip.exe     ← pip terisolasi
# │   └── activate    ← Script untuk mengaktifkan venv
# └── Lib/            ← Tempat install packages
#     └── site-packages/

# ═══════════════════════════════════════════════════
# LANGKAH 3: Aktifkan Virtual Environment
# ═══════════════════════════════════════════════════
# Windows (PowerShell):
env\Scripts\activate

# Windows (CMD):
env\Scripts\activate.bat

# Linux/Mac:
source env/bin/activate

# Prompt berubah menjadi:
# (env) D:\starter-kit>
# ↑ Tanda bahwa venv sudah aktif!

# ═══════════════════════════════════════════════════
# LANGKAH 4: Install Dependencies
# ═══════════════════════════════════════════════════
pip install -r requirements.txt
# Apa yang terjadi:
# pip membaca requirements.txt dan install SEMUA package:
# - Django==5.0.6           ← Framework web utama
# - gunicorn==22.0.0        ← Production server
# - python-dotenv==1.0.1    ← Baca file .env
# - whitenoise==6.7.0       ← Serve static files
# - openpyxl==3.1.2         ← Export Excel
# - python-barcode==0.15.1  ← Generate barcode produk
# - Pillow==10.2.0          ← Proses gambar (thumbnail, avatar)
# - numpy==1.26.4           ← Kalkulasi (face recognition)
#
# Output akhir:
# Successfully installed Django-5.0.6 gunicorn-22.0.0 ...

# ═══════════════════════════════════════════════════
# LANGKAH 5: Setup Environment File (.env)
# ═══════════════════════════════════════════════════
# Buat file .env di root project (samping manage.py):
# Windows:
copy .env.example .env
# Linux:
# cp .env.example .env

# Edit .env dengan notepad / VS Code:
# DEBUG=True
# SECRET_KEY=django-insecure-ganti-ini-dengan-key-random-anda
# BASE_URL=http://127.0.0.1:8000

# Apa itu .env?
# File .env menyimpan KONFIGURASI RAHASIA yang tidak boleh
# di-commit ke Git (ada di .gitignore):
# - SECRET_KEY: kunci enkripsi Django (JANGAN share!)
# - DEBUG: True saat development, False saat production
# - API keys, database passwords, dll

# ═══════════════════════════════════════════════════
# LANGKAH 6: Jalankan Migrasi Database
# ═══════════════════════════════════════════════════
python manage.py migrate
# Apa yang terjadi:
# 1. Django membuat file db.sqlite3 (database SQLite)
# 2. Membuat 35+ tabel sesuai dengan semua model:
#    - auth_user, auth_profile
#    - produk_produk, produk_kategori, produk_satuan
#    - penjualan_salesorder, penjualan_salesorderitem
#    - ... semua tabel lainnya
# 3. Membuat tabel sistem Django:
#    - django_session (untuk login)
#    - django_migrations (riwayat migrasi)
#    - django_content_type
#
# Output:
# Operations to perform:
#   Apply all migrations: admin, auth, activity_log, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying produk.0001_initial... OK
#   ... (banyak migrasi)
#   OK

# ═══════════════════════════════════════════════════
# LANGKAH 7: Buat Akun Superuser
# ═══════════════════════════════════════════════════
python manage.py createsuperuser
# Django akan tanya:
# Username: admin
# Email: admin@example.com
# Password: ********
# Password (again): ********
# Superuser created successfully.
#
# Akun ini role = SUPERUSER → bisa akses SEMUA fitur

# ═══════════════════════════════════════════════════
# LANGKAH 8: Jalankan Development Server
# ═══════════════════════════════════════════════════
python manage.py runserver
# Output:
# Watching for file changes with StatReloader
# Performing system checks...
# System check identified no issues (0 silenced).
# February 22, 2026 - 00:00:00
# Django version 5.0.6, using settings 'config.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.

# ═══════════════════════════════════════════════════
# LANGKAH 9: Buka di Browser!
# ═══════════════════════════════════════════════════
# Buka http://127.0.0.1:8000/
# → Halaman LOGIN muncul
# → Masukkan username: admin, password: (yang tadi dibuat)
# → Dashboard ERP terbuka! 🎉
```

### Troubleshooting Setup:

```
MASALAH                              SOLUSI
────────────────────────────────     ──────────────────────────────────
'python' is not recognized          → Install Python, centang "Add to PATH"
                                     → Restart terminal setelah install

pip install gagal                    → Cek koneksi internet
(connection error)                   → Coba: pip install --trusted-host
                                       pypi.org -r requirements.txt

ModuleNotFoundError: No module       → venv belum aktif!
named 'django'                       → Jalankan: env\Scripts\activate

Error "port 8000 already in use"     → Ada server lain jalan di port 8000
                                     → Gunakan port lain:
                                       python manage.py runserver 8001

Migration error                      → Hapus db.sqlite3 (HATI-HATI: data hilang)
(database corrupted)                 → Jalankan ulang: python manage.py migrate

Static files tidak muncul            → Cek STATICFILES_DIRS di settings.py
(halaman polos tanpa CSS)            → Jalankan: python manage.py collectstatic
                                     → Pastikan WhiteNoise di MIDDLEWARE

Execution Policy error               → PowerShell tidak izinkan script
(PowerShell)                         → Jalankan:
                                       Set-ExecutionPolicy -Scope CurrentUser
                                       -ExecutionPolicy RemoteSigned
```

### Struktur Folder Setelah Setup:

```
D:\starter-kit\                      ← ROOT project
├── .env                             ← Konfigurasi rahasia (JANGAN commit!)
├── manage.py                        ← "Remote control" Django
├── requirements.txt                 ← Daftar package yang dibutuhkan
├── db.sqlite3                       ← Database (otomatis dibuat saat migrate)
├── env\                             ← Virtual environment (JANGAN commit!)
│   ├── Scripts\                     ← Python & pip terisolasi
│   └── Lib\                         ← Package terinstall
├── config\                          ← Konfigurasi Django
│   ├── settings.py                  ← Pengaturan utama
│   ├── urls.py                      ← URL routing utama
│   └── wsgi.py                      ← Entry point production
├── auth\                            ← Modul autentikasi
├── apps\                            ← Semua modul ERP
│   ├── produk\                      ← Modul Produk
│   ├── penjualan\                   ← Modul Penjualan
│   ├── pembelian\                   ← Modul Pembelian
│   ├── pos\                         ← Modul POS (Kasir)
│   └── ...                          ← Modul lainnya
├── templates\                       ← Semua file HTML
├── src\assets\                      ← File CSS, JS, gambar
├── media\                           ← File upload (gambar produk, avatar)
└── DOKUMENTASI\                     ← File dokumentasi ini!
```

---

## H. Referensi & Sumber Belajar

| Topik | URL | Kenapa Berguna |
|-------|-----|---------------|
| Dokumentasi Django | [docs.djangoproject.com](https://docs.djangoproject.com) | Referensi utama semua fitur Django |
| Django Tutorial | [docs.djangoproject.com/en/5.0/intro/](https://docs.djangoproject.com/en/5.0/intro/) | Tutorial step-by-step untuk pemula |
| Bootstrap 5 | [getbootstrap.com/docs/5.3](https://getbootstrap.com/docs/5.3) | Referensi semua class CSS Bootstrap |
| DataTables | [datatables.net](https://datatables.net) | Dokumentasi plugin tabel interaktif |
| Select2 | [select2.org](https://select2.org) | Dokumentasi dropdown searchable |
| Remix Icon | [remixicon.com](https://remixicon.com) | Library ikon (2000+ ikon gratis) |
| Chart.js | [chartjs.org](https://www.chartjs.org) | Dokumentasi library chart |
| pdfMake | [pdfmake.org](http://pdfmake.org) | Generate PDF di browser |
| Python Tutorial | [python.org/about/gettingstarted](https://www.python.org/about/gettingstarted/) | Belajar Python dari nol |
| Docker Guide | [docs.docker.com/get-started](https://docs.docker.com/get-started/) | Belajar Docker container |
| Nginx Basics | [nginx.org/en/docs/beginners_guide.html](http://nginx.org/en/docs/beginners_guide.html) | Panduan dasar Nginx |

---

*← Kembali ke [00_PENDAHULUAN.md](00_PENDAHULUAN.md)*
