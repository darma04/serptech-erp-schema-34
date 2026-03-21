# 🔧 16 — Perbaikan & Peningkatan UI/UX — Catatan Lengkap

## DAFTAR ISI
- [A. Ringkasan Perubahan](#a-ringkasan-perubahan)
- [B. Laporan Keuangan — Export Excel & PDF](#b-laporan-keuangan)
- [C. Dashboard — Perbaikan Mobile & Responsive](#c-dashboard-responsive)
- [D. Dark Mode — Perbaikan Kontras & Sidebar](#d-dark-mode)
- [E. Metode Pembayaran — Halaman List](#e-metode-pembayaran-list)
- [F. Metode Pembayaran — Halaman Detail](#f-metode-pembayaran-detail)
- [G. Invoice Detail — Tabel Bordered](#g-invoice-detail)
- [H. Pola Desain yang Digunakan](#h-pola-desain)
- [I. PO/SO Form — Auto-Product-Creation](#i-po-so-auto-product)
- [J. Transfer Stock — Select2 AJAX Searchable](#j-transfer-stock-select2)
- [K. Roles Table — Filtering & Actions](#k-roles-table)
- [L. Auth Localization — Bahasa Indonesia](#l-auth-localization)
- [M. Back Navigation — history.back()](#m-back-navigation)
- [N. Permission System — Caching Optimasi](#n-permission-caching)
- [O. POS Layout — Kasir, Customer Autocomplete, Responsive](#o-pos-layout)
- [P. Dashboard — Simplifikasi Layout & Wave Chart](#p-dashboard-simplifikasi)
- [Q. POS — Star Rating, Scrollbar, Category Pills](#q-pos-star-rating)
- [R. Audit Keamanan — Concurrency, Race Condition & Validasi Stok](#r-audit-keamanan)
- [S. Dashboard Chart — Smart Aggregation & Filter Waktu Cabang](#s-dashboard-chart-smart-aggregation)

---

## A. Ringkasan Perubahan

Berikut ringkasan semua perbaikan dan peningkatan yang telah dilakukan pada sistem ERP, mulai dari modul Laporan Keuangan hingga perbaikan terakhir pada halaman Invoice Detail:

| No | Area | File Utama | Perubahan |
|----|------|-----------|-----------|
| 1 | Laporan Keuangan | `laporan/` templates & views | Standardisasi export Excel & PDF di 14+ halaman |
| 2 | Dashboard | `dashboard/index.html` | Perbaikan layout mobile, spacing kartu statistik |
| 3 | Dark Mode | `layout/partials/styles.html` | Perbaikan kontras teks, sidebar, tabel, form |
| 4 | Metode Pembayaran List | `metode_pembayaran_list.html` | Kolom Nama Pemilik, ringkasan footer, filter card |
| 5 | Metode Pembayaran Detail | `metode_pembayaran_detail.html` | Logo besar 240px, layout list-group, mobile spacing |
| 6 | Invoice Detail | `pos/invoice_detail.html` | Tabel bordered dengan rounded corners |
| 7 | PO/SO Form | `pembelian/views.py`, `penjualan/views.py` | Auto-create produk baru dari PO, SKU auto-generate, markup 20% |
| 8 | Transfer Stock | `inventory/transfer_stok_form.html` | Select2 AJAX searchable dropdown untuk produk |
| 9 | Roles Table | `access/role_list.html` | Filtering lengkap, actions column, responsive |
| 10 | Auth Localization | `auth/login.html`, `register.html` | Pesan error Bahasa Indonesia, dynamic branding |
| 11 | Back Navigation | `user_management/` templates | Tombol Kembali pakai `history.back()` |
| 12 | Permission Caching | `apps/core/permissions.py` | Caching 30 detik, 1 query/role vs 20-40 query/page |
| 13 | POS Layout | `templates/pos/index.html`, `apps/pos/views.py` | Pilih Kasir Select2, customer autocomplete, 3-column mobile grid, dark mode border, responsive spacing |
| 14 | Dashboard Simplifikasi | `dashboard/index.html`, `dashboard/views.py` | Hapus 5 section (pembelian, biaya, slider, keuntungan/cabang, biaya/kategori), wave chart cabang, filter waktu icon navbar, pengguna terbaru 100% lebar, 1 inisial avatar |
| 15 | POS Estetika | `pos/index.html`, `pos/views.py` | Star rating bintang 1-5, custom scrollbar, category pills restyling, hapus badge kasir, harga/nama same font size |
| 16 | Audit Keamanan & Concurrency | `inventory/models.py`, `penjualan/models.py`, `pembelian/models.py`, `pos/models.py`, `biaya/models.py`, `pos/views.py`, `penjualan/views.py`, `pembelian/views.py`, `laporan/views.py` | Fix race condition stok, nomor duplikat, stok negatif, SO edit protection, PO filter fix, POS limit fix |
| 17 | Dashboard Chart Smart Aggregation | `dashboard/views.py` | Smart Aggregation harian/bulanan, filter waktu cabang_stats, default values chart |

---

## B. Laporan Keuangan — Export Excel & PDF

### Apa yang Diperbaiki?

Sebelumnya, export Excel menggunakan format CSV biasa yang tidak mempertahankan ringkasan (RINGKASAN) data. Export PDF belum ada branding perusahaan.

### Perubahan:

```
SEBELUM:
├── Export Excel → CSV biasa (hanya data mentah)
├── Export PDF  → Tidak ada branding
└── Format      → Tidak konsisten antar halaman

SESUDAH:
├── Export Excel → HTML Table format (.xls) dengan RINGKASAN
│   → Kolom terpisah untuk total, rata-rata, dll
│   → Header tabel dengan styling
├── Export PDF  → pdfMake dengan branding perusahaan
│   → Logo, nama, alamat perusahaan di header
│   → Tabel data terformat rapi
└── Format      → Konsisten di 14+ halaman CRUD & laporan
```

### File yang Dimodifikasi:

```
templates/
├── produk/
│   ├── produk_list.html         → Export Excel & PDF produk
│   ├── kategori_list.html       → Export Excel & PDF kategori
│   └── satuan_list.html         → Export Excel & PDF satuan
├── inventory/
│   ├── gudang_list.html         → Export Excel & PDF gudang
│   ├── stok_list.html           → Export Excel & PDF stok
│   └── transfer_stok_list.html  → Export Excel & PDF transfer
├── pembelian/
│   └── purchase_order_list.html → Export Excel & PDF PO
├── penjualan/
│   └── sales_order_list.html    → Export Excel & PDF SO
├── pos/
│   └── invoice_list.html        → Export Excel & PDF invoice
├── biaya/
│   └── biaya_list.html          → Export Excel & PDF biaya
├── laporan/
│   ├── laporan_produk.html      → Export Excel & PDF laporan produk
│   ├── laporan_stok.html        → Export Excel & PDF laporan stok
│   ├── laporan_penjualan.html   → Export Excel & PDF penjualan
│   └── laporan_pembelian.html   → Export Excel & PDF pembelian
└── pengaturan/
    └── metode_pembayaran_list.html → Export Excel & PDF metode
```

### Pola Export Excel (HTML Table):

```javascript
// ═══ POLA EXPORT EXCEL STANDAR ═══
// Digunakan di SEMUA halaman list yang punya tombol Export

function exportToExcel() {
    // 1. Buat HTML table dengan header
    let html = '<table>';
    
    // 2. Header perusahaan (dari context Django)
    html += '<tr><td colspan="7" style="font-size:16pt;font-weight:bold;">';
    html += '{{ company_settings.nama_perusahaan }}';
    html += '</td></tr>';
    
    // 3. Header kolom tabel
    html += '<tr>';
    html += '<th style="background:#696CFF;color:white;">No</th>';
    html += '<th style="background:#696CFF;color:white;">Nama</th>';
    // ... kolom lainnya
    html += '</tr>';
    
    // 4. Data baris dari DataTables
    var table = $('#myTable').DataTable();
    table.rows().every(function() {
        var data = this.data();
        html += '<tr>';
        html += '<td>' + data[0] + '</td>';
        // ... kolom lainnya
        html += '</tr>';
    });
    
    // 5. RINGKASAN di bawah tabel
    html += '<tr><td colspan="4" style="font-weight:bold;">RINGKASAN</td></tr>';
    html += '<tr><td>Total Saldo:</td><td>' + totalSaldo + '</td></tr>';
    
    html += '</table>';
    
    // 6. Download sebagai .xls
    var blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'laporan.xls';
    a.click();
}
```

### Pola Export PDF (pdfMake):

```javascript
// ═══ POLA EXPORT PDF STANDAR ═══
// Menggunakan library pdfMake yang sudah di-load global

function exportToPDF() {
    // 1. Definisi dokumen
    var docDefinition = {
        pageOrientation: 'landscape',
        
        // 2. Header perusahaan
        content: [
            {
                text: '{{ company_settings.nama_perusahaan }}',
                style: 'header'
            },
            {
                text: '{{ company_settings.alamat }}',
                style: 'subheader'
            },
            
            // 3. Tabel data
            {
                table: {
                    headerRows: 1,
                    widths: ['auto', '*', 'auto', 'auto'],
                    body: [
                        // Header
                        [
                            { text: 'No', style: 'tableHeader' },
                            { text: 'Nama', style: 'tableHeader' },
                            // ... kolom lainnya
                        ],
                        // Data rows (diisi dari DataTables)
                    ]
                }
            }
        ],
        
        // 4. Styling
        styles: {
            header: { fontSize: 16, bold: true, color: '#696CFF' },
            subheader: { fontSize: 10, color: '#666' },
            tableHeader: {
                bold: true,
                fillColor: '#696CFF',
                color: 'white'
            }
        }
    };
    
    // 5. Generate & download
    pdfMake.createPdf(docDefinition).download('laporan.pdf');
}
```

---

## C. Dashboard — Perbaikan Mobile & Responsive

### Apa yang Diperbaiki?

Pada tampilan mobile (< 576px), kartu-kartu statistik dashboard saling bertumpuk tanpa jarak, dan grafik chart overflow keluar layar.

### Perubahan di `dashboard/index.html`:

```html
<!-- ═══ SEBELUM: Kartu statistik tanpa spacing mobile ═══ -->
<div class="col-sm-6 col-xl-3">
    <div class="card">...</div>
</div>

<!-- ═══ SESUDAH: Tambah margin untuk mobile ═══ -->
<div class="col-sm-6 col-xl-3 mb-3 mb-xl-0">
    <!-- mb-3      = margin-bottom di HP (spacing antar kartu) -->
    <!-- mb-xl-0   = HAPUS margin di desktop (kartu sejajar) -->
    <div class="card">...</div>
</div>
```

### Perubahan di `styles.html` (CSS Responsive):

```css
/* ═══ FIX: Dashboard card spacing di mobile ═══ */
@media (max-width: 576px) {
    /* Kurangi padding container */
    .container-xxl.container-p-y {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    
    /* Chart tidak overflow */
    .apexcharts-canvas {
        max-width: 100% !important;
    }
    
    /* Kartu statistik lebih compact */
    .card-body {
        padding: 1rem !important;
    }
}
```

### Kenapa `!important`?

```
Sneat core.css memiliki specificity tinggi:
  .layout-wrapper .content-wrapper .container-xxl { padding: 1.625rem; }
  specificity = 0,0,3,0

CSS kita di styles.html:
  .container-xxl.container-p-y { padding: 0.75rem; }
  specificity = 0,0,2,0  ← KALAH!

Solusi: tambah !important agar CSS kita menang:
  .container-xxl.container-p-y { padding: 0.75rem !important; }
  → !important SELALU menang, apapun specificity-nya
```

---

## D. Dark Mode — Perbaikan Kontras & Sidebar

### Apa yang Diperbaiki?

Saat dark mode diaktifkan (`data-theme="dark"`), beberapa elemen memiliki kontras rendah — teks sulit dibaca, border tidak terlihat, dan sidebar terlalu gelap.

### Daftar Perbaikan CSS di `styles.html`:

```css
/* ═══ FIX 1: Sidebar menu text di dark mode ═══ */
[data-theme="dark"] .menu-inner .menu-item .menu-link {
    color: rgba(255, 255, 255, 0.8) !important;
    /* Sebelum: teks abu-abu terlalu gelap di background gelap */
    /* Sesudah: teks putih 80% opacity — kontras tinggi */
}

[data-theme="dark"] .menu-inner .menu-item.active > .menu-link {
    color: #ffffff !important;
    /* Menu aktif: putih penuh untuk penekanan */
}

/* ═══ FIX 2: Card background di dark mode ═══ */
[data-theme="dark"] .card {
    background-color: #2b2c40 !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    /* Sebelum: card nyaris tidak terlihat di background gelap */
    /* Sesudah: card sedikit lebih terang dari background */
}

/* ═══ FIX 3: Tabel di dark mode ═══ */
[data-theme="dark"] .table > :not(caption) > * > * {
    color: rgba(255, 255, 255, 0.87) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    /* Teks tabel: putih 87% — standar Material Design untuk dark */
    /* Border: putih 12% — garis halus tapi masih terlihat */
}

[data-theme="dark"] .table-light,
[data-theme="dark"] .bg-label-secondary {
    background-color: rgba(255, 255, 255, 0.08) !important;
    /* Header tabel: sedikit lebih terang dari body */
}

/* ═══ FIX 4: Form input di dark mode ═══ */
[data-theme="dark"] .form-control,
[data-theme="dark"] .form-select {
    background-color: #2b2c40 !important;
    color: #e0e0e0 !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
}

/* ═══ FIX 5: Modal dialog di dark mode ═══ */
[data-theme="dark"] .modal-content {
    background-color: #2b2c40 !important;
}

/* ═══ FIX 6: Dropdown di dark mode ═══ */
[data-theme="dark"] .dropdown-menu {
    background-color: #2b2c40 !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

[data-theme="dark"] .dropdown-item {
    color: rgba(255, 255, 255, 0.8) !important;
}

[data-theme="dark"] .dropdown-item:hover {
    background-color: rgba(105, 108, 255, 0.16) !important;
}
```

### Cara Kerja Dark Mode di Sneat:

```
1. User klik toggle dark mode (di navbar → template customizer)

2. JavaScript menambah atribut ke <html>:
   <html data-theme="dark" data-style="dark">

3. Sneat CSS otomatis switch:
   core.css    → core-dark.css (CSS variables berubah)
   --bs-body-bg: #232333    ← background gelap
   --bs-body-color: #CFD3EC ← teks terang

4. CSS kita di styles.html menggunakan selector:
   [data-theme="dark"] .target { ... }
   → HANYA aktif saat dark mode ON

5. Saat user switch ke light:
   <html data-theme="light">
   → Selector [data-theme="dark"] TIDAK MATCH
   → CSS dark mode kita TIDAK aktif
```

---

## E. Metode Pembayaran — Halaman List

**File:** `templates/pengaturan/metode_pembayaran_list.html`

### Perubahan 1: Kolom "Nama Pemilik" Baru

```html
<!-- ═══ SEBELUM: 10 kolom (tanpa Nama Pemilik) ═══ -->
<thead>
    <tr>
        <th>Gambar</th>
        <th>Nama</th>
        <!-- langsung ke Kode -->
        <th>Kode</th>
        ...
    </tr>
</thead>

<!-- ═══ SESUDAH: 11 kolom (dengan Nama Pemilik) ═══ -->
<thead>
    <tr>
        <th>Gambar</th>
        <th>Nama</th>
        <th>Nama Pemilik</th>  <!-- ← KOLOM BARU -->
        <th>Kode</th>
        ...
    </tr>
</thead>
```

**Dampak penambahan kolom:**
```
Semua indeks kolom di JavaScript bergeser +1:
  Kolom Kode:      index 3 → index 4
  Kolom Saldo:     index 4 → index 5
  Kolom Pendapatan: index 5 → index 6
  ... dan seterusnya

Hal yang perlu diupdate:
  ✓ DataTables columnDefs (orderable, sortable)
  ✓ Export Excel (kolom mapping)
  ✓ Export PDF (kolom mapping)
  ✓ Filter column visibility
  ✓ Footer ringkasan colspan
```

### Perubahan 2: Ringkasan Footer Sejajar

```html
<!-- ═══ SEBELUM: Ringkasan di satu kolom gabungan ═══ -->
<tfoot>
    <tr>
        <td colspan="6">
            <strong>RINGKASAN</strong>
            <!-- Semua total di satu tempat — tidak sejajar dengan kolom -->
        </td>
    </tr>
</tfoot>

<!-- ═══ SESUDAH: Setiap total sejajar dengan kolomnya ═══ -->
<tfoot class="table-footer-summary">
    <tr>
        <!-- Kolom 1-4: Label RINGKASAN -->
        <td colspan="4" class="text-start ps-4">
            <strong>RINGKASAN</strong>
            <small>(dari semua data)</small>
        </td>
        <!-- Kosong untuk kolom Nama Pemilik -->
        <td></td>
        <!-- Total Saldo — SEJAJAR dengan kolom Saldo di thead -->
        <td class="text-end fw-bold">
            {{ ringkasan.total_saldo|rupiah }}
        </td>
        <!-- Total Pendapatan — sejajar dengan kolom Pendapatan -->
        <td class="text-end fw-bold text-success">
            {{ ringkasan.total_pendapatan|rupiah }}
        </td>
        <!-- Total Pengeluaran — sejajar dengan kolom Pengeluaran -->
        <td class="text-end fw-bold text-danger">
            {{ ringkasan.total_pengeluaran|rupiah }}
        </td>
        <!-- Total Transaksi — sejajar dengan kolom Transaksi -->
        <td class="text-end fw-bold">
            {{ ringkasan.total_transaksi }}
        </td>
        <!-- Kosong untuk Status, Dibuat Pada, Aksi -->
        <td colspan="3"></td>
    </tr>
</tfoot>
```

### Perubahan 3: Filter Card yang Lebih Lengkap

```html
<!-- ═══ Filter card baru: 4 elemen dalam satu baris ═══ -->
<div class="card mb-4">
    <div class="card-body">
        <div class="row g-3 align-items-end">
            
            <!-- 1. Filter Status (Dropdown) -->
            <div class="col-md-3 col-sm-6">
                <label class="form-label">Status</label>
                <select class="form-select" id="filterStatus">
                    <option value="">Semua Status</option>
                    <option value="Aktif">Aktif</option>
                    <option value="Nonaktif">Nonaktif</option>
                </select>
            </div>
            
            <!-- 2. Filter Nama Pemilik (Input) -->
            <div class="col-md-3 col-sm-6">
                <label class="form-label">Nama Pemilik</label>
                <input type="text" class="form-control" 
                       id="filterPemilik" placeholder="Cari pemilik...">
            </div>
            
            <!-- 3. Pilih Kolom (Dropdown Checklist) -->
            <div class="col-md-3 col-sm-6">
                <label class="form-label">Pilih Kolom</label>
                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle w-100"
                            data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        Pilih Kolom
                    </button>
                    <ul class="dropdown-menu">
                        <!-- Checkbox untuk setiap kolom -->
                        <li><label class="dropdown-item">
                            <input type="checkbox" checked 
                                   data-column="0"> Gambar
                        </label></li>
                        <!-- ... kolom lainnya -->
                    </ul>
                </div>
            </div>
            
            <!-- 4. Tombol Reset -->
            <div class="col-md-3 col-sm-6">
                <button class="btn btn-label-danger w-100" 
                        id="resetFilter">
                    <i class="ri-refresh-line me-1"></i>Reset Filter
                </button>
            </div>
            
        </div>
    </div>
</div>
```

**JavaScript untuk filter:**

```javascript
// ═══ Filter Status (dropdown) ═══
$('#filterStatus').on('change', function() {
    // column(8) = kolom Status (index 8 setelah tambah Nama Pemilik)
    table.column(8).search(this.value).draw();
});

// ═══ Filter Nama Pemilik (input text) ═══
$('#filterPemilik').on('keyup', function() {
    // column(2) = kolom Nama Pemilik (index 2)
    table.column(2).search(this.value).draw();
});

// ═══ Toggle Kolom (checkbox) ═══
$('[data-column]').on('change', function() {
    var colIndex = $(this).data('column');
    var column = table.column(colIndex);
    column.visible(!column.visible());
    // checked → kolom tampil, unchecked → kolom tersembunyi
});

// ═══ Reset Filter ═══
$('#resetFilter').on('click', function() {
    $('#filterStatus').val('').trigger('change');
    $('#filterPemilik').val('');
    table.search('').columns().search('').draw();
    // Semua filter di-reset ke default
});
```

---

## F. Metode Pembayaran — Halaman Detail

**File:** `templates/pengaturan/metode_pembayaran_detail.html`

### Perubahan: Redesain Bagian "Informasi Metode Pembayaran"

**Prinsip desain:** Menggunakan `list-group-flush` untuk menciptakan baris-baris informasi yang rapi, dengan label di kiri dan nilai di kanan — mirip dengan tabel tapi tanpa menggunakan `<table>`.

```html
<!-- ═══ SEBELUM: Grid layout dengan label di atas value ═══ -->
<div class="row g-3">
    <div class="col-md-6">
        <small class="text-muted">Nama Metode:</small>
        <div class="fw-medium">{{ metode.nama }}</div>
    </div>
    <div class="col-md-6">
        <small class="text-muted">Nama Pemilik:</small>
        <div class="fw-medium">{{ metode.nama_pemilik }}</div>
    </div>
    <!-- Label DI ATAS value = tidak sejajar, boros ruang vertikal -->
</div>

<!-- ═══ SESUDAH: List-group dengan label kiri, value kanan ═══ -->
<div class="row g-4 align-items-stretch">
    
    <!-- Kolom Kiri: Logo Besar -->
    <div class="col-12 col-sm-4 d-flex flex-column">
        <label class="form-label text-muted mb-2 text-center">Logo</label>
        <div class="flex-grow-1 d-flex align-items-center justify-content-center">
            {% if metode.gambar %}
            <img src="{{ metode.gambar.url }}" 
                 style="width: 240px; height: 240px; object-fit: contain;">
            <!-- 240px = lebih besar dari sebelumnya (180px) -->
            {% else %}
            <div style="width: 240px; height: 240px;">
                <i class="ri-wallet-3-line" style="font-size: 5rem;"></i>
            </div>
            {% endif %}
        </div>
    </div>
    
    <!-- Kolom Kanan: Info Detail -->
    <div class="col-12 col-sm-8 d-flex flex-column">
        <ul class="list-group list-group-flush flex-grow-1">
            <!-- Setiap baris: label kiri, value kanan -->
            <li class="list-group-item d-flex justify-content-between 
                        align-items-center py-3">
                <span class="text-muted">Nama Metode</span>
                <span class="fw-bold">{{ metode.nama }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between 
                        align-items-center py-3">
                <span class="text-muted">Nama Pemilik</span>
                <span class="fw-bold">{{ metode.nama_pemilik }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between 
                        align-items-center py-3">
                <span class="text-muted">Kode</span>
                <code class="bg-label-info px-2 py-1 rounded">
                    {{ metode.kode }}
                </code>
            </li>
            <!-- ... Status, Deskripsi, Dibuat, Terakhir Diubah -->
        </ul>
    </div>
</div>
```

### Kenapa `list-group-flush`?

```
list-group       = daftar item Bootstrap dengan border atas-bawah
list-group-flush = TANPA border luar (menyatu dengan card induk)

Struktur yang dihasilkan:
┌──────────────────────────────────────────────────┐
│ Informasi Metode Pembayaran                      │
├────────────────┬─────────────────────────────────┤
│                │ Nama Metode          Dana       │
│    ┌────┐      │─────────────────────────────────│
│    │LOGO│      │ Nama Pemilik    Darma Gunawan   │
│    │240 │      │─────────────────────────────────│
│    │px  │      │ Kode           0882006663601    │
│    └────┘      │─────────────────────────────────│
│                │ Status              ✓ Aktif     │
│                │─────────────────────────────────│
│                │ Deskripsi       E-Wallet Indo    │
│                │─────────────────────────────────│
│                │ Dibuat       06 Feb 2026, 12:19 │
└────────────────┴─────────────────────────────────┘
```

### Class CSS Penting:

```
align-items-stretch  → Logo dan info sama tinggi
flex-grow-1          → Info mengisi sisa ruang vertikal
justify-content-between → Label kiri, value kanan
py-3                 → Padding atas-bawah seragam per baris
```

---

## G. Invoice Detail — Tabel Bordered

**File:** `templates/pos/invoice_detail.html`

### Apa yang Diperbaiki?

Tabel item invoice sebelumnya menggunakan `table-hover` tanpa border — kurang rapi dan tidak konsisten dengan style halaman detail lainnya.

### Perubahan:

```html
<!-- ═══ SEBELUM: Tabel tanpa border ═══ -->
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <!-- Header dengan background abu-abu bawaan -->
        </thead>
        <tfoot class="table-light">
            <tr class="table-primary">
                <!-- Baris total -->
            </tr>
        </tfoot>
    </table>
</div>

<!-- ═══ SESUDAH: Tabel dengan border rapi ═══ -->
<div class="table-responsive border rounded-3">
    <!-- border rounded-3 = border luar melengkung -->
    <table class="table table-bordered mb-0">
        <!-- table-bordered = border di SETIAP sel -->
        <!-- mb-0 = tanpa margin bawah (menyatu dengan border luar) -->
        <thead>
            <tr>
                <th class="bg-label-secondary" style="width: 50px;">No</th>
                <th class="bg-label-secondary">Produk</th>
                <th class="bg-label-secondary text-end">Harga</th>
                <th class="bg-label-secondary text-center">Qty</th>
                <th class="bg-label-secondary text-end">Diskon</th>
                <th class="bg-label-secondary text-end">Subtotal</th>
                <!-- bg-label-secondary = background abu-abu muda transparan -->
            </tr>
        </thead>
        <tfoot>
            <tr class="bg-label-primary">
                <!-- bg-label-primary = background ungu muda transparan -->
                <td colspan="5" class="text-end fw-bold h5 mb-0">Total:</td>
                <td class="text-end fw-bold h5 mb-0 text-primary">
                    {{ transaction.total_harga|rupiah }}
                </td>
            </tr>
        </tfoot>
    </table>
</div>
```

### Perbedaan Visual:

```
SEBELUM (table-hover, tanpa border):
┌────────────────────────────────────────────┐
  NO   PRODUK          HARGA    QTY   SUB
  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  1    Diamond ML     75,000   10    750,000
  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                          Total:    750,000
└────────────────────────────────────────────┘

SESUDAH (table-bordered, rounded-3):
╭────┬──────────────┬────────┬─────┬────────╮
│ NO │ PRODUK       │ HARGA  │ QTY │ SUB    │  ← bg-label-secondary
├────┼──────────────┼────────┼─────┼────────┤
│ 1  │ Diamond ML   │ 75,000 │ 10  │750,000 │
├────┴──────────────┴────────┴─────┼────────┤
│                      Subtotal:   │750,000 │
├──────────────────────────────────┼────────┤
│                         Total:   │750,000 │  ← bg-label-primary
╰──────────────────────────────────┴────────╯
```

### Bug yang Diperbaiki:

```html
<!-- BUG: Tag </td> hilang pada kolom Qty -->
<!-- Sebelum: -->
<td class="text-center">{{ item.jumlah }} {{ item.produk.satuan.nama }}
<td class="text-end">{{ item.diskon|rupiah }}</td>
<!-- ↑ Tidak ada </td> sebelum <td> berikutnya! -->
<!-- Browser mungkin auto-close, tapi ini INVALID HTML -->

<!-- Sesudah (diperbaiki): -->
<td class="text-center">{{ item.jumlah }} {{ item.produk.satuan.nama }}</td>
<!-- ↑ Tag </td> ditambahkan → HTML valid -->
<td class="text-end">{{ item.diskon|rupiah }}</td>
```

---

## H. Pola Desain yang Digunakan

### 1. Pola List-Group untuk Halaman Detail

Kapan menggunakan `list-group` vs `table`:

```
list-group-flush → Halaman DETAIL (satu objek)
    Cocok untuk: label-value pair
    Contoh: Detail Metode Pembayaran, Profil User
    ✓ Mudah responsive (label & value bisa stack di mobile)
    ✓ Padding & spacing mudah dikontrol
    ✓ Tidak perlu <th>, <td> — lebih semantik

table-bordered → Halaman LIST (banyak objek / item)
    Cocok untuk: data tabular (baris x kolom)
    Contoh: Daftar Produk, Item Invoice
    ✓ Border memisahkan sel dengan jelas
    ✓ Sort, filter, pagination via DataTables
    ✓ Export mudah (sudah format tabel)
```

### 2. Pola Wrapper Border Rounded

```html
<!-- Pola: border rounded di wrapper, mb-0 di tabel -->
<div class="table-responsive border rounded-3">
    <table class="table table-bordered mb-0">
        ...
    </table>
</div>

<!-- Kenapa mb-0?
     table Bootstrap default punya margin-bottom: 1rem
     Ini menyebabkan GAP antara tabel dan border wrapper bawah
     mb-0 menghilangkan gap tersebut
-->
```

### 3. Pola bg-label-* untuk Header/Footer

```
bg-label-primary   → Ungu muda transparan (rgba ~16%)
bg-label-secondary → Abu-abu muda transparan
bg-label-success   → Hijau muda transparan
bg-label-danger    → Merah muda transparan
bg-label-info      → Biru muda transparan
bg-label-warning   → Kuning muda transparan

Kelebihan vs bg-primary:
  bg-primary   → Background 100% solid (teks HARUS putih)
  bg-label-primary → Background transparan (teks tetap gelap/terang)
  → Lebih halus, cocok untuk header tabel & badge
```

### 4. Pola Responsive Spacing

```html
<!-- Pola: Margin mobile, hapus di desktop -->
<div class="col-xl-4 mt-4 mt-xl-0">
    <!-- mt-4     = margin-top di mobile (jarak dari elemen atas) -->
    <!-- mt-xl-0  = HAPUS margin-top di desktop XL (elemen sejajar) -->
</div>

<!-- Kapan pakai?
     Saat dua kolom yang sejajar di desktop tapi STACK di mobile
     Di mobile, elemen bawah butuh spacing dari elemen atas
     Di desktop, elemen sejajar → tidak perlu spacing vertikal
-->
```

---

## I. PO/SO Form — Auto-Product-Creation

### Apa yang Diperbaiki?

Saat membuat Purchase Order (PO) baru, user bisa langsung menginput nama produk **yang belum ada di database**. Sistem otomatis membuat record Produk baru.

### Alur Kerja PO Create:

```
1. User input nama produk, jumlah, harga di form PO
2. Untuk SETIAP item:
   a. Buat record Produk baru:
      - SKU auto-generate: PRD-xxxxxxxxxx (10 digit random)
      - Harga jual = harga_beli × 1.2 (markup 20%)
      - Kategori & satuan dari dropdown (fallback ke yang pertama)
   b. Buat PurchaseOrderItem (relasi PO → Produk)
   c. Update Stok langsung di gudang tujuan
3. PO status langsung 'received' (simplified workflow)
4. Kirim notifikasi Telegram (opsional)
5. Log ke activity_log
```

### File yang Terlibat:

```
apps/pembelian/views.py     → PurchaseOrderCreateView.form_valid()
apps/pembelian/forms.py     → PurchaseOrderForm
apps/produk/models.py       → Produk, Stok (auto-created)
templates/pembelian/        → purchase_order_form.html (JS add row)
```

### Fitur Unik — Hapus PO Rollback:

Saat PO dihapus (`PurchaseOrderDeleteView`), sistem juga:
- Rollback stok (kurangi jumlah dari gudang)
- Hapus produk orphan (produk yang hanya ada di PO ini, tidak di SO/POS/transfer)

---

## J. Transfer Stock — Select2 AJAX Searchable

### Apa yang Diperbaiki?

Dropdown produk di form Transfer Stok diganti dari `<select>` biasa ke **Select2 AJAX searchable**. User bisa mengetik nama/SKU produk dan hasil pencarian diambil secara dinamis dari API.

### Implementasi:

```javascript
// Di template transfer_stok_form.html
$('.select2-produk').select2({
    ajax: {
        url: '/api/produk/search/',  // API endpoint
        dataType: 'json',
        delay: 250,                  // Debounce 250ms
        data: function(params) {
            return { q: params.term }; // Kirim query pencarian
        },
        processResults: function(data) {
            return { results: data.results };
        }
    },
    minimumInputLength: 2,  // Minimal 2 karakter sebelum search
    placeholder: 'Cari produk...',
    allowClear: true
});
```

### Dampak:
- User tidak perlu scroll ratusan produk di dropdown
- Pencarian lebih cepat dan akurat
- Formset add/remove row tetap bekerja dengan Select2

---

## K. Roles Table — Filtering & Actions

### Apa yang Diperbaiki?

Tabel Roles di halaman Permission Management diperbaiki agar memiliki:
1. **Actions column** — tombol Edit dan Delete per baris berfungsi
2. **Filter card** — pencarian dan filter lengkap seperti di Produk List
3. **Responsive** — tidak ada horizontal scroll pada desktop

### Pola Filter yang Digunakan:

```html
<!-- Filter card mirip pola CRUD standar -->
<div class="card mb-4">
    <div class="card-body">
        <div class="row g-3 align-items-end">
            <div class="col-md-4">
                <input type="text" id="searchRole" placeholder="Cari role...">
            </div>
            <div class="col-md-2">
                <button onclick="resetFilter()">Reset</button>
            </div>
        </div>
    </div>
</div>
```

---

## L. Auth Localization — Bahasa Indonesia

### Apa yang Diperbaiki?

Halaman Login, Register, dan Forgot Password dilokalisasi ke **Bahasa Indonesia** sepenuhnya:

### Perubahan Pesan Error:

```python
# File: auth/login/views.py — SEBELUM (English)
messages.error(request, "Invalid username or password.")

# File: auth/login/views.py — SESUDAH (Indonesia)
messages.error(request, "Username atau kata sandi salah.")
messages.error(request, "Silakan masukkan username dan kata sandi Anda.")
messages.error(request, "Email tidak ditemukan dalam sistem.")
messages.error(request, "Username tidak ditemukan dalam sistem.")
```

### Dynamic Branding:

Halaman auth menggunakan `company_settings` dari context processor untuk menampilkan nama dan logo perusahaan secara dinamis, bukan hardcoded.

### File yang Diubah:

```
auth/login/views.py         → Pesan error Bahasa Indonesia
auth/register/views.py      → Pesan error Bahasa Indonesia
auth/forgot_password/views.py → Pesan error Bahasa Indonesia
templates/auth/login.html    → Layout & teks Bahasa Indonesia
templates/auth/register.html → Layout & teks Bahasa Indonesia
```

---

## M. Back Navigation — history.back()

### Apa yang Diperbaiki?

Tombol "Kembali" di halaman Edit User dan View User Details sebelumnya selalu redirect ke User Management (`/users/`). Setelah perbaikan, tombol menggunakan `history.back()` sehingga kembali ke halaman **sebelumnya** (bisa Role CRUD, bisa User List, tergantung dari mana user datang).

### Perubahan:

```html
<!-- SEBELUM: Hardcoded URL -->
<a href="{% url 'user_management:list' %}" class="btn btn-secondary">
    Kembali
</a>

<!-- SESUDAH: Dynamic back -->
<a href="javascript:history.back()" class="btn btn-secondary">
    Kembali
</a>
```

---

## N. Permission System — Caching Optimasi

### Apa yang Diperbaiki?

Sistem permission sebelumnya melakukan **1 query database per-pengecekan**. Satu halaman bisa mengecek 20-40 permission (sidebar menu, tombol aksi, filter tabel), menghasilkan **20-40 query HANYA untuk permission**.

### Solusi — Cache per Role:

```python
# File: apps/core/permissions.py

def _get_role_permissions_cache(role):
    """Load SEMUA permission role dalam 1 query, cache 30 detik."""
    from django.core.cache import cache
    
    cache_key = f'role_perms_{role}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached  # Cache HIT
    
    # Cache MISS → 1 query untuk SEMUA permission
    all_perms = RolePermission.objects.filter(role__iexact=role).values(...)
    perms_dict = {}  # {(module, sub): {can_view, can_create, ...}}
    for p in all_perms:
        perms_dict[(p['module'], p['sub_module'])] = {...}
    
    cache.set(cache_key, perms_dict, 30)  # TTL 30 detik
    return perms_dict
```

### Hasil:

| Metrik | Sebelum | Sesudah |
|--------|---------|---------|
| Query per halaman | 20-40 | 1 (atau 0 dari cache) |
| Waktu permission check | ~50ms | ~2ms |
| Cache TTL | - | 30 detik |

---

*Lanjut ke [00_PENDAHULUAN.md](00_PENDAHULUAN.md) untuk memulai dari awal →*

---

## O. POS Layout — Kasir, Customer Autocomplete, Responsive

### Apa yang Diperbaiki?

Halaman POS mengalami beberapa peningkatan signifikan pada layout dan interaksi:

```
SEBELUM:
├── Input "Nama Customer" (teks biasa, tidak terhubung data)
├── Keranjang header: icon sampah + badge kasir hardcoded
├── Modal: dropdown select Customer terpisah + form fields
├── Suggestion dropdown: background transparan
└── Spacing: Daftar Produk terlalu rapat ke kategori

SESUDAH:
├── Dropdown "Pilih Kasir" (data dari User aktif)
├── Keranjang header: badge kasir dinamis (sesuai pilihan)
├── Modal: customer autocomplete di field Nama + auto-fill
├── Suggestion dropdown: background solid sesuai card
└── Spacing: jarak konsisten antara judul, kategori, dan search
```

### File yang Dimodifikasi:

| File | Perubahan |
|------|-----------|
| `templates/pos/index.html` | Layout + CSS + JavaScript |
| `apps/pos/views.py` | Tambah `user_list` ke context |

### Perubahan 1: Dropdown "Pilih Kasir"

```html
<!-- SEBELUM: Input teks biasa -->
<input type="text" id="customerName" placeholder="Masukkan nama">

<!-- SESUDAH: Dropdown dari database -->
<select class="form-select" id="kasirSelect">
    {% for user in user_list %}
    <option {% if user == request.user %}selected{% endif %}>
        {{ user.get_full_name|default:user.username }}
    </option>
    {% endfor %}
</select>
```

**Backend — Tambah user_list ke context:**
```python
# apps/pos/views.py — POSIndexView.get_context_data()
from django.contrib.auth import get_user_model
User = get_user_model()
context['user_list'] = User.objects.filter(is_active=True)
```

### Perubahan 2: Badge Kasir Dinamis

```html
<!-- Badge di keranjang otomatis update -->
<span class="badge bg-label-info" id="kasirBadge">
    <i class="ri-user-line me-1"></i>Kasir:
    <span id="kasirBadgeName">{{ request.user.get_full_name }}</span>
</span>
```

```javascript
// JavaScript: update badge saat kasir diganti
document.getElementById('kasirSelect').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    document.getElementById('kasirBadgeName').textContent = selectedOption.text;
});
```

### Perubahan 3: Customer Autocomplete di Modal Pembayaran

```
Alur kerja field "Nama Customer":

1. User mengetik huruf di field Nama
   → JavaScript filter data customer dari Django context
   → Suggestion list muncul dengan background solid

2a. Klik nama dari suggestion (customer terdaftar):
    → Nama, Telepon, Email, Alamat terisi otomatis
    → Field Telepon/Email/Alamat menjadi readonly
    → custSelectedId diset ke ID customer

2b. Ketik nama baru (tidak ada di database):
    → Muncul pesan "Customer baru — data akan dibuat otomatis"
    → Semua field tetap editable
    → custSelectedId tetap kosong

3. Saat proses transaksi:
    → customerName dari custInputNama
    → customerId dari custSelectedId (null jika baru)
```

```javascript
// Data customer dari Django template (untuk autocomplete client-side)
const customerDataList = [
    {% for cust in customer_list %}
    { id: {{ cust.id }}, nama: "{{ cust.nama|escapejs }}",
      telepon: "...", email: "...", alamat: "..." },
    {% endfor %}
];

// Event listener: filter saat mengetik
custNamaInput.addEventListener('input', function() {
    const matches = customerDataList.filter(
        c => c.nama.toLowerCase().includes(query)
    );
    // Tampilkan suggestion list atau pesan "customer baru"
});
```

### Perubahan 4: Styling Suggestion Dropdown

```html
<!-- Background solid agar tidak transparan -->
<div id="custSuggestionList" class="list-group position-absolute w-100"
     style="z-index: 1050; max-height: 200px; overflow-y: auto;
            background: var(--bs-body-bg, #fff);
            border: 1px solid var(--bs-border-color, #d9dee3);
            border-radius: 0.375rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
</div>
```

### Ringkasan Perubahan Layout Modal Pembayaran:

```
┌─────────────────────────────────────────┐
│ 🔵 Pembayaran                        ✕ │
├─────────────────────────────────────────┤
│                                         │
│ 🏦 Metode Pembayaran                   │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │ Dana │  │ BCA  │  │ Cash │          │
│  └──────┘  └──────┘  └──────┘          │
│─────────────────────────────────────────│
│ 👤 Customer (Opsional)                  │
│  ┌───────────────────────────────────┐  │
│  │ Nama Customer  [ketik untuk cari] │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ Darma Gunawan (0882...)     │  │  │ ← suggestion
│  │  └─────────────────────────────┘  │  │
│  │ Telepon [08xxx]  Email [a@b.c]   │  │
│  │ Alamat  [Jl. ...]               │  │
│  └───────────────────────────────────┘  │
│─────────────────────────────────────────│
│ 📝 Catatan (Opsional)                   │
│  [                                    ] │
│─────────────────────────────────────────│
│ 💰 Uang Diterima                        │
│  Rp [         0         ]              │
│  [Uang Pas] [20rb] [50rb] [100rb]      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │     Total Tagihan               │   │
│  │     Rp 87.000                   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │     Kembalian                   │   │
│  │     Rp 0                        │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Batal]          [✓ Proses Transaksi]  │
└─────────────────────────────────────────┘
```

---

*Lanjut ke [00_PENDAHULUAN.md](00_PENDAHULUAN.md) untuk memulai dari awal →*

---

### Perubahan 5: Select2 pada "Pilih Kasir" (Konsistensi UI)

```
SEBELUM:
├── Pilih Gudang → Select2 (tinggi 48px, icon panah segitiga)
├── Pilih Kasir  → Native form-select (tinggi standar, icon panah browser)
└── Tampilan TIDAK konsisten antara keduanya

SESUDAH:
├── Pilih Gudang → Select2 (sama)
├── Pilih Kasir  → Select2 (sama persis — ukuran, font, icon panah)
└── Kedua dropdown identik di desktop, tablet, dan mobile
```

```javascript
// Inisialisasi Select2 pada kasirSelect agar identik dengan gudangSelect
$('#kasirSelect').select2({
    placeholder: '-- Pilih Kasir --',
    allowClear: false,
    dropdownParent: $('.warehouse-card')
});

// Update badge Kasir saat kasir diganti
$('#kasirSelect').on('change', function () {
    const selectedText = $(this).find('option:selected').text().trim();
    $('#kasirBadgeName').text(selectedText);
});
```

### Perubahan 6: Grid 3 Kolom di Mobile

```
SEBELUM (mobile 375px):
┌─────────────────────┐
│  Diamond Mobile     │  ← 1 card per baris (memenuhi layar)
│  Legends            │
└─────────────────────┘
┌─────────────────────┐
│  Buku               │
└─────────────────────┘

SESUDAH (mobile 375px):
┌──────┐ ┌──────┐ ┌──────┐
│Diamnd│ │ Buku │ │ buku │  ← 3 cards per baris
└──────┘ └──────┘ └──────┘
```

```css
/* Pastikan 3 kolom di semua ukuran layar (termasuk mobile) */
#productGrid > .product-item {
    flex: 0 0 33.333333% !important;
    max-width: 33.333333% !important;
    width: 33.333333% !important;
}
/* Desktop xl: tetap 4 kolom */
@media (min-width: 1200px) {
    #productGrid > .product-item {
        flex: 0 0 25% !important;
        max-width: 25% !important;
    }
}
```

### Perubahan 7: Border Card Produk (Dark Mode Support)

```css
/* Light mode: border lebih tegas */
.pos-product-card {
    border: 1px solid rgba(0, 0, 0, 0.25);  /* sebelumnya 0.125 */
}

/* Dark mode: border putih transparan */
html.dark-style .pos-product-card {
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}
html.dark-style .pos-product-card:hover {
    border-color: rgba(105, 108, 255, 0.5) !important;
}
```

### Perubahan 8: Kasir Badge Posisi Kanan + Spacing Section

```css
/* Badge Kasir tetap kanan di semua ukuran layar */
.cart-header-flex {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
}

/* Spacing antara Daftar Produk dan Keranjang: via Bootstrap gy-4 pada row */
/* <div class="row gy-4"> → vertical gap 1.5rem saat kolom stack di mobile */
```

### Ringkasan Semua Perubahan POS Layout:

| No | Perubahan | Sebelum | Sesudah |
|----|-----------|---------|----------|
| 1 | Dropdown Kasir | Input teks biasa | Select2 dropdown dari database User |
| 2 | Badge Kasir | Hardcoded | Dinamis, update saat ganti kasir |
| 3 | Customer | Dropdown select terpisah | Autocomplete di field Nama + auto-fill |
| 4 | Suggestion | Background transparan | Background solid |
| 5 | Select2 Kasir | Native form-select | Select2 identik dengan Pilih Gudang |
| 6 | Grid Mobile | 1 card/baris | 3 cards/baris |
| 7 | Border Card | Samar (0.125) | Tegas (0.25) + dark mode support |
| 8 | Badge Mobile | Turun ke bawah, rata kiri | Tetap kanan dengan flex-nowrap |
| 9 | Spacing | Daftar Produk-Keranjang menempel | Bootstrap `gy-4` pada row (1.5rem vertical gap) |

### Perubahan 9: Spacing via Bootstrap Gutter (`gy-4`)

```html
<!-- SEBELUM: CSS custom margin-top -->
<div class="row">
    <div class="col-xl-8 col-lg-7">Daftar Produk</div>
    <div class="col-xl-4 col-lg-5 cart-section-col">Keranjang</div>
</div>
<!-- + @media (max-width: 1199.98px) { .cart-section-col { margin-top: 1.5rem; } } -->

<!-- SESUDAH: Bootstrap native gutter -->
<div class="row gy-4">  <!-- gy-4 = 1.5rem vertical gap -->
    <div class="col-xl-8 col-lg-7">Daftar Produk</div>
    <div class="col-xl-4 col-lg-5 cart-section-col">Keranjang</div>
</div>
<!-- Tidak perlu CSS custom — Bootstrap menangani spacing secara otomatis -->
```

**Mengapa `gy-4` lebih baik daripada CSS custom:**
```
gy-4 (Bootstrap native):
├── Otomatis berlaku saat kolom stack (mobile/tablet)
├── Tidak berlaku saat kolom side-by-side (desktop)
├── Konsisten dengan gutter system Bootstrap
├── Tidak ada risiko margin collapse
└── Nilainya (1.5rem) sama dengan .warehouse-card margin-bottom

CSS custom margin-top:
├── Perlu media query manual
├── Bisa conflik dengan Bootstrap gutter
├── Lebih sulit maintain
└── Risiko duplikasi spacing
```

### Referensi: Nilai Bootstrap Gutter (`gy-*`)

| Class | Nilai | Piksel (~) | Kapan Dipakai |
|-------|-------|------------|---------------|
| `gy-0` | 0 | 0px | Tanpa gap |
| `gy-1` | 0.25rem | 4px | Gap sangat kecil |
| `gy-2` | 0.5rem | 8px | Gap kecil |
| `gy-3` | 1rem | 16px | Gap standar |
| `gy-4` | 1.5rem | 24px | Gap besar (yang kita pakai) |
| `gy-5` | 3rem | 48px | Gap sangat besar |
| `g-3` | 1rem | 16px | Gap horizontal + vertikal |
| `g-4` | 1.5rem | 24px | Gap horizontal + vertikal |

---

---

## P. Dashboard — Simplifikasi Layout & Wave Chart

**File:** `templates/dashboard/index.html`, `apps/dashboard/views.py`

### Apa yang Diubah?

Dashboard disederhanakan agar lebih fokus pada metrik utama. Beberapa section yang kurang esensial dihapus, dan grafik penjualan per cabang diganti dari bar chart menjadi wave/area chart yang lebih modern.

### Section yang DIHAPUS:
```
✗ Total Pembelian (radial bar)         — tidak esensial di ringkasan
✗ Total Biaya (radial bar)             — ada di modul Biaya
✗ Slider Metode Pembayaran (Swiper)    — data ini ada di Pengaturan
✗ Keuntungan per Cabang (bar chart)    — diganti wave chart baru
✗ Biaya per Kategori (bar chart)       — ada di modul Biaya
```

### Fitur BARU:

#### 1. Wave Chart Penjualan per Cabang
```javascript
// Grafik area smooth (wave) menggantikan bar chart
// Setiap cabang (gudang) punya line sendiri
// Menampilkan data penjualan per bulan

type: 'area'
stroke: { curve: 'smooth', width: 2 }
fill: { type: 'gradient', gradient: { opacityFrom: 0.4, opacityTo: 0.05 } }

// Data dari views.py → JSON ke template
// Filter: mendukung filter waktu dari navbar
```

#### 2. Filter Waktu di Navbar (Icon)
```
SEBELUM: Filter waktu = card besar di atas dashboard (memakan tempat)
SESUDAH: Filter waktu = icon kalender (ri-calendar-line) di navbar

Cara kerja:
- Icon hanya muncul di halaman Dashboard (cek URL via JS)
- Klik icon → dropdown muncul dengan 4 pilihan:
  ├── Hari Ini
  ├── Minggu Ini
  ├── Bulan Ini
  └── Kustom (date range picker)
- Pilih filter → submit ke GET params → reload data dashboard
- Grafik penjualan per cabang ikut terfilter
```

#### 3. Pengguna Terbaru 100% Lebar
```
SEBELUM: Pengguna terbaru sharing kolom dengan Aktivitas Terbaru
SESUDAH: Pengguna terbaru lebar penuh (col-12), responsive

Perubahan avatar:
- SEBELUM: 2 inisial (misal "DA" untuk Darma Adi)
- SESUDAH: 1 inisial (misal "D" untuk Darma Adi)
```

### Impact pada views.py:
```python
# Data yang DIHAPUS dari context:
# - total_pembelian, total_biaya (radial bars)
# - build_card_data() (slider metode pembayaran)
# - keuntungan_cabang_data (bar chart)
# - biaya_kategori_data (bar chart)

# Data yang DITAMBAH/DIPERTAHANKAN:
# - penjualan_cabang_labels, penjualan_cabang_data (wave chart)
# - Filter waktu GET params → datetime range filtering
```

---

## Q. POS — Star Rating, Scrollbar, Category Pills

**File:** `templates/pos/index.html`, `apps/pos/views.py`

### Apa yang Diubah?

Halaman POS mendapat beberapa peningkatan estetika dan fungsionalitas untuk tampilan yang lebih profesional, konsisten, dan user-friendly.

### Perubahan 1: Star Rating Produk (Bintang 1-5)

```
Setiap kartu produk kini menampilkan rating bintang:

┌──────────────┐
│  [Gambar]     │
│  Beras Premium│
│  ⭐⭐⭐⭐⭐     │  ← Star rating berdasarkan jumlah pembelian
│  Rp 15.000   │
│  Stok: 50 pcs│
│  [Tambah]    │
└──────────────┘

Alur data rating:
views.py:
  1. Query POSTransactionItem (status='paid')
  2. Group by produk_id → Sum jumlah
  3. Cari max_sold (produk paling laris)
  4. Rasio ke rating: ≥80%→5⭐, ≥60%→4⭐, ≥40%→3⭐, ≥20%→2⭐, <20%→1⭐
  5. JSON → template → JavaScript render bintang

CSS:
  .star-filled { color: #ffab00; font-size: 0.7rem; }   (emas)
  .star-empty  { color: #d0d4da; font-size: 0.7rem; }   (abu-abu)
```

### Perubahan 2: Custom Scrollbar

```css
/* Scrollbar produk grid dan keranjang — konsisten dengan sidebar */
#productGrid::-webkit-scrollbar,
.cart-scroll::-webkit-scrollbar {
    width: 5px;                    /* Tipis */
}

#productGrid::-webkit-scrollbar-thumb {
    background: rgba(105, 108, 255, 0.4);  /* Ungu semi-transparan */
    border-radius: 10px;
}

/* Firefox support */
#productGrid {
    scrollbar-width: thin;
    scrollbar-color: rgba(105,108,255,0.4) transparent;
}
```

### Perubahan 3: Category Pills Restyling

```css
/* Border radius diubah agar konsisten dengan tombol lain */
.category-pill {
    border-radius: 0.375rem !important;  /* Sama dengan tombol Riwayat */
    /* SEBELUM: border-radius: 50rem (fully rounded) */
    transition: all 0.2s ease;
}

/* State inaktif — teks tetap terlihat (bukan transparan) */
.category-pill:not(.active) {
    background: transparent;
    color: var(--bs-primary);
}
```

### Perubahan 4: Badge Kasir Dihapus

```
SEBELUM:
  Keranjang header: "🛒 Keranjang  Kasir: [Nama]"
  ↑ Badge redundan karena sudah ada Select2 "Pilih Kasir"

SESUDAH:
  Keranjang header: "🛒 Keranjang"
  ↑ Lebih bersih. Kasir dipilih via Select2 di atas.

JavaScript references ke kasirBadgeName di-remove agar tidak error.
```

### Perubahan 5: Ukuran Harga = Nama

```css
/* Harga produk sekarang sama besar dengan nama produk */
.product-price {
    font-size: inherit;  /* Mengikuti ukuran parent, sama dengan nama */
    /* SEBELUM: font-size: 1.1rem — lebih besar, memakan ruang */
}
```

### Kenapa Perubahan Ini Penting?

```
1. Star Rating  → Feedback visual tentang popularitas produk
                   Kasir bisa lihat produk mana paling laris

2. Scrollbar    → Konsistensi visual dengan sidebar
                   Pengalaman scroll yang halus dan tidak mengganggu

3. Category Pills → Konsistensi dengan tombol lain (Riwayat, Scan)
                     Teks selalu terlihat di semua state

4. Badge Kasir  → Menghilangkan redundansi informasi
                   UI lebih bersih dan fokus

5. Harga = Nama → Menghemat ruang vertikal di kartu produk
                   Lebih rapi secara visual
```

---

## R. Audit Keamanan — Concurrency, Race Condition & Validasi Stok

### Apa yang Diperbaiki?

Audit keamanan mendalam pada Maret 2026 mengungkap **12 masalah** (9 kritis + 3 sedang) yang dapat menyebabkan **data korup saat multiple user mengakses bersamaan**.

### Daftar Masalah & Solusi:

| # | Masalah | Severity | File | Solusi |
|---|---------|----------|------|--------|
| K1 | Race condition pada stok | 🔴 Kritis | `inventory/models.py`, `penjualan/models.py`, `pembelian/models.py`, `pos/views.py` | `select_for_update()` + `transaction.atomic()` |
| K2 | Nomor transaksi bisa duplikat | 🔴 Kritis | 6 file `models.py` | `select_for_update()` di semua `generate_nomor()` |
| K3 | Stok bisa negatif | 🔴 Kritis | `inventory/models.py`, `penjualan/models.py` | Validasi `if stok.jumlah < qty` sebelum kurangi |
| K4 | SO bisa diedit setelah confirmed | 🔴 Kritis | `penjualan/views.py` | `dispatch()` override redirect jika bukan draft |
| K6 | POS race condition `create_transaction()` | 🔴 Kritis | `pos/views.py` | Validasi + kurangi stok dalam satu `atomic()` |
| K7 | Filter PO salah di laporan keuangan | 🔴 Kritis | `laporan/views.py` | `'confirmed'` → `'approved'` |
| K8 | Laporan POS dibatasi 50 transaksi | 🔴 Kritis | `laporan/views.py` | Hapus `[:50]` slice |
| K9 | Bare `except:` tanpa tipe exception | 🔴 Kritis | 6 file `models.py` | `except (ValueError, IndexError):` |
| S1 | PO create tanpa `transaction.atomic()` | 🟡 Sedang | `pembelian/views.py` | Wrapper `transaction.atomic()` |
| S2 | PO delete tanpa atomic rollback | 🟡 Sedang | `pembelian/views.py` | `transaction.atomic()` + `select_for_update()` |
| S3 | Bare except di PO create | 🟡 Sedang | `pembelian/views.py` | `except (ValueError, InvalidOperation):` |

### Pola Fix 1: Race Condition → `select_for_update()` + `transaction.atomic()`

**Masalah:**
```
User A membaca stok: 10          User B membaca stok: 10
User A kurangi: 10 - 3 = 7       User B kurangi: 10 - 5 = 5
User A simpan: stok = 7          User B simpan: stok = 5  ← SALAH!
→ Seharusnya: 10 - 3 - 5 = 2, bukan 5!
```

**Solusi:**
```python
# SEBELUM (rawan race condition):
stok = Stok.objects.get(produk=produk, gudang=gudang)
stok.jumlah -= qty
stok.save()

# SESUDAH (aman — thread lain menunggu):
with transaction.atomic():
    # select_for_update() mengunci baris di database
    # Thread lain yang query baris ini akan MENUNGGU sampai lock dilepas
    stok = Stok.objects.select_for_update().get(produk=produk, gudang=gudang)
    stok.jumlah -= qty
    stok.save()
# Lock dilepas setelah keluar atomic block
```

**File yang menerapkan pola ini:**
- `inventory/models.py` → `TransferStok.approve()`, `AdjustmentStok.save()`
- `penjualan/models.py` → `SalesOrder.confirm_order()`
- `pembelian/models.py` → `PurchaseOrder.receive_goods()`
- `pos/views.py` → `CreateTransactionView.post()`
- `pembelian/views.py` → `PurchaseOrderCreateView`, `PurchaseOrderDeleteView`

### Pola Fix 2: Nomor Duplikat → Lock saat Generate

**Masalah:**
```
User A query last_number: 5      User B query last_number: 5
User A generate: SO/2024/01/0006 User B generate: SO/2024/01/0006  ← DUPLIKAT!
```

**Solusi:**
```python
def generate_nomor(self):
    prefix = f"SO/{today.year}/{today.month:02d}"
    # select_for_update() mengunci query → thread lain menunggu
    last_so = SalesOrder.objects.select_for_update().filter(
        nomor_so__startswith=prefix
    ).order_by('-nomor_so').first()
    # ... increment + return
```

**Diterapkan di 6 `generate_nomor()`:**
`TransferStok`, `AdjustmentStok`, `SalesOrder`, `PurchaseOrder`, `POSTransaction`, `TransaksiBiaya`

### Pola Fix 3: Stok Negatif → Validasi Eksplisit

```python
# Cegah stok jadi negatif
if stok.jumlah < qty:
    raise ValueError(
        f"Stok {produk.nama} tidak mencukupi. "
        f"Tersedia: {stok.jumlah}, Dibutuhkan: {qty}"
    )
stok.jumlah -= qty
stok.save()
```

### Pola Fix 4: SO Edit Protection → `dispatch()` Override

```python
class SalesOrderUpdateView(UpdatePermissionMixin, UpdateView):
    def dispatch(self, request, *args, **kwargs):
        """Cegah edit SO yang sudah dikonfirmasi."""
        so = self.get_object()
        if so.status != 'draft':
            messages.error(request, 'SO tidak dapat diedit, status bukan Draft.')
            return redirect('penjualan:sales-order-detail', pk=so.pk)
        return super().dispatch(request, *args, **kwargs)
```

### Pola Fix 5: Bare `except:` → Exception Spesifik

```python
# SEBELUM (menangkap SEMUA error — termasuk SystemExit, KeyboardInterrupt):
except:
    new_number = 1

# SESUDAH (hanya tangkap error yang diharapkan):
except (ValueError, IndexError):
    new_number = 1
```

### Diagram Alur Concurrency Control:

```
┌────────────────────────────────────────────────────────────────┐
│                ALUR PROTEKSI CONCURRENCY                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  User A: Buat SO                  User B: Buat SO              │
│     │                                │                         │
│     ▼                                ▼                         │
│  generate_nomor()               generate_nomor()               │
│     │                                │                         │
│     ▼                                │ (MENUNGGU)              │
│  select_for_update() ──LOCK──►       │                         │
│     │                                │                         │
│  Baca last: 0005                     │                         │
│  Generate: 0006                      │                         │
│  Save → COMMIT ──UNLOCK──►           ▼                         │
│                               select_for_update()              │
│                               Baca last: 0006 (yg baru)        │
│                               Generate: 0007 ✅ (UNIK)         │
│                               Save → COMMIT                    │
│                                                                │
│  Hasil: SO/2024/01/0006        Hasil: SO/2024/01/0007          │
│         ✅ Tidak duplikat!             ✅ Tidak duplikat!       │
└────────────────────────────────────────────────────────────────┘
```

### Verifikasi:

```
✅ Django system check: 0 issues
✅ Server startup: OK — http://127.0.0.1:8000/
✅ Semua 9 file berhasil dicompile tanpa syntax error
✅ Login page render normal
```

---

## S. Dashboard Chart — Smart Aggregation & Filter Waktu Cabang

### Apa yang Diperbaiki?

Grafik "Penjualan per Cabang" di dashboard **terlihat kosong** saat user menerapkan filter waktu pendek (contoh: 1-9 Maret 2026). Penyebabnya:

```
MASALAH 1: Agregasi Selalu Per-Bulan
─────────────────────────────────────
Filter 1-9 Maret → hanya 1 bulan → 1 data point per cabang
→ ApexCharts hanya render 1 titik (dot), bukan garis
→ Chart terlihat KOSONG padahal datanya ada

MASALAH 2: Tidak Ada Default Values
────────────────────────────────────
Jika terjadi error di inner try block, variabel
sales_cabang_labels dan sales_cabang_series tidak pernah di-set
→ Template json_script tag crash / undefined
→ JavaScript exit early → chart tidak render sama sekali

MASALAH 3: Filter Waktu Tidak Diterapkan ke Query Cabang
──────────────────────────────────────────────────────────
Query cabang_stats (revenue SO, profit SO, revenue POS, profit POS,
pembelian PO) TIDAK menggunakan filter_start / filter_end
→ Data cabang selalu menampilkan ALL TIME, bukan sesuai filter
```

### File yang Dimodifikasi:

| File | Perubahan |
|------|-----------|
| `apps/dashboard/views.py` | Smart Aggregation, default values, filter waktu cabang_stats |

### Perbaikan 1: Smart Aggregation (Harian/Bulanan)

```python
# Hitung rentang hari dari filter
if filter_start and filter_end:
    rentang_hari = (filter_end - filter_start).days + 1
else:
    rentang_hari = 180  # Default → pakai bulanan

# Pilih mode agregasi secara otomatis
use_daily = rentang_hari <= 62  # ≤ 2 bulan → per hari

if use_daily:
    # MODE HARIAN: query SO + POS per tanggal per gudang
    # Label X-axis: "01 Mar", "02 Mar", "03 Mar"...
    for hari in hari_list:
        so_rev = SalesOrder.objects.filter(
            gudang=gudang, tanggal__date=hari, ...
        ).aggregate(total=Sum('total_harga'))['total'] or 0
else:
    # MODE BULANAN: query SO + POS per bulan per gudang
    # Label X-axis: "Oct 2025", "Nov 2025"...
    for bulan in bulan_list:
        so_rev = SalesOrder.objects.filter(
            gudang=gudang, tanggal__year=bulan['year'], ...
        ).aggregate(total=Sum('total_harga'))['total'] or 0
```

### Perbaikan 2: Default Values di 3 Lokasi

```python
# 1. Pre-try init (sebelum try block):
context['sales_cabang_labels'] = []
context['sales_cabang_series'] = []
context['cabang_profit_data'] = []

# 2. Inner except handler (ERP cards error):
except Exception as erp_error:
    context.setdefault('sales_cabang_labels', [])
    context.setdefault('sales_cabang_series', [])

# 3. Outer except handler (fatal dashboard error):
except Exception as e:
    context.update({
        'sales_cabang_labels': [],
        'sales_cabang_series': [],
        ...
    })
```

### Perbaikan 3: Filter Waktu pada cabang_stats Query

```python
# SEBELUM: query tanpa filter waktu
so_rev = SalesOrder.objects.filter(
    gudang=gudang, status__in=[...]
).aggregate(...)  # ← ALL TIME!

# SESUDAH: query dengan filter waktu
so_filter = {'gudang': gudang, 'status__in': [...]}
if filter_start:
    so_filter['tanggal__date__gte'] = filter_start
if filter_end:
    so_filter['tanggal__date__lte'] = filter_end
so_rev = SalesOrder.objects.filter(**so_filter).aggregate(...)
```

### Verifikasi:

```
✅ Django system check: 0 issues
✅ Browser: filter 1-9 Mar → chart tampil garis harian per cabang
✅ Browser: default → chart tetap bulanan 6 bulan terakhir
✅ Bagian lain dashboard tidak ada error
```

---

*Lanjut ke [10_KOMPONEN_UI_SNEAT.md](10_KOMPONEN_UI_SNEAT.md) untuk panduan tata letak dan komponen UI →*
