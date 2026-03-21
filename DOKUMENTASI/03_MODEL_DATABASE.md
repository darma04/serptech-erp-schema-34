# 🗄️ 03 — Model & Database — Penjelasan Sangat Detail

## A. Apa itu Model Django? Kenapa Pakai Model?

### Masalah Tanpa Model (SQL mentah):
```python
# TANPA MODEL — harus tulis SQL mentah (rawan error, tidak portable)
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE produk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama VARCHAR(200) NOT NULL,
        harga_jual DECIMAL(15,2) DEFAULT 0,
        aktif BOOLEAN DEFAULT 1
    )
""")
# Problem:
# 1. SQL berbeda untuk setiap database (SQLite vs PostgreSQL vs MySQL)
# 2. Tidak ada validasi otomatis
# 3. Tidak ada relasi yang jelas
# 4. Rawan SQL injection jika tidak hati-hati
```

### Solusi Django Model (ORM):
```python
# DENGAN MODEL — tulis Python, Django generate SQL otomatis
class Produk(models.Model):
    nama = models.CharField(max_length=200)
    harga_jual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    aktif = models.BooleanField(default=True)
```

**ORM (Object-Relational Mapping)** = teknik mengubah class Python menjadi tabel database. Django ORM otomatis:
- Generate SQL yang tepat untuk database yang digunakan
- Menyediakan validasi tipe data
- Mencegah SQL injection
- Mendukung relasi antar tabel

---

## B. Anatomi Model — Baris per Baris

### Model Kategori (Paling Sederhana):

```python
# File: apps/produk/models.py

from django.db import models
# ↑ Import modul 'models' dari package 'django.db'
# 'django.db' = Django Database module
# 'models' berisi semua class untuk definisi model:
#   - models.Model (class dasar semua model)
#   - models.CharField, models.IntegerField, dll (tipe field)
#   - models.ForeignKey (relasi antar tabel)
# Dari mana? Otomatis terinstall saat install Django

from django.contrib.auth.models import User
# ↑ Import model User BAWAAN Django
# User sudah punya: id, username, email, password, first_name, last_name,
#                   is_active, is_staff, is_superuser, date_joined
# Kita TIDAK perlu membuat model User sendiri — Django sudah sediakan
# Dari mana? Package django.contrib.auth (sudah di INSTALLED_APPS)


class Kategori(models.Model):
    # ↑ class Kategori = nama model (akan menjadi nama tabel: produk_kategori)
    # (models.Model) = Kategori mewarisi (inherit) dari class Model
    #   → Artinya Kategori otomatis punya id, save(), delete(), objects, dll
    #   → Ini konsep OOP: Inheritance (pewarisan)
    
    nama = models.CharField(max_length=100, verbose_name="Nama Kategori")
    # ↑ Field 'nama' bertipe CharField
    #   CharField = karakter/teks pendek → menjadi kolom VARCHAR di database
    #   max_length=100 → maksimal 100 karakter (WAJIB untuk CharField)
    #   verbose_name="Nama Kategori" → label yang ditampilkan di form/admin
    #
    # Di database menjadi: nama VARCHAR(100) NOT NULL
    # Contoh data: "Makanan", "Minuman", "Elektronik"
    
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    # ↑ Field 'deskripsi' bertipe TextField
    #   TextField = teks panjang tanpa batas → menjadi kolom TEXT di database
    #   blank=True → boleh KOSONG di FORM (user tidak wajib mengisi)
    #   null=True → boleh NULL di DATABASE (kolom bisa berisi NULL)
    #
    # PENTING: blank vs null
    #   blank=True → validasi form: "field ini opsional, boleh kosong"
    #   null=True → database: "kolom ini boleh berisi NULL"
    #   Biasanya keduanya diset bersamaan untuk field opsional
    #
    # Di database menjadi: deskripsi TEXT NULL
    
    dibuat_oleh = models.ForeignKey(
        User,                           # → Relasi ke tabel auth_user
        on_delete=models.SET_NULL,      # → Jika user dihapus: set NULL (jangan hapus kategori)
        null=True,                      # → Boleh NULL (kategori bisa tanpa pembuat)
        related_name='kategori_dibuat'  # → Akses balik: user.kategori_dibuat.all()
    )
    # ↑ ForeignKey = relasi Many-to-One
    #   "Banyak kategori bisa dibuat oleh satu user"
    #   Di database: kolom dibuat_oleh_id INTEGER REFERENCES auth_user(id)
    #
    #   on_delete = apa yang terjadi jika User (parent) DIHAPUS?
    #     CASCADE   → ikut terhapus (produk dihapus → stok terhapus)
    #     SET_NULL  → diset NULL (user dihapus → kategori tetap ada)
    #     PROTECT   → TIDAK BISA hapus (satuan tidak bisa dihapus jika masih dipakai)
    #     SET_DEFAULT → diset ke nilai default
    #
    #   related_name = nama untuk akses BALIK dari User ke Kategori
    #     user.kategori_dibuat.all()  → semua kategori yang dibuat user ini
    #     Tanpa related_name: user.kategori_set.all() (nama default)
    
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    # ↑ DateTimeField = tanggal + waktu → kolom DATETIME di database
    #   auto_now_add=True → otomatis diisi SAAT PERTAMA KALI objek dibuat
    #   Setelah itu TIDAK berubah — jadi ini menandakan "tanggal pembuatan"
    #
    # Contoh output: 2026-02-21 10:30:45.123456
    
    diupdate_pada = models.DateTimeField(auto_now=True)
    # ↑ auto_now=True → otomatis diisi SETIAP KALI objek disimpan (save())
    #   Ini menandakan "terakhir diupdate"
    #   Berbeda dengan auto_now_add yang hanya sekali saat create
    
    class Meta:
        """Konfigurasi metadata model untuk Django."""
        verbose_name = "Kategori"          # Nama tampilan singular
        verbose_name_plural = "Kategori"   # Nama tampilan plural (di admin)
        ordering = ['nama']                # Urutan default: A-Z berdasarkan nama
        # ordering berlaku otomatis saat Kategori.objects.all()
        # ['nama'] = ascending (A-Z)
        # ['-nama'] = descending (Z-A)
        # ['-dibuat_pada', 'nama'] = terbaru dulu, lalu A-Z
    
    def __str__(self):
        """
        Representasi string — dipanggil saat print(kategori) atau di dropdown.
        Contoh output: "Makanan"
        """
        return self.nama
```

**Tabel database yang dihasilkan:**
```sql
-- Django otomatis membuat SQL ini saat migrate:
CREATE TABLE "produk_kategori" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nama" varchar(100) NOT NULL,
    "deskripsi" text NULL,
    "dibuat_pada" datetime NOT NULL,
    "diupdate_pada" datetime NOT NULL,
    "dibuat_oleh_id" integer NULL REFERENCES "auth_user" ("id")
);
```

**Contoh data di database:**
```
┌────┬─────────────┬──────────────────┬─────────────────────┬──────────────┐
│ id │ nama        │ deskripsi        │ dibuat_pada         │ dibuat_oleh_id│
├────┼─────────────┼──────────────────┼─────────────────────┼──────────────┤
│ 1  │ Makanan     │ Produk makanan   │ 2026-02-01 10:00:00 │ 1            │
│ 2  │ Minuman     │ NULL             │ 2026-02-01 10:05:00 │ 1            │
│ 3  │ Elektronik  │ Barang elektronik│ 2026-02-02 14:30:00 │ 2            │
└────┴─────────────┴──────────────────┴─────────────────────┴──────────────┘
```

---

## C. Semua Jenis Field — dengan Contoh Nyata

### Field Teks

```python
# CharField — Teks pendek (WAJIB ada max_length)
nama = models.CharField(max_length=200)
# Database: VARCHAR(200) NOT NULL
# Kapan pakai: Nama produk, nama user, SKU, barcode
# Contoh data: "Beras Premium 5kg", "PRD-00001"

# TextField — Teks panjang (TANPA max_length)
deskripsi = models.TextField(blank=True, null=True)
# Database: TEXT NULL
# Kapan pakai: Deskripsi, keterangan, catatan panjang
# Contoh data: "Beras premium dari Cianjur, dikemas 5kg..."

# EmailField — Email (CharField + validasi format email)
email = models.EmailField(max_length=100, unique=True)
# Database: VARCHAR(100) NOT NULL UNIQUE
# Validasi otomatis: harus format xxx@yyy.zzz
# Contoh data: "admin@serptech.com"
```

### Field Angka

```python
# DecimalField — Angka desimal PRESISI (untuk uang!)
harga_jual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
# Database: DECIMAL(15,2)
# max_digits=15 → total digit maksimal (termasuk di belakang koma)
# decimal_places=2 → 2 digit di belakang koma
# Range: 0.00 sampai 9,999,999,999,999.99
# Contoh data: 15000.00, 1250000.50
# KENAPA DecimalField bukan FloatField untuk harga?
#   FloatField menggunakan floating-point (binary) → 0.1 + 0.2 = 0.30000000000000004
#   DecimalField menggunakan fixed-point → 0.1 + 0.2 = 0.3 (PRESISI)
#   Untuk uang, SELALU gunakan DecimalField!

# IntegerField — Bilangan bulat
jumlah_karyawan = models.IntegerField(default=0)
# Database: INTEGER
# Contoh data: 1, 42, 1000
```

