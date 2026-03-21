# 📦 08 — Fitur & Modul ERP — Penjelasan Sangat Detail

## Daftar Semua Modul ERP

Project ini terdiri dari **16 modul** yang saling terhubung. Berikut penjelasan detail setiap modul: apa fungsinya, halaman-halamannya, model database yang digunakan, dan bagaimana modul tersebut terhubung dengan modul lain.

---

## 1. Dashboard (`apps/dashboard/`)

**URL:** `/` (halaman utama setelah login)

**Fungsi:** Menampilkan **ringkasan statistik bisnis** dalam satu halaman. Manajemen bisa melihat kondisi bisnis secara cepat tanpa harus buka-buka modul lain.

**Komponen (Update Maret 2026 — layout disederhanakan):**
| Widget | Data yang Ditampilkan | Sumber Data (Model) |
|--------|----------------------|---------------------|
| Card Statistik | Total aset, harga beli, harga jual, estimasi keuntungan | `Produk`, `Stok` di-aggregate |
| Chart Penjualan | Area chart penjualan bulan ini (gradient smooth) | `SalesOrder` + `POSTransaction` per hari |
| Chart Penjualan/Cabang | Wave/area chart per gudang, **Smart Aggregation**: per-hari (\u226462 hari) / per-bulan (>62 hari), filter waktu navbar | `SalesOrder` + `POSTransaction` per gudang |
| Produk Terlaris | Top 10 produk by penjualan | `SalesOrderItem` + `POSTransactionItem` |
| Pengguna Terbaru | Daftar user terbaru 100% lebar, 1 inisial avatar | `User.objects.order_by('-date_joined')` |
| Filter Waktu | Icon kalender di navbar (hanya muncul di dashboard) | GET params → views.py filter |

> **Section yang dihapus:** Total Pembelian (radial), Total Biaya (radial), Slider Metode Pembayaran, Keuntungan per Cabang (bar chart), Biaya per Kategori (bar chart).

**Kenapa Dashboard penting?**
Tanpa dashboard, untuk mengetahui "berapa penjualan bulan ini?", harus buka modul Laporan → filter tanggal → hitung manual. Dengan dashboard, jawabannya **langsung terlihat** saat login.

---

## 2. Produk (`apps/produk/`)

**URL:** `/produk/`

**Fungsi:** Mengelola **data master produk** — fondasi seluruh sistem ERP. Semua modul lain (inventory, penjualan, pembelian) mereferensikan data produk.

### Model yang Diperlukan:

```python
Kategori → Mengelompokkan produk (Makanan, Minuman, Elektronik)
Satuan   → Satuan ukur produk (pcs, kg, liter, box)
Produk   → Data produk itu sendiri (nama, SKU, harga, gambar)
Gudang   → Lokasi penyimpanan (Gudang Jakarta, Gudang Surabaya)
Stok     → Jumlah produk per gudang (pivot table: produk × gudang)
```

### Halaman dan URL:
| URL | View | Fungsi | Permission |
|-----|------|--------|------------|
| `/produk/kategori/` | KategoriListView | Daftar kategori | produk.kategori.read |
| `/produk/kategori/add/` | KategoriCreateView | Form tambah kategori | produk.kategori.create |
| `/produk/kategori/<id>/edit/` | KategoriUpdateView | Form edit kategori | produk.kategori.write |
| `/produk/kategori/<id>/delete/` | KategoriDeleteView | Hapus kategori (AJAX) | produk.kategori.delete |
| `/produk/satuan/` | SatuanListView | Daftar satuan | produk.satuan.read |
| `/produk/list/` | ProdukListView | Daftar semua produk | produk.daftar_produk.read |
| `/produk/tambah/` | ProdukCreateView | Form tambah produk | produk.daftar_produk.create |
| `/produk/<id>/edit/` | ProdukUpdateView | Form edit produk | produk.daftar_produk.write |
| `/produk/import/` | ProdukImportView | Import dari Excel | produk.daftar_produk.create |

### Fitur Khusus:
- **Auto-generate SKU:** Saat produk disimpan tanpa SKU → `Produk.save()` otomatis generate (contoh: MAK-00001)
- **Import Excel:** Upload file .xlsx → baca dengan `openpyxl` → bulk create produk
- **Property `stok_total`:** Hitung total stok di SEMUA gudang tanpa query terpisah
- **Upload Gambar:** Disimpan di `media/produk/` → ditampilkan di daftar & detail

### Koneksi ke Modul Lain:
```
Produk ──→ PurchaseOrderItem (produk yang dibeli)
Produk ──→ SalesOrderItem (produk yang dijual)
Produk ──→ TransferStokItem (produk yang ditransfer antar gudang)
Produk ──→ InvoiceItem (produk yang dijual via POS)
Produk ──→ LaporanProduk, LaporanStok (data laporan)
```

---

## 3. Inventory / Persediaan (`apps/inventory/`)

**URL:** `/inventory/`

**Fungsi:** Mengelola **gudang dan pergerakan stok** barang.

### Halaman:
| URL | Fungsi | Penjelasan |
|-----|--------|------------|
| `/inventory/gudang/` | Daftar gudang | Lihat semua lokasi penyimpanan |
| `/inventory/stok/` | Stok per gudang | Matriks: produk × gudang × jumlah |
| `/inventory/transfer/` | Daftar transfer | Riwayat pemindahan barang antar gudang |
| `/inventory/transfer/create/` | Buat transfer | Form: dari gudang A → gudang B, produk apa, berapa |
| `/inventory/adjustment/` | Daftar adjustment | Riwayat koreksi stok |
| `/inventory/adjustment/create/` | Buat adjustment | Koreksi stok: hilang, rusak, bonus |

