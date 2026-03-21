# 🎨 05 — Template, Layout & Komponen UI — Penjelasan Sangat Detail

## A. Apa itu Template Engine Django? Kenapa Tidak Tulis HTML Biasa?

**Masalah HTML biasa:**
```html
<!-- HTML statis — TIDAK bisa menampilkan data dari database -->
<h1>Daftar Produk</h1>
<p>Beras - Rp 15.000</p>    <!-- Harus diedit manual setiap ada produk baru! -->
<p>Indomie - Rp 3.500</p>
```

**Solusi Django Template Engine:**
```html
<!-- Template Django — DINAMIS, data dari database -->
<h1>Daftar Produk ({{ produk_list|length }} item)</h1>
{% for p in produk_list %}
    <p>{{ p.nama }} - Rp {{ p.harga_jual|floatformat:0 }}</p>
{% endfor %}
<!-- Otomatis menampilkan SEMUA produk dari database -->
<!-- Jika ada 100 produk, 100 baris otomatis di-generate -->
```

**Output HTML yang dihasilkan:**
```html
<h1>Daftar Produk (3 item)</h1>
<p>Beras - Rp 15000</p>
<p>Indomie - Rp 3500</p>
<p>Aqua - Rp 4000</p>
```

---

## B. Sintaks Template Django — Detail

### 1. `{{ variabel }}` — Menampilkan Nilai

```html
{{ produk.nama }}
<!-- Output: Beras Premium -->
<!-- Django ambil atribut 'nama' dari objek 'produk' yang dikirim oleh view -->

{{ produk.kategori.nama }}
<!-- Output: Makanan -->
<!-- Django otomatis mengikuti relasi ForeignKey:
     produk.kategori → objek Kategori → .nama → "Makanan" -->

{{ produk.stok_total }}
<!-- Output: 180 -->
<!-- Memanggil @property stok_total di model Produk -->
<!-- Kenapa bisa tanpa ()? Karena @property membuat method seperti attribute -->

{{ produk.gambar.url }}
<!-- Output: /media/produk/beras.jpg -->
<!-- .url = method bawaan ImageField yang menghasilkan URL gambar -->

{{ request.user.username }}
<!-- Output: admin -->
<!-- request.user = user yang sedang login (dari AuthenticationMiddleware) -->
```

### 2. `{% tag %}` — Logika Template

#### if/elif/else — Kondisi
```html
{% if produk.aktif %}
    <span class="badge bg-success">Aktif</span>
    <!-- Output: <span class="badge bg-success">Aktif</span> -->
{% elif produk.stok_total == 0 %}
    <span class="badge bg-warning">Habis</span>
{% else %}
    <span class="badge bg-danger">Nonaktif</span>
{% endif %}
<!-- ↑ {% endif %} WAJIB ada — menandakan akhir blok if -->
<!-- Django template TIDAK pakai indentation (beda dengan Python) -->
```

**Operator yang bisa digunakan di `{% if %}`:**
```html
{% if jumlah > 0 %}          <!-- lebih besar -->
{% if jumlah >= 10 %}         <!-- lebih besar atau sama -->
{% if jumlah == 0 %}          <!-- sama dengan -->
{% if jumlah != 0 %}          <!-- tidak sama dengan -->
{% if produk.aktif %}         <!-- truthy (True, bukan kosong, bukan 0) -->
{% if not produk.aktif %}     <!-- falsy -->
{% if a and b %}              <!-- keduanya true -->
{% if a or b %}               <!-- salah satu true -->
{% if "laptop" in nama %}     <!-- substring check -->
```

#### for — Perulangan
```html
<table>
    <thead><tr><th>No</th><th>Nama</th><th>Harga</th></tr></thead>
    <tbody>
        {% for produk in produk_list %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <!-- forloop.counter = nomor urut: 1, 2, 3, ...
                 forloop.counter0 = mulai dari 0: 0, 1, 2, ...
                 forloop.first = True jika iterasi pertama
                 forloop.last = True jika iterasi terakhir
                 forloop.revcounter = hitungan mundur: 3, 2, 1 -->
            
            <td>{{ produk.nama }}</td>
            <td>Rp {{ produk.harga_jual|floatformat:0 }}</td>
        </tr>
        {% empty %}
        <!-- ↑ {% empty %} = ditampilkan jika produk_list KOSONG (0 data) -->
        <tr>
            <td colspan="3" class="text-center">Belum ada data produk</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Output jika ada 2 produk:**
```html
<tr>
    <td>1</td>
    <td>Beras Premium</td>
    <td>Rp 15000</td>