### Field Tanggal & Waktu

```python
# DateTimeField — Tanggal + waktu
dibuat_pada = models.DateTimeField(auto_now_add=True)
# auto_now_add=True → otomatis saat CREATE (hanya sekali)
# Contoh output: 2026-02-21 17:30:45.123456

diupdate_pada = models.DateTimeField(auto_now=True)
# auto_now=True → otomatis setiap kali SAVE (update terakhir)

tanggal_lahir = models.DateField(blank=True, null=True)
# DateField — hanya tanggal (tanpa waktu)
# Contoh output: 2000-01-15
```

### Field Boolean & File

```python
# BooleanField — True / False
aktif = models.BooleanField(default=True)
# Database: BOOLEAN (0 atau 1)
# default=True → jika tidak diisi, otomatis True
# Di form: checkbox ☑

# ImageField — Upload gambar
gambar = models.ImageField(upload_to='produk/', blank=True, null=True)
# upload_to='produk/' → disimpan di folder media/produk/
# Contoh path: media/produk/beras_premium.jpg
# Membutuhkan library Pillow (pip install Pillow)
# Di template: <img src="{{ produk.gambar.url }}">
```

---

## D. Relasi Antar Model — Penjelasan Sangat Detail

### 1. ForeignKey (Many-to-One) — Relasi Paling Umum

**Konsep:** Banyak produk bisa punya SATU kategori yang sama.

```python
class Produk(models.Model):
    kategori = models.ForeignKey(
        Kategori,                    # → Tabel yang direferensikan
        on_delete=models.SET_NULL,   # → Apa terjadi jika Kategori dihapus
        null=True,                   # → Boleh tanpa kategori
        related_name='produk',       # → Akses balik dari Kategori
        verbose_name="Kategori"      # → Label di form
    )
```

**Di database:**
```
Tabel: produk_produk
┌────┬──────────┬──────────────┐
│ id │ nama     │ kategori_id  │  ← FK ke produk_kategori.id
├────┼──────────┼──────────────┤
│ 1  │ Beras    │ 1            │  ← Kategori "Makanan" (id=1)
│ 2  │ Indomie  │ 1            │  ← Kategori "Makanan" (id=1)
│ 3  │ Aqua     │ 2            │  ← Kategori "Minuman" (id=2)
│ 4  │ Laptop   │ NULL         │  ← Tanpa kategori
└────┴──────────┴──────────────┘
```

**Cara akses di Python:**
```python
# Dari Produk → Kategori (MAJU / forward)
produk = Produk.objects.get(pk=1)
print(produk.kategori)        # Output: Makanan
print(produk.kategori.nama)   # Output: Makanan
print(produk.kategori.id)     # Output: 1

# Dari Kategori → Produk (BALIK / reverse) menggunakan related_name
kategori = Kategori.objects.get(pk=1)
print(kategori.produk.all())  # Output: <QuerySet [Beras, Indomie]>
print(kategori.produk.count()) # Output: 2
# ↑ 'produk' berasal dari related_name='produk' di ForeignKey
```

### 2. OneToOneField — Satu ke Satu

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
```

**Konsep:** Setiap User punya TEPAT 1 Profile, dan sebaliknya.

**Cara akses:**
```python
user = User.objects.get(username='admin')
print(user.profile)        # Output: admin (Profile object)
print(user.profile.role)   # Output: SUPERUSER
print(user.profile.phone)  # Output: 081234567890
```

---

## E. Property dan Method Spesial

### Property `stok_total` — Hitung Total Stok di Semua Gudang

```python
@property
def stok_total(self):
    return self.stok_set.aggregate(models.Sum('jumlah'))['jumlah__sum'] or 0
```

**Penjelasan setiap bagian:**
- `@property` → Decorator Python yang membuat method bisa diakses seperti attribute
  - Tanpa `@property`: `produk.stok_total()` → pakai tanda kurung
  - Dengan `@property`: `produk.stok_total` → tanpa tanda kurung (lebih natural)
- `self.stok_set` → Semua record Stok yang terkait produk ini (reverse relation)
- `.aggregate(models.Sum('jumlah'))` → SQL: `SELECT SUM(jumlah) FROM stok WHERE produk_id=self.id`
- `['jumlah__sum']` → Ambil hasil aggregate (nama key otomatis: field__function)
- `or 0` → Jika hasilnya None (tidak ada stok), return 0

**Contoh:**
```python
produk = Produk.objects.get(nama="Beras")
# Stok di database:
# Gudang Jakarta: 100
# Gudang Surabaya: 50
# Gudang Bandung: 30

print(produk.stok_total)  # Output: 180
# SQL yang dijalankan: SELECT SUM(jumlah) FROM produk_stok WHERE produk_id=1
```

### Method `generate_sku()` — Auto-Generate SKU

```python
def generate_sku(self):
    prefix = "PRD"                                       # Default jika tanpa kategori
    if self.kategori:
        prefix = self.kategori.nama[:3].upper()           # 3 huruf pertama, UPPERCASE
    
    last_product = Produk.objects.filter(
        sku__startswith=prefix                             # Filter: SKU dimulai dengan prefix
    ).order_by('-sku').first()                             # Urutkan descending, ambil pertama
    
    if last_product:
        last_number = int(last_product.sku.split('-')[-1]) # Parse nomor dari SKU terakhir
        new_number = last_number + 1                       # Increment
    else:
        new_number = 1                                     # Belum ada → mulai dari 1
    
    return f"{prefix}-{new_number:05d}"                   # Format: MAK-00001
```

**Langkah demi langkah:**
```
Kategori = "Makanan"
1. prefix = "Makanan"[:3] = "Mak" → .upper() = "MAK"
2. Query: Produk WHERE sku LIKE 'MAK%' ORDER BY sku DESC LIMIT 1
3. Hasil: last_product.sku = "MAK-00005"
4. split('-') = ["MAK", "00005"] → [-1] = "00005" → int = 5
5. new_number = 5 + 1 = 6
6. f"MAK-{6:05d}" = "MAK-00006"
```

---

## F. Operasi Database (ORM) — Contoh Lengkap dengan Output

### CREATE — Membuat Data Baru
```python
# Cara 1: create() — langsung simpan ke database
kategori = Kategori.objects.create(
    nama="Elektronik",
    deskripsi="Barang elektronik"
)
print(kategori)     # Output: Elektronik
print(kategori.id)  # Output: 4 (auto-generated)
print(kategori.dibuat_pada)  # Output: 2026-02-21 17:30:00

# Cara 2: instantiate lalu save()
produk = Produk(nama="Laptop", harga_jual=15000000)
produk.save()  # Baru disimpan ke database saat save() dipanggil
```

### READ — Membaca Data
```python
# Semua data
semua = Produk.objects.all()
# Output: <QuerySet [<Produk: PRD-00001 - Beras>, <Produk: PRD-00002 - Aqua>]>

# Filter
makanan = Produk.objects.filter(kategori__nama="Makanan")
# Output: <QuerySet [<Produk: MAK-00001 - Beras>, <Produk: MAK-00002 - Indomie>]>
# ↑ kategori__nama → "ikuti relasi FK ke Kategori, lalu filter field nama"
#   Double underscore (__) = "traverse relation"

# Satu data spesifik
produk = Produk.objects.get(pk=1)  # pk = primary key
# Output: <Produk: PRD-00001 - Beras>
# ⚠ get() akan ERROR jika data tidak ditemukan (DoesNotExist) atau lebih dari 1

# Filter lanjutan
mahal = Produk.objects.filter(harga_jual__gte=100000)  # gte = greater than or equal
murah = Produk.objects.filter(harga_jual__lt=10000)     # lt = less than
cari = Produk.objects.filter(nama__icontains="beras")   # icontains = case-insensitive LIKE
```

### UPDATE — Mengubah Data
```python
produk = Produk.objects.get(pk=1)
produk.harga_jual = 20000
produk.save()
# SQL: UPDATE produk_produk SET harga_jual=20000 WHERE id=1

# Bulk update (tanpa load object — lebih cepat)
Produk.objects.filter(kategori__nama="Makanan").update(aktif=False)
# SQL: UPDATE produk_produk SET aktif=0 WHERE kategori_id IN (SELECT id FROM...)
```

### DELETE — Menghapus Data
```python
produk = Produk.objects.get(pk=1)
produk.delete()
# SQL: DELETE FROM produk_produk WHERE id=1
# Output: (1, {'produk.Produk': 1})
# ↑ Artinya: 1 objek dihapus, yaitu 1 Produk
```

---

## G. Diagram Relasi Lengkap

```
────────────────────── MODUL PRODUK ──────────────────────
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Kategori │◄─FK─│  Produk  │─FK─►│  Satuan  │
│          │     │          │     │          │
│ id       │     │ id       │     │ id       │
│ nama     │     │ sku      │     │ nama     │
│ deskripsi│     │ nama     │     │ singkatan│
└──────────┘     │ harga_beli│     └──────────┘
                 │ harga_jual│
                 │ gambar   │     ┌──────────┐
                 │ aktif    │─FK─►│  Gudang  │
                 └────┬─────┘     │          │
                      │           │ kode     │
                      │           │ nama     │
                      │           │ pajak_%  │
              ┌───────▼───────┐   └──────────┘
              │ Stok (pivot)  │←──FK──┘
              │               │
              │ produk_id(FK) │
              │ gudang_id(FK) │
              │ jumlah        │
              │               │
              │ unique_together│
              │ (produk,gudang)│
              └───────────────┘