### Bagaimana Transfer Stok Bekerja?

```
LANGKAH 1: Admin buat Transfer Stok
    Dari: Gudang Jakarta
    Ke: Gudang Surabaya
    Produk: Beras Premium, Jumlah: 50

LANGKAH 2: Sistem eksekusi (saat status = Completed)
    → Stok Gudang Jakarta: 100 - 50 = 50 (berkurang)
    → Stok Gudang Surabaya: 30 + 50 = 80 (bertambah)
    → Total stok TETAP sama: 50 + 80 = 130 (hanya pindah lokasi)

LANGKAH 3: Data tersimpan di tabel:
    TransferStok: {dari: Jakarta, ke: Surabaya, status: Completed}
    TransferStokItem: {produk: Beras, jumlah: 50}
    Stok: updated otomatis
```

---

## 4. Pembelian (`apps/pembelian/`)

**URL:** `/pembelian/`

**Fungsi:** Mengelola **pembelian barang dari supplier**. Alur: Buat PO → Konfirmasi → Terima Barang → Stok Bertambah.

### Alur Purchase Order (PO):
```
┌─────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐
│  DRAFT  │ ──► │ CONFIRMED │ ──► │ RECEIVED │ ──► │ COMPLETED │
│         │     │           │     │          │     │           │
│ PO dibuat│     │ PO dikirim│     │ Barang   │     │ Proses    │
│ belum   │     │ ke supplier│     │ diterima │     │ selesai   │
│ final   │     │           │     │ Stok +   │     │           │
└─────────┘     └───────────┘     └──────────┘     └───────────┘
```

**Saat PO status "RECEIVED":**
- Stok produk di gudang tujuan otomatis BERTAMBAH
- Contoh: PO untuk 100 Beras → stok Beras di Gudang Jakarta: 50 + 100 = 150

---

## 5. Penjualan (`apps/penjualan/`)

**URL:** `/penjualan/`

**Fungsi:** Mengelola **penjualan ke customer**. Alur: Buat SO → Konfirmasi → Kirim → Stok Berkurang.

### Alur Sales Order (SO):
```
┌─────────┐     ┌───────────┐     ┌──────────┐
│  DRAFT  │ ──► │ CONFIRMED │ ──► │ SHIPPED  │
│         │     │           │     │          │
│ SO dibuat│     │ SO final  │     │ Barang   │
│         │     │ Stok -    │     │ dikirim  │
└─────────┘     └───────────┘     └──────────┘
```

**Saat SO status "CONFIRMED":**
- Stok produk di gudang BERKURANG otomatis
- Contoh: SO untuk 20 Beras → stok Beras: 150 - 20 = 130

---

## 6. POS / Kasir (`apps/pos/`)

**URL:** `/pos/`

**Fungsi:** Antarmuka **kasir digital** — untuk penjualan langsung di toko.

### Komponen Halaman POS:

| Komponen | Fungsi | Sumber Data |
|----------|--------|-------------|
| Pilih Gudang | Memilih gudang/cabang aktif (Select2) | `Gudang.objects.filter(aktif=True)` |
| Pilih Kasir | Memilih kasir yang bertugas (Select2) | `User.objects.filter(is_active=True)` |
| Daftar Produk | Grid produk dengan filter kategori & pencarian | `Produk`, `Kategori` |
| Star Rating | Bintang 1-5 berdasarkan jumlah pembelian | `POSTransactionItem` (qty terjual) |
| Keranjang | Daftar item yang akan dibeli | JavaScript (client-side) |
| Modal Pembayaran | Form pembayaran + customer + metode | `MetodePembayaran`, `Customer` |

### Fitur UI Terbaru (Update Maret 2026):

#### A. Star Rating Produk (Bintang 1-5)
```
Setiap kartu produk memiliki rating bintang berdasarkan jumlah pembelian:

ALUR DATA:
views.py → Query POSTransactionItem (status='paid')
         → Group by produk_id, Sum('jumlah')
         → Hitung rasio terhadap produk paling laris
         → Mapping ke rating:
            ≥80% → ⭐⭐⭐⭐⭐ (5 bintang)
            ≥60% → ⭐⭐⭐⭐ (4 bintang)
            ≥40% → ⭐⭐⭐ (3 bintang)
            ≥20% → ⭐⭐ (2 bintang)
            <20% → ⭐ (1 bintang, default)
         → Kirim sebagai JSON ke template
         → JavaScript render ikon bintang (ri-star-fill)

CSS: .star-filled { color: #ffab00 }  (emas)
     .star-empty  { color: #d0d4da }  (abu-abu)
```

#### B. Custom Scrollbar (Konsisten dengan Sidebar)
```
Daftar produk dan keranjang menggunakan scrollbar kustom:
- Lebar: 5px (tipis dan rapi)
- Warna thumb: rgba(105, 108, 255, 0.4) — ungu semi-transparan
- Hover: opacity meningkat ke 0.7
- Firefox: scrollbar-width: thin + scrollbar-color
- Chrome/Safari: ::-webkit-scrollbar pseudo-elements
- Konsisten dengan scrollbar sidebar utama
```

#### C. Category Pills (Tombol Filter Kategori)
```
Tombol filter kategori produk (Semua, Elektronik, Makanan, dll):
- Border-radius: 0.375rem (sama dengan tombol Riwayat, bukan fully rounded)
- State aktif: bg-primary + text-white
- State inaktif: bg-transparent + text-primary (font tetap terlihat)
- State hover: bg-primary-light + transisi 0.2s
- Dark mode: warna menyesuaikan tema otomatis
```