</tr>
<tr>
    <td>2</td>
    <td>Indomie Goreng</td>
    <td>Rp 3500</td>
</tr>
```

**Output jika 0 produk:**
```html
<tr>
    <td colspan="3" class="text-center">Belum ada data produk</td>
</tr>
```

### 3. `{{ variabel|filter }}` — Format Data

```html
{{ harga|floatformat:0 }}
<!-- Input: 15000.50 → Output: 15001 -->
<!-- floatformat:0 = bulatkan ke 0 desimal -->
<!-- floatformat:2 = 2 desimal: 15000.50 -->

{{ tanggal|date:"d F Y" }}
<!-- Input: 2026-02-21 → Output: 21 February 2026 -->
<!-- Format: d=hari, F=bulan(full), Y=tahun(4digit) -->
<!-- "d M Y" → 21 Feb 2026 -->
<!-- "d/m/Y" → 21/02/2026 -->

{{ deskripsi|default:"-" }}
<!-- Jika deskripsi kosong/None → Output: "-" -->
<!-- Jika deskripsi = "Bagus" → Output: "Bagus" -->

{{ deskripsi|truncatewords:10 }}
<!-- Potong setelah 10 kata, tambah "..." -->
<!-- Input: "Beras premium dari Cianjur yang dipanen dengan hati-hati oleh petani berpengalaman" -->
<!-- Output: "Beras premium dari Cianjur yang dipanen dengan hati-hati oleh ..." -->

{{ jumlah|add:5 }}
<!-- Input: 10 → Output: 15 (tamb 5) -->

{{ nama|upper }}
<!-- Input: "beras" → Output: "BERAS" -->

{{ nama|lower }}
<!-- Input: "BERAS" → Output: "beras" -->

{{ list|length }}
<!-- Input: [a, b, c] → Output: 3 -->

{{ aktif|yesno:"Ya,Tidak,Belum Diisi" }}
<!-- True → "Ya", False → "Tidak", None → "Belum Diisi" -->
```

---

## C. Template Inheritance (Pewarisan) — Cara Kerja Layout

### Konsep: Seperti "Cetakan" dan "Isi"

```
┌──────────────────────────────────────────────┐
│ master.html (CETAKAN UTAMA)                  │
│ ┌──────────────────────────────────────────┐ │
│ │ <html> <head> CSS global </head>        │ │
│ │ <body>                                   │ │
│ │   ┌──────────────────────────────────┐   │ │
│ │   │ layout_vertical.html (ISI LV.1)  │   │ │
│ │   │ ┌───────┐ ┌───────────────────┐  │   │ │
│ │   │ │Sidebar│ │                   │  │   │ │
│ │   │ │Menu   │ │  {% block content│  │   │ │
│ │   │ │       │ │  %}               │  │   │ │
│ │   │ │       │ │                   │  │   │ │
│ │   │ │       │ │  produk_list.html │  │   │ │
│ │   │ │       │ │  (ISI LEVEL 2)   │  │   │ │
│ │   │ │       │ │                   │  │   │ │
│ │   │ │       │ │  {% endblock %}   │  │   │ │
│ │   │ └───────┘ └───────────────────┘  │   │ │
│ │   └──────────────────────────────────┘   │ │
│ │   JS global                              │ │
│ │ </body> </html>                          │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### File Layout:

```html
<!-- templates/layout/master.html — BASE TEMPLATE -->
{% load static %}
<!-- ↑ {% load static %} = Load template tag 'static'
     Tanpa ini: {% static 'css/style.css' %} akan ERROR
     'static' berasal dari django.contrib.staticfiles -->

<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<!-- ↑ LANGUAGE_CODE berasal dari context processor
     Output: <html lang="id"> -->

<head>
    <title>{% block title %}ERP{% endblock %}</title>
    <!-- ↑ {% block title %} = "lubang" yang bisa diisi oleh template anak
         Jika tidak diisi: menampilkan default "ERP"
         Jika diisi: menampilkan isi dari template anak -->
    
    <!-- CSS Global (semua halaman) -->
    <link rel="stylesheet" href="{% static 'vendor/css/rtl/core.css' %}">
    <!-- ↑ {% static 'path' %} = generate URL file statis
         Output: /static/vendor/css/rtl/core.css -->
    
    {% block vendor_css %}{% endblock %}
    <!-- ↑ "Lubang" untuk CSS vendor tambahan per halaman
         Contoh: DataTables CSS hanya diload di halaman yang pakai tabel -->
    
    {% block page_css %}{% endblock %}
    <!-- ↑ "Lubang" untuk CSS custom per halaman -->
</head>

<body>
    {% block layout_content %}{% endblock %}
    <!-- ↑ "Lubang" utama — diisi oleh layout_vertical.html -->
    
    <!-- JS Global -->
    <script src="{% static 'vendor/js/bootstrap.js' %}"></script>
    <script src="{% static 'vendor/libs/jquery/jquery.js' %}"></script>
    
    {% block vendor_js %}{% endblock %}
    {% block page_js %}{% endblock %}
</body>
</html>
```

```html
<!-- templates/layout/layout_vertical.html — LAYOUT DENGAN SIDEBAR -->
{% extends layout_path %}
<!-- ↑ {% extends %} = "template ini mewarisi dari template lain"
     layout_path berasal dari TemplateLayout.init()
     Nilainya: 'layout/master.html' -->

{% block layout_content %}
    <!-- Sidebar -->
    {% include 'layout/partials/menu/vertical_menu.html' %}
    <!-- ↑ {% include %} = sisipkan file template lain di sini
         Seperti copy-paste isi file ke posisi ini
         vertical_menu.html = sidebar menu kiri -->
    
    <!-- Navbar -->
    {% include 'layout/partials/navbar/navbar.html' %}
    
    <!-- KONTEN UTAMA -->
    <div class="content-wrapper">
        {% block content %}{% endblock %}
        <!-- ↑ "Lubang" yang diisi oleh halaman spesifik -->
    </div>
    
    <!-- Footer -->
    {% include 'layout/partials/footer/footer.html' %}
{% endblock layout_content %}
```

### Cara Membuat Halaman Baru (Langkah Demi Langkah):