────────────── MODUL PEMBELIAN & PENJUALAN ──────────────
┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│ Supplier │◄─FK─│PurchaseOrder │──┤──│PurchaseOrderItem │
│          │     │              │  │  │                  │
│ nama     │     │ nomor        │  │  │ produk_id (FK)   │
│ telepon  │     │ tanggal      │  │  │ jumlah           │
│ alamat   │     │ status       │  │  │ harga            │
└──────────┘     │ total        │  │  └──────────────────┘
                 └──────────────┘  │
                                   │→ Stok bertambah saat status "Received"

┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│ Customer │◄─FK─│  SalesOrder  │──┤──│  SalesOrderItem  │
│          │     │              │  │  │                  │
│ nama     │     │ nomor        │  │  │ produk_id (FK)   │
│ telepon  │     │ tanggal      │  │  │ jumlah           │
│ alamat   │     │ status       │  │  │ harga            │
└──────────┘     └──────────────┘  │  └──────────────────┘
                                   │→ Stok berkurang saat dikonfirmasi
```

---

## H. ERD (Entity Relationship Diagram) Lengkap — Seluruh 35 Model

### Kenapa ERD Penting?

**ERD (Entity Relationship Diagram)** = peta visual yang menunjukkan SEMUA tabel database dan bagaimana mereka saling terhubung.

```
Tanpa ERD:                              Dengan ERD:
┌──────────────┐                       ┌──────────────────────────┐
│ "Tabel apa   │                       │ Saya bisa LIHAT:         │
│  saja yang   │ ← Bingung!           │ - Semua 35 tabel         │
│  ada?"       │                       │ - Relasi FK antar tabel  │
│ "Ini konek   │                       │ - Data apa mengalir      │
│  ke mana?"   │                       │   ke mana                │
└──────────────┘                       └──────────────────────────┘
```

### Daftar Lengkap 35 Model (Dikelompokkan per Domain):

```
╔══════════════════════════════════════════════════════════════════════╗
║                    SELURUH MODEL SISTEM ERP                         ║
║                    Total: 38 Model (9 Domain)                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🔐 AUTH & USER (3 model)                                           ║
║  ├── User (bawaan Django)  ← auth_user                              ║
║  ├── Profile               ← auth_profile (OneToOne → User)        ║
║  └── RolePermission        ← core_rolepermission                    ║
║                                                                      ║
║  📦 PRODUK & INVENTORY (7 model)                                    ║
║  ├── Kategori              ← produk_kategori                        ║
║  ├── Satuan                ← produk_satuan                          ║
║  ├── Produk                ← produk_produk                          ║
║  ├── Gudang                ← produk_gudang                          ║
║  ├── Stok                  ← produk_stok (pivot: produk × gudang)  ║
║  ├── TransferStok          ← inventory_transferstok                 ║
║  ├── TransferStokItem      ← inventory_transferstokitem             ║
║  └── AdjustmentStok        ← inventory_adjustmentstok               ║
║                                                                      ║
║  🛒 PEMBELIAN (3 model)                                             ║
║  ├── Supplier              ← pembelian_supplier                     ║
║  ├── PurchaseOrder         ← pembelian_purchaseorder                ║
║  └── PurchaseOrderItem     ← pembelian_purchaseorderitem            ║
║                                                                      ║
║  💰 PENJUALAN (3 model)                                             ║
║  ├── Customer              ← penjualan_customer                     ║
║  ├── SalesOrder            ← penjualan_salesorder                   ║
║  └── SalesOrderItem        ← penjualan_salesorderitem               ║
║                                                                      ║
║  🏪 POS / KASIR (3 model)                                          ║
║  ├── MetodePembayaran      ← pos_metodepembayaran                   ║
║  ├── POSTransaction        ← pos_postransaction                     ║
║  └── POSTransactionItem    ← pos_postransactionitem                 ║
║                                                                      ║
║  💸 BIAYA (2 model)                                                 ║
║  ├── KategoriBiaya         ← biaya_kategoribiaya                    ║
║  └── TransaksiBiaya        ← biaya_transaksibiaya                   ║
║                                                                      ║
║  👥 HR / SDM (6 model)                                              ║
║  ├── Departemen            ← hr_departemen                          ║
║  ├── Jabatan               ← hr_jabatan                             ║
║  ├── Karyawan              ← hr_karyawan                            ║
║  ├── FotoWajah             ← hr_fotowajah                           ║
║  ├── PengaturanAbsensi     ← hr_pengaturanabsensi                   ║
║  ├── Absensi               ← hr_absensi                             ║
║  └── Penggajian            ← hr_penggajian                          ║
║                                                                      ║
║  ⚙️ SISTEM & AUTOMATION (5 model)                                   ║
║  ├── PengaturanPerusahaan  ← pengaturan_pengaturanperusahaan        ║
║  ├── TemplateCetak         ← pengaturan_templatecetak               ║
║  ├── BackupHistory         ← pengaturan_backuphistory               ║
║  ├── PengaturanTelegram    ← automation_pengaturantelegram          ║
║  ├── TemplatePesan         ← automation_templatepesan               ║
║  └── LogNotifikasi         ← automation_lognotifikasi               ║
║                                                                      ║
║  📊 AUDIT (1 model)                                                 ║
║  └── UserActivity          ← activity_log_useractivity              ║
║                                                                      ║
║  🛡️ FRAUD DETECTION (3 model)                                      ║
║  ├── FraudRule             ← fraud_detection_fraudrule (Singleton)  ║
║  ├── FraudAlert            ← fraud_detection_fraudalert             ║
║  └── CashReconciliation   ← fraud_detection_cashreconciliation     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### ERD Visual — Relasi Antar Semua Model:

```
═══════════════════════════════════════════════════════════════════════
                         AUTH & USER DOMAIN
═══════════════════════════════════════════════════════════════════════

┌─────────────────┐   OneToOne   ┌─────────────────────┐
│   User          │◄════════════►│  Profile             │
│   (Django)      │              │                     │
│   ─────────     │              │  ─────────          │
│   id            │              │  id                 │
│   username      │              │  user_id (FK→User)  │
│   email         │              │  role (VARCHAR)     │
│   password (hash)│             │  phone              │
│   first_name    │              │  avatar             │
│   last_name     │              │  email_token        │
│   is_active     │              │  forget_pwd_token   │
│   is_staff      │              │  forget_pwd_expiry  │
│   date_joined   │              └─────────────────────┘
└────────┬────────┘
         │  role dipakai sebagai key di:
         ▼
┌─────────────────────────┐
│  RolePermission          │
│  ─────────               │
│  id                      │
│  role (VARCHAR)          │ ← Cocokkan dengan Profile.role
│  module (VARCHAR)         │ ← 'produk', 'penjualan', dll
│  sub_module (VARCHAR)     │ ← 'kategori', 'sales_order', dll
│  can_view (BOOLEAN)       │
│  can_create (BOOLEAN)     │
│  can_edit (BOOLEAN)       │
│  can_delete (BOOLEAN)     │
│                           │
│  unique_together:         │
│  (role, module, sub_module)│
└───────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                   PRODUK & INVENTORY DOMAIN
═══════════════════════════════════════════════════════════════════════

┌────────────┐       ┌──────────────────┐       ┌───────────┐
│  Kategori  │◄──FK──│     Produk       │──FK──►│  Satuan   │
│            │       │                  │       │           │
│ id         │       │ id               │       │ id        │
│ nama       │       │ sku (auto)       │       │ nama      │
│ deskripsi  │       │ nama             │       │ singkatan │
└────────────┘       │ harga_beli       │       └───────────┘
                     │ harga_jual       │
                     │ gambar           │       ┌───────────┐
                     │ barcode          │       │  Gudang   │
                     │ aktif            │       │           │
                     │ kategori_id (FK) │       │ id        │
                     │ satuan_id (FK)   │       │ kode      │
                     │ dibuat_oleh (FK) │       │ nama      │
                     └──────┬───────────┘       │ alamat    │
                            │                   │ pajak_%   │
                            │                   └─────┬─────┘
                      ┌─────▼─────┐                   │
                      │   Stok    │◄──────FK──────────┘
                      │  (PIVOT)  │
                      │           │ ← Penghubung Produk × Gudang
                      │ produk_id │   Setiap record = stok produk X
                      │ gudang_id │   di gudang Y
                      │ jumlah    │
                      │           │
                      │ UNIQUE:   │
                      │(produk,   │
                      │ gudang)   │
                      └───────────┘
                            │ stok berubah karena:
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   TransferStok      PurchaseOrder        SalesOrder
   (pindah gudang)   (beli → stok naik)   (jual → stok turun)


═══════════ TRANSFER STOK (SUBCRUD) ═══════════

┌─────────────────────┐          ┌──────────────────────┐
│   TransferStok      │──HasMany─│  TransferStokItem    │
│   (PARENT)          │          │  (CHILD)             │
│   ─────────         │          │  ─────────           │
│   id                │          │  id                  │
│   nomor             │          │  transfer_id (FK)    │
│   gudang_asal (FK)  │          │  produk_id (FK)      │
│   gudang_tujuan(FK) │          │  jumlah              │
│   catatan           │          └──────────────────────┘
│   status            │
│   dibuat_oleh (FK)  │
└─────────────────────┘

┌─────────────────────┐
│  AdjustmentStok     │ ← Standalone (bukan SUBCRUD)
│  ─────────          │   Koreksi stok manual
│  id                 │
│  produk_id (FK)     │
│  gudang_id (FK)     │
│  jumlah_sebelum     │
│  jumlah_sesudah     │
│  alasan             │
│  dibuat_oleh (FK)   │
└─────────────────────┘


═══════════════════════════════════════════════════════════════════════
                     PEMBELIAN DOMAIN (SUBCRUD)
═══════════════════════════════════════════════════════════════════════

┌────────────┐       ┌──────────────────┐         ┌────────────────────┐
│  Supplier  │◄──FK──│  PurchaseOrder   │──HasMany─│ PurchaseOrderItem │
│            │       │  (PARENT)        │          │ (CHILD)           │
│ id         │       │  ─────────       │          │ ─────────         │
│ nama       │       │  id              │          │ id                │
│ email      │       │  nomor           │          │ po_id (FK)        │
│ telepon    │       │  tanggal         │          │ produk_id (FK)    │
│ alamat     │       │  supplier_id(FK) │          │ jumlah            │
│ kontak     │       │  status          │          │ harga             │
└────────────┘       │  subtotal        │          │ diskon            │
                     │  diskon          │          │ subtotal          │
                     │  pajak           │          └────────────────────┘
                     │  total_harga     │
                     │  catatan         │
                     │  gudang_id (FK)  │ ← Stok masuk ke gudang ini
                     │  dibuat_oleh(FK) │
                     └──────────────────┘
                         │
                         │  Status flow:
                         │  draft → confirmed → received → cancelled
                         │  Saat "received" → Stok di gudang BERTAMBAH


═══════════════════════════════════════════════════════════════════════
                     PENJUALAN DOMAIN (SUBCRUD)
═══════════════════════════════════════════════════════════════════════

┌────────────┐       ┌──────────────────┐         ┌────────────────────┐
│  Customer  │◄──FK──│   SalesOrder     │──HasMany─│  SalesOrderItem   │
│            │       │   (PARENT)       │          │  (CHILD)          │
│ id         │       │  ─────────       │          │  ─────────        │
│ nama       │       │  id              │          │  id               │
│ email      │       │  nomor           │          │  so_id (FK)       │
│ telepon    │       │  tanggal         │          │  produk_id (FK)   │
│ alamat     │       │  customer_id(FK) │          │  jumlah           │
│ kontak     │       │  status          │          │  harga            │
└────────────┘       │  subtotal        │          │  diskon           │
                     │  diskon          │          │  subtotal         │
                     │  pajak           │          └────────────────────┘
                     │  total_harga     │
                     │  catatan         │
                     │  gudang_id (FK)  │ ← Stok keluar dari gudang ini
                     │  dibuat_oleh(FK) │
                     └──────────────────┘
                         │
                         │  Status flow:
                         │  draft → confirmed → delivered → cancelled
                         │  Saat "confirmed" → Stok di gudang BERKURANG


═══════════════════════════════════════════════════════════════════════
                     POS / KASIR DOMAIN (SUBCRUD)
═══════════════════════════════════════════════════════════════════════

┌────────────────────┐   ┌─────────────────────┐     ┌────────────────────────┐
│ MetodePembayaran   │   │  POSTransaction     │─Has─│  POSTransactionItem    │
│                    │   │  (PARENT)           │Many │  (CHILD)               │
│ id                 │   │  ─────────          │     │  ─────────             │
│ nama               │◄──│  id                 │     │  id                    │
│ aktif              │FK │  nomor_transaksi    │     │  transaksi_id (FK)     │
└────────────────────┘   │  kasir (FK→User)    │     │  produk_id (FK)        │
                         │  gudang_id (FK)     │     │  jumlah                │
                         │  nama_customer      │     │  harga                 │
                         │  metode_bayar (FK)  │     │  subtotal              │
                         │  subtotal           │     └────────────────────────┘
                         │  diskon             │
                         │  pajak              │
                         │  total_harga        │     Alur:
                         │  bayar              │     1. Kasir pilih produk dari grid
                         │  kembalian          │     2. Tambah ke keranjang
                         │  catatan            │     3. Bayar → create transaction
                         │  dibuat_pada        │     4. Stok OTOMATIS berkurang
                         └─────────────────────┘     5. Kirim notifikasi Telegram


═══════════════════════════════════════════════════════════════════════
                     BIAYA DOMAIN (CRUD)
═══════════════════════════════════════════════════════════════════════

┌────────────────┐       ┌──────────────────────┐
│ KategoriBiaya  │◄──FK──│   TransaksiBiaya     │
│                │       │                      │
│ id             │       │ id                   │
│ nama           │       │ tanggal              │
│ deskripsi      │       │ kategori_id (FK)     │
│ dibuat_oleh    │       │ jumlah               │ ← nominal biaya
│                │       │ keterangan           │
└────────────────┘       │ bukti (ImageField)   │ ← foto kuitansi
                         │ dibuat_oleh (FK)     │
                         └──────────────────────┘
                         Contoh: Bayar listrik Rp 500.000


═══════════════════════════════════════════════════════════════════════
                     HR / SDM DOMAIN
═══════════════════════════════════════════════════════════════════════

┌──────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Departemen  │◄─FK──│   Jabatan    │◄─FK──│    Karyawan      │
│              │      │              │      │                  │
│ id           │      │ id           │      │ id               │
│ nama         │      │ nama         │      │ user_id (FK)     │
│ deskripsi    │      │ departemen_id│      │ nip              │
│ dibuat_oleh  │      │ deskripsi    │      │ nama_lengkap     │
└──────────────┘      │ gaji_pokok   │      │ jabatan_id (FK)  │
                      └──────────────┘      │ tanggal_lahir    │
                                            │ jenis_kelamin    │
                                            │ alamat           │
                                            │ telepon          │
                                            │ email            │
                                            │ foto             │
                                            │ tanggal_masuk    │
                                            │ status           │
                                            │ dibuat_oleh      │
                                            └──────┬───────────┘
                            ┌──────────────────────┼──────────────┐
                            ▼                      ▼              ▼
                    ┌──────────────┐      ┌──────────────┐  ┌──────────┐
                    │  FotoWajah   │      │   Absensi    │  │Penggajian│
                    │              │      │              │  │          │
                    │ karyawan(FK) │      │ karyawan(FK) │  │karyawan  │
                    │ foto         │      │ tanggal      │  │  _id(FK) │
                    │ deskripsi    │      │ jam_masuk    │  │bulan     │
                    └──────────────┘      │ jam_keluar   │  │tahun     │
                    Untuk face           │ status       │  │gaji_pokok│
                    recognition          │ lokasi_masuk │  │tunjangan │
                                         │ foto_masuk   │  │potongan  │
                                         │ catatan      │  │total     │
                                         └──────────────┘  └──────────┘

                    ┌──────────────────────┐
                    │  PengaturanAbsensi   │ ← Singleton (1 record)
                    │                      │
                    │ jam_masuk_default     │ ← 08:00
                    │ jam_keluar_default    │ ← 17:00
                    │ toleransi_menit      │ ← 15 menit
                    │ radius_lokasi        │ ← 100 meter
                    │ latitude             │ ← Koordinat kantor
                    │ longitude            │
                    │ wajib_foto           │ ← Apakah perlu selfie?
                    │ gunakan_face_recog   │ ← Apakah pakai face recognition?
                    └──────────────────────┘


═══════════════════════════════════════════════════════════════════════
                     SISTEM & AUTOMATION DOMAIN
═══════════════════════════════════════════════════════════════════════

┌──────────────────────┐
│ PengaturanPerusahaan │ ← Singleton (1 record)
│                      │
│ nama_perusahaan      │   Dipakai di:
│ tagline              │   - Header semua halaman
│ alamat               │   - Export PDF (kop surat)
│ telepon              │   - Login page (branding)
│ email                │   - Invoice / faktur
│ website              │   - Footer
│ logo (ImageField)    │
│ favicon (ImageField) │
│ nama_sistem          │ ← Judul di browser tab
└──────────────────────┘

┌──────────────────────┐
│   TemplateCetak      │ ← Template untuk Invoice/Faktur
│                      │
│ nama                 │
│ jenis                │ ← 'invoice', 'purchase_order', dll
│ konten (TextField)   │ ← HTML template
│ aktif                │
└──────────────────────┘

┌──────────────────────┐
│   BackupHistory      │ ← Riwayat backup database
│                      │
│ tanggal              │
│ file_path            │
│ ukuran               │
│ status               │
│ dibuat_oleh (FK)     │
└──────────────────────┘

────────── TELEGRAM NOTIFICATION ──────────

┌──────────────────────┐     ┌──────────────────────┐
│ PengaturanTelegram   │     │   TemplatePesan      │
│ (Singleton)          │     │                      │
│                      │     │ id                   │
│ bot_token            │     │ nama                 │
│ chat_id              │     │ jenis                │ ← 'sales_order', 'pos', dll
│ aktif                │     │ template_pesan       │ ← Template dengan {{variable}}
└──────────────────────┘     │ aktif                │
         │                   └──────────────────────┘
         │ dipakai oleh                │
         ▼                             ▼
┌──────────────────────────────────────────────┐
│             LogNotifikasi                     │
│                                               │
│ id                                            │
│ jenis          ← 'sales_order', 'pos'        │
│ nomor_referensi ← 'SO-20260001'              │
│ pesan          ← Pesan yang dikirim           │
│ status         ← 'sukses' / 'gagal'          │
│ error_message  ← Pesan error jika gagal       │
│ dibuat_pada    ← Timestamp                    │
└───────────────────────────────────────────────┘

────────── AUDIT TRAIL ──────────

┌────────────────────────────────────────────────┐
│              UserActivity                       │
│                                                 │
│ id                                              │
│ user_id (FK → User)    ← Siapa yang melakukan  │
│ action                 ← 'create','update',     │
│                           'delete','login', dll │
│ model_name             ← 'Produk', 'SalesOrder' │
│ object_id              ← ID record: '42'       │
│ object_repr            ← 'Laptop ASUS'         │
│ description            ← 'Menambah produk baru' │
│ changes (JSON)         ← {"harga": {"old":      │
│                            10000,"new":15000}}  │
│ source_type            ← 'purchase','sales'     │
│ quantity_before        ← 100                    │
│ quantity_after         ← 95                     │
│ quantity_change        ← -5                     │
│ gudang_name            ← 'Gudang Jakarta'       │
│ ip_address             ← '192.168.1.1'          │
│ user_agent             ← 'Mozilla/5.0...'       │
│ timestamp              ← auto                   │
└─────────────────────────────────────────────────┘

────────── FRAUD DETECTION ──────────

┌──────────────────────┐
│     FraudRule        │ ← Singleton (1 record)
│     (Pengaturan)     │
│                      │
│ block_delete_paid    │ ← Blokir hapus data lunas (on/off)
│ block_negative_stock │ ← Blokir stok minus (on/off)
│ max_discount_percent │ ← Batas diskon maksimal (%)
│ jam_operasional_mulai│ ← Jam buka toko (default 07:00)
│ jam_operasional_slsai│ ← Jam tutup toko (default 22:00)
│ updated_by (FK→User) │
└──────────────────────┘
           │ dibaca oleh signals.py
           ▼
┌──────────────────────────────────────┐
│           FraudAlert                  │
│                                       │
│ id                                    │
│ jenis          ← 'hapus_lunas',      │
│                   'diskon_besar', dll │
│ severity       ← 'low'...'critical'  │
│ status         ← 'pending'...        │
│                   'rejected'          │
│ deskripsi      ← Penjelasan anomali  │
│ user_terkait(FK) ← Pelaku            │
│ nominal        ← Nominal terkait     │
│ model_name     ← 'POSTransaction'    │
│ object_id      ← ID record asli      │
│ data_snapshot  ← JSON (evidence)     │
│ catatan_owner  ← Catatan reviewer    │
│ reviewed_by(FK)← Siapa yang review   │
│ activity(FK)   ← UserActivity terkait│
│ created_at     ← auto                │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│      CashReconciliation              │
│      (Blind Cash Closing)            │
│                                       │
│ id                                    │
│ kasir (FK→User)    ← Kasir shift     │
│ gudang (FK→Gudang) ← Cabang/outlet   │
│ shift_start        ← Jam mulai shift │
│ shift_end          ← Jam akhir shift │
│ expected_amount    ← Uang dari sistem│
│ actual_amount      ← Uang fisik laci │
│ discrepancy        ← actual-expected │
│ status             ← open/closed/    │
│                      reviewed         │
│ reviewed_by(FK)    ← Reviewer         │
│ catatan            ← Catatan kasir   │
└──────────────────────────────────────┘
```