#### D. Perubahan UI Lainnya
```
- Badge "Kasir" di keranjang DIHAPUS (redundan dengan Pilih Kasir)
- Ukuran harga produk = ukuran nama produk (menghemat ruang)
- Product grid: max-height dengan overflow-y: auto
- Card produk: hover effect dengan transform scale(1.03)
- Empty state: ikon ri-dropbox-line + pesan jika tidak ada produk
```

### Cara Kerja POS:
```
1. Kasir pilih gudang dan kasir yang bertugas (Select2 dropdown)

2. Kasir scan barcode / ketik nama produk
   → JavaScript search & filter produk
   → Filter kategori via category pills
   → Produk ditemukan → klik "Tambah" / tambahkan ke keranjang

3. Keranjang belanja (di browser — JavaScript)
   Beras Premium    x2    @15.000 = 30.000
   Aqua 600ml       x3    @4.000  = 12.000
   ────────────────────────────────────────
   Subtotal                         42.000
   Pajak (11%)                       4.620
   ────────────────────────────────────────
   TOTAL                            46.620

4. Klik "Bayar Sekarang" → buka Modal Pembayaran
   → Pilih metode pembayaran (Cash / Transfer / QRIS)
   → Input data Customer (autocomplete dari database)
   → Input uang diterima + tombol jumlah cepat
   → Catatan opsional

5. Server:
   → Buat record POSTransaction (nomor unik TRX-20260221-001)
   → Buat POSTransactionItem untuk setiap produk
   → Kurangi stok di gudang toko
   → Return data transaksi → JavaScript generate struk (pdfMake)
```

### Fitur Customer Autocomplete di Modal Pembayaran:
```
Field "Nama Customer" berfungsi sebagai pencarian:
  → Ketik huruf → muncul suggestion list dari database Customer
  → Klik nama → Telepon, Email, Alamat terisi otomatis (readonly)
  → Ketik nama baru (tidak ada di DB) → field lain kosong & editable
  → Data customer tersimpan bersama transaksi
```

---

## 7-8. Biaya & Laporan

### Biaya (`apps/biaya/`) — `/biaya/`
Pencatatan pengeluaran operasional (sewa, listrik, gaji, marketing). CRUD sederhana dengan filter tanggal.

### Laporan (`apps/laporan/`) — `/laporan/`
| Laporan | Data | Export |
|---------|------|--------|
| Laporan Produk | Semua produk + stok + harga | Excel, PDF |
| Laporan Stok | Stok per gudang per produk | Excel, PDF |
| Laporan Penjualan | SO + POS, filter tanggal | Excel, PDF |
| Laporan Pembelian | PO, filter tanggal + supplier | Excel, PDF |

**Export Excel:** Data diformat sebagai HTML table → dikirim sebagai file .xls → Excel membacanya. Termasuk RINGKASAN (total, rata-rata). Format ini sudah **distandarkan di 14+ halaman** CRUD dan laporan.

**Export PDF:** Menggunakan library **pdfMake** di JavaScript. Data tabel + branding perusahaan (nama, logo, alamat) di-generate menjadi file PDF langsung di browser. Format konsisten di semua halaman.

> Detail pola export dan daftar file yang distandarkan: [16_PERBAIKAN_DAN_PENINGKATAN.md — Bagian B](16_PERBAIKAN_DAN_PENINGKATAN.md)

---

## 9. HR Management (`apps/hr/`) — `/hr/`

**Fungsi:** Mengelola **data SDM / sumber daya manusia** — karyawan, departemen, jabatan, absensi, dan penggajian.

### Halaman dan URL:

| URL | Fungsi | Model |
|-----|--------|-------|
| `/hr/karyawan/` | Daftar karyawan + filter | Karyawan |
| `/hr/karyawan/add/` | Tambah karyawan baru | Karyawan |
| `/hr/karyawan/<id>/edit/` | Edit data karyawan | Karyawan |
| `/hr/karyawan/<id>/` | Detail karyawan | Karyawan |
| `/hr/departemen/` | Daftar departemen | Departemen |
| `/hr/jabatan/` | Daftar jabatan | Jabatan |
| `/hr/absensi/` | Rekap absensi | Absensi |
| `/hr/absensi/create/` | Input absensi harian | Absensi |
| `/hr/penggajian/` | Daftar penggajian | Penggajian |
| `/hr/penggajian/create/` | Buat slip gaji | Penggajian |

### Fitur Khusus:
- **Relasi Departemen → Jabatan → Karyawan** — struktur organisasi lengkap
- **Absensi dengan status:** Hadir, Izin, Sakit, Alpha
- **Penggajian:** Gaji pokok + tunjangan - potongan = gaji bersih
- **Export laporan** karyawan dan penggajian ke Excel/PDF

---

## 10. Automation / Telegram Bot (`apps/automation/`) — `/automation/`

**Fungsi:** Integrasi **Telegram Bot** untuk notifikasi otomatis event bisnis.

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/automation/telegram/` | Konfigurasi Telegram Bot |
| `/automation/telegram/test/` | Kirim pesan test |

### Notifikasi yang Dikirim:
```
📦 Purchase Order Baru
   PO-2026-0042 telah dibuat oleh Admin
   Supplier: PT Sumber Jaya
   Total: Rp 5.500.000

📊 Stok Habis Alert
   ⚠️ Beras Premium — Stok: 3 unit (minimum: 10)
   Segera buat Purchase Order!

💰 Sales Order Baru
   SO-2026-0088 — Customer: Toko Makmur
   Total: Rp 2.350.000
```

### Cara Kerja:
```
Event di Django (PO/SO/Stok) ──→ Signal handler ──→ Telegram API
                                                       │
                                                       ▼
                                                   Group Chat
                                                   Telegram