```html
<!-- templates/produk/produk_list.html — HALAMAN SPESIFIK -->
{% extends 'layout/layout_vertical.html' %}
<!-- ↑ Halaman ini mewarisi layout_vertical.html
     Yang berarti sudah otomatis punya: sidebar, navbar, footer -->

{% load static %}

{% block title %}Daftar Produk{% endblock %}
<!-- Output di tab browser: "Daftar Produk" (bukan default "ERP") -->

{% block vendor_css %}
{{ block.super }}
<!-- ↑ {{ block.super }} = SIMPAN CSS dari parent (jangan timpa)
     Tanpa ini: CSS vendor dari parent class hilang -->
<link rel="stylesheet" href="{% static 'vendor/libs/datatables-bs5/datatables.bootstrap5.css' %}">
<!-- ↑ Hanya halaman ini yang load CSS DataTables
     Halaman lain yang tidak pakai tabel TIDAK load CSS ini (hemat bandwidth) -->
{% endblock %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <!-- ↑ container-xxl = container Bootstrap (max-width: 1400px)
         flex-grow-1 = isi sisa ruang vertical (CSS flexbox)
         container-p-y = padding atas-bawah dari Sneat -->
    
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <!-- ↑ d-flex = display: flex
                 justify-content-between = elemen disebar rata kiri-kanan
                 align-items-center = sejajarkan vertikal tengah -->
            
            <h5 class="mb-0">Daftar Produk</h5>
            <!-- ↑ mb-0 = margin-bottom: 0 -->
            
            {% if can_create.produk %}
            <!-- ↑ can_create dari context processor user_permissions
                 Cek: apakah user login punya permission create di modul produk?
                 Jika Ya: tombol Tambah MUNCUL
                 Jika Tidak: tombol Tambah TERSEMBUNYI -->
            <a href="{% url 'produk:tambah' %}" class="btn btn-primary btn-sm">
                <i class="ri-add-line me-1"></i>Tambah Produk
                <!-- ↑ ri-add-line = ikon plus dari Remix Icon
                     me-1 = margin-end (kanan) 1 unit -->
            </a>
            {% endif %}
        </div>
        
        <div class="card-body">
            <table class="table table-hover" id="produkTable">
                <!-- ↑ table = styling tabel Bootstrap
                     table-hover = baris berubah warna saat mouse hover
                     id="produkTable" = ID unik untuk DataTables JS -->
                <thead>
                    <tr>
                        <th>No</th>
                        <th>SKU</th>
                        <th>Nama</th>
                        <th>Kategori</th>
                        <th>Harga Jual</th>
                        <th>Stok</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in produk_list %}
                    <tr id="row-{{ p.pk }}">
                        <td>{{ forloop.counter }}</td>
                        <td><code>{{ p.sku }}</code></td>
                        <!-- ↑ <code> = monospace font, cocok untuk kode/SKU -->
                        <td>{{ p.nama }}</td>
                        <td>{{ p.kategori.nama|default:"-" }}</td>
                        <td>Rp {{ p.harga_jual|floatformat:0 }}</td>
                        <td>{{ p.stok_total }}</td>
                        <td>
                            {% if can_edit.produk %}
                            <a href="{% url 'produk:edit' pk=p.pk %}" 
                               class="btn btn-sm btn-icon btn-text-secondary">
                                <i class="ri-pencil-line"></i>
                            </a>
                            {% endif %}
                            {% if can_delete.produk %}
                            <button class="btn btn-sm btn-icon btn-text-danger"
                                    onclick="hapus({{ p.pk }}, '{{ p.nama }}')">
                                <i class="ri-delete-bin-line"></i>
                            </button>
                            {% endif %}
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center py-4">
                            <i class="ri-inbox-line ri-3x text-muted d-block mb-2"></i>
                            Belum ada data produk
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock content %}

{% block page_js %}
<script>
// DataTables — tabel interaktif
$('#produkTable').DataTable({
    responsive: false,
    // ↑ responsive: false = JANGAN sembunyikan kolom di layar kecil
    //   Kenapa false? Agar user SELALU bisa lihat semua kolom
    //   Sebagai gantinya, tabel bisa di-scroll horizontal
    
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>><"table-responsive"rt><"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
    // ↑ dom = layout DataTables (di mana elemen-elemennya ditaruh)
    //   l = length changing (pilih berapa baris per halaman)
    //   f = filtering (search box)
    //   r = processing
    //   t = table
    //   i = info ("Menampilkan 1-10 dari 50 data")
    //   p = pagination
    //   "table-responsive" = wrapper div untuk scroll horizontal
    
    language: {
        sEmptyTable: "Tidak ada data",
        sLengthMenu: "Tampilkan _MENU_ data",
        sSearch: "Cari:",
        sInfo: "Menampilkan _START_ s/d _END_ dari _TOTAL_ data",
        oPaginate: { sPrevious: "Sebelumnya", sNext: "Selanjutnya" }
    },
    // ↑ language = lokalisasi teks DataTables ke Bahasa Indonesia
    
    pageLength: 25
    // ↑ Default menampilkan 25 baris per halaman
});
</script>
{% endblock page_js %}
```

---

## D. Komponen UI Sneat Bootstrap 5

### Card — Kontainer Konten
```html
<div class="card mb-4">
    <!-- card = kontainer Bootstrap dengan shadow dan rounded corner
         mb-4 = margin-bottom 4 unit (1.5rem) -->
    <div class="card-header">
        <!-- Area judul card (background sedikit berbeda) -->
        <h5 class="card-title mb-0">Judul</h5>
    </div>
    <div class="card-body">
        <!-- Area konten utama card -->
    </div>
    <div class="card-footer">
        <!-- Area bawah card (untuk tombol aksi) -->
    </div>
</div>
```

### Badge — Label Status
```html
<span class="badge bg-success">Aktif</span>
<!-- bg-success = background hijau. Warna: success=hijau, danger=merah,
     warning=kuning, info=biru muda, primary=biru, secondary=abu -->

<span class="badge bg-label-primary">Label</span>
<!-- bg-label-primary = outline style (background transparan, border berwarna) -->
```

### Button — Tombol
```html
<!-- Tombol solid -->
<button class="btn btn-primary">Simpan</button>
<!-- btn = styling tombol dasar Bootstrap
     btn-primary = warna biru (primary color)
     Warna lain: btn-success, btn-danger, btn-warning -->

<!-- Tombol kecil dengan ikon -->
<button class="btn btn-sm btn-icon btn-text-secondary">
    <i class="ri-pencil-line"></i>
</button>
<!-- btn-sm = ukuran kecil
     btn-icon = hanya ikon tanpa teks (bentuk kotak)
     btn-text-secondary = style teks (transparan, hover abu) -->
```