### Tabel Ringkasan Relasi (FK) Antar Model:

| Dari (Child) | → Ke (Parent) | Tipe Relasi | on_delete | Penjelasan |
|---|---|---|---|---|
| Profile | → User | OneToOne | CASCADE | 1 user = 1 profile |
| RolePermission | — (standalone) | — | — | Dicocokkan via `role` string |
| Produk | → Kategori | FK | SET_NULL | Produk boleh tanpa kategori |
| Produk | → Satuan | FK | SET_NULL | Produk boleh tanpa satuan |
| Stok | → Produk | FK | CASCADE | Hapus produk = hapus stok |
| Stok | → Gudang | FK | CASCADE | Hapus gudang = hapus stok |
| TransferStok | → Gudang (asal) | FK | PROTECT | Tidak bisa hapus gudang aktif |
| TransferStok | → Gudang (tujuan) | FK | PROTECT | Tidak bisa hapus gudang aktif |
| TransferStokItem | → TransferStok | FK | CASCADE | Hapus parent = hapus child |
| TransferStokItem | → Produk | FK | CASCADE | — |
| PurchaseOrder | → Supplier | FK | SET_NULL | PO tetap ada jika supplier dihapus |
| PurchaseOrderItem | → PurchaseOrder | FK | CASCADE | Hapus PO = hapus semua item |
| PurchaseOrderItem | → Produk | FK | CASCADE | — |
| SalesOrder | → Customer | FK | SET_NULL | SO tetap ada jika customer dihapus |
| SalesOrderItem | → SalesOrder | FK | CASCADE | Hapus SO = hapus semua item |
| SalesOrderItem | → Produk | FK | CASCADE | — |
| POSTransaction | → User (kasir) | FK | SET_NULL | — |
| POSTransaction | → Gudang | FK | SET_NULL | — |
| POSTransaction | → MetodePembayaran | FK | SET_NULL | — |
| POSTransactionItem | → POSTransaction | FK | CASCADE | — |
| POSTransactionItem | → Produk | FK | CASCADE | — |
| TransaksiBiaya | → KategoriBiaya | FK | SET_NULL | — |
| Karyawan | → User | FK | SET_NULL | — |
| Karyawan | → Jabatan | FK | SET_NULL | — |
| Jabatan | → Departemen | FK | CASCADE | — |
| FotoWajah | → Karyawan | FK | CASCADE | — |
| Absensi | → Karyawan | FK | CASCADE | — |
| Penggajian | → Karyawan | FK | CASCADE | — |

### Alur Data Antar Domain (Big Picture):

```
┌──────────┐  beli dari   ┌──────────┐  stok masuk  ┌──────────┐
│ SUPPLIER │ ──────────── │ PURCHASE │ ───────────► │   STOK   │
│          │              │  ORDER   │              │ (Gudang) │
└──────────┘              └──────────┘              └─────┬────┘
                                                          │
                         ┌────────────────────────────────┤
                         │                                │
                         ▼                                ▼
                   ┌──────────┐  stok keluar     ┌──────────┐
                   │  SALES   │ ◄─────────────── │   POS    │
                   │  ORDER   │                  │ (Kasir)  │
                   └────┬─────┘                  └────┬─────┘
                        │                             │
                        ▼                             ▼
                   ┌──────────┐              ┌──────────────┐
                   │ CUSTOMER │              │ Walk-in      │
                   │ (B2B)    │              │ Customer     │
                   └──────────┘              └──────────────┘
                        │                             │
                        └──────────┬──────────────────┘
                                   ▼
                            ┌──────────────┐
                            │   LAPORAN    │  ← Aggregasi semua data
                            │  Keuangan   │     (Pendapatan - Pengeluaran = Laba)
                            │  Stok       │
                            │  Penjualan  │
                            └──────────────┘
```

---

## I. Panduan Migrasi Database — Dari Nol Hingga Production

### Apa itu Migrasi?

**Migrasi** = file Python yang merekam perubahan pada model database, seperti "version control untuk database".

```
Tanpa Migrasi (SQL manual):           Dengan Migrasi (Django):
┌─────────────────────────┐          ┌─────────────────────────┐
│ ALTER TABLE produk      │          │ # models.py             │
│ ADD COLUMN diskon       │          │ diskon = DecimalField() │
│ DECIMAL(5,2)            │          │                         │
│ DEFAULT 0;              │          │ $ makemigrations        │
│                         │          │ $ migrate               │
│ ← Harus tulis SQL      │          │ ← Django generate SQL   │
│   untuk setiap database │          │   otomatis!             │
└─────────────────────────┘          └─────────────────────────┘
```

### Perintah Migrasi yang Penting:

```bash
# ═══ Langkah 1: Buat file migrasi ═══
python manage.py makemigrations
# Apa yang terjadi:
# 1. Django scan semua models.py di INSTALLED_APPS
# 2. Bandingkan dengan file migrasi terakhir
# 3. Generate file baru: apps/produk/migrations/0002_produk_diskon.py
# 4. File ini BERISI instruksi Python untuk mengubah database
#
# Output:
# Migrations for 'produk':
#   apps/produk/migrations/0002_produk_diskon.py
#     - Add field diskon to produk

# ═══ Langkah 2: Jalankan migrasi ═══
python manage.py migrate
# Apa yang terjadi:
# 1. Django baca file migrasi yang BELUM dijalankan
# 2. Execute SQL: ALTER TABLE produk_produk ADD COLUMN diskon...
# 3. Catat di tabel django_migrations bahwa migrasi sudah jalan
#
# Output:
# Running migrations:
#   Applying produk.0002_produk_diskon... OK

# ═══ Cek status migrasi ═══
python manage.py showmigrations
# Output:
# produk
#  [X] 0001_initial        ← Sudah dijalankan
#  [X] 0002_produk_diskon  ← Sudah dijalankan
#  [ ] 0003_produk_barcode ← Belum dijalankan

# ═══ Lihat SQL yang akan dijalankan (tanpa execute) ═══
python manage.py sqlmigrate produk 0002
# Output:
# ALTER TABLE "produk_produk" ADD COLUMN "diskon" decimal(5, 2) DEFAULT 0;
```

### Kapan Harus Makemigrations?

```
✅ HARUS makemigrations setelah:
  - Tambah field baru di model
  - Hapus field dari model
  - Ubah tipe field (CharField → TextField)
  - Ubah opsi field (max_length, null, blank)
  - Tambah model baru
  - Hapus model
  - Ubah relasi (ForeignKey, OneToOne)

❌ TIDAK perlu makemigrations setelah:
  - Ubah method/property di model (stok_total, __str__)
  - Ubah class Meta (ordering, verbose_name)
  - Ubah views.py, forms.py, urls.py, templates
```

---

## J. ORM Lanjutan — Query yang Sering Dipakai di ERP

### Aggregate — Hitung Total, Rata-rata, dll:

```python
from django.db.models import Sum, Count, Avg, Min, Max

# Total semua penjualan bulan ini
from datetime import date
bulan_ini = date.today().replace(day=1)

total = SalesOrder.objects.filter(
    tanggal__gte=bulan_ini,
    status__in=['confirmed', 'delivered']
).aggregate(
    total_pendapatan=Sum('total_harga'),     # Jumlah total_harga
    jumlah_transaksi=Count('id'),            # Berapa SO
    rata_rata=Avg('total_harga'),            # Rata-rata per SO
)
# Output: {'total_pendapatan': 15000000, 'jumlah_transaksi': 25, 'rata_rata': 600000}

# Akses hasilnya:
print(f"Total: Rp {total['total_pendapatan']:,.0f}")
# Output: Total: Rp 15,000,000
```

### Annotate — Tambah Kolom Kalkulasi:

```python
# Daftar produk BESERTA total stok di semua gudang
produk_list = Produk.objects.annotate(
    total_stok=Sum('stok__jumlah')  # ← traverse FK ke tabel Stok
).order_by('-total_stok')           # ← urutkan stok terbanyak dulu

for p in produk_list:
    print(f"{p.nama}: {p.total_stok} unit")
# Output:
# Beras Premium: 500 unit
# Indomie: 350 unit
# Aqua: 200 unit
```

### Select Related & Prefetch Related — Optimasi Query:

```python
# ❌ PROBLEM: N+1 Query (LAMBAT!)
produk_list = Produk.objects.all()
for p in produk_list:
    print(p.kategori.nama)  # ← Setiap akses FK = 1 query baru!
# Jika ada 100 produk → 101 query total (1 + 100)

# ✅ SOLUSI: select_related (JOIN di SQL)
produk_list = Produk.objects.select_related('kategori', 'satuan').all()
for p in produk_list:
    print(p.kategori.nama)  # ← Tidak ada query tambahan!
# Hanya 1 query total! (pakai SQL JOIN)

# Kapan pakai select_related vs prefetch_related?
# select_related  → untuk ForeignKey / OneToOne (JOIN)
# prefetch_related → untuk ManyToMany / reverse FK (query terpisah)
```

### Q Objects — Query Kompleks (AND/OR):

```python
from django.db.models import Q

# Cari produk: nama mengandung "beras" ATAU harga > 100000
hasil = Produk.objects.filter(
    Q(nama__icontains="beras") | Q(harga_jual__gt=100000)
)
# SQL: WHERE nama LIKE '%beras%' OR harga_jual > 100000

# Cari produk: aktif DAN (kategori makanan ATAU kategori minuman)
hasil = Produk.objects.filter(
    Q(aktif=True) & (Q(kategori__nama="Makanan") | Q(kategori__nama="Minuman"))
)
# SQL: WHERE aktif=1 AND (kategori.nama='Makanan' OR kategori.nama='Minuman')
```

---

## K. Migrasi Database — Deep Dive

### Apa itu Migrasi?

Migrasi = **instruksi perubahan** untuk database. Setiap kali kita ubah model, Django membuat file migrasi yang berisi instruksi SQL yang diperlukan.

```
┌──────────────────────┐    makemigrations    ┌──────────────────────┐    migrate     ┌──────────┐
│   models.py          │  ──────────────────→ │   0001_initial.py    │ ────────────→ │ Database │
│   (definisi Python)  │                      │   (instruksi SQL)    │               │ (tabel)  │
└──────────────────────┘                      └──────────────────────┘               └──────────┘

Ubah model → makemigrations (buat instruksi) → migrate (jalankan instruksi)
```

### Perintah Migrasi Lengkap:

```bash
# 1. BUAT file migrasi dari perubahan model
python manage.py makemigrations
# Output: apps/produk/migrations/0003_auto_20260223.py
#   - Migrations for 'produk':
#     - Add field barcode to produk

# 2. LIHAT SQL yang akan dijalankan (preview, tidak eksekusi)
python manage.py sqlmigrate produk 0003
# Output: ALTER TABLE "produk_produk" ADD COLUMN "barcode" varchar(50) NULL;

# 3. JALANKAN migrasi ke database
python manage.py migrate
# Output: Applying produk.0003_auto_20260223... OK

# 4. CEK status migrasi (sudah dijalankan atau belum)
python manage.py showmigrations
# Output:
# produk
#   [X] 0001_initial          ← Sudah dijalankan
#   [X] 0002_add_sku          ← Sudah dijalankan
#   [ ] 0003_add_barcode      ← BELUM dijalankan!

# 5. ROLLBACK migrasi (kembali ke migrasi sebelumnya)
python manage.py migrate produk 0002
# Output: Unapplying produk.0003_add_barcode... OK
# ↑ Menghapus kolom barcode dari database

# 6. Migrasi untuk APP tertentu saja
python manage.py makemigrations produk
python manage.py migrate produk
```

### Troubleshooting Migrasi:

#### 1. Conflict — Dua Developer Buat Migrasi Bersamaan
```bash
# ERROR: Conflicting migrations detected
# Solusi: merge migrasi
python manage.py makemigrations --merge
# Django akan buat file migrasi baru yang menggabungkan keduanya
```

#### 2. "No changes detected" padahal model SUDAH diubah
```bash
# Kemungkinan penyebab:
# 1. App belum terdaftar di INSTALLED_APPS
# 2. File __init__.py tidak ada di folder migrations/
# 3. Yang diubah bukan field (method/property tidak butuh migrasi)

# Solusi 1: Specify app name
python manage.py makemigrations produk

# Solusi 2: Cek INSTALLED_APPS di settings.py
INSTALLED_APPS = [
    'apps.produk',  # ← Pastikan ada!
]
```

#### 3. Database Error Saat Migrate
```bash
# ERROR: django.db.utils.OperationalError: table already exists
# Solusi: fake migrasi yang sudah ada di database
python manage.py migrate --fake produk 0003

# ERROR: Cannot add NOT NULL column without default
# Solusi: tambahkan default atau null=True di model
nama = models.CharField(max_length=200, default='')  # ← tambah default
# ATAU
nama = models.CharField(max_length=200, null=True)   # ← izinkan NULL
```

#### 4. Reset Migrasi (Development Only!)
```bash
# ⚠️ HANYA untuk development! JANGAN di production!

# Hapus database
del db.sqlite3

# Hapus semua file migrasi (kecuali __init__.py)
# Di setiap folder migrations/

# Buat ulang migrasi dari awal
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Struktur File Migrasi:

```python
# apps/produk/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        # ↑ Migrasi ini BERGANTUNG pada migrasi auth
    ]

    operations = [
        migrations.CreateModel(
            name='Kategori',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('nama', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Produk',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('nama', models.CharField(max_length=200)),
                ('kategori', models.ForeignKey(
                    on_delete=models.SET_NULL, null=True,
                    to='produk.Kategori'
                )),
            ],
        ),
    ]
```

---

## L. Custom Manager & QuerySet

### Apa itu Manager?

Manager = **pintu masuk** ke database queries. Default manager: `objects`.

```python
Produk.objects.all()       # 'objects' = default manager
Produk.objects.filter()    # Semua query lewat manager
Produk.objects.create()    # Create juga lewat manager
```

### Custom Manager — Tambah Method Query:

```python
# ═══ apps/produk/models.py ═══