```

---

## 11. User Management (`apps/user_management/`) — `/users/`

**Fungsi:** Administrasi **akun pengguna** sistem ERP.

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/users/` | Daftar semua user |
| `/users/create/` | Buat akun user baru |
| `/users/<id>/edit/` | Edit user (nama, email, role) |
| `/users/<id>/` | Detail user (profil + aktivitas) |

### Fitur Khusus:
- **Assign Role:** Setiap user di-assign ke satu atau lebih Role (Admin, Kasir, Manager, dll)
- **Nonaktifkan Akun:** Set `is_active = False` → user tidak bisa login
- **Ganti Password:** Admin bisa reset password user lain
- **Relasi ke Permission:** User → Role → Permission (RBAC chain)

---

## 12. Permission Management (`apps/permission_management/`) — `/access/`

**Fungsi:** UI visual untuk mengatur **hak akses RBAC** (Role-Based Access Control).

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/access/roles/` | Daftar semua Role |
| `/access/roles/add/` | Buat role baru |
| `/access/roles/<id>/edit/` | Edit permission role |

### Cara Kerja Permission:
```
┌──────────────────────────────────────────────────────┐
│ Edit Role: "Kasir"                                    │
│                                                        │
│ Modul          │ Read │ Create │ Edit │ Delete │       │
│ ───────────────┼──────┼────────┼──────┼────────│       │
│ Produk         │  ☑   │   ☐    │  ☐   │   ☐   │       │
│  └ Kategori    │  ☑   │   ☐    │  ☐   │   ☐   │       │
│  └ Satuan      │  ☑   │   ☐    │  ☐   │   ☐   │       │
│ POS            │  ☑   │   ☑    │  ☑   │   ☐   │       │
│ Penjualan      │  ☑   │   ☐    │  ☐   │   ☐   │       │
│ Inventory      │  ☐   │   ☐    │  ☐   │   ☐   │       │
│ ...            │      │        │      │        │       │
└──────────────────────────────────────────────────────┘

Hasil:
- Kasir BISA: lihat produk, lihat penjualan, buat transaksi POS
- Kasir TIDAK BISA: tambah/edit/hapus produk, akses inventory
```

### Model Permission:
```python
# Hierarki: Role → RolePermission → Permission (config/sidebar_config)
Role              # "Kasir", "Manager", "Admin"
RolePermission    # Role=Kasir, permission_key="pos.kasir.create", granted=True
# permission_key format: "{modul}.{submodul}.{aksi}"
```

---

## 13. Pengaturan (`apps/pengaturan/`) — `/pengaturan/`

**Fungsi:** Konfigurasi **sistem dan profil**.

### Halaman:
| URL | Fungsi | Model |
|-----|--------|-------|
| `/pengaturan/profil/` | Edit profil user login | User, Profile |
| `/pengaturan/perusahaan/` | Data perusahaan | PengaturanPerusahaan |
| `/pengaturan/pembayaran/` | Metode pembayaran | MetodePembayaran |
| `/pengaturan/pembayaran/add/` | Tambah metode | MetodePembayaran |
| `/pengaturan/pembayaran/<id>/` | Detail metode | MetodePembayaran |
| `/pengaturan/template-cetak/` | Template laporan | TemplateCetak |

### Detail Metode Pembayaran:
```
┌─────────────────────────────────────────────┐
│ Metode Pembayaran                            │
├──────────┬──────────┬────────┬──────────────┤
│ Nama     │ Pemilik  │ Saldo  │ Status       │
├──────────┼──────────┼────────┼──────────────┤
│ BCA      │ PT ABC   │ 5.2 Jt │ ✅ Aktif    │
│ Mandiri  │ PT ABC   │ 3.1 Jt │ ✅ Aktif    │
│ Cash     │ Kasir    │ 850 Rb │ ✅ Aktif    │
│ QRIS     │ GoPay    │ 1.5 Jt │ ❌ Nonaktif │
└──────────┴──────────┴────────┴──────────────┘
```

### Data Perusahaan (Penting — muncul di SEMUA halaman):
```python
# Disuntikkan via context processor ke semua template:
# config/context_processors.py → pengaturan_perusahaan()

{{ system_title }}          # "PT. Sumber Jaya Makmur"
{{ system_logo_url }}       # "/media/pengaturan/logo.png"
{{ system_favicon_url }}    # "/media/pengaturan/favicon.ico"
{{ company_address }}       # "Jl. Sudirman No. 123, Jakarta"
{{ company_phone }}         # "021-5555-1234"
```

---

## 14. Activity Log (`apps/activity_log/`) — `/activity-log/`

**Fungsi:** Sistem **audit trail** — mencatat SEMUA aktivitas user secara otomatis.

### Cara Kerja (Otomatis via Middleware + Signals):
```
┌──────────────────────────────────────────────────────────────┐
│ User melakukan action                                        │
│                                                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ActivityLogMiddleware (middleware.py)                      │ │
│ │ → Catat: user, IP, URL, method, timestamp                 │ │
│ │ → Otomatis untuk SETIAP request                           │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Django Signals (signals.py)                               │ │
│ │ → pre_save: Simpan nilai SEBELUM berubah                  │ │
│ │ → post_save: Bandingkan → catat field yang berubah        │ │
│ │ → post_delete: Catat item yang dihapus                    │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Stock Signals (stock_signals.py)                          │ │
│ │ → Catat detail perubahan stok: gudang, jumlah ±           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Halaman:
| URL | Fungsi |
|-----|--------|
| `/activity-log/` | Timeline SEMUA aktivitas user |