### Modal — Dialog Popup
```html
<div class="modal fade" id="hapusModal" tabindex="-1">
    <!-- modal = dialog popup Bootstrap
         fade = animasi fade in/out
         id = ID unik untuk referensi di JavaScript -->
    <div class="modal-dialog modal-dialog-centered">
        <!-- modal-dialog-centered = posisi tengah layar (vertikal & horizontal) -->
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Konfirmasi Hapus</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                <!-- data-bs-dismiss="modal" = tutup modal saat diklik (Bootstrap attribute) -->
            </div>
            <div class="modal-body">
                <p>Yakin ingin menghapus <strong id="namaItem"></strong>?</p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-label-secondary" data-bs-dismiss="modal">Batal</button>
                <button class="btn btn-danger" id="btnHapus">Hapus</button>
            </div>
        </div>
    </div>
</div>

<script>
// Cara menampilkan modal dari JavaScript:
const modal = new bootstrap.Modal(document.getElementById('hapusModal'));
document.getElementById('namaItem').textContent = 'Beras Premium';
modal.show();  // Modal muncul di tengah layar
</script>
```

---

## E. File styles.html — Custom CSS Responsive & Dark Mode

### Apa itu styles.html?

File `templates/layout/partials/styles.html` adalah **partial template** yang di-include di `master.html`. File ini berisi inline CSS custom yang **menimpa** styling bawaan Sneat untuk memperbaiki masalah responsive dan dark mode.

### Isi styles.html (642 baris):

```
styles.html
├── Baris 1–36     → Vendor CSS links (Bootstrap, Sneat core, dll)
├── Baris 37       → <style> tag pembuka
├── Baris 38–81    → Fix: Pagination scrollbar horizontal (≤ 991px)
├── Baris 83–122   → Fix: Export buttons responsive (≤ 991px + ≤ 575px)
├── Baris 124–388  → Fix: Global mobile margin/padding (≤ 576px)
│                    → Container, card, form, tabel, badge, pagination, dll
├── Baris 390–427  → Fix: Tablet responsive (577–767px)
├── Baris 429–642  → Fix: Dark mode teks kontras (selector [data-theme="dark"])
│                    → Sidebar menu, card, tabel, form, modal, dropdown, dll
└── Baris 642      → </style> tag penutup
```

### Kenapa styles.html dan Bukan File CSS Terpisah?

```
1. Inline <style> = TIDAK perlu collectstatic
   → Langsung bekerja di development dan production
   → Tidak ada masalah 404 static file

2. Ditaruh di partials → di-include SEKALI di master.html
   → Otomatis berlaku di SEMUA halaman (75+ templates)
   → Tidak perlu import manual per halaman

3. Menggunakan !important → MENIMPA styling bawaan Sneat
   → Sneat core.css memiliki specificity tinggi
   → !important diperlukan untuk override
```

### Cara Menambah CSS Baru:

Buka `templates/layout/partials/styles.html`, dan tambahkan CSS baru **di dalam** tag `<style>` yang sudah ada:

```css
/* Tambahkan sebelum </style> penutup */

/* Contoh: custom style untuk komponen baru */
@media (max-width: 576px) {
  .my-custom-component {
    font-size: 0.875rem !important;
    padding: 0.5rem !important;
  }
}
```

> **Panduan lengkap CSS responsive dan dark mode ada di:**
> [10_KOMPONEN_UI_SNEAT.md — Bagian O & O.2](10_KOMPONEN_UI_SNEAT.md)

---

## F. TemplateLayout — Engine Inti Layout

### Apa itu TemplateLayout?

`TemplateLayout` adalah class di `web_project/__init__.py` yang **WAJIB** dipanggil di setiap view. Class ini menginisialisasi context template dengan data layout, tema, dan konfigurasi.

### Mengapa WAJIB?

```
TANPA TemplateLayout.init():
  ❌ Sidebar tidak punya data menu → kosong
  ❌ Navbar tidak punya data user → error
  ❌ Template tidak tahu layout mana → error extends
  ❌ Dark mode / RTL mode tidak berfungsi

DENGAN TemplateLayout.init():
  ✅ Semua layout data tersedia
  ✅ Konsisten di 75+ halaman
```