class ProdukManager(models.Manager):
    """Custom Manager untuk model Produk."""

    def aktif(self):
        """Hanya produk yang aktif."""
        return self.filter(aktif=True)

    def by_kategori(self, kategori_nama):
        """Filter produk berdasarkan nama kategori."""
        return self.filter(kategori__nama__iexact=kategori_nama)

    def stok_kosong(self):
        """Produk dengan stok total = 0 atau tidak punya stok."""
        from django.db.models import Sum
        return self.annotate(
            total=Sum('stok__jumlah')
        ).filter(
            models.Q(total=0) | models.Q(total__isnull=True)
        )

    def terlaris(self, limit=10):
        """Top N produk berdasarkan total penjualan."""
        from django.db.models import Sum
        return self.annotate(
            total_terjual=Sum('salesorderitem__kuantitas')
        ).order_by('-total_terjual')[:limit]


class Produk(models.Model):
    # ...
    objects = ProdukManager()  # ← Ganti default manager

# Pemakaian:
Produk.objects.aktif()                      # Semua produk aktif
Produk.objects.by_kategori('Makanan')       # Produk kategori Makanan
Produk.objects.stok_kosong()                # Produk stok habis
Produk.objects.terlaris(5)                  # Top 5 terlaris
Produk.objects.aktif().by_kategori('Makanan')  # Chain!
```

### Custom QuerySet (Lebih Fleksibel):

```python
class ProdukQuerySet(models.QuerySet):
    """Custom QuerySet — bisa di-chain dan dipakai di Manager."""

    def aktif(self):
        return self.filter(aktif=True)

    def mahal(self, min_harga=100000):
        return self.filter(harga_jual__gte=min_harga)

    def murah(self, max_harga=50000):
        return self.filter(harga_jual__lte=max_harga)


class Produk(models.Model):
    # ...
    objects = ProdukQuerySet.as_manager()
    # ↑ as_manager() mengubah QuerySet menjadi Manager