### Data yang Dicatat:
| Field | Contoh |
|-------|--------|
| `user` | admin |
| `action` | UPDATE |
| `model_name` | Produk |
| `object_repr` | "Beras Premium" |
| `changes` | `{"harga_jual": ["15000", "16000"]}` |
| `ip_address` | 192.168.1.100 |
| `timestamp` | 2026-02-23 19:00:00 |

---

## Diagram Koneksi Antar Modul — Detail

```
                     ┌──────────────────────┐
                     │      DASHBOARD       │
                     │  (ringkasan semua)   │
                     └──────────┬───────────┘
                                │ query semua modul
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
    ┌───────────┐       ┌──────────────┐      ┌──────────────┐
    │  PRODUK   │◄──────│  INVENTORY   │      │   LAPORAN    │
    │ (master)  │       │ (stok,gudang)│      │ (aggregate)  │
    └─────┬─────┘       └──────┬───────┘      └──────────────┘
          │                     │                     ▲
     ┌────┴────┐          ┌─────┴─────┐               │
     ▼         ▼          ▼           ▼               │
 ┌────────┐┌────────┐┌────────┐┌──────────┐          │
 │PEMBELIAN││PENJUALAN││ POS  ││ TRANSFER │──────────┘
 │  (PO)  ││  (SO)  ││(kasir)││  STOK    │
 │stok +  ││stok -  ││stok - ││stok ± 0  │
 └────────┘└────────┘└────────┘└──────────┘
       │         │        │
       └─────────┼────────┘
                 ▼
    ┌─────────────────────────┐
    │   MODUL PENDUKUNG       │
    │                         │
    │ ┌────────────────────┐  │
    │ │ ACTIVITY LOG       │  │ ← catat SEMUA aksi (otomatis)
    │ │ (audit trail)      │  │
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ PENGATURAN         │  │ ← konfigurasi: perusahaan, pembayaran, template
    │ │ (settings)         │  │
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ USER MANAGEMENT    │  │ ← kelola akun user
    │ │ + PERMISSION MGMT  │  │ ← kelola role & permission
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ HR MANAGEMENT      │  │ ← karyawan, absensi, gaji
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ AUTOMATION         │  │ ← notifikasi Telegram
    │ │ (Telegram Bot)     │  │
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ AI MANAJEMEN       │  │ ← AI Dashboard + AI Chat Assistant
    │ │ (Business Intel.)  │  │
    │ └────────────────────┘  │
    │ ┌────────────────────┐  │
    │ │ BIAYA              │  │ ← pencatatan pengeluaran
    │ │ (Expenses)         │  │
    │ └────────────────────┘  │
    └─────────────────────────┘
```

---

## Tabel Perubahan Stok — Kapan Stok Berubah?

| Event | Stok Change | Proteksi Concurrency | Contoh |
|-------|-------------|---------------------|--------|
| PO Received | **+ (bertambah)** | `select_for_update()` + `transaction.atomic()` | Terima 100 Beras dari supplier → stok +100 |
| SO Confirmed | **- (berkurang)** | `select_for_update()` + `transaction.atomic()` + validasi stok negatif | Kirim 20 Beras ke customer → stok -20 |
| POS Transaction | **- (berkurang)** | `select_for_update()` + `transaction.atomic()` + validasi stok | Jual 5 Beras via kasir → stok -5 |
| Transfer Stok | **± 0 (pindah)** | `select_for_update()` + `transaction.atomic()` + validasi stok asal | Pindah 30 Beras Jakarta→Surabaya → JKT -30, SBY +30 |
| Stock Adjustment (+) | **+ (bertambah)** | `select_for_update()` + `transaction.atomic()` | Koreksi: bonus, barang ditemukan → stok +10 |
| Stock Adjustment (-) | **- (berkurang)** | `select_for_update()` + `transaction.atomic()` + validasi stok negatif | Koreksi: hilang, rusak, kedaluwarsa → stok -5 |

> **Proteksi Concurrency (Update Maret 2026):** Semua operasi stok sekarang menggunakan `select_for_update()` untuk mengunci baris stok dan `transaction.atomic()` untuk menjamin atomicity. Ini mencegah race condition saat multiple user mengakses stok bersamaan.

### Method yang Mengubah Stok (dengan proteksi concurrency):

```python
# ═══ CONTOH: PurchaseOrder.receive_goods() (apps/pembelian/models.py) ═══
# Update Maret 2026: Dilindungi transaction.atomic() + select_for_update()

def receive_goods(self, user):
    """Terima barang — update stok dengan proteksi race condition."""
    if self.status != 'approved':
        raise ValueError("PO harus disetujui terlebih dahulu")

    # Seluruh proses dalam atomic transaction + select_for_update()
    # untuk mencegah race condition saat multiple user receive bersamaan
    with transaction.atomic():
        for item in self.items.select_related('produk'):
            # Lock baris stok untuk mencegah concurrent write
            stok, _ = Stok.objects.select_for_update().get_or_create(
                produk=item.produk, gudang=self.gudang,
                defaults={'jumlah': 0}
            )
            stok.jumlah += item.jumlah_konversi or item.jumlah
            stok.save()

        self.status = 'received'
        self.save()


# ═══ CONTOH: SalesOrder.confirm_order() (apps/penjualan/models.py) ═══
# Update Maret 2026: Validasi stok negatif + proteksi concurrency

def confirm_order(self, user=None):
    """Konfirmasi order — kurangi stok dengan validasi dan lock."""
    if self.status != 'draft':
        raise ValueError("Hanya order dengan status Draft yang bisa dikonfirmasi")

    with transaction.atomic():
        for item in self.items.select_related('produk'):
            stok = Stok.objects.select_for_update().get(
                produk=item.produk, gudang=self.gudang
            )
            qty_stok = item.jumlah_konversi if item.jumlah_konversi else item.jumlah

            # Validasi: cegah stok negatif
            if stok.jumlah < qty_stok:
                raise ValueError(f"Stok {item.produk.nama} tidak mencukupi")

            stok.jumlah -= qty_stok
            stok.save()

        self.status = 'confirmed'
        self.save()
```