### Cara Kerja (Step by Step):

```python
# Di setiap View, WAJIB panggil TemplateLayout.init():

class ProdukListView(ListView):
    model = Produk
    template_name = 'produk/produk_list.html'

    def get_context_data(self, **kwargs):
        # Step 1: Ambil context default dari Django (queryset, pagination, dll)
        context = super().get_context_data(**kwargs)

        # Step 2: Perkaya context dengan data layout
        context = TemplateLayout.init(self, context)
        # ↑ Setelah ini, context berisi:
        #   - layout_path: 'layout/master.html' (untuk {% extends %})
        #   - layout: 'vertical' (tipe layout)
        #   - rtl_mode: False (arah teks)
        #   - hasCustomizer: True (panel pengaturan tema)
        #   - + semua variabel dari TEMPLATE_CONFIG

        return context
```

### Alur Internal TemplateLayout.init():

```
TemplateLayout.init(self, context)
    │
    ├── 1. TemplateHelper.init_context(context)
    │       → Baca TEMPLATE_CONFIG dari settings.py
    │       → Set context['layout'] = 'vertical'
    │       → Set context['hasCustomizer'] = True
    │       → Set context['menuFixed'] = True
    │       → Set context['navbarFull'] = False
    │
    ├── 2. Ambil layout = context['layout']  # 'vertical'
    │
    ├── 3. TemplateHelper.set_layout('layout_vertical.html', context)
    │       → return 'layout/layout_vertical.html'
    │       → Disimpan di context['layout_path']
    │
    ├── 4. Cek cookie 'django_text_direction'
    │       → Jika cookie = 'rtl': context['rtl_mode'] = True
    │       → Jika tidak: gunakan default dari TEMPLATE_CONFIG
    │
    └── 5. TemplateHelper.map_context(context)
            → Petakan variabel → CSS class
            → Contoh: menuFixed=True → 'layout-menu-fixed'
```

### Layout yang Tersedia:

| Layout | File Template | Dipakai Untuk |
|--------|--------------|---------------|
| `vertical` | `layout_vertical.html` | Semua halaman utama ERP (95% halaman) |
| `horizontal` | `layout_horizontal.html` | Alternatif layout (menu atas) |
| `without_menu` | `layout_without_menu.html` | Halaman login, register |
| `blank` | `layout_blank.html` | Halaman error (404, 500) |

---

## G. Semua Block Template yang Tersedia

### Block = "Lubang" yang Bisa Diisi

Setiap template anak bisa mengisi block-block ini:

```html
<!-- ═══ Di master.html ═══ -->

{% block title %}ERP{% endblock %}
<!-- Judul di tab browser. Default: "ERP" -->

{% block vendor_css %}{% endblock %}
<!-- CSS vendor tambahan: DataTables, Select2, Flatpickr, dll -->
<!-- Hanya diload di halaman yang butuh (hemat bandwidth) -->

{% block page_css %}{% endblock %}
<!-- CSS custom per halaman -->

{% block layout_content %}{% endblock %}
<!-- Konten utama (diisi oleh layout_vertical.html) -->

{% block vendor_js %}{% endblock %}
<!-- JS vendor tambahan: DataTables, ApexCharts, dll -->

{% block page_js %}{% endblock %}
<!-- JS custom per halaman -->
```

```html
<!-- ═══ Di layout_vertical.html ═══ -->

{% block content %}{% endblock %}
<!-- Konten spesifik halaman (diisi oleh produk_list.html, dll) -->
```

### `{{ block.super }}` — JANGAN Timpa, TAMBAHKAN:

```html
{% block vendor_css %}
{{ block.super }}
<!-- ↑ SIMPAN CSS dari parent, lalu TAMBAH yang baru -->
<!-- Tanpa block.super: CSS parent HILANG → styling rusak! -->
<link rel="stylesheet" href="{% static 'vendor/libs/datatables/datatables.css' %}">
{% endblock %}
```

### Diagram Semua Block:

```
┌─── master.html ───────────────────────────────────────────┐
│ <head>                                                     │
│   {% block title %}                                        │
│   {% block vendor_css %}                                   │
│   {% block page_css %}                                     │
│ </head>                                                    │
│ <body>                                                     │
│   {% block layout_content %}                               │
│   ┌─── layout_vertical.html ──────────────────────────┐   │
│   │ Sidebar (include vertical_menu.html)                │   │
│   │ Navbar  (include navbar.html)                       │   │
│   │ ┌─── {% block content %} ──────────────────────┐   │   │
│   │ │                                               │   │   │
│   │ │  produk_list.html / produk_form.html / ...   │   │   │
│   │ │  (HALAMAN SPESIFIK — yang kita tulis)        │   │   │
│   │ │                                               │   │   │
│   │ └──────────────────────────────────────────────┘   │   │
│   │ Footer (include footer.html)                        │   │
│   └────────────────────────────────────────────────────┘   │
│   {% block vendor_js %}                                    │
│   {% block page_js %}                                      │
│ </body>                                                    │
└────────────────────────────────────────────────────────────┘
```

---

## H. Pola Template CRUD — Standar Project

### 1. Template List (Daftar):

```html
<!-- Pattern: {model}_list.html -->
{% extends 'layout/layout_vertical.html' %}
{% load static %}
{% load currency_filters %}

{% block title %}Daftar {Model}{% endblock %}

{% block vendor_css %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'vendor/libs/datatables-bs5/datatables.bootstrap5.css' %}">
{% endblock %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Daftar {Model}</h5>
            {% if can_create.{app} %}
            <a href="{% url '{app}:tambah' %}" class="btn btn-primary btn-sm">
                <i class="ri-add-line me-1"></i>Tambah
            </a>
            {% endif %}
        </div>
        <div class="card-body">
            <table class="table table-hover" id="{model}Table">
                <thead>
                    <tr>
                        <th>No</th>
                        <th>Nama</th>
                        <!-- ... kolom lain ... -->
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in object_list %}
                    <tr id="row-{{ item.pk }}">
                        <td>{{ forloop.counter }}</td>
                        <td>{{ item.nama }}</td>
                        <td>
                            {% if can_edit.{app} %}
                            <a href="{% url '{app}:edit' pk=item.pk %}" 
                               class="btn btn-sm btn-icon btn-text-secondary">
                                <i class="ri-pencil-line"></i>
                            </a>
                            {% endif %}
                            {% if can_delete.{app} %}
                            <button class="btn btn-sm btn-icon btn-text-danger"
                                    onclick="hapus({{ item.pk }}, '{{ item.nama }}')">
                                <i class="ri-delete-bin-line"></i>
                            </button>
                            {% endif %}
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="3" class="text-center py-4">Belum ada data</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal Hapus -->
{% include 'partials/_delete_modal.html' %}
{% endblock %}

{% block vendor_js %}
{{ block.super }}
<script src="{% static 'vendor/libs/datatables-bs5/datatables-bootstrap5.js' %}"></script>
{% endblock %}

{% block page_js %}
<script>
$('#{model}Table').DataTable({
    responsive: false,
    pageLength: 25,
    language: {
        sEmptyTable: "Tidak ada data",
        sSearch: "Cari:",
        sInfo: "Menampilkan _START_ s/d _END_ dari _TOTAL_ data"
    }
});
</script>
{% endblock %}
```

### 2. Template Form (Tambah/Edit):

