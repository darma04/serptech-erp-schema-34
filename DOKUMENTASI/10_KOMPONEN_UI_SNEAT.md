# 🎨 10 — Komponen UI Sneat Bootstrap 5 — Panduan Super Lengkap

## DAFTAR ISI
- [A. Asal-Usul: Apa itu Sneat?](#a-asal-usul-apa-itu-sneat)
- [B. Sistem Layout Template (Inheritance)](#b-sistem-layout-template)
- [C. Grid System Bootstrap 5 — Posisi & Tata Letak](#c-grid-system-bootstrap-5)
- [D. Komponen Card + Posisi & Variasi](#d-komponen-card)
- [E. Sidebar Menu (Vertikal)](#e-sidebar-menu)
- [F. Navbar (Navigation Bar)](#f-navbar)
- [G. Tabel & DataTables](#g-tabel--datatables)
- [H. Komponen Form Lengkap](#h-komponen-form-lengkap)
- [I. Komponen Button (Tombol)](#i-komponen-button)
- [J. Komponen Modal (Dialog)](#j-komponen-modal)
- [K. Alert, Toast, Messages](#k-alert-toast-messages)
- [L. Badge & Label Status](#l-badge--label-status)
- [M. Icon (Remix Icon)](#m-icon-remix-icon)
- [N. Charts & Grafik (ApexCharts)](#n-charts--grafik-apexcharts)
- [O. Dark Mode & Theme System](#o-dark-mode--theme-system)
- [P. Error Handler (404, 403, 500)](#p-error-handler)
- [Q. Halaman Login](#q-halaman-login)
- [R. Pola Template Lengkap CRUD](#r-pola-template-lengkap-crud)

---

## A. Asal-Usul: Apa itu Sneat?

**Sneat** = Admin Dashboard Template buatan [Pixinvent](https://pixinvent.com/) berbasis **Bootstrap 5**.

```
Pixinvent Product Line:
├── Materialize → berbasis MaterializeCSS
├── Vuexy       → berbasis React/Vue
├── Sneat       → berbasis Bootstrap 5 ← YANG KITA PAKAI
└── Frest       → berbasis Bootstrap 5

Versi yang kita pakai: STARTER KIT (bukan Full Version)
→ Hanya berisi layout system + tema, TANPA halaman demo
→ Semua konten dan fitur kita bangun sendiri dari nol
```

### File-File Bawaan Sneat di Project Kita:

```
static/                        ← SEMUA ini dari Sneat starter kit
├── vendor/
│   ├── css/
│   │   ├── core.css           ← CSS inti Bootstrap 5 + custom Sneat
│   │   ├── core-dark.css      ← Otomatis switch di dark mode
│   │   ├── theme-default.css  ← Warna tema default (#696CFF indigo)
│   │   └── rtl/               ← CSS Right-to-Left (Arab)
│   ├── js/
│   │   ├── bootstrap.js       ← Bootstrap 5 JavaScript
│   │   ├── helpers.js         ← Sneat helper: isDarkStyle, etc
│   │   ├── menu.js            ← Sidebar menu open/close/toggle
│   │   └── template-customizer.js ← Panel kustomisasi (dark/light, sidebar)
│   ├── libs/
│   │   ├── jquery/            ← jQuery 3.x
│   │   ├── popper/            ← Dropdown positioning
│   │   ├── perfect-scrollbar/ ← Custom scrollbar sidebar
│   │   ├── node-waves/        ← Material design ripple effect
│   │   ├── hammer/            ← Touch gesture support
│   │   ├── typeahead-js/      ← Search autocomplete
│   │   ├── datatables-bs5/    ← DataTables + Bootstrap styling
│   │   ├── select2/           ← Searchable dropdown
│   │   ├── apex-charts/       ← ApexCharts (grafik dashboard)
│   │   └── swiper/            ← Swiper (slider/carousel)
│   └── fonts/
│       ├── remixicon/         ← 2000+ ikon (ri-*)
│       └── flag-icons.css     ← Ikon bendera negara
├── css/demo.css               ← Custom CSS
├── js/config.js               ← Config tema JS (colors, isDarkStyle)
└── js/main.js                 ← Custom JS utama
```

---

## B. Sistem Layout Template (Inheritance)

### Apa itu Template Inheritance?

Template inheritance = konsep **mewarisi** struktur HTML dari template induk, sehingga kita tidak perlu menulis ulang header, sidebar, footer di setiap halaman.

```
Analogi:
┌─────────────────────────────────────────────────────┐
│ Template Inheritance ≈ Bangunan Rumah               │
│                                                     │
│ master.html     = Fondasi + Rangka rumah (semua)    │
│ layout_vertical = Dinding + Atap + Pintu            │
│ produk_list     = Isi perabotan di dalam kamar      │
│                                                     │
│ Kamu TIDAK perlu bangun fondasi ulang               │
│ untuk setiap kamar — cukup isi perabotannya saja!  │
└─────────────────────────────────────────────────────┘
```

### Hierarki Template 3 Level:

```
LEVEL 0: master.html ──────────────────────────────────
│
│  Isi: DOCTYPE, <html>, <head>, <body>
│  CSS global, JS global, favicon, <title>
│  
│  Block yang disediakan:
│  ├── {% block title %}      → Judul tab browser
│  ├── {% block vendor_css %} → CSS library
│  ├── {% block page_css %}   → CSS halaman
│  ├── {% block layout %}     → ← INI YANG DI-OVERRIDE LEVEL 1
│  ├── {% block vendor_js %}  → JS library
│  └── {% block page_js %}    → JS halaman
│
├── LEVEL 1: layout_vertical.html ──────────────────
│   │
│   │  Isi: Sidebar + Navbar + Content Area + Footer
│   │  OVERRIDE: {% block layout %} dari master
│   │  MENYEDIAKAN: {% block content %} ← untuk Level 2
│   │
│   │  Struktur HTML yang dihasilkan:
│   │  ┌─────────────────────────────────────┐
│   │  │ ┌──────┐ ┌────────────────────────┐ │
│   │  │ │      │ │      NAVBAR            │ │
│   │  │ │  S   │ ├────────────────────────┤ │
│   │  │ │  I   │ │                        │ │
│   │  │ │  D   │ │   {% block content %}  │ │
│   │  │ │  E   │ │   ← HALAMAN KAMU      │ │
│   │  │ │  B   │ │                        │ │
│   │  │ │  A   │ │                        │ │
│   │  │ │  R   │ ├────────────────────────┤ │
│   │  │ │      │ │      FOOTER            │ │
│   │  │ └──────┘ └────────────────────────┘ │
│   │  └─────────────────────────────────────┘
│   │
│   ├── LEVEL 2: produk_list.html ─────────────
│   │   {% extends 'layout/layout_vertical.html' %}
│   │   {% block content %}
│   │     <div class="container-xxl">
│   │       ... ISI HALAMAN ...
│   │     </div>
│   │   {% endblock %}
│   │
│   ├── LEVEL 2: kategori_form.html
│   ├── LEVEL 2: dashboard.html
│   └── LEVEL 2: (75+ template lain)
│
├── LEVEL 1: layout_blank.html ──────────────────
│   │
│   │  Isi: KOSONG (tanpa sidebar, navbar, footer)
│   │  Digunakan untuk: Login, Register, Error pages
│   │
│   ├── LEVEL 2: login.html
│   └── LEVEL 2: register.html
│
└── LEVEL 1: layout_horizontal.html ───────────────
    │  Isi: Menu horizontal di atas (tanpa sidebar)
```

### Cara `{% extends %}` Bekerja:

```
Langkah demi langkah saat Django render produk_list.html:

1. Django baca: {% extends 'layout/layout_vertical.html' %}
   → "Saya butuh layout_vertical.html sebagai induk"

2. Django baca layout_vertical.html: {% extends 'layout/master.html' %}
   → "Saya butuh master.html sebagai kakek"

3. Django mulai dari PALING ATAS (master.html):
   - Render DOCTYPE, <head>, CSS, dll
   - Sampai di {% block layout %} → STOP, cari isi dari child

4. layout_vertical: mengisi {% block layout %} dengan sidebar + navbar + content
   - Sampai di {% block content %} → STOP, cari isi dari grandchild

5. produk_list.html: mengisi {% block content %} dengan tabel produk

6. Kembali ke master.html: lanjut render JS global

HASIL AKHIR: HTML lengkap dikirim ke browser
```

### `{{ block.super }}` — Menambah, Bukan Mengganti:

```html
{# ═══ TANPA block.super (MENGGANTI) ═══ #}
{% block vendor_css %}
<link href="datatables.css" />
{# ❌ CSS global dari master.html HILANG! #}
{% endblock %}

{# ═══ DENGAN block.super (MENAMBAH) ═══ #}
{% block vendor_css %}
{{ block.super }}
{# ↑ Pertahankan semua CSS dari parent template #}
<link href="datatables.css" />
{# ✅ CSS global TETAP ADA + datatables.css ditambahkan #}
{% endblock %}

{# ATURAN: SELALU gunakan {{ block.super }} di vendor_css dan vendor_js! #}
```

---

## C. Grid System Bootstrap 5 — Posisi & Tata Letak

### Apa itu Grid System?

Grid = sistem **tata letak responsif** Bootstrap yang membagi layar menjadi **12 kolom**.

```
Layar dibagi menjadi 12 kolom yang tidak terlihat:
│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │

col-4 = 4 kolom dari 12 = 33.3% lebar
col-6 = 6 kolom dari 12 = 50% lebar
col-8 = 8 kolom dari 12 = 66.7% lebar
col-12 = 12 kolom dari 12 = 100% lebar (full width)
```

### Breakpoints (Ukuran Layar):

| Class | Layar | Lebar | Device |
|-------|-------|-------|--------|
| `col-` | Extra small | < 576px | HP portrait |
| `col-sm-` | Small | ≥ 576px | HP landscape |
| `col-md-` | Medium | ≥ 768px | Tablet |
| `col-lg-` | Large | ≥ 992px | Laptop |
| `col-xl-` | Extra large | ≥ 1200px | Desktop |
| `col-xxl-` | XXL | ≥ 1400px | Monitor besar |

### Contoh Layout Grid yang Dipakai di Project:

```html
{# ═══ CONTOH 1: 3 Kartu Statistik Sejajar ═══ #}
<div class="row g-3">
    {# row   = container grid (wajib ada row untuk col) #}
    {# g-3   = gap/gutter 1rem antar kolom #}
    
    <div class="col-md-4">
        {# col-md-4 = lebar 4/12 (33%) di layar medium+ #}
        {# Di HP (< 768px): otomatis full width (100%) #}
        <div class="card">
            <div class="card-body">Total Produk: 50</div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">Total Stok: 500</div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">Total Nilai: Rp 50.000.000</div>
        </div>
    </div>
</div>

{# Hasilnya:
   Desktop (≥768px):   [Card 1][Card 2][Card 3]   ← 3 kolom sejajar
   HP (<768px):        [Card 1]                    ← stack vertikal
                       [Card 2]
                       [Card 3]
#}
```

```html
{# ═══ CONTOH 2: Form 2 Kolom ═══ #}
<div class="row g-3">
    <div class="col-md-6">
        {# col-md-6 = 50% lebar di layar ≥768px #}
        <label class="form-label">Nama</label>
        <input type="text" class="form-control">
    </div>
    <div class="col-md-6">
        <label class="form-label">Email</label>
        <input type="email" class="form-control">
    </div>
    <div class="col-12">
        {# col-12 = selalu 100% lebar (full width) #}
        <label class="form-label">Alamat</label>
        <textarea class="form-control"></textarea>
    </div>
</div>

{# Hasilnya:
   Desktop: [Nama        ][Email       ]   ← 2 kolom
            [Alamat ─ full width ───────]   ← 1 kolom full
   HP:      [Nama        ]                 ← stack
            [Email       ]
            [Alamat      ]
#}
```

```html
{# ═══ CONTOH 3: Dashboard Layout — Kolom Beda Ukuran ═══ #}
<div class="row g-3">
    {# Kolom kiri: chart besar (8/12 = 66.7%) #}
    <div class="col-md-8">
        <div class="card">
            <div class="card-header"><h5>Grafik Penjualan</h5></div>
            <div class="card-body">
                <div id="salesChart"></div>
            </div>
        </div>
    </div>
    
    {# Kolom kanan: info kecil (4/12 = 33.3%) #}
    <div class="col-md-4">
        <div class="card mb-3">
            <div class="card-body">Total Hari Ini: Rp 5.000.000</div>
        </div>
        <div class="card">
            <div class="card-body">Transaksi: 25</div>
        </div>
    </div>
</div>

{# Hasilnya:
   ┌──────────────────────┐ ┌────────────┐
   │                      │ │ Total Hari │
   │   GRAFIK PENJUALAN   │ │  Ini       │
   │   (col-md-8 = 66%)   │ ├────────────┤
   │                      │ │ Transaksi  │
   │                      │ │  25        │
   └──────────────────────┘ └────────────┘
        col-md-8                col-md-4
#}
```

### CSS Utility untuk Posisi Card:

```html
{# ═══ SPACING (Margin & Padding) ═══ #}
<div class="mb-3">    {# margin-bottom: 1rem #}</div>
<div class="mb-4">    {# margin-bottom: 1.5rem #}</div>
<div class="mt-3">    {# margin-top: 1rem #}</div>
<div class="me-2">    {# margin-end/right: 0.5rem #}</div>
<div class="ms-auto">  {# margin-start/left: auto (dorong ke kanan) #}</div>
<div class="p-3">     {# padding: 1rem semua sisi #}</div>
<div class="py-4">    {# padding atas-bawah: 1.5rem #}</div>
<div class="px-3">    {# padding kiri-kanan: 1rem #}</div>

{# ═══ FLEXBOX (Susunan Horizontal) ═══ #}
<div class="d-flex">                         {# display: flex #}
<div class="d-flex justify-content-between"> {# ujung kiri dan kanan #}
<div class="d-flex justify-content-center">  {# tengah #}
<div class="d-flex align-items-center">      {# rata tengah vertikal #}
<div class="d-flex flex-wrap">               {# wrap ke baris baru jika penuh #}
<div class="d-flex gap-2">                   {# jarak 0.5rem antar item #}

{# ═══ CONTAINER ═══ #}
<div class="container-xxl">  {# max-width: 1400px, center #}
<div class="flex-grow-1">    {# isi sisa ruang vertikal/horizontal #}
<div class="container-p-y">  {# padding atas-bawah standar Sneat #}

{# ═══ CONTOH KOMBINASI ═══ #}
{# Header halaman: judul di kiri, tombol di kanan #}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h4 class="mb-1">Daftar Produk</h4>
        <p class="text-muted mb-0">Kelola data produk</p>
    </div>
    <a href="{% url 'produk:add' %}" class="btn btn-primary">
        <i class="ri-add-line me-1"></i>Tambah
    </a>
</div>
```

---

## D. Komponen Card + Posisi & Variasi

### Card Dasar:

```html
<div class="card">
    {# card = kotak putih, shadow halus, border-radius: 0.5rem #}
    {# Background: var(--bs-card-bg) → otomatis dark/light #}
    
    <div class="card-header">
        {# Padding: 1.5rem, border-bottom: 1px solid #}
        <h5 class="mb-0">Judul</h5>
    </div>
    
    <div class="card-body">
        {# Padding: 1.5rem semua sisi #}
        <p>Konten</p>
    </div>
    
    <div class="card-footer text-end">
        {# text-end = text-align: right #}
        <button class="btn btn-primary">Simpan</button>
    </div>
</div>
```

### Card Statistik (Pola Dashboard):

```html
{# ═══ CARD DENGAN AVATAR ICON ═══ #}
<div class="card">
    <div class="card-body">
        <div class="d-flex align-items-center">
            <div class="avatar me-3">
                {# avatar = kotak 40x40px #}
                <span class="avatar-initial rounded bg-label-primary">
                    {# avatar-initial = fill warna #}
                    {# rounded = border-radius bulat #}
                    {# bg-label-primary = warna ungu muda transparan #}
                    <i class="ri-shopping-bag-3-line ri-24px"></i>
                </span>
            </div>
            <div>
                <h4 class="mb-0">{{ total_produk }}</h4>
                <span class="text-muted">Total Produk</span>
            </div>
        </div>
    </div>
</div>
```

### Mengatur Posisi & Susunan Card:

```html
{# ═══ 4 CARD SEJAJAR SAMA RATA ═══ #}
<div class="row g-3 mb-4">
    <div class="col-sm-6 col-xl-3">
        {# col-sm-6   = 2 kolom di tablet #}
        {# col-xl-3   = 4 kolom di desktop besar #}
        <div class="card"><div class="card-body">Card 1</div></div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card"><div class="card-body">Card 2</div></div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card"><div class="card-body">Card 3</div></div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card"><div class="card-body">Card 4</div></div>
    </div>
</div>

{# Hasilnya di berbagai layar:
   Desktop XL:  [C1][C2][C3][C4]      ← 4 kolom
   Tablet:      [C1][C2]              ← 2 kolom
                [C3][C4]
   HP:          [C1]                   ← 1 kolom
                [C2]
                [C3]
                [C4]
#}

{# ═══ CARD TINGGI SAMA (Stretch) ═══ #}
<div class="row g-3">
    <div class="col-md-6 d-flex">
        {# d-flex membuat card STRETCH tingginya sama dengan sebelah #}
        <div class="card w-100">
            <div class="card-body">
                Konten pendek
            </div>
        </div>
    </div>
    <div class="col-md-6 d-flex">
        <div class="card w-100">
            <div class="card-body">
                Konten panjang yang membuat
                card ini lebih tinggi dari sebelah
                tapi sebelah akan ikut tingginya
            </div>
        </div>
    </div>
</div>
```

### Contoh Layout Kompleks: Halaman POS

Halaman POS menunjukkan penggunaan card dan grid dalam tata letak yang kompleks:

```
Struktur Tata Letak POS:
┌───────────────────────────────────────────────────┐
│ Card Pilih Gudang/Cabang + Pilih Kasir            │  ← warehouse-card
│ (margin-bottom: 1.5rem → jarak ke section bawah)  │
└───────────────────────────────────────────────────┘
                    ↕ 1.5rem gap
┌────────────────────────────┐ ┌──────────────────┐
│ Card Daftar Produk         │ │ Card Keranjang   │
│ (col-xl-8 col-lg-7)       │ │ (col-xl-4 lg-5)  │
│                            │ │                  │
│ ┌──────┐ ┌──────┐ ┌──────┐│ │ Badge Kasir      │
│ │Produk│ │Produk│ │Produk││ │ → flex-nowrap     │
│ │ Card │ │ Card │ │ Card ││ │                  │
│ └──────┘ └──────┘ └──────┘│ │ Cart Items       │
│ (col-xl-3 col-4)         │ │                  │
│ → 3 kolom di mobile      │ │ Total + Bayar    │
│ → 4 kolom di desktop     │ │                  │
└────────────────────────────┘ └──────────────────┘
      ↕ gy-4 (1.5rem gap saat stack di mobile/tablet)
```

```html
{# ═══ TATA LETAK POS: 3 LEVEL CARD ═══ #}

{# LEVEL 1: Card Header (Pilih Gudang + Kasir) #}
<div class="card warehouse-card">
    {# warehouse-card = custom CSS: margin-bottom 1.5rem + bg primary #}
    <div class="card-body">
        <div class="row g-3">
            {# g-3 = gap antar kolom 1rem #}
            <div class="col-md-6">
                {# col-md-6 = setengah layar di tablet+ #}
                <select id="gudangSelect" class="form-select"></select>
            </div>
            <div class="col-md-6">
                <select id="kasirSelect" class="form-select"></select>
            </div>
        </div>
    </div>
</div>

{# LEVEL 2: Row Utama (Produk + Keranjang) #}
<div class="row gy-4">
    {# gy-4 = vertical gap 1.5rem saat kolom stack di mobile #}
    {# Hanya berlaku saat kolom STACK, TIDAK berlaku saat side-by-side #}
    
    {# Kolom Kiri: Daftar Produk (2/3 layar) #}
    <div class="col-xl-8 col-lg-7">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                {# d-flex + justify-content-between = judul kiri, badge kanan #}
                <h5 class="mb-0">Daftar Produk</h5>
                <span class="badge bg-primary">10 Produk</span>
            </div>
            <div class="card-body">

                {# LEVEL 3: Grid Produk (card di dalam card) #}
                <div class="row g-3" id="productGrid">
                    {# Product items: responsive columns #}
                    <div class="col-xl-3 col-lg-4 col-md-4 col-4 product-item">
                        {# col-xl-3 = 4 kolom di desktop besar #}
                        {# col-4    = 3 kolom di semua ukuran (termasuk mobile) #}
                        <div class="card pos-product-card h-100">
                            {# h-100 = tinggi 100% (sama rata dengan sebelah) #}
                            <div class="card-body">
                                <h6>Nama Produk</h6>
                                <div class="product-price">Rp 75.000</div>
                                <button class="btn btn-primary btn-sm w-100">Tambah</button>
                            </div>
                        </div>
                    </div>
                    {# ... product items lainnya ... #}
                </div>
            </div>
        </div>
    </div>
    
    {# Kolom Kanan: Keranjang (1/3 layar) #}
    <div class="col-xl-4 col-lg-5 cart-section-col">
        <div class="card">
            <div class="card-header cart-header-flex">
                {# cart-header-flex = custom flex: nowrap + space-between #}
                {# Memastikan badge selalu di kanan, tidak turun ke bawah #}
                <h5 class="mb-0">Keranjang</h5>
                <span class="badge bg-label-info" id="kasirBadge">
                    Kasir: <span id="kasirBadgeName">Nama</span>
                </span>
            </div>
            <div class="card-body">
                {# Cart content... #}
            </div>
        </div>
    </div>
</div>
```

### Tips Tata Letak Card:

```
ATURAN UMUM:
1. Selalu bungkus kolom dalam <div class="row">
2. Gunakan g-* untuk gap horizontal+vertikal
3. Gunakan gy-* untuk gap vertikal saja (saat kolom stack)
4. Gunakan gx-* untuk gap horizontal saja
5. Card di dalam card → row baru di dalam card-body
6. h-100 pada card untuk tinggi rata
7. d-flex + justify-content-between untuk header card

BORDER & DARK MODE:
1. Default border: border: 1px solid rgba(0,0,0,0.25)
2. Dark mode: html.dark-style .card { border: 1px solid rgba(255,255,255,0.2) }
3. Hover: border-color berubah saat hover

POSISI BADGE/ELEMENT DI HEADER:
1. Gunakan d-flex justify-content-between align-items-center
2. Tambah flex-wrap: nowrap agar tidak turun pada mobile
3. Badge: white-space: nowrap + flex-shrink: 0
```

---

## E. Sidebar Menu (Vertikal)

### Cara Kerja Sidebar:

```
1. Data menu disimpan di FILE JSON:
   templates/layout/partials/menu/vertical/json/vertical_menu.json

2. JSON di-load oleh Python (context processor):
   config/context_processors.py → menu_data

3. Template render menu secara LOOP:
   vertical_menu.html → {% for item in menu_data.menu %}

4. Setiap item di-CEK permission:
   menu_item_template.html → cek apakah user punya akses

5. CSS & JS menangani visual:
   menu.js → toggle collapse, active state
   core.css → styling sidebar
```

### Struktur JSON Menu:

```json
{
  "menu": [
    {
      "menu_header": "Dashboard"
    },
    {
      "name": "Dashboard",
      "icon": "ri-home-smile-line",
      "slug": "dashboard",
      "url": "/",
      "module": "dashboard",
      "permission_action": "read"
    },
    {
      "menu_header": "Master Data"
    },
    {
      "name": "Produk",
      "icon": "ri-shopping-bag-3-line",
      "slug": "produk",
      "url": null,
      "submenu": [
        {
          "name": "Daftar Produk",
          "slug": "daftar_produk",
          "url": "/produk/list/",
          "module": "produk",
          "sub_module": "daftar_produk",
          "permission_action": "read"
        },
        {
          "name": "Kategori",
          "slug": "kategori",
          "url": "/produk/kategori/",
          "module": "produk",
          "sub_module": "kategori",
          "permission_action": "read"
        }
      ]
    }
  ]
}
```

### HTML Sidebar (Simplified):

```html
{# templates/layout/partials/menu/vertical/vertical_menu.html #}

<aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    {# layout-menu  = styling Sneat #}
    {# menu-vertical = mode vertikal (sidebar kiri) #}
    {# bg-menu-theme = warna otomatis dark/light #}
    
    {# LOGO #}
    <div class="app-brand demo">
        <a href="{% url 'dashboard:index' %}" class="app-brand-link">
            {% include 'partials/logo.html' %}
            <span class="app-brand-text">{{ system_title }}</span>
        </a>
    </div>
    
    {# MENU ITEMS #}
    <ul class="menu-inner py-1">
        {% for item in menu_data.menu %}
            {% if "menu_header" in item %}
                {# ═══ HEADER (teks pemisah grup) ═══ #}
                <li class="menu-header">
                    <span>{{ item.menu_header }}</span>
                </li>
            {% else %}
                {# ═══ MENU ITEM (link navigasi) ═══ #}
                <li class="menu-item {% if item is active %}active open{% endif %}">
                    <a href="{{ item.url }}" class="menu-link {% if item.submenu %}menu-toggle{% endif %}">
                        <i class="menu-icon {{ item.icon }}"></i>
                        <div>{{ item.name }}</div>
                    </a>
                    
                    {% if item.submenu %}
                    {# ═══ SUBMENU (dropdown) ═══ #}
                    <ul class="menu-sub">
                        {% for sub in item.submenu %}
                        <li class="menu-item">
                            <a href="{{ sub.url }}" class="menu-link">
                                <div>{{ sub.name }}</div>
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </li>
            {% endif %}
        {% endfor %}
    </ul>
</aside>
```

### Cara Menambah Menu Sidebar Baru:

```json
// Tambah di vertical_menu.json:
{
    "name": "Catatan",
    "icon": "ri-sticky-note-line",
    "slug": "catatan",
    "url": "/catatan/list/",
    "module": "catatan",
    "sub_module": "catatan",
    "permission_action": "read"
}
// Setelah ditambah → restart server → menu muncul di sidebar
```

---

## F. Navbar (Navigation Bar)

Navbar = bar horizontal di atas halaman, berisi search, user info, notifications.

```html
{# templates/layout/partials/navbar/navbar.html (simplified) #}

<nav class="layout-navbar container-xxl navbar navbar-expand-xl navbar-detached 
            align-items-center bg-navbar-theme" id="layout-navbar">
    {# layout-navbar     = styling Sneat #}
    {# navbar-detached   = tidak menempel di atas (ada gap) #}
    {# bg-navbar-theme   = warna otomatis dark/light #}
    
    {# ═══ HAMBURGER MENU (Mobile) ═══ #}
    <div class="layout-menu-toggle navbar-nav align-items-xl-center me-3 me-xl-0 d-xl-none">
        <a class="nav-item nav-link px-0 me-xl-4" href="javascript:void(0)">
            <i class="ri-menu-fill ri-22px"></i>
        </a>
    </div>
    
    {# ═══ SEARCH BAR ═══ #}
    <div class="navbar-nav-right d-flex align-items-center">
        <div class="navbar-nav align-items-center">
            <div class="nav-item navbar-search-wrapper">
                <a class="nav-link search-toggler">
                    <i class="ri-search-line ri-22px"></i>
                    <span class="d-none d-md-inline-block">Search (Ctrl+/)</span>
                </a>
            </div>
        </div>
        
        {# ═══ USER DROPDOWN (Kanan) ═══ #}
        <ul class="navbar-nav flex-row align-items-center ms-auto">
            <li class="nav-item navbar-dropdown dropdown-user dropdown">
                <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                    <div class="avatar avatar-online">
                        <img src="{{ user.profile.avatar }}" class="rounded-circle">
                    </div>
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="/pengaturan/profil/">Profil</a></li>
                    <li><a class="dropdown-item" href="/logout/">Logout</a></li>
                </ul>
            </li>
        </ul>
    </div>
</nav>
```

---

## G. Tabel & DataTables

### DataTables — Tabel Interaktif:

DataTables = library jQuery yang memberi tabel HTML kemampuan: **search, sort, pagination, export**.

```javascript
// ═══ INISIALISASI DATATABLES LENGKAP ═══
$('#myTable').DataTable({
    // ─── BAHASA INDONESIA ───
    language: {
        sEmptyTable:    "Tidak ada data yang tersedia",
        sProcessing:    "Sedang memproses...",
        sLengthMenu:    "Tampilkan _MENU_ data",
        sZeroRecords:   "Tidak ditemukan data yang sesuai",
        sInfo:          "Menampilkan _START_ sampai _END_ dari _TOTAL_ data",
        sInfoEmpty:     "Menampilkan 0 sampai 0 dari 0 data",
        sInfoFiltered:  "(disaring dari _MAX_ total data)",
        sSearch:        "Cari:",
        oPaginate: {
            sFirst:    "Pertama",
            sPrevious: "Sebelumnya",
            sNext:     "Selanjutnya",
            sLast:     "Terakhir"
        }
    },
    
    // ─── PENGATURAN ───
    order: [[0, 'asc']],       // Sort kolom pertama ascending
    pageLength: 25,             // 25 baris per halaman
    lengthMenu: [               // Opsi jumlah per halaman
        [10, 25, 50, 100, -1], 
        ['10', '25', '50', '100', 'Semua']
    ],
    responsive: false,          // false = scroll horizontal, true = collapse
    columnDefs: [
        { orderable: false, targets: [-1] }  // Kolom terakhir tidak sortable
    ],
    
    // ─── DOM LAYOUT ───
    // Mengatur posisi elemen DataTables
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
         '<"table-responsive"rt>' +
         '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
    // l = Length (dropdown "Tampilkan N data")  → kiri atas
    // f = Filter (search box)                  → kanan atas
    // r = pRocessing indicator                 → tengah
    // t = Table                                → tengah
    // i = Info ("Menampilkan 1-25 dari 100")   → kiri bawah
    // p = Pagination                           → kanan bawah
    
    initComplete: function() {
        // Callback setelah DataTables selesai inisialisasi
        $('.dataTables_filter input').attr('placeholder', 'Cari produk...');
    }
});
```

---

## H. Komponen Form Lengkap

### Semua Jenis Input Sneat:

```html
{# ═══ TEXT INPUT ═══ #}
<input type="text" class="form-control" placeholder="Nama">
{# form-control = styling Sneat: border, padding, focus glow #}

{# ═══ PASSWORD ═══ #}
<div class="input-group">
    <input type="password" class="form-control" id="password">
    <span class="input-group-text cursor-pointer" onclick="togglePassword()">
        <i class="ri-eye-off-line"></i>
    </span>
</div>

{# ═══ SELECT / DROPDOWN ═══ #}
<select class="form-select">
    <option value="">-- Pilih --</option>
    <option value="1">Option 1</option>
</select>

{# ═══ TEXTAREA ═══ #}
<textarea class="form-control" rows="4" placeholder="Deskripsi"></textarea>

{# ═══ CHECKBOX ═══ #}
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="aktif">
    <label class="form-check-label" for="aktif">Aktif</label>
</div>

{# ═══ RADIO ═══ #}
<div class="form-check">
    <input class="form-check-input" type="radio" name="tipe" id="tipe1" value="1">
    <label class="form-check-label" for="tipe1">Tipe A</label>
</div>

{# ═══ SWITCH TOGGLE ═══ #}
<div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" id="toggle">
    <label class="form-check-label" for="toggle">Aktif</label>
</div>

{# ═══ INPUT GROUP (PREFIX/SUFFIX) ═══ #}
<div class="input-group">
    <span class="input-group-text">Rp</span>
    <input type="number" class="form-control" value="0">
    <span class="input-group-text">,00</span>
</div>

{# ═══ FILE UPLOAD ═══ #}
<input class="form-control" type="file" accept="image/*">

{# ═══ DATE PICKER ═══ #}
<input type="date" class="form-control" value="2026-02-21">

{# ═══ FLOATING LABEL ═══ #}
<div class="form-floating">
    <input type="text" class="form-control" id="nama" placeholder="Nama">
    <label for="nama">Nama Produk</label>
    {# Label naik ke atas saat di-focus/diisi #}
</div>
```

---

## I. Komponen Button (Tombol)

### Semua Varian:

```html
{# ═══ SOLID (Isi penuh) ═══ #}
<button class="btn btn-primary">Primary #696CFF</button>
<button class="btn btn-success">Success #71DD37</button>
<button class="btn btn-danger">Danger #FF4C51</button>
<button class="btn btn-warning">Warning #FFAB00</button>
<button class="btn btn-info">Info #03C3EC</button>
<button class="btn btn-secondary">Secondary #8592A3</button>

{# ═══ LABEL (Soft/Outline — CUSTOM SNEAT) ═══ #}
<button class="btn btn-label-primary">Label Primary</button>
<button class="btn btn-label-success">Label Success</button>
{# btn-label-* = BUKAN bawaan Bootstrap, ini custom Sneat #}
{# Efek: background transparan muda, teks berwarna #}

{# ═══ OUTLINE (Border saja — BAWAAN BOOTSTRAP) ═══ #}
<button class="btn btn-outline-primary">Outline</button>

{# ═══ UKURAN ═══ #}
<button class="btn btn-sm btn-primary">Kecil</button>   {# h=31px #}
<button class="btn btn-primary">Normal</button>          {# h=38px #}
<button class="btn btn-lg btn-primary">Besar</button>    {# h=48px #}

{# ═══ DENGAN IKON ═══ #}
<button class="btn btn-primary">
    <i class="ri-add-line me-1"></i>Tambah
</button>

{# ═══ ICON ONLY (tanpa teks) ═══ #}
<button class="btn btn-sm btn-icon btn-label-warning">
    <i class="ri-edit-line"></i>
</button>

{# ═══ LOADING STATE ═══ #}
<button class="btn btn-primary" disabled>
    <span class="spinner-border spinner-border-sm me-1"></span>
    Menyimpan...
</button>
```

---

## J. Komponen Modal (Dialog)

```html
{# ═══ MODAL KONFIRMASI HAPUS — POLA STANDAR ═══ #}
<div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        {# modal-dialog-centered = posisi tengah layar #}
        <div class="modal-content">
            <div class="modal-header bg-danger py-3">
                <h5 class="modal-title text-white mb-0">
                    <i class="ri-delete-bin-line me-2"></i>Konfirmasi Hapus
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center py-4">
                <i class="ri-error-warning-line text-danger" style="font-size: 4rem;"></i>
                <h4 class="mt-3">Yakin ingin menghapus?</h4>
                <p class="text-muted">Item: <strong id="deleteName"></strong></p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-label-secondary" data-bs-dismiss="modal">Batal</button>
                <button type="button" class="btn btn-danger" id="confirmDeleteBtn">Ya, Hapus</button>
            </div>
        </div>
    </div>
</div>

{# Cara buka modal dari JavaScript: #}
<script>
function confirmDelete(id, nama) {
    document.getElementById('deleteName').textContent = nama;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();  // ← Bootstrap JS API
}
</script>
```

### Ukuran Modal:

```html
<div class="modal-dialog">                        {# Default: 500px #}
<div class="modal-dialog modal-sm">                {# Small: 300px #}
<div class="modal-dialog modal-lg">                {# Large: 800px #}
<div class="modal-dialog modal-xl">                {# Extra Large: 1140px #}
<div class="modal-dialog modal-fullscreen">        {# Full screen #}
```

---

## K. Alert, Toast, Messages

### Django Messages → Alert:

```python
# Di views.py (Python):
from django.contrib import messages

def form_valid(self, form):
    messages.success(self.request, 'Data berhasil disimpan!')
    # Tag: success, error, warning, info
    return super().form_valid(form)
```

```html
{# Di template (HTML): #}
{% if messages %}
{% for message in messages %}
<div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
    {% if message.tags == 'success' %}
        <i class="ri-checkbox-circle-line me-2"></i>
    {% elif message.tags == 'error' %}
        <i class="ri-error-warning-line me-2"></i>
    {% endif %}
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endfor %}
{% endif %}
```

### Toast Notification JavaScript (setelah AJAX):

```javascript
function showToast(message, type) {
    const colors = { success: 'alert-success', error: 'alert-danger', warning: 'alert-warning' };
    const icons = { success: 'ri-checkbox-circle-line', error: 'ri-error-warning-line' };
    
    const html = `
    <div class="alert ${colors[type]} alert-dismissible fade show 
                position-fixed top-0 start-50 translate-middle-x mt-3" 
         style="z-index: 9999; min-width: 300px;" role="alert">
        <i class="${icons[type]} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', html);
    setTimeout(() => document.querySelector('.alert')?.remove(), 3000);
}
```

---

## L. Badge & Label Status

```html
{# ═══ BADGE SOLID ═══ #}
<span class="badge bg-success">Aktif</span>
<span class="badge bg-danger">Nonaktif</span>
<span class="badge bg-warning">Pending</span>

{# ═══ BADGE LABEL (Soft — CUSTOM SNEAT) ═══ #}
<span class="badge bg-label-success">Lunas</span>
<span class="badge bg-label-danger">Belum Bayar</span>
<span class="badge bg-label-warning">Sebagian</span>

{# ═══ BADGE ROUNDED ═══ #}
<span class="badge rounded-pill bg-primary">99+</span>

{# ═══ CONTOH: Status Dinamis dari Django ═══ #}
{% if order.status == 'draft' %}
    <span class="badge bg-label-warning">Draft</span>
{% elif order.status == 'confirmed' %}
    <span class="badge bg-label-info">Dikonfirmasi</span>
{% elif order.status == 'done' %}
    <span class="badge bg-label-success">Selesai</span>
{% endif %}
```

---

## M. Icon (Remix Icon)

### Ikon Paling Sering Dipakai:

| Ikon | Class | Kegunaan |
|------|-------|----------|
| ➕ | `ri-add-line` | Tombol Tambah |
| ✏️ | `ri-edit-line` | Tombol Edit |
| 🗑️ | `ri-delete-bin-line` | Tombol Hapus |
| 👁️ | `ri-eye-line` | Detail/Preview |
| 💾 | `ri-save-line` | Simpan |
| ❌ | `ri-close-line` | Batal/Tutup |
| 🔍 | `ri-search-line` | Cari |
| 📦 | `ri-shopping-bag-3-line` | Produk |
| 📁 | `ri-folder-line` | Kategori |
| 🏠 | `ri-home-4-line` | Gudang |
| 📊 | `ri-line-chart-line` | Laporan |
| 📄 | `ri-file-pdf-line` | PDF |
| 📗 | `ri-file-excel-2-line` | Excel |
| ✅ | `ri-checkbox-circle-line` | Sukses |
| ⚠️ | `ri-error-warning-line` | Error |
| 🔄 | `ri-refresh-line` | Reset |

Dokumentasi lengkap: [https://remixicon.com/](https://remixicon.com/)

---

## N. Charts & Grafik (ApexCharts)

### Apa itu ApexCharts?

ApexCharts = library JavaScript untuk membuat grafik/chart interaktif. Di project ini digunakan untuk **dashboard**.

### Alur Data: Django → ApexCharts:

```
LANGKAH 1: Django hitung data di views.py
─────────────────────────────────────────
# apps/dashboard/views.py
class DashboardView(TemplateView):
    def get_context_data(self, **kwargs):
        # Ambil penjualan per hari di bulan ini
        penjualan = SalesOrder.objects.filter(
            tanggal__month=today.month
        ).values('tanggal__day').annotate(
            total=Sum('grand_total')
        )
        
        # Siapkan data untuk chart
        chart_data = [float(p['total']) for p in penjualan]
        chart_labels = [str(p['tanggal__day']) for p in penjualan]
        
        context['sales_chart_data'] = chart_data    # [150000, 200000, ...]
        context['sales_chart_labels'] = chart_labels  # ['1', '2', '3', ...]
        return context

LANGKAH 2: Django inject data ke HTML via json_script
─────────────────────────────────────────
{# dashboard/index.html #}
{{ sales_chart_data|json_script:"sales-chart-data" }}
{# Output HTML: #}
{# <script id="sales-chart-data" type="application/json"> #}
{#   [150000, 200000, 180000, 250000] #}
{# </script> #}

{{ sales_chart_labels|json_script:"sales-chart-labels" }}

LANGKAH 3: JavaScript ambil data + render chart
─────────────────────────────────────────
<script>
// Ambil data dari tag <script id="sales-chart-data">
const data = JSON.parse(document.getElementById('sales-chart-data').textContent);
const labels = JSON.parse(document.getElementById('sales-chart-labels').textContent);

// Buat chart
const chart = new ApexCharts(document.querySelector('#salesChart'), {
    chart: { type: 'area', height: 300 },
    series: [{ name: 'Penjualan', data: data }],
    xaxis: { categories: labels },
    // ... konfigurasi lain
});
chart.render();
</script>
```

### Jenis Chart yang Digunakan di Dashboard:

```javascript
// ═══ 1. AREA CHART — Tren Penjualan Bulanan ═══
{
    chart: { type: 'area', height: 120, sparkline: { enabled: true } },
    series: [{ name: 'Penjualan', data: [150000, 200000, 180000] }],
    stroke: { width: 2, curve: 'smooth' },  // Garis halus
    fill: {
        type: 'gradient',           // Isi gradien di bawah garis
        gradient: { opacityFrom: 0.8, opacityTo: 0.1 }
    },
    colors: ['#696CFF'],            // Warna ungu primary
    tooltip: {
        y: { formatter: (val) => 'Rp ' + val.toLocaleString('id-ID') }
    }
}

// ═══ 2. BAR CHART — Keuntungan per Cabang ═══
{
    chart: { type: 'bar', height: 153 },
    series: [{ name: 'Profit', data: [50, 80, 60, 90, 70] }],
    plotOptions: {
        bar: {
            borderRadius: 8,        // Ujung bar membulat
            columnWidth: '43%'      // Lebar bar
        }
    },
    colors: ['#71DD37'],            // Warna hijau success
    xaxis: {
        categories: ['Cab1', 'Cab2', 'Cab3', 'Cab4', 'Cab5']
    }
}

// ═══ 3. RADIAL BAR — Progress Lingkaran ═══
{
    chart: { type: 'radialBar', height: 90, width: 90 },
    series: [75],                    // 75% progress
    plotOptions: {
        radialBar: {
            hollow: { 
                size: '52%',         // Lubang tengah 52%
                image: '/icon.png',  // Ikon di tengah
                imageWidth: 24
            },
            dataLabels: { show: false }
        }
    },
    colors: ['#696CFF']
}

// ═══ 4. BAR CHART DISTRIBUTED — Biaya per Kategori ═══
{
    chart: { type: 'bar', height: 314 },
    plotOptions: {
        bar: {
            distributed: true,       // Setiap bar warna berbeda!
            borderRadius: 8
        }
    },
    series: [{ data: [30000, 50000, 20000, 45000] }],
    colors: ['#E8E8FF', '#696CFF', '#E8E8FF', '#696CFF'],
    xaxis: { categories: ['Gaji', 'Sewa', 'Utilitas', 'Marketing'] }
}
```

---

## O. Dark Mode & Theme System

### Cara Kerja:

```
1. Konfigurasi awal di config/template.py → TEMPLATE_CONFIG:
   'style': 'light',        # Default: light mode
   'hasCustomizer': True,   # Tampilkan panel customizer (kanan bawah)

2. TemplateHelper.init_context() membaca TEMPLATE_CONFIG:
   → Set context['style'] = 'light'
   → Set context['theme'] = 'theme-default'
   
3. master.html menggunakan variabel tersebut:
   <html class="light-style" data-theme="theme-default">
   
4. CSS otomatis berubah berdasarkan class:
   .light-style → core.css + theme-default.css
   .dark-style  → core-dark.css + theme-default-dark.css
   
5. Template Customizer (JS) mengubah class via JavaScript:
   Saat user klik toggle dark mode:
   document.documentElement.className = 'dark-style'
   → CSS otomatis berubah
```

### CSS Variable (Dark Mode Aware):

| Variable | Light | Dark | Fungsi |
|----------|-------|------|--------|
| `--bs-body-bg` | `#f5f5f9` | `#232333` | Background halaman |
| `--bs-body-color` | `#697a8d` | `#cfd3ec` | Teks utama |
| `--bs-card-bg` | `#ffffff` | `#2b2c40` | Background card |
| `--bs-border-color` | `#d9dee3` | `#444564` | Border |
| `--bs-primary` | `#696cff` | `#696cff` | Warna utama |

```css
/* BENAR — otomatis dark/light: */
.custom { background: var(--bs-body-bg); color: var(--bs-body-color); }

/* SALAH — tidak berubah di dark mode: */
.custom { background: #ffffff; color: #333; }
```

### Custom CSS Fix untuk Dark Mode:

Sneat starter kit memiliki **masalah**: beberapa teks "hilang" saat dark mode karena kontras rendah. Fix sudah ditambahkan di `templates/layout/partials/styles.html` baris 429–642 menggunakan selector `[data-theme="dark"]`:

```css
/* ═══ Contoh Fix di styles.html ═══ */

/* Sidebar menu header (MASTER DATA, TRANSAKSI, dll) — terlalu gelap di dark mode */
[data-theme="dark"] .menu-header-text {
  color: rgba(255, 255, 255, 0.45) !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Menu link teks — perlu lebih terang */
[data-theme="dark"] .menu-link {
  color: rgba(255, 255, 255, 0.75) !important;
}
[data-theme="dark"] .menu-link:hover {
  color: rgba(255, 255, 255, 0.95) !important;
}

/* Card heading — harus kontras tinggi */
[data-theme="dark"] .card h1, [data-theme="dark"] .card h2,
[data-theme="dark"] .card h3, [data-theme="dark"] .card h4,
[data-theme="dark"] .card h5, [data-theme="dark"] .card h6 {
  color: rgba(255, 255, 255, 0.9) !important;
}

/* Form inputs — teks harus terbaca */
[data-theme="dark"] .form-control,
[data-theme="dark"] .form-select {
  color: rgba(255, 255, 255, 0.85) !important;
}
```

**Tabel komponen yang diperbaiki:**

| Komponen | Nilai Dark Mode | Keterangan |
|----------|----------------|------------|
| Menu headers sidebar | `rgba(255,255,255,0.45)` | MASTER DATA, TRANSAKSI, dll |
| Menu links | `rgba(255,255,255,0.75)` | Dashboard, Produk, dll |
| Sub-menu links | `rgba(255,255,255,0.6)` | Sub-item dropdown |
| Active menu item | `#ffffff` | Item yang sedang diklik |
| Card headings h1–h6 | `rgba(255,255,255,0.9)` | Judul card |
| Card body text | `rgba(255,255,255,0.85)` | Paragraf dalam card |
| `.text-muted` | `rgba(255,255,255,0.5)` | Teks secondary |
| Table headers/cells | `0.7` / `0.8` opacity | Tabel DataTables |
| Form labels/inputs | `0.75` / `0.85` opacity | Label dan input |
| Modal title/body | `0.9` / `0.8` opacity | Dialog popup |

---

## O.2. Custom CSS Mobile Responsive

### Masalah & Solusi

Sneat Bootstrap 5 starter kit dirancang untuk desktop. Di layar HP (≤ 576px), padding/margin terlalu besar dan menyebabkan layout "longgar". Fix sudah ditambahkan di `templates/layout/partials/styles.html`.

### Lokasi CSS di styles.html:

```
styles.html (642 baris):
├── Baris 38–81    → Pagination Scrollbar Fix (≤ 991px)
├── Baris 83–122   → Export Buttons Responsive (≤ 991px + ≤ 575px)
├── Baris 124–388  → Global Mobile Margin/Padding (≤ 576px)
├── Baris 390–427  → Tablet Responsive (577–767px)
└── Baris 429–642  → Dark Mode Fix (semua ukuran layar)
```

### Breakpoint yang Digunakan:

| Breakpoint | Layar | Komponen yang Diatur |
|-----------|-------|---------------------|
| `≤ 991px` | Tablet + HP | Pagination scrollbar, export buttons wrap |
| `≤ 576px` | HP | Semua komponen (container, card, form, tabel, dll) |
| `577–767px` | Tablet kecil | Container, grid, card, tabel, heading |
| `≤ 575px` | HP kecil | Export buttons stack vertikal |

### Contoh: Pagination Scrollbar Fix

```css
/* Masalah: Scrollbar horizontal muncul di area pagination */
/* Solusi: Sembunyikan scrollbar, tapi tetap izinkan scroll di tabel */

@media (max-width: 991px) {
  .card-datatable {
    overflow-x: hidden !important;
    scrollbar-width: none !important;          /* Firefox */
    -ms-overflow-style: none !important;       /* IE/Edge */
  }
  .card-datatable::-webkit-scrollbar {
    display: none !important;                  /* Chrome/Safari */
  }
  /* Tabel tetap bisa scroll horizontal */
  .dataTables_wrapper > .table-responsive {
    overflow-x: auto !important;
  }
}
```

### Contoh: Export Buttons Responsive

```css
/* Masalah: Tombol export (PDF, Excel, Print) gepeng di mobile */

/* Tablet: wrap konten */
@media (max-width: 991px) {
  .card-header.d-flex.justify-content-between {
    flex-wrap: wrap !important;
    gap: 0.5rem !important;
  }
}

/* HP kecil: stack vertikal */
@media (max-width: 575px) {
  .card-header .d-flex.gap-2 {
    flex-direction: column !important;
  }
  .card-header .d-flex.gap-2 > .btn {
    width: 100% !important;
    font-size: 0.8125rem !important;
  }
}
```

### Contoh: Global Mobile Compact (≤ 576px)

```css
@media (max-width: 576px) {
  /* Container: kurangi padding samping */
  .container-p-y {
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
  }

  /* Card: padding lebih compact */
  .card > .card-body { padding: 0.875rem !important; }
  .card > .card-header { padding: 0.875rem 0.875rem 0.5rem !important; }

  /* Form: ukuran lebih kecil */
  .form-control, .form-select {
    font-size: 0.8125rem !important;
    padding: 0.4375rem 0.75rem !important;
  }

  /* Tabel: padding sel dikurangi */
  .table th, .table td {
    padding: 0.5rem 0.625rem !important;
    font-size: 0.8rem !important;
  }

  /* Pagination compact */
  .pagination .page-link {
    padding: 0.3rem 0.6rem !important;
    font-size: 0.75rem !important;
  }

  /* Modal compact */
  .modal .modal-body { padding: 0.875rem !important; }
}
```

### Cara Menambah CSS Custom Baru:

```css
/* Tambahkan di styles.html, sebelum tag </style> penutup */

/* Contoh: Custom card shadow untuk HP */
@media (max-width: 576px) {
  .card {
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    /* Shadow lebih subtle di mobile untuk hemat render */
  }
}

/* Contoh: Custom dark mode untuk komponen baru */
[data-theme="dark"] .custom-widget {
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.8) !important;
}
```

---

## P. Error Handler (404, 403, 500)

### Cara Kerja Error Handler di Django:

```python
# ═══ LANGKAH 1: Definisi handler di web_project/views.py ═══

def custom_error_404(request, exception):
    """Halaman Tidak Ditemukan (404)"""
    context = {
        'layout_path': 'layout/layout_blank.html',  # Layout TANPA sidebar
        'status': 404,
        'style': request.COOKIES.get('style', 'light'),
    }
    return render(request, 'pages_misc_error.html', context, status=404)

def custom_error_403(request, exception):
    """Akses Ditolak (403) — user tidak punya permission"""
    context = {
        'layout_path': 'layout/layout_blank.html',
        'status': 403,
        'style': request.COOKIES.get('style', 'light'),
    }
    return render(request, 'pages_misc_not_authorized.html', context, status=403)

def custom_error_500(request):
    """Server Error (500) — bug di kode"""
    context = {
        'layout_path': 'layout/layout_blank.html',
        'status': 500,
        'style': request.COOKIES.get('style', 'light'),
    }
    return render(request, 'pages_misc_server_error.html', context, status=500)
```

```python
# ═══ LANGKAH 2: Daftarkan di config/urls.py ═══

handler404 = custom_error_404
handler403 = custom_error_403
handler400 = custom_error_400
handler500 = custom_error_500
```

```
Kenapa error handler perlu custom?
→ Default Django: halaman error JELEK (putih, teks kecil)
→ Custom: halaman error CANTIK, sesuai tema Sneat
→ Layout blank: tanpa sidebar (user mungkin belum login)
→ Dark mode aware: mengikuti preferensi user dari cookie
```

---

## Q. Halaman Login

### Cara Kerja Login di Project Ini:

```
1. User akses URL apapun tanpa login
2. Django middleware (AuthenticationMiddleware) deteksi → belum login
3. Redirect ke /login/ 
4. Login view (auth/views.py) tampilkan form
5. User isi username + password → POST
6. Django authenticate() → cek di database
7. Jika berhasil → login(request, user) → redirect ke dashboard
8. Jika gagal → tampilkan error "Kredensial tidak valid"
```

### Template Login:

```html
{# templates/auth/login.html (simplified) #}

{% extends 'layout/layout_blank.html' %}
{# ↑ Layout BLANK = tanpa sidebar, navbar, footer #}
{# Hanya ada: <html>, <head>, CSS, dan <body> kosong #}

{% block content %}
<div class="authentication-wrapper authentication-basic px-4">
    <div class="authentication-inner py-4">
        {# Card login di tengah layar #}
        <div class="card p-2">
            <div class="card-body">
                {# Logo #}
                <div class="app-brand justify-content-center mb-4">
                    <img src="{{ system_logo_url }}" height="50" alt="Logo">
                </div>
                
                <h4 class="mb-1">Selamat Datang! 👋</h4>
                <p class="mb-4">Masuk ke akun Anda</p>
                
                {# Form Login #}
                <form method="POST" action="{% url 'login' %}">
                    {% csrf_token %}
                    
                    {# Username #}
                    <div class="mb-3">
                        <label class="form-label" for="username">Username</label>
                        <input type="text" class="form-control" id="username" 
                               name="username" placeholder="Masukkan username" 
                               autofocus required>
                    </div>
                    
                    {# Password + Toggle Visibility #}
                    <div class="mb-3">
                        <label class="form-label" for="password">Password</label>
                        <div class="input-group">
                            <input type="password" class="form-control" 
                                   id="password" name="password" 
                                   placeholder="••••••••" required>
                            <span class="input-group-text cursor-pointer" 
                                  id="togglePassword">
                                <i class="ri-eye-off-line"></i>
                            </span>
                        </div>
                    </div>
                    
                    {# Remember Me + Lupa Password #}
                    <div class="mb-3 d-flex justify-content-between">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" 
                                   id="remember" name="remember">
                            <label class="form-check-label" for="remember">
                                Ingat saya
                            </label>
                        </div>
                        <a href="{% url 'forgot_password' %}">Lupa Password?</a>
                    </div>
                    
                    {# Tombol Login #}
                    <button class="btn btn-primary d-grid w-100" type="submit">
                        Masuk
                    </button>
                </form>
                
                {# Error Messages #}
                {% if messages %}
                {% for message in messages %}
                <div class="alert alert-danger mt-3">{{ message }}</div>
                {% endfor %}
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## R. Pola Template Lengkap CRUD

### Template LIST:

```
┌──────────────────────────────────────────┐
│ header: Judul + Btn Tambah              │
├──────────────────────────────────────────┤
│ row g-3 mb-4: Statistik cards           │
│ ┌─col-md-4─┐┌─col-md-4─┐┌─col-md-4─┐  │
│ │Card stat1 ││Card stat2 ││Card stat3│  │
│ └──────────┘└──────────┘└──────────┘  │
├──────────────────────────────────────────┤
│ card: Filter + Kolom                    │
├──────────────────────────────────────────┤
│ card:                                    │
│ ├─header: "Daftar X" + Export buttons   │
│ ├─datatable: search, sort, pagination   │
│ └─footer: ringkasan                     │
├──────────────────────────────────────────┤
│ modal: Konfirmasi hapus                 │
└──────────────────────────────────────────┘
```

### Template FORM:

```
┌──────────────────────────────────────────┐
│ h4: "Tambah X" / "Edit X"              │
├──────────────────────────────────────────┤
│ <form method="POST">                    │
│   {% csrf_token %}                      │
│   card:                                  │
│   ├─body: row g-3                       │
│   │  ┌─col-md-6─┐ ┌─col-md-6─┐         │
│   │  │ Input 1  │ │ Input 2  │          │
│   │  └──────────┘ └──────────┘         │
│   │  ┌─col-12────────────────┐          │
│   │  │ Textarea              │          │
│   │  └────────────────────────┘         │
│   └─footer: [Batal] [Simpan]           │
│ </form>                                  │
└──────────────────────────────────────────┘
```

---

*Lanjut ke [11_PANDUAN_MEMBUAT_MODUL_BARU.md](11_PANDUAN_MEMBUAT_MODUL_BARU.md) →*