---

## Dependency Map — Modul Mana Bergantung ke Mana?

```
┌─────────────────────────────────────────────────────────────┐
│                   MODULE DEPENDENCY MAP                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LEVEL 0 (Foundation — tanpa dependency):                   │
│    ┌──────────┐  ┌────────────┐  ┌────────────────┐        │
│    │ PENGATURAN│  │ CORE       │  │ ACTIVITY LOG   │        │
│    │           │  │ (template  │  │ (standalone)   │        │
│    │           │  │  tags,     │  │                │        │
│    │           │  │  perms)    │  │                │        │
│    └──────────┘  └────────────┘  └────────────────┘        │
│                                                              │
│  LEVEL 1 (Depends on Foundation):                           │
│    ┌──────────┐  ┌────────────┐                             │
│    │ PRODUK   │  │ USER MGMT  │                             │
│    │          │  │ + PERM MGMT│                             │
│    └──────────┘  └────────────┘                             │
│                                                              │
│  LEVEL 2 (Depends on Produk):                               │
│    ┌──────────┐  ┌────────────┐  ┌──────────┐              │
│    │INVENTORY │  │ PEMBELIAN  │  │PENJUALAN │              │
│    │ (gudang, │  │   (PO)     │  │  (SO)    │              │
│    │  stok)   │  │            │  │          │              │
│    └──────────┘  └────────────┘  └──────────┘              │
│                                                              │
│  LEVEL 3 (Depends on multiple):                             │
│    ┌──────────┐  ┌────────────┐  ┌──────────┐              │
│    │   POS    │  │  LAPORAN   │  │DASHBOARD │              │
│    │ (produk, │  │ (produk,   │  │(semua    │              │
│    │  stok,   │  │  PO, SO,   │  │ modul)   │              │
│    │  bayar)  │  │  stok)     │  │          │              │
│    └──────────┘  └────────────┘  └──────────┘              │
│                                                              │
│  INDEPENDENT (Tidak bergantung ke modul lain):              │
│    ┌──────────┐  ┌────────────┐                             │
│    │   HR     │  │ AUTOMATION │                             │
│    │(karyawan)│  │ (Telegram) │                             │
│    └──────────┘  └────────────┘                             │
│                                                              │
│  CROSS-MODULE (Query data dari banyak modul):               │
│    ┌──────────────────────────┐                             │
│    │ AI MANAJEMEN             │                             │
│    │ (query produk, penjualan,│                             │
│    │  POS, pelanggan, stok,   │                             │
│    │  keuntungan, biaya)      │                             │
│    └──────────────────────────┘                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 15. AI Manajemen (`apps/ai_assistant/`) — `/ai/`

**Fungsi:** Modul kecerdasan buatan untuk **analitik bisnis dan chat assistant**. Terdiri dari 2 sub-modul: **AI Dashboard** (visualisasi skor kesehatan bisnis, prediksi, anomali) dan **AI Assistant** (chatbot cerdas yang memahami konteks data ERP).

### Struktur File:

```
apps/ai_assistant/
├── __init__.py             ← Package marker
├── apps.py                 ← AppConfig
├── models.py               ← AIAssistantConfig (singleton), ChatHistory, ChatFeedback
├── views.py                ← API Chat, AI Dashboard, Pengaturan
├── urls.py                 ← URL routing
├── intents.py              ← Deteksi intent & data gatherers (20+ intent)
├── admin.py                ← Admin panel registration
├── management/
│   └── commands/
│       └── send_weekly_report.py  ← Management command laporan mingguan
└── migrations/             ← Database migrations
```

### Model Database:

```python
AIAssistantConfig   → Singleton: provider (Gemini/OpenAI/Groq), API key, model, temperature
ChatHistory         → Riwayat percakapan per user (mendukung context memory)
ChatFeedback        → Feedback 👍/👎 dari user untuk setiap respons AI
```

### Halaman dan URL:

| URL | View/Fungsi | Fungsi | Permission |
|-----|-------------|--------|------------|
| `/ai/dashboard/` | AIDashboardView | Dashboard analitik AI | ai_assistant.dashboard_ai.read |
| `/ai/` | AIAssistantSettingsView | Pengaturan AI Assistant | ai_assistant.pengaturan_ai.read |
| `/ai/chat/` | ai_chat_api (POST) | API chat AI (AJAX) | Login required |
| `/ai/insight/` | auto_insight (GET) | Auto insight bisnis harian | Login required |
| `/ai/feedback/` | chat_feedback (POST) | Simpan feedback 👍/👎 | Login required |
| `/ai/history/` | chat_history_api (GET) | Load riwayat chat | Login required |
| `/ai/clear/` | clear_history (POST) | Hapus riwayat chat | Login required |

### Provider AI yang Didukung:

| Provider | Model Default | Biaya | Cara Panggil |
|----------|--------------|-------|--------------|
| Google Gemini | gemini-2.0-flash | Gratis (tier awal) | SDK `google.genai` + fallback urllib |
| OpenAI ChatGPT | gpt-4o-mini | Berbayar | REST API via urllib |
| Groq | llama-3.3-70b-versatile | **Gratis** (14.400 req/hari) | REST API OpenAI-compatible |

### Fitur AI Assistant:

#### A. Deteksi Intent Otomatis (20+ intent)

```
User mengetik pertanyaan
     │
     ▼
 detect_intent(message)
     │ → Cocokkan kata kunci dari INTENT_KEYWORDS
     │ → Setiap intent punya daftar kata kunci (bahasa Indonesia + Inggris)
     ▼
 gather_data(intent, message)
     │ → Query ORM sesuai intent
     │ → Parse konteks waktu ("minggu ini", "bulan lalu")
     │ → Return dict ringkasan data
     ▼
 AI API (Gemini/OpenAI/Groq)
     │ → SYSTEM_PROMPT + data bisnis + pertanyaan user
     │ → AI generate respons + Quick Action links
     ▼
 Response JSON → Frontend tampilkan di chat widget