```html
<!-- Pattern: {model}_form.html — SATU template untuk tambah DAN edit -->
{% extends 'layout/layout_vertical.html' %}

{% block title %}
    {% if object %}Edit{% else %}Tambah{% endif %} {Model}
{% endblock %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <div class="card">
        <div class="card-header">
            <h5>{% if object %}Edit{% else %}Tambah{% endif %} {Model}</h5>
        </div>
        <div class="card-body">
            <form method="POST" enctype="multipart/form-data">
                {% csrf_token %}
                <!-- enctype → WAJIB jika form ada upload file/gambar -->

                {% for field in form %}
                <div class="mb-3">
                    <label class="form-label">{{ field.label }}</label>
                    {{ field }}
                    {% if field.errors %}
                    <div class="text-danger mt-1">{{ field.errors.0 }}</div>
                    {% endif %}
                </div>
                {% endfor %}

                <div class="mt-4">
                    <button type="submit" class="btn btn-primary">Simpan</button>
                    <a href="{% url '{app}:list' %}" class="btn btn-label-secondary">Batal</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

### 3. Template Detail (View):

```html
<!-- Pattern: {model}_detail.html -->
{% extends 'layout/layout_vertical.html' %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <div class="card">
        <div class="card-header d-flex justify-content-between">
            <h5>Detail {Model}</h5>
            <a href="{% url '{app}:list' %}" class="btn btn-label-secondary btn-sm">
                <i class="ri-arrow-left-line me-1"></i>Kembali
            </a>
        </div>
        <div class="card-body">
            <table class="table table-bordered">
                <tr>
                    <th width="200">Nama</th>
                    <td>{{ object.nama }}</td>
                </tr>
                <!-- ... field lain ... -->
            </table>
        </div>
    </div>
</div>
{% endblock %}
```

---

## I. Kesalahan Umum Template & Best Practice

### 1. Lupa `{% csrf_token %}`

```html
<!-- ❌ SALAH — form POST tanpa CSRF token -->
<form method="POST">
    <input name="nama" value="Beras">
    <button type="submit">Simpan</button>
</form>
<!-- HASIL: Django return 403 Forbidden! -->

<!-- ✅ BENAR — selalu pakai {% csrf_token %} -->
<form method="POST">
    {% csrf_token %}
    <input name="nama" value="Beras">
    <button type="submit">Simpan</button>
</form>
```

### 2. Lupa `{{ block.super }}`

```html
<!-- ❌ SALAH — CSS parent HILANG -->
{% block vendor_css %}
<link rel="stylesheet" href="{% static 'vendor/libs/datatables.css' %}">
{% endblock %}
<!-- CSS Bootstrap/Sneat dari parent tidak dimuat! -->

<!-- ✅ BENAR — SIMPAN CSS parent -->
{% block vendor_css %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'vendor/libs/datatables.css' %}">
{% endblock %}
```

### 3. Lupa `{% load %}` Template Tags

```html
<!-- ❌ SALAH — pakai |rupiah tanpa load -->
{{ produk.harga_jual|rupiah }}
<!-- HASIL: error TemplateSyntaxError! -->

<!-- ✅ BENAR — load dulu di awal file -->
{% load currency_filters %}
{{ produk.harga_jual|rupiah }}
```

### 4. Path `{% extends %}` Salah

```html
<!-- ❌ SALAH — path relatif atau typo -->
{% extends 'layout_vertical.html' %}
{% extends '../layout/layout_vertical.html' %}
<!-- HASIL: TemplateDoesNotExist error! -->

<!-- ✅ BENAR — path dari folder templates/ -->
{% extends 'layout/layout_vertical.html' %}
<!-- Django cari: templates/layout/layout_vertical.html -->
```

### 5. Lupa `TemplateLayout.init()` di View

```python
# ❌ SALAH — tanpa init()
class ProdukListView(ListView):
    model = Produk
    template_name = 'produk/produk_list.html'
    # Sidebar kosong! Navbar error!

# ✅ BENAR — selalu init()
class ProdukListView(ListView):
    model = Produk
    template_name = 'produk/produk_list.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
```

### 6. Akses Atribut None Object

```html
<!-- ❌ MASALAH — jika produk.kategori = None -->
{{ produk.kategori.nama }}
<!-- Output: "" (kosong, bukan error — Django handle None secara silent) -->
<!-- Tapi UI terlihat kosong tanpa penjelasan -->

<!-- ✅ LEBIH BAIK — pakai |default -->
{{ produk.kategori.nama|default:"-" }}
<!-- Output: "-" jika kategori None -->
```

### Best Practice Ringkasan:

| No | Rule | Alasan |
|----|------|--------|
| 1 | Selalu `{% csrf_token %}` di form POST | Keamanan CSRF |
| 2 | Selalu `{{ block.super }}` saat override block | Jangan hilangkan CSS/JS parent |
| 3 | Selalu `{% load %}` sebelum pakai custom tags | Template error tanpa load |
| 4 | Selalu `TemplateLayout.init()` di view | Layout tidak berfungsi tanpa init |
| 5 | Gunakan `|default:"-"` untuk field nullable | UI tidak kosong tanpa penjelasan |
| 6 | Satu template form untuk tambah DAN edit | `{% if object %}` membedakan mode |
| 7 | Pakai `{% empty %}` di setiap `{% for %}` | Pesan jika data kosong |
| 8 | Gunakan `id` unik di elemen interaktif | DataTables, modal, AJAX butuh ID |

---

*Lanjut ke [06_FORM_DAN_VALIDASI.md](06_FORM_DAN_VALIDASI.md) →*
