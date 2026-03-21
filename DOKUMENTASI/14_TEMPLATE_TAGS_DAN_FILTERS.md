# 🏷️ 14 — Template Tags & Filters — Panduan Lengkap

## DAFTAR ISI
- [A. Apa itu Template Tags & Filters?](#a-apa-itu-template-tags--filters)
- [B. Template Tags Bawaan Django](#b-template-tags-bawaan-django)
- [C. Template Filters Bawaan Django](#c-template-filters-bawaan-django)
- [D. Custom Template Tags di Project ERP](#d-custom-template-tags-di-project-erp)
- [E. Custom Template Filters di Project ERP](#e-custom-template-filters-di-project-erp)
- [F. Cara Membuat Custom Tag/Filter Sendiri](#f-cara-membuat-custom-tagfilter-sendiri)

---

## A. Apa itu Template Tags & Filters?

### Definisi:

```
Template Tags = PERINTAH / LOGIKA di dalam template HTML Django.
Template Filters = TRANSFORMASI data sebelum ditampilkan.

Analogi:
┌───────────────────────────────────────────────────┐
│ Tags ≈ MESIN / PERINTAH                          │
│   {% if kondisi %}    → "kalau condisi"           │
│   {% for x in list %} → "ulangi untuk setiap x"  │
│   {% url 'name' %}    → "buatkan URL"             │
│   {% load theme %}    → "aktifkan modul"          │
│                                                    │
│ Filters ≈ PIPA TRANSFORMASI                       │
│   {{ nama|upper }}    → "UBAH KE HURUF BESAR"    │
│   {{ harga|rupiah }}  → "FORMAT KE RUPIAH"        │
│   {{ teks|truncatewords:10 }} → "POTONG 10 KATA" │
└───────────────────────────────────────────────────┘

Sintaks:
  Tags:    {% tag_name argument %}
  Filters: {{ variabel|filter_name }}
  Filters with arg: {{ variabel|filter_name:argument }}
```

---

## B. Template Tags Bawaan Django

### Tags yang SERING Dipakai di Project:

```html
{# ═══ {% if %} — Logika Kondisional ═══ #}
{% if produk.stok > 0 %}
    <span class="badge bg-label-success">Tersedia</span>
{% elif produk.stok == 0 %}
    <span class="badge bg-label-danger">Habis</span>
{% else %}
    <span class="badge bg-label-warning">Preorder</span>
{% endif %}

{# Operator yang didukung: #}
{# ==, !=, <, >, <=, >=, and, or, not, in, not in #}

{# Contoh lanjutan: #}
{% if user.is_superuser or request.user|is_admin %}
    {# Tampilkan menu admin #}
{% endif %}

{% if "produk" in request.path %}
    {# Kita di halaman produk #}
{% endif %}


{# ═══ {% for %} — Loop ═══ #}
{% for produk in produk_list %}
    <tr>
        <td>{{ forloop.counter }}</td>     {# Index mulai dari 1 #}
        <td>{{ forloop.counter0 }}</td>    {# Index mulai dari 0 #}
        <td>{{ produk.nama }}</td>
        {% if forloop.first %}
            <td>★ Pertama</td>
        {% endif %}
        {% if forloop.last %}
            <td>★ Terakhir</td>
        {% endif %}
    </tr>
{% empty %}
    {# Ditampilkan jika list KOSONG #}
    <tr>
        <td colspan="3" class="text-center">Tidak ada data</td>
    </tr>
{% endfor %}


{# ═══ {% url %} — Generate URL dari nama ═══ #}
<a href="{% url 'produk:list' %}">Daftar Produk</a>
{# Output: <a href="/produk/list/">Daftar Produk</a> #}

<a href="{% url 'produk:edit' produk.pk %}">Edit</a>
{# Output: <a href="/produk/5/edit/">Edit</a> #}

{# Format: {% url 'namespace:name' arg1 arg2 %} #}


{# ═══ {% static %} — URL File Statis ═══ #}
{% load static %}
<link href="{% static 'vendor/css/core.css' %}" rel="stylesheet">
{# Output: <link href="/static/vendor/css/core.css" rel="stylesheet"> #}

<img src="{% static 'img/logo.png' %}" alt="Logo">


{# ═══ {% load %} — Muat Template Tags ═══ #}
{% load static %}             {# Tag {% static %} #}
{% load theme %}              {# Custom tags tema Sneat #}
{% load currency_filters %}   {# Custom filter |rupiah #}
{% load i18n %}               {# Tag internasionalisasi #}


{# ═══ {% include %} — Sertakan Template Lain ═══ #}
{% include 'partials/logo.html' %}
{# Menyisipkan isi logo.html di tempat ini #}

{% include 'partials/menu_item.html' with item=menu_item %}
{# Sisipkan + kirim variabel ke template yang di-include #}


{# ═══ {% block %} + {% extends %} — Template Inheritance ═══ #}
{% extends 'layout/layout_vertical.html' %}

{% block title %}Produk{% endblock %}

{% block content %}
    {# Isi halaman #}
{% endblock %}


{# ═══ {% csrf_token %} — Token Keamanan Form ═══ #}
<form method="POST">
    {% csrf_token %}
    {# WAJIB di setiap form POST — jika tidak ada, Django reject request #}
</form>


{# ═══ {% with %} — Variabel Sementara ═══ #}
{% with total=produk_list.count %}
    <h4>Total: {{ total }} produk</h4>
{% endwith %}
{# Variabel 'total' hanya ada di dalam {% with %}...{% endwith %} #}


{# ═══ {% comment %} — Komentar Multi-Baris ═══ #}
{% comment %}
    Kode ini tidak akan di-render oleh Django.
    Bagus untuk catatan developer.
{% endcomment %}

{# Komentar single line (tidak tampil di HTML output) #}
<!-- Ini komentar HTML biasa (TAMPIL di HTML output) -->


{# ═══ {{ value|json_script:"id" }} — Data ke JavaScript ═══ #}
{{ sales_data|json_script:"sales-data" }}
{# Output: <script id="sales-data" type="application/json">[100,200,300]</script> #}
```

---

## C. Template Filters Bawaan Django

### Filters yang Sering Dipakai:

```html
{# ═══ FORMAT TEKS ═══ #}
{{ nama|upper }}              {# "toko abc" → "TOKO ABC" #}
{{ nama|lower }}              {# "TOKO ABC" → "toko abc" #}
{{ nama|title }}              {# "toko abc" → "Toko Abc" #}
{{ nama|capfirst }}           {# "toko abc" → "Toko abc" #}
{{ deskripsi|truncatewords:10 }}  {# Potong jadi 10 kata + "..." #}
{{ deskripsi|truncatechars:50 }}  {# Potong jadi 50 karakter + "..." #}
{{ deskripsi|striptags }}     {# Hapus semua HTML tags #}
{{ deskripsi|linebreaks }}    {# Konversi \n ke <p> / <br> #}
{{ deskripsi|linebreaksbr }}  {# Konversi \n ke <br> saja #}

{# ═══ FORMAT ANGKA ═══ #}
{{ harga|floatformat:0 }}     {# 500000.00 → "500000" (tanpa desimal) #}
{{ harga|floatformat:2 }}     {# 500000 → "500000.00" (2 desimal) #}
{{ jumlah|add:5 }}            {# 10 → 15 (tambah 5) #}
{{ persen|default:"0" }}      {# None → "0" (nilai default jika kosong) #}
{{ stok|default_if_none:"0" }} {# None → "0" (hanya jika None) #}

{# ═══ FORMAT TANGGAL ═══ #}
{{ created_at|date:"d M Y" }}     {# "21 Feb 2026" #}
{{ created_at|date:"d/m/Y" }}     {# "21/02/2026" #}
{{ created_at|date:"d M Y H:i" }} {# "21 Feb 2026 22:46" #}
{{ created_at|timesince }}        {# "2 jam yang lalu" #}
{{ created_at|timeuntil }}        {# "3 hari lagi" #}

{# ═══ FORMAT LIST ═══ #}
{{ tag_list|join:", " }}       {# ["A", "B", "C"] → "A, B, C" #}
{{ produk_list|length }}       {# [a, b, c] → 3 #}
{{ produk_list|first }}        {# Elemen pertama #}
{{ produk_list|last }}         {# Elemen terakhir #}

{# ═══ FORMAT BOOLEAN ═══ #}
{{ aktif|yesno:"Ya,Tidak" }}  {# True → "Ya", False → "Tidak" #}
{{ aktif|yesno:"Aktif,Nonaktif,Belum Diisi" }}

{# ═══ KEAMANAN ═══ #}
{{ html_content|safe }}        {# Render HTML (HATI-HATI XSS!) #}
{{ html_content|escape }}      {# Escape HTML tags (aman) #}
```

---

## D. Custom Template Tags di Project ERP

### File: `web_project/template_tags/theme.py`

Template tags untuk tema Sneat dan pengecekan akses.

```python
# Cara pakai: {% load theme %}

# ═══ TAGS ═══

{% get_theme_variables 'template_name' %}
# Mengambil variabel tema berdasarkan nama template
# Isi: konfigurasi warna, font, layout

{% get_theme_config 'layout' %}
# Mengambil konfigurasi tema (layout type)

{% current_url request %}
# Mengembalikan URL absolut saat ini
# Contoh: http://127.0.0.1:8000/produk/list/
```

### Filter Pengecekan Akses:

```html
{% load theme %}

{# ═══ Cek Group User ═══ #}
{% if user|has_group:'admin' %}
    {# User ada di group "admin" #}
{% endif %}

{# ═══ Cek Permission Bawaan Django ═══ #}
{% if user|has_permission:'produk.can_add_produk' %}
    <button>Tambah</button>
{% endif %}

{# ═══ Cek Role ═══ #}
{% if user|is_admin %}      {# Apakah di group "admin"? #}
{% if user|is_superuser %}  {# Apakah superuser? #}
{% if user|is_staff %}      {# Apakah staff? #}

{# ═══ Cek URL Aktif di Sidebar ═══ #}
{% if submenu|filter_by_url:request %}
    {# Submenu ini aktif (URL cocok) → beri class "active" #}
{% endif %}
```

---

## E. Custom Template Filters di Project ERP

### File: `apps/core/templatetags/currency_filters.py`

```python
# Cara pakai: {% load currency_filters %}
```

```html
{# ═══ Format Rupiah ═══ #}
{{ produk.harga_jual|rupiah }}
{# 500000 → "Rp 500,000" #}
{# 2500000.50 → "Rp 2,500,001" (dibulatkan) #}

{# ═══ Parse JSON String ═══ #}
{{ json_string|json_load_safe }}
{# '{"key": "value"}' → dictionary Python {key: value} #}
{# Dipakai untuk: metadata JSON yang disimpan sebagai string #}

{# ═══ Ganti Underscore ═══ #}
{{ nama_field|replace_underscore:" " }}
{# "harga_jual" → "harga jual" #}
{# Dipakai untuk: menampilkan nama field yang readable #}
```

---

## F. Cara Membuat Custom Tag/Filter Sendiri

### Langkah-Langkah:

```python
# ═══ LANGKAH 1: Buat folder templatetags ═══
# apps/myapp/templatetags/__init__.py     ← File kosong (wajib!)
# apps/myapp/templatetags/my_filters.py   ← File filter

# ═══ LANGKAH 2: Tulis code filter ═══
# apps/myapp/templatetags/my_filters.py

from django import template

register = template.Library()   # ← WAJIB: registry

# ─── SIMPLE FILTER ───
@register.filter
def currency_idr(value):
    """Format angka ke Rupiah Indonesia.
    Usage: {{ 500000|currency_idr }} → "Rp 500.000"
    """
    try:
        value = float(value)
        formatted = f"{value:,.0f}".replace(',', '.')
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return value


# ─── FILTER DENGAN ARGUMENT ───
@register.filter
def multiply(value, arg):
    """Kalikan dua angka.
    Usage: {{ produk.harga|multiply:produk.stok }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


# ─── FILTER BOOLEAN ───
@register.filter
def status_badge(value):
    """Konversi status ke class badge.
    Usage: <span class="badge {{ order.status|status_badge }}">
    """
    mapping = {
        'draft': 'bg-label-warning',
        'confirmed': 'bg-label-info',
        'processing': 'bg-label-primary',
        'done': 'bg-label-success',
        'cancelled': 'bg-label-danger',
    }
    return mapping.get(value, 'bg-label-secondary')


# ─── SIMPLE TAG (lebih powerful dari filter) ───
@register.simple_tag
def greeting(name, time_of_day='pagi'):
    """Tag dengan multiple arguments.
    Usage: {% greeting "Admin" "sore" %}
    """
    return f"Selamat {time_of_day}, {name}!"


# ─── INCLUSION TAG (render template lain) ───
@register.inclusion_tag('partials/stat_card.html')
def stat_card(title, value, icon, color='primary'):
    """Render kartu statistik.
    Usage: {% stat_card "Total Produk" 150 "ri-shopping-bag-3-line" "success" %}
    """
    return {
        'title': title,
        'value': value,
        'icon': icon,
        'color': color,
    }
```

```html
{# ═══ LANGKAH 3: Gunakan di template ═══ #}
{% load my_filters %}

<p>{{ produk.harga|currency_idr }}</p>
<p>Subtotal: {{ produk.harga|multiply:produk.stok|currency_idr }}</p>
<span class="badge {{ order.status|status_badge }}">{{ order.get_status_display }}</span>
{% greeting request.user.first_name "sore" %}
{% stat_card "Total Produk" total_produk "ri-shopping-bag-3-line" %}
```

### Struktur Folder yang Benar:

```
apps/
├── core/
│   ├── templatetags/          ← Folder templatetags
│   │   ├── __init__.py        ← File kosong (WAJIB!)
│   │   └── currency_filters.py ← Custom filters kita
│   ├── models.py
│   └── ...
└── myapp/
    ├── templatetags/          ← Setiap app bisa punya sendiri
    │   ├── __init__.py
    │   └── my_filters.py
    └── ...
```

**Aturan Penting:**
1. Folder `templatetags` harus di dalam app yang terdaftar di `INSTALLED_APPS`
2. Harus ada `__init__.py` di folder `templatetags`
3. Harus `register = template.Library()` di file filter
4. Harus `{% load nama_file %}` di template sebelum dipakai
5. Setelah buat filter baru: restart server Django!

---

*Lanjut ke [15_CHARTS_DAN_DASHBOARD.md](15_CHARTS_DAN_DASHBOARD.md) →*