```

**Daftar Intent:**

| Intent | Kata Kunci | Data yang Dikumpulkan |
|--------|-----------|----------------------|
| `penjualan` | penjualan, omzet, revenue | SO + POS, top produk, growth |
| `produk` | produk, barang, item | Total, kategori, stok rendah |
| `stok` | stok, gudang, inventory | Stok per gudang, total |
| `biaya` | biaya, pengeluaran, expense | Total biaya bulan ini |
| `pembelian` | pembelian, PO, purchase | PO pending/received |
| `keuntungan` | laba, profit, untung | Revenue - COGS - biaya |
| `karyawan` | karyawan, HR, gaji | Total, per departemen |
| `pos` | kasir, POS, transaksi | Transaksi hari ini |
| `pelanggan` | pelanggan, customer | Top customer, inactive |
| `analisa_pelanggan` | analisa pelanggan, top customer | Top 10, frekuensi, inactive |
| `laporan_meeting` | laporan meeting, presentasi | Data lengkap semua modul |
| `executive_summary` | executive summary, ringkasan | Ringkasan kuartal |
| `swot` | SWOT, strengths, weakness | Auto SWOT dari data |
| `stok_kritis` | stok habis, low stock | Produk stok 0 dan rendah |
| `margin_produk` | margin produk, profit margin | Margin per produk |
| `laporan_terjadwal` | laporan terjadwal, weekly report | Info setup laporan otomatis |

#### B. Konteks Waktu Cerdas

AI memahami permintaan waktu dalam bahasa Indonesia:
```
"Penjualan hari ini"        → filter today
"Omzet minggu ini"          → filter Monday – Sunday
"Penjualan bulan lalu"      → filter bulan sebelumnya
"Revenue 7 hari terakhir"   → filter 7 hari ke belakang
"Biaya 3 bulan terakhir"    → filter 90 hari ke belakang
```

Fungsi: `_parse_time_context(message)` di `intents.py`

#### C. Quick Action Links

Setiap respons AI menyertakan link navigasi ke halaman ERP yang relevan:
```
📌 Quick Actions:
→ [Lihat Daftar Produk](/produk/list/)
→ [Buka Stok Inventory](/inventory/stok/)
→ [Buka Gudang](/inventory/gudang/)
```

URL map didefinisikan di `SYSTEM_PROMPT` (`views.py`).

#### D. Analisa Pelanggan Mendalam

```python
_gather_analisa_pelanggan():
  → Top 10 customer by total belanja (SO + POS)
  → Customer tidak aktif (30+ hari tanpa transaksi)
  → Frekuensi pembelian per customer
  → Total belanja per customer
  → Rekomendasi strategi retensi
```

#### E. Laporan Terjadwal (Scheduled Reports)

```bash
# Management command: generate laporan mingguan
python manage.py send_weekly_report

# Preview tanpa simpan:
python manage.py send_weekly_report --print-only

# Setup otomatis (Windows Task Scheduler):
schtasks /create /tn "ERP Weekly Report" /tr "python manage.py send_weekly_report" /sc weekly /d MON /st 07:00
```

### AI Dashboard — Widget Analytics:

| Widget | Data | Sumber |
|--------|------|--------|
| Skor Kesehatan Bisnis | Skor 0-100 dari 5 komponen | Revenue, stok, pelanggan, margin, growth |
| Prediksi Revenue | Estimasi bulan depan | Moving average 3 bulan |
| Deteksi Anomali | Perubahan tidak wajar | Perbandingan vs rata-rata |
| Tren Revenue 6 Bulan | Grafik line chart | SalesOrder + POS per bulan |
| Distribusi Stok | Pie chart | Kategori stok (habis/rendah/normal) |
| Insight Otomatis | Rekomendasi AI | Berdasarkan data aktual |

### Koneksi ke Modul Lain:

```
AI Manajemen ──→ Produk (query stok, produk, kategori)
             ──→ Penjualan (query SO, customer, revenue)
             ──→ POS (query transaksi, invoice)
             ──→ Pembelian (query PO, supplier)
             ──→ Inventory (query gudang, stok per gudang)
             ──→ Biaya (query pengeluaran)
             ──→ HR (query karyawan, departemen)
             ──→ Laporan (data agregat untuk AI dashboard)
```

### Konfigurasi AI (Singleton):

```python
# AIAssistantConfig — hanya 1 record di database (pk=1)
config = AIAssistantConfig.load()  # Buat default jika belum ada

