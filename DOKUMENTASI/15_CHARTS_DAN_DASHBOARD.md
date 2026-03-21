# 📊 15 — Charts, Dashboard & Data Visualization — Panduan Lengkap

## DAFTAR ISI
- [A. Arsitektur Dashboard](#a-arsitektur-dashboard)
- [B. ApexCharts — Library Grafik](#b-apexcharts)
- [C. Area Chart (Tren Penjualan)](#c-area-chart-tren-penjualan)
- [D. Bar Chart (Perbandingan)](#d-bar-chart-perbandingan)
- [E. Radial Bar (Progress Lingkaran)](#e-radial-bar-progress-lingkaran)
- [F. Swiper Carousel (Slider)](#f-swiper-carousel-slider)
- [G. Dashboard View — Data dari 7 Modul](#g-dashboard-view)
- [H. Alur Data Lengkap: Database → Chart](#h-alur-data-lengkap)
- [I. Membuat Chart Baru](#i-membuat-chart-baru)
- [J. Responsive & Dark Mode Charts](#j-responsive--dark-mode)

---

## A. Arsitektur Dashboard

Dashboard ERP kita menampilkan data dari **7 modul berbeda** dalam 1 halaman:

> **UPDATE Maret 2026:** Layout dashboard telah disederhanakan. Beberapa section dihapus:
> Total Pembelian, Total Biaya, Slider Metode Pembayaran, Keuntungan per Cabang,
> dan Biaya per Kategori. Grafik Penjualan per Cabang diganti dari bar chart menjadi
> wave/area chart yang modern. Filter waktu dipindah ke icon di navbar.
>
> **UPDATE Maret 2026 (v2):** Grafik Penjualan per Cabang sekarang menggunakan
> **Smart Aggregation** — otomatis agregasi per HARI untuk filter pendek (≤62 hari)
> dan per BULAN untuk filter panjang/default. Filter waktu juga diterapkan ke semua
> query statistik cabang (revenue, profit, pembelian). Default values ditambahkan
> untuk mencegah crash jika terjadi error.

```
Dashboard = Data dari SELURUH bisnis di 1 layar:

┌─────────────────────────────────────────────────────────┐
│ NAVBAR: [Menu] [...search...] [🌙 Dark] [📅 Filter] [👤]│
│         Filter waktu → icon kalender di navbar          │
│         Hanya muncul di halaman Dashboard               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌── Row 1: Ringkasan Angka ─────────────────────────┐ │
│  │ [Total Aset] [Harga Beli] [Harga Jual] [Estimasi] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 2: Chart Penjualan ─────────────────────────┐ │
│  │ ┌─ col-12 ───────────────────────────────────────┐ │ │
│  │ │ Area Chart: Penjualan Bulan Ini                 │ │ │
│  │ │ [smooth line + gradient fill]                   │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 3: Chart Penjualan per Cabang ──────────────┐ │
│  │ Wave/Area Chart: Revenue per cabang/gudang         │ │
│  │ [smooth curve, gradient, tooltip Rp format]        │ │
│  │ SMART AGGREGATION:                                 │ │
│  │   Filter ≤62 hari → per HARI (01 Mar, 02 Mar..)   │ │
│  │   Filter >62 hari / default → per BULAN            │ │
│  │ Difilter oleh filter waktu di navbar               │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 4: Tabel ──────────────────────────────────┐  │
│  │ [Produk Terlaris — Top 10]                        │  │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌── Row 5: Pengguna Terbaru (100% lebar) ──────────┐  │
│  │ Avatar (1 inisial) | Nama | Role | Tgl Bergabung  │  │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

Section yang DIHAPUS (sebelumnya ada di Row 2-4):
  ✗ Total Pembelian (radial bar)
  ✗ Total Biaya (radial bar)
  ✗ Slider Metode Pembayaran (Swiper carousel)
  ✗ Keuntungan per Cabang (bar chart) → DIGANTI wave chart
  ✗ Biaya per Kategori (bar chart)

Sumber Data:
├── apps/penjualan/models.py   → Sales Order, revenue, growth
├── apps/pembelian/models.py   → Purchase Order
├── apps/produk/models.py      → Stok, aset, produk terlaris
├── apps/biaya/models.py       → Biaya operasional
├── apps/inventory/models.py   → Gudang, cabang
├── apps/pos/models.py         → POS transaction
└── auth_user                  → Pengguna terbaru (1 inisial)
```

### File-File yang Terlibat:

```
apps/dashboard/views.py        → DashboardView (~1280 baris)
                                  Mengumpulkan data dari 7 modul
                                  Query aggregate, annotate, filter
                                  Smart aggregation harian/bulanan

templates/dashboard/index.html  → Template (~1400 baris)
                                  HTML layout + CSS + JavaScript
                                  ApexCharts rendering
                                  Swiper carousel

static/vendor/libs/apex-charts/ → Library ApexCharts
static/vendor/libs/swiper/     → Library Swiper
static/vendor/css/pages/       → CSS cards dashboard
static/js/config.js            → Konfigurasi warna tema
```

---

## B. ApexCharts — Library Grafik

### Apa itu ApexCharts?

```
ApexCharts = Library JavaScript open-source untuk membuat grafik interaktif.
→ Support: Line, Area, Bar, Pie, Donut, Radial, Heatmap, dll
→ Responsive (otomatis resize)
→ Animasi smooth
→ Dark mode support
→ Website: https://apexcharts.com/

BUKAN Chart.js!
Di project ini kita pakai ApexCharts (bukan Chart.js).
```

### Cara Include di Template:

```html
{# Vendor CSS (di head) #}
{% block vendor_css %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'vendor/libs/apex-charts/apex-charts.css' %}" />
{% endblock %}

{# Vendor JS (di bawah body) #}
{% block vendor_js %}
{{ block.super }}
<script src="{% static 'vendor/libs/apex-charts/apexcharts.js' %}"></script>
{% endblock %}
```

### Pola Dasar ApexCharts:

```javascript
// ═══ 3 LANGKAH membuat chart ═══

// 1. Siapkan elemen HTML di template:
//    <div id="myChart"></div>

// 2. Buat konfigurasi:
const config = {
    chart: {
        type: 'bar',          // Tipe chart
        height: 300,          // Tinggi pixel
    },
    series: [{
        name: 'Penjualan',    // Label series
        data: [30, 40, 35, 50, 49, 60]  // Data angka
    }],
    xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun']
    }
};

// 3. Render:
const chart = new ApexCharts(document.querySelector('#myChart'), config);
chart.render();
```

---

## C. Area Chart (Tren Penjualan)

Area chart = garis + area berwarna di bawahnya. Cocok untuk **tren waktu**.

```javascript
// ═══ Seperti yang dipakai di dashboard ═══

const config = {
    chart: {
        type: 'area',           // Tipe: area chart
        height: 120,            // Tinggi compact
        sparkline: {
            enabled: true       // Mode sparkline: tanpa axis, minimal
        },
        toolbar: { show: false }  // Sembunyikan toolbar (zoom, export, dll)
    },
    
    series: [{
        name: 'Penjualan',
        data: [150000, 200000, 180000, 250000, 220000]
        // ↑ Data dari Python (via json_script)
    }],
    
    // Garis:
    stroke: {
        width: 2,               // Ketebalan garis: 2px
        curve: 'smooth'         // Garis halus (bukan patah-patah)
    },
    
    // Isi area di bawah garis:
    fill: {
        type: 'gradient',       // Gradient dari atas (terang) ke bawah (transparan)
        gradient: {
            shadeIntensity: 0.4,
            opacityFrom: 0.8,   // Opacity atas: 80%
            opacityTo: 0.1,     // Opacity bawah: 10%
        }
    },
    
    // Warna:
    colors: ['#696CFF'],        // Warna primary Sneat (ungu)
    
    // Tooltip (popup saat hover):
    tooltip: {
        enabled: true,
        x: {
            formatter: function(val, opts) {
                return 'Tgl ' + labels[opts.dataPointIndex];
            }
        },
        y: {
            formatter: function(val) {
                return 'Rp ' + val.toLocaleString('id-ID');
                // 250000 → "Rp 250.000"
            }
        }
    },
    
    // Sumbu X:
    xaxis: {
        categories: ['1', '2', '3', '4', '5'],
        labels: { show: false }   // Sembunyikan label X (sparkline)
    },
    
    // Sumbu Y:
    yaxis: {
        min: 0,                   // Mulai dari 0
        labels: { show: false }   // Sembunyikan label Y
    }
};

const chartEl = document.querySelector('#saleThisMonthChart');
if (chartEl) {
    new ApexCharts(chartEl, config).render();
}
```

---

## D. Bar Chart (Perbandingan)

Bar chart = batang vertikal atau horizontal. Cocok untuk **membandingkan** kategori.

### Bar Chart Standar (Keuntungan per Cabang):

```javascript
const config = {
    chart: {
        type: 'bar',
        height: 153,
        toolbar: { show: false }
    },
    
    series: [{
        name: 'Profit',
        data: [50000, 80000, 60000, 90000, 70000]
    }],
    
    plotOptions: {
        bar: {
            borderRadius: 8,        // Ujung bar membulat
            columnWidth: '43%',     // Lebar bar 43% dari kolom
        }
    },
    
    colors: ['#71DD37'],            // Warna hijau (success)
    
    xaxis: {
        categories: ['Cab 1', 'Cab 2', 'Cab 3', 'Cab 4', 'Cab 5'],
        labels: {
            style: {
                colors: '#697a8d',  // Warna label teks
                fontSize: '11px',
            }
        }
    },
    
    yaxis: { labels: { show: false } },  // Sembunyikan sumbu Y
    dataLabels: { enabled: false },       // Jangan tampilkan angka di bar
    legend: { show: false },              // Sembunyikan legenda
};
```

### Bar Chart Distributed (Setiap Bar Beda Warna):

```javascript
const config = {
    chart: { type: 'bar', height: 314 },
    
    plotOptions: {
        bar: {
            distributed: true,     // ← KUNCI: setiap bar warna BERBEDA
            borderRadius: 8,
            columnWidth: '55%',
        }
    },
    
    series: [{
        name: 'Biaya',
        data: [30000, 50000, 20000, 45000, 15000]
    }],
    
    // Warna untuk SETIAP bar:
    colors: ['#E8E8FF', '#696CFF', '#E8E8FF', '#696CFF', '#E8E8FF'],
    // Bar 1: ungu muda, Bar 2: ungu tua, dst (bergantian)
    
    xaxis: {
        categories: ['Gaji', 'Sewa', 'Utilitas', 'Marketing', 'Lainnya'],
    }
};
```

---

## E. Radial Bar (Progress Lingkaran)

Radial bar = lingkaran progress. Cocok untuk **persentase**.

```javascript
const config = {
    chart: {
        type: 'radialBar',
        height: 90,
        width: 90,
        sparkline: { enabled: true }
    },
    
    series: [75],               // 75% progress
    
    plotOptions: {
        radialBar: {
            hollow: {
                size: '52%',    // Lubang tengah 52% dari diameter
                image: '/static/img/icons/order.png',  // Ikon di tengah
                imageWidth: 24,
                imageHeight: 24,
            },
            track: {
                background: '#E8E8FF',  // Warna track belakang
                strokeWidth: '100%'     // Lebar track
            },
            dataLabels: { show: false } // Sembunyikan angka persentase
        }
    },
    
    stroke: { lineCap: 'round' },  // Ujung progress membulat
    colors: ['#696CFF'],            // Warna progress
};
```

### Dynamic Radial Bars (Factory Function):

```javascript
// Di dashboard, kita pakai factory function untuk membuat radial bar yang dynamic:

function createRadialBar(color, value, icon) {
    return {
        chart: { type: 'radialBar', height: 90, width: 90, sparkline: { enabled: true } },
        series: [value],
        colors: [color],
        plotOptions: {
            radialBar: {
                hollow: { size: '52%', image: icon, imageWidth: 24, imageHeight: 24 },
                track: { background: '#E8E8FF' },
                dataLabels: { show: false }
            }
        }
    };
}

// Render semua radial bar dari HTML data attributes:
document.querySelectorAll('.chart-progress').forEach(el => {
    const config = createRadialBar(
        el.dataset.color,     // Dari: data-color="#696CFF"
        el.dataset.series,    // Dari: data-series="75"
        el.dataset.icon       // Dari: data-icon="/img/order.png"
    );
    new ApexCharts(el, config).render();
});
```

---

## F. Swiper Carousel (Slider)

Swiper = library slider/carousel responsif.

```html
{# ═══ HTML SLIDER ═══ #}
<div class="swiper" id="swiper-weekly-sales">
    <div class="swiper-wrapper">
        {# Setiap slide dibungkus swiper-slide: #}
        {% for item in weekly_sales %}
        <div class="swiper-slide">
            <div class="card bg-primary text-white p-3">
                <h6>{{ item.kategori }}</h6>
                <h3>{{ item.total|rupiah }}</h3>
                <span>{{ item.qty }} item terjual</span>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="swiper-pagination"></div>
</div>
```

```javascript
// ═══ INISIALISASI SWIPER ═══
new Swiper('#swiper-weekly-sales', {
    loop: true,               // Putar terus (slide terakhir → pertama)
    autoplay: {
        delay: 2500,           // Geser otomatis per 2.5 detik
        disableOnInteraction: false,  // Tetap autoplay setelah user interact
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,       // Dot pagination bisa diklik
    },
    slidesPerView: 1,          // 1 slide terlihat
    spaceBetween: 16,          // Jarak antar slide: 16px
    breakpoints: {
        768: { slidesPerView: 2 },  // Tablet: 2 slide
        1200: { slidesPerView: 3 }, // Desktop: 3 slide
    }
});
```

---

## G. Dashboard View — Data dari 7 Modul

### Ringkasan `DashboardView` (~1280 baris):

```python
# apps/dashboard/views.py

class DashboardView(TemplateView):
    """
    View TERBESAR di project: ~1280 baris!
    Mengumpulkan data dari SELURUH modul.
    Fitur: Smart Aggregation (harian/bulanan), filter waktu, default values.
    """
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # ─── DATA PRODUK ───
        # Query: Hitung total aset = SUM(harga_beli × stok)
        produk = Produk.objects.aggregate(
            total_aset=Sum(F('harga_beli') * F('stok')),
            total_harga_beli=Sum('harga_beli'),
            total_harga_jual=Sum('harga_jual'),
        )
        context['total_aset'] = produk['total_aset'] or 0
        
        # ─── DATA PENJUALAN ───
        # Filter: bulan ini
        bulan_ini = SalesOrder.objects.filter(
            tanggal__year=today.year,
            tanggal__month=today.month,
        )
        context['total_penjualan'] = bulan_ini.aggregate(Sum('grand_total'))
        
        # Chart data: penjualan per hari
        sales_per_day = bulan_ini.values('tanggal__day').annotate(
            total=Sum('grand_total')
        ).order_by('tanggal__day')
        context['sales_chart_data'] = [float(s['total']) for s in sales_per_day]
        context['sales_chart_labels'] = [str(s['tanggal__day']) for s in sales_per_day]
        
        # ─── DATA KEUNTUNGAN PER CABANG ───
        cabang = Gudang.objects.all()
        profit_data = []
        for g in cabang:
            revenue = SalesOrder.objects.filter(gudang=g).aggregate(Sum('grand_total'))
            cost = PurchaseOrder.objects.filter(gudang=g).aggregate(Sum('grand_total'))
            profit = (revenue['grand_total__sum'] or 0) - (cost['grand_total__sum'] or 0)
            profit_data.append(float(profit))
        context['live_visitors_data'] = profit_data
        context['cabang_names'] = [g.nama for g in cabang]
        
        # ─── DATA BIAYA PER KATEGORI ───
        biaya_qs = Biaya.objects.values('kategori__nama').annotate(total=Sum('jumlah'))
        context['visits_by_day_data'] = [float(b['total']) for b in biaya_qs]
        context['biaya_labels'] = [b['kategori__nama'][:6] for b in biaya_qs]
        
        # ─── PRODUK TERLARIS ─── (top 10)
        context['produk_terlaris'] = SalesOrderItem.objects.values(
            'produk__nama'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:10]
        
        # ─── PENGGUNA TERBARU ───
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        
        return context
```

### Smart Aggregation — Grafik Penjualan per Cabang:

Grafik "Penjualan per Cabang" menggunakan **Smart Aggregation** yang otomatis
memilih mode agregasi berdasarkan rentang filter waktu:

```
┌──────────────────────────────────────────────────────────┐
│           SMART AGGREGATION LOGIC                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  rentang_hari = (filter_end - filter_start).days + 1     │
│                                                          │
│  if rentang_hari <= 62:                                  │
│      → MODE HARIAN                                       │
│      → Label: "01 Mar", "02 Mar", "03 Mar"...            │
│      → Query: tanggal__date=hari per gudang              │
│      → Hasil: chart bergelombang informatif              │
│                                                          │
│  else:                                                   │
│      → MODE BULANAN                                      │
│      → Label: "Oct 2025", "Nov 2025"...                  │
│      → Query: tanggal__year + tanggal__month per gudang  │
│      → Hasil: chart tren jangka panjang                  │
│                                                          │
│  Default (tanpa filter): BULANAN (6 bulan terakhir)      │
└──────────────────────────────────────────────────────────┘
```

**Kenapa Smart Aggregation?**
Sebelumnya, chart selalu menggunakan agregasi per-**bulan**. Jika filter
hanya mencakup 1 bulan (misal: 1 – 9 Maret), chart hanya menampilkan
**1 titik** (dot) per cabang — terlihat kosong. Dengan Smart Aggregation,
chart otomatis beralih ke per-hari sehingga menampilkan garis
bergelombang yang informatif.

```python
# Contoh kode Smart Aggregation (dashboard/views.py):

# Hitung rentang hari
if filter_start and filter_end:
    rentang_hari = (filter_end - filter_start).days + 1
else:
    rentang_hari = 180  # Default → bulanan

use_daily = rentang_hari <= 62

if use_daily:
    # MODE HARIAN: query per tanggal
    for hari in hari_list:
        so_rev = SalesOrder.objects.filter(
            gudang=gudang, tanggal__date=hari, ...
        ).aggregate(total=Sum('total_harga'))['total'] or 0
else:
    # MODE BULANAN: query per bulan
    for bulan in bulan_list:
        so_rev = SalesOrder.objects.filter(
            gudang=gudang, tanggal__year=bulan['year'], ...
        ).aggregate(total=Sum('total_harga'))['total'] or 0
```

### Default Values — Mencegah Chart Crash:

```python
# Di views.py, default values diinisialisasi SEBELUM try block:
context['sales_cabang_labels'] = []  # Label sumbu X chart
context['sales_cabang_series'] = []  # Data series per cabang
context['cabang_profit_data'] = []   # Data profit per cabang

# Ditambahkan juga di KEDUA except handler:
# - Inner except (ERP cards error)
# - Outer except (fatal dashboard error)
# Sehingga chart selalu ter-render meskipun terjadi error.
```

---

## H. Alur Data Lengkap: Database → Chart

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   DATABASE   │     │    PYTHON    │     │  JAVASCRIPT  │
│   (SQLite)   │ ──→ │  (View.py)   │ ──→ │ (ApexCharts) │
└──────────────┘     └──────────────┘     └──────────────┘

Langkah 1: DATABASE → PYTHON
─────────────────────────────
# Django ORM query
sales = SalesOrder.objects.filter(
    tanggal__month=2
).values('tanggal__day').annotate(
    total=Sum('grand_total')
)

# SQL yang dijalankan:
# SELECT tanggal AS day, SUM(grand_total) AS total
# FROM penjualan_salesorder
# WHERE MONTH(tanggal) = 2
# GROUP BY tanggal

# Hasil: [{'tanggal__day': 1, 'total': 150000}, ...]

Langkah 2: PYTHON → CONTEXT
─────────────────────────────
chart_data = [float(s['total']) for s in sales]  
# [150000.0, 200000.0, 180000.0]

chart_labels = [str(s['tanggal__day']) for s in sales]  
# ['1', '2', '3']

context['sales_chart_data'] = chart_data
context['sales_chart_labels'] = chart_labels

Langkah 3: CONTEXT → HTML (json_script)
────────────────────────────────────────
{{ sales_chart_data|json_script:"sales-data" }}
# Output: <script id="sales-data">[150000.0, 200000.0, 180000.0]</script>

Langkah 4: HTML → JAVASCRIPT (JSON.parse)
──────────────────────────────────────────
const data = JSON.parse(document.getElementById('sales-data').textContent);
// data = [150000, 200000, 180000]

Langkah 5: JAVASCRIPT → CHART (ApexCharts)
────────────────────────────────────────────
new ApexCharts(element, {
    series: [{ data: data }],
    // ...
}).render();
// → CHART MUNCUL DI LAYAR! 🎉
```

---

## I. Membuat Chart Baru

### Langkah Step-by-Step:

```python
# ═══ LANGKAH 1: Tambah data di views.py ═══

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Contoh: chart produk per kategori
    produk_per_kat = Produk.objects.values('kategori__nama').annotate(
        jumlah=Count('id')
    ).order_by('-jumlah')
    
    context['produk_per_kategori'] = [p['jumlah'] for p in produk_per_kat]
    context['kategori_names'] = [p['kategori__nama'] for p in produk_per_kat]
    return context
```

```html
{# ═══ LANGKAH 2: Inject data ke template ═══ #}
{{ produk_per_kategori|json_script:"produk-kat-data" }}
{{ kategori_names|json_script:"produk-kat-labels" }}

{# ═══ LANGKAH 3: Buat elemen HTML ═══ #}
<div class="card">
    <div class="card-header"><h5>Produk per Kategori</h5></div>
    <div class="card-body">
        <div id="produkPerKategoriChart"></div>
    </div>
</div>
```

```javascript
// ═══ LANGKAH 4: Render chart ═══
const data = JSON.parse(document.getElementById('produk-kat-data').textContent);
const labels = JSON.parse(document.getElementById('produk-kat-labels').textContent);

const chartEl = document.querySelector('#produkPerKategoriChart');
if (chartEl) {
    new ApexCharts(chartEl, {
        chart: { type: 'bar', height: 300, toolbar: { show: false } },
        series: [{ name: 'Produk', data: data }],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '50%' } },
        colors: ['#696CFF'],
        xaxis: { categories: labels },
        dataLabels: { enabled: false },
    }).render();
}
```

---

## J. Responsive & Dark Mode Charts

### Responsive (Otomatis Resize):

```javascript
{
    chart: { type: 'bar', height: 300 },
    
    responsive: [
        {
            breakpoint: 992,     // Di bawah 992px (tablet):
            options: {
                chart: { height: 250 },
                plotOptions: { bar: { columnWidth: '55%' } }
            }
        },
        {
            breakpoint: 576,     // Di bawah 576px (HP):
            options: {
                chart: { height: 200 },
                plotOptions: { bar: { columnWidth: '70%' } }
            }
        }
    ]
}
```

### Dark Mode (Otomatis Ikut Tema):

```javascript
// Sneat menyediakan variabel global isDarkStyle:
let labelColor, borderColor;

if (isDarkStyle) {
    // Config dari static/js/config.js:
    labelColor = config.colors_dark.textMuted;    // '#7C7C9A'
    borderColor = config.colors_dark.borderColor;  // '#444564'
} else {
    labelColor = config.colors.textMuted;          // '#a8aab4'
    borderColor = config.colors.borderColor;       // '#e6e5e8'
}

// Pakai di chart config:
{
    xaxis: {
        labels: { style: { colors: labelColor } }
    },
    grid: {
        borderColor: borderColor
    }
}
```

---

*Selesai! Semua 16 file dokumentasi mencakup pembuatan ERP dari A-Z.*