# Pemakaian — bisa di-chain tanpa batas:
Produk.objects.aktif().mahal().order_by('nama')
# SQL: SELECT * FROM produk WHERE aktif=1 AND harga_jual >= 100000 ORDER BY nama
```

### Kapan Manager vs QuerySet?

| Fitur | Custom Manager | Custom QuerySet |
|-------|---------------|-----------------|
| Chainable | ❌ Terbatas | ✅ Ya |
| Method di result juga | ❌ Tidak | ✅ Ya |
| Kompleksitas | Sederhana | Lebih lengkap |
| Direkomendasikan | Quick & simple | Production code |

---

## M. Django Signals — Event System

### Apa itu Signal?

Signals = **mekanisme event** di Django. Ketika suatu aksi terjadi (save, delete, login), Django mengirim **sinyal**, dan **receiver** (fungsi) yang sudah terdaftar akan dipanggil **otomatis**.

```
┌────────────┐    Signal    ┌────────────────┐    Otomatis    ┌────────────────┐
│ Produk     │ ============>│ Django Signal  │ ============>│ Signal Handler │
│ .save()    │  post_save   │ System         │  dispatch     │ log_perubahan()│
└────────────┘              └────────────────┘               └────────────────┘
```

### Semua Signal Bawaan Django:

| Signal | Kapan Dipicu? | Parameter Penting |
|--------|--------------|-------------------|
| `pre_save` | **SEBELUM** model disimpan | `instance`, `sender` |
| `post_save` | **SETELAH** model disimpan | `instance`, `created` (True=baru) |
| `pre_delete` | **SEBELUM** model dihapus | `instance` |
| `post_delete` | **SETELAH** model dihapus | `instance` |
| `user_logged_in` | User berhasil login | `user`, `request` |
| `user_logged_out` | User logout | `user`, `request` |
| `m2m_changed` | Relasi ManyToMany berubah | `instance`, `action`, `pk_set` |

### Contoh Nyata #1 — Auto-Log Login/Logout:

```python
# ═══ apps/activity_log/signals.py ═══
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserActivity

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    OTOMATIS dipanggil setiap kali user berhasil login.
    Tidak perlu panggil manual — Django yang panggil!
    """
    UserActivity.objects.create(
        user=user,
        action='login',
        description=f"{user.username} logged in",
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    # → Setiap login → record baru di tabel UserActivity
```

### Contoh Nyata #2 — Delta Tracking (Catat Perubahan Field):

```python
# ═══ LANGKAH 1: pre_save — Simpan state LAMA ═══
def capture_old_state(sender, instance, **kwargs):
    """
    SEBELUM save → ambil data lama dari database.
    Simpan di instance._old_state untuk dibandingkan nanti.
    """
    if instance.pk:  # Hanya untuk update (bukan create baru)
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_state = old
        except sender.DoesNotExist:
            instance._old_state = None

# ═══ LANGKAH 2: post_save — Bandingkan LAMA vs BARU ═══
def log_model_change(sender, instance, created, **kwargs):
    """
    SETELAH save → bandingkan old vs new field-by-field.
    Catat perbedaan sebagai JSON.
    """
    if created:
        action = 'create'  # Objek baru
    else:
        action = 'update'  # Objek diupdate

    # Hitung delta (perbedaan)
    if not created and hasattr(instance, '_old_state'):
        changes = {}
        for field in instance._meta.fields:
            old_val = getattr(instance._old_state, field.name)
            new_val = getattr(instance, field.name)
            if old_val != new_val:
                changes[field.name] = {
                    'old': str(old_val),
                    'new': str(new_val)
                }
        # changes = {'harga_jual': {'old': '10000', 'new': '15000'}}

    UserActivity.objects.create(
        user=request.user,
        action=action,
        model_name=sender.__name__,
        object_repr=str(instance),
        changes=json.dumps(changes),
    )
```

### Contoh Nyata #3 — Register Signals untuk SEMUA Model:

```python
# ═══ apps/activity_log/signals.py ═══
def register_signals():
    """
    Daftarkan signal handlers untuk SEMUA model di project.
    Dipanggil saat Django startup via apps.py → ready().
    """
    from django.apps import apps

    # Model yang TIDAK perlu di-log
    EXCLUDED_APPS = ['admin', 'auth', 'contenttypes', 'sessions', 'activity_log']
    EXCLUDED_MODELS = ['LogEntry', 'Permission', 'Session', 'UserActivity']

    for model in apps.get_models():
        app_label = model._meta.app_label
        if app_label in EXCLUDED_APPS or model.__name__ in EXCLUDED_MODELS:
            continue

        # Daftarkan 3 signal sekaligus
        pre_save.connect(capture_old_state, sender=model, weak=False)
        post_save.connect(log_model_change, sender=model, weak=False)
        post_delete.connect(log_model_delete, sender=model, weak=False)
    # → SETIAP model (Produk, Kategori, PO, SO, dll) otomatis di-log!
```

### Koneksi Signal ↔ apps.py:

```python
# ═══ apps/activity_log/apps.py ═══
class ActivityLogConfig(AppConfig):
    name = 'apps.activity_log'

    def ready(self):
        """
        Dipanggil SAAT DJANGO STARTUP (sekali saja).
        Di sinilah kita daftarkan semua signals.
        """
        from .signals import register_signals
        register_signals()  # ← Daftarkan signal handlers

        from . import stock_signals  # noqa: F401
        # ↑ Import agar signal decorators (@receiver) aktif
```

### Stock Signals — Tracking Khusus Perubahan Stok:

```python
# ═══ apps/activity_log/stock_signals.py ═══
def log_stock_change(user, produk, gudang, action, source_type, 
                     source_id, source_repr, quantity_before, 
                     quantity_after, description=None, request=None):
    """
    Log detail perubahan stok — LEBIH DETAIL dari signal generik.
    Mencatat: produk, gudang, qty sebelum/sesudah, sumber perubahan.
    """
    UserActivity.objects.create(
        user=user,
        action=action,                    # 'stock_in', 'stock_out', dll
        model_name='Stok',
        object_repr=f"{produk.nama} ({gudang.nama})",
        source_type=source_type,          # 'purchase', 'sales', 'pos'
        source_id=str(source_id),
        source_repr=source_repr,          # 'PO-2026-0042'
        quantity_before=quantity_before,   # 100
        quantity_after=quantity_after,     # 150
        quantity_change=quantity_after - quantity_before,  # +50
        gudang_id=str(gudang.pk),
        gudang_name=gudang.nama,
    )

# Dipanggil dari views:
# log_purchase_stock_in(po, user)   ← Saat PO diterima
# log_sales_stock_out(so, user)     ← Saat SO dikonfirmasi
# log_pos_stock_out(transaksi, user)← Saat transaksi POS
# log_transfer_stock(transfer, user)← Saat transfer stok
# log_adjustment_stock(adj, user)   ← Saat adjustment stok
```

---

## N. Database Indexes & Constraints

### Apa itu Index?

Index = **daftar isi** di database. Tanpa index, database harus scan SELURUH tabel untuk mencari data (seperti membaca buku dari halaman 1 sampai terakhir). Dengan index, database langsung tahu di mana data berada.

### Contoh Index di Project — UserActivity:

```python
# ═══ apps/activity_log/models.py ═══
class UserActivity(models.Model):
    user = models.ForeignKey(User, ...)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            # Index 1: Cari log berdasarkan waktu (DESC)
            models.Index(fields=['-timestamp']),
            # SQL: CREATE INDEX ON activity_log (-timestamp)
            # Tanpa index: scan 100.000 record → 500ms
            # Dengan index: langsung ke record terbaru → 1ms

            # Index 2: Cari log per user, urutkan waktu
            models.Index(fields=['user', '-timestamp']),
            # Query: UserActivity.objects.filter(user=user).order_by('-timestamp')

            # Index 3: Cari per action, urutkan waktu
            models.Index(fields=['action', '-timestamp']),
            # Query: UserActivity.objects.filter(action='create')

            # Index 4: Cari perubahan per model + objek tertentu
            models.Index(fields=['model_name', 'object_id']),
            # Query: "Semua log untuk Produk id=5"

            # Index 5: Cari per sumber stok
            models.Index(fields=['source_type', '-timestamp']),
            # Query: "Semua perubahan stok dari POS"
        ]
```

### Kapan HARUS Buat Index?

```
✅ BUAT INDEX jika:
  - Field sering dipakai di filter() / WHERE clause
  - Field sering dipakai di order_by() / ORDER BY
  - Field dipakai di JOIN (ForeignKey → OTOMATIS ada index)
  - Tabel besar (>10.000 row) dan query lambat

❌ JANGAN buat index jika:
  - Tabel kecil (<1.000 row) → index malah overhead
  - Field jarang di-query
  - Field sering di-UPDATE (index harus diupdate juga)
  - Terlalu banyak index (>5-6 per tabel)
```

### Jenis Constraint di Django:

```python
class Produk(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    # ↑ unique=True → CONSTRAINT: tidak boleh ada SKU yang sama

    nama = models.CharField(max_length=200)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL)
    harga_jual = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            # 1. Unique Together — Kombinasi field harus unik
            models.UniqueConstraint(
                fields=['nama', 'kategori'],
                name='unique_produk_per_kategori'
            ),
            # ↑ Tidak boleh ada produk dengan nama DAN kategori yang sama
            # Contoh: "Beras" di "Makanan" boleh SATU saja

            # 2. Check Constraint — Validasi di level database
            models.CheckConstraint(
                check=models.Q(harga_jual__gte=0),
                name='harga_jual_tidak_negatif'
            ),
            # ↑ harga_jual HARUS >= 0
            # Database akan TOLAK jika insert harga negatif
        ]
```

### Index vs Constraint — Apa Bedanya?

| Fitur | Index | Constraint |
|-------|-------|------------|
| Tujuan | **Mempercepat** query | **Mencegah** data invalid |
| Contoh | Cari produk lebih cepat | Harga tidak boleh negatif |
| Jika dilanggar | Tidak ada efek | ERROR, data ditolak |
| Dampak performa | Mempercepat SELECT, memperlambat INSERT/UPDATE | Minimal |
| Wajib? | Opsional (optimasi) | Tergantung aturan bisnis |

---

## O. Kesalahan Umum & Best Practice Model

### ❌ Kesalahan Umum

#### 1. DecimalField vs FloatField untuk Uang
```python
# ❌ SALAH — presisi floating-point hilang!
harga = models.FloatField()
# 0.1 + 0.2 = 0.30000000000000004 (BUG!)

# ✅ BENAR — presisi tepat
harga = models.DecimalField(max_digits=15, decimal_places=2)
# 0.1 + 0.2 = 0.30 (BENAR)
```

#### 2. Lupa `on_delete` di ForeignKey
```python
# ❌ SALAH — Django 2.0+ WAJIB sebutkan on_delete
kategori = models.ForeignKey(Kategori)
# TypeError: __init__() missing required argument: 'on_delete'

# ✅ BENAR
kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
```

#### 3. N+1 Query Problem (Paling Sering!)
```python
# ❌ SALAH — 101 query untuk 100 produk!
for produk in Produk.objects.all():
    print(produk.kategori.nama)  # ← 1 query per produk!

# ✅ BENAR — hanya 1 query (JOIN)!
for produk in Produk.objects.select_related('kategori'):
    print(produk.kategori.nama)  # ← Sudah di-load!
```

#### 4. Lupa `makemigrations` Setelah Ubah Model
```python
# Tambah field baru:
class Produk(models.Model):
    barcode = models.CharField(max_length=50, blank=True)  # ← BARU

# ❌ SALAH — langsung migrate tanpa makemigrations
python manage.py migrate  # → No migrations to apply

# ✅ BENAR — makemigrations dulu!
python manage.py makemigrations  # → Detect perubahan
python manage.py migrate         # → Apply ke database
```

#### 5. `blank=True` tanpa `null=True` untuk Non-String Field
```python
# ❌ SALAH — DecimalField kosong → IntegrityError
harga_diskon = models.DecimalField(blank=True)
# Form boleh kosong, tapi database tidak terima NULL!

# ✅ BENAR — izinkan NULL di database juga
harga_diskon = models.DecimalField(blank=True, null=True)
# Form boleh kosong → database simpan NULL

# ⚠️ PENGECUALIAN: CharField dan TextField
# Untuk string field, JANGAN pakai null=True
nama = models.CharField(blank=True, default='')
# ↑ String kosong disimpan sebagai '' bukan NULL
# Karena Django convention: string kosong = '' (bukan NULL)
```

### ✅ Best Practice Production

| # | Practice | Penjelasan |
|---|----------|------------|
| 1 | Selalu pakai `DecimalField` untuk uang | Presisi tepat, tidak ada bug float |
| 2 | Tambahkan `select_related` di ListView | Hindari N+1 problem |
| 3 | Gunakan `@property` untuk kalkulasi | Seperti `stok_total`, `margin` |
| 4 | Buat `__str__` di semua model | Tampilan di admin & debugging |
| 5 | Tambahkan `dibuat_pada` & `diupdate_pada` | Audit trail timestamps |
| 6 | Gunakan `choices` untuk field enum | Seperti `status`, `action`, `source_type` |
| 7 | Index field yang sering di-filter | `Meta.indexes` untuk query cepat |
| 8 | Unique constraint untuk data unik | SKU, nomor PO, email |
| 9 | `on_delete=SET_NULL` untuk FK opsional | Jangan DELETE cascade jika tidak perlu |
| 10 | Review SQL dengan `sqlmigrate` | Pahami apa yang terjadi di database |
| 11 | `select_for_update()` untuk operasi stok | Cegah race condition saat concurrent write |
| 12 | `transaction.atomic()` untuk operasi multi-tabel | Rollback otomatis jika ada error di tengah proses |
| 13 | Validasi stok sebelum kurangi | Cegah stok negatif: `if stok.jumlah < qty: raise ValueError(...)` |

---

## N. Concurrency Control — Proteksi Data Saat Multi-User

### Kenapa Penting?

Saat banyak user mengakses sistem ERP bersamaan (misalnya 2 kasir POS di waktu yang sama), bisa terjadi **race condition** — data stok menjadi tidak akurat karena 2 proses membaca dan menulis data yang sama secara bersamaan.

### `transaction.atomic()` — Transaksi Database

```python
from django.db import transaction

# Semua operasi di dalam with block dijamin ATOMIK:
# - Jika SEMUA berhasil → COMMIT (simpan permanen)
# - Jika ADA yang gagal → ROLLBACK (batalkan semua perubahan)
with transaction.atomic():
    stok_a.jumlah -= 50   # Kurangi di gudang A
    stok_a.save()
    stok_b.jumlah += 50   # Tambah di gudang B
    stok_b.save()
    # Jika stok_b.save() error → stok_a juga di-rollback!
```

### `select_for_update()` — Row-Level Locking

```python
# TANPA lock → rawan race condition:
stok = Stok.objects.get(produk=produk, gudang=gudang)  # Baca (semua bisa baca)
stok.jumlah -= qty
stok.save()  # Tulis → bisa menimpa perubahan user lain!

# DENGAN lock → aman:
with transaction.atomic():
    stok = Stok.objects.select_for_update().get(  # Baca + KUNCI baris
        produk=produk, gudang=gudang
    )
    # → Thread lain yang query baris ini akan MENUNGGU sampai lock dilepas
    stok.jumlah -= qty
    stok.save()
# → Lock dilepas setelah atomic block selesai, thread lain bisa lanjut
```

### Diterapkan di Semua Operasi Stok:

| Method | Model/View | Jenis Operasi |
|--------|------------|---------------|
| `TransferStok.approve()` | `inventory/models.py` | Transfer antar gudang |
| `AdjustmentStok.save()` | `inventory/models.py` | Koreksi stok manual |
| `SalesOrder.confirm_order()` | `penjualan/models.py` | Kurangi stok saat SO confirmed |
| `PurchaseOrder.receive_goods()` | `pembelian/models.py` | Tambah stok saat PO diterima |
| `CreateTransactionView.post()` | `pos/views.py` | Kurangi stok saat transaksi POS |
| Semua `generate_nomor()` | 6 file models | Cegah nomor transaksi duplikat |

> Detail lengkap: [16_PERBAIKAN_DAN_PENINGKATAN.md — Section R](16_PERBAIKAN_DAN_PENINGKATAN.md)

---

*Lanjut ke [04_VIEWS_DAN_URL.md](04_VIEWS_DAN_URL.md) →*