config.provider       # 'gemini', 'openai', 'groq'
config.api_key        # API key dari provider
config.model_name     # 'llama-3.3-70b-versatile'
config.temperature    # 0.7 (kreativitas AI)
config.max_tokens     # 1024 (batas panjang respons)
config.aktif          # True/False (on/off fitur AI)
```

### Permission RBAC:

AI Manajemen terintegrasi dengan sistem permission RBAC:
```
RolePermission:
  module = 'ai_assistant'
  sub_module = 'dashboard_ai'    → Akses AI Dashboard
  sub_module = 'pengaturan_ai'   → Akses AI Assistant / Pengaturan

  can_view = True   → Menu muncul di sidebar
  can_create = True → (untuk fitur chat)
  can_edit = True   → (untuk edit pengaturan)
```

---

## 16. Fraud Detection (`apps/fraud_detection/`)

**URL Prefix:** `/fraud/`
**App Label:** `fraud_detection`

**Fungsi:** Modul deteksi anomali kecurangan dan rekonsiliasi kas. Melindungi bisnis dari kerugian akibat manipulasi data, pencurian, atau kesalahan kasir melalui **pemantauan otomatis** dan **blind cash closing**.

### Halaman & URL:
| Halaman | URL | Keterangan |
|---------|-----|------------|
| Dashboard Fraud | `/fraud/` | Ringkasan anomali & statistik keamanan |
| Daftar Anomali | `/fraud/alerts/` | List semua anomali yang terdeteksi |
| Detail Anomali | `/fraud/alerts/<id>/` | Detail lengkap per anomali |
| Rekonsiliasi Kas | `/fraud/cash/` | Daftar blind cash closing |
| Detail Rekonsiliasi | `/fraud/cash/<id>/` | Detail per rekonsiliasi |
| Pengaturan Fraud | `/fraud/settings/` | Konfigurasi aturan deteksi fraud |

### Model Database:

**FraudRule** — Singleton pengaturan pencegahan fraud:
```python
FraudRule:
  blokir_hapus_lunas      # Boolean — blokir aksi hapus transaksi yang sudah lunas
  batas_diskon_persen     # Integer — batas maksimal diskon (%) sebelum dianggap anomali
  batas_void_per_shift    # Integer — batas maksimal void per shift
  batas_selisih_kas       # Decimal — toleransi selisih kas (Rp)
  notif_anomali           # Boolean — kirim notifikasi saat anomali terdeteksi
  updated_at              # DateTime — waktu terakhir diupdate
```

**FraudAlert** — Log anomali terdeteksi:
```python
FraudAlert:
  jenis      # CharField — 'diskon_besar', 'hapus_lunas', 'void_berulang', dll
  severity   # CharField — 'low', 'medium', 'high', 'critical'
  status     # CharField — 'pending', 'investigated', 'cleared', 'rejected'
  nominal    # DecimalField — nominal terkait anomali
  deskripsi  # TextField — penjelasan detail anomali
  user_terkait  # FK → User — user yang melakukan aksi suspicious
  activity      # FK → UserActivity — activity log yang memicu anomali
  created_at    # DateTime — waktu anomali terdeteksi
```

**CashReconciliation** — Rekonsiliasi kas kasir (blind cash closing):
```python
CashReconciliation:
  kasir        # FK → User — kasir yang melakukan tutup kas
  gudang       # FK → Gudang — cabang/outlet
  tanggal      # DateField — tanggal shift
  sistem_kas   # DecimalField — total kas menurut sistem (POS)
  fisik_kas    # DecimalField — total kas fisik yang dihitung kasir
  discrepancy  # DecimalField — selisih (fisik - sistem)
  status       # CharField — 'open', 'closed', 'reviewed'
  catatan      # TextField — catatan manajer/SPV
  created_at   # DateTime
```

### Alur Operasional:

1. **Pengaturan Aturan** → Admin mengkonfigurasi batas via Pengaturan Fraud (FraudRule)
2. **Deteksi Otomatis** → Middleware/Signal mendeteksi anomali saat user melakukan aksi
3. **Alert Dibuat** → Sistem buat FraudAlert dengan severity & detail lengkap
4. **Review Manajer** → Manajer/SPV memeriksa anomali di Daftar Anomali
5. **Tindak Lanjut** → Status diubah: `investigated` → `cleared` (aman) / `rejected` (fraud)
6. **Blind Cash Closing** → Kasir input uang fisik → Sistem bandingkan → Manajer review

### Integrasi dengan Modul Lain:

| Modul | Koneksi |
|-------|--------|
| Activity Log | FraudAlert.activity FK → UserActivity (anomali dipicu oleh activity) |
| POS | CashReconciliation mengacu pada transaksi POS per shift |
| Produk/Gudang | CashReconciliation.gudang FK → Gudang (cabang) |
| AI Assistant | Intent `fraud_detection` → fungsi `_gather_fraud_detection()` mengumpulkan data fraud untuk AI |
| Manajemen Data | Statistik FraudAlert & CashReconciliation ditampilkan, data ikut backup/reset/restore |

### Permission RBAC:

```
RolePermission:
  module = 'fraud_detection'
  sub_module = 'dashboard_fraud'     → Akses Dashboard Fraud
  sub_module = 'daftar_anomali'      → Akses Daftar Anomali
  sub_module = 'rekonsiliasi_kas'    → Akses Rekonsiliasi Kas
  sub_module = 'pengaturan_fraud'    → Akses Pengaturan Fraud

  can_view = True   → Menu muncul di sidebar
  can_create = True → Buat rekonsiliasi baru
  can_edit = True   → Edit uang fisik, tindak lanjut anomali
  can_delete = True → Hapus data
```

---

*Lanjut ke [09_TIPS_DAN_BEST_PRACTICE.md](09_TIPS_DAN_BEST_PRACTICE.md) →*

*Dokumentasi perbaikan UI/UX terbaru: [16_PERBAIKAN_DAN_PENINGKATAN.md](16_PERBAIKAN_DAN_PENINGKATAN.md)*
