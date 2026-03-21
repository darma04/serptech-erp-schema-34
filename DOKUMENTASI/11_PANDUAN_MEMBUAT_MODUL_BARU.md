# 🛠️ 11 — Panduan Lengkap CRUD, SUBCRUD & Fitur ERP

## DAFTAR ISI

### Bagian 1: Membuat Modul CRUD Dasar (Step by Step)
- [A. Overview: Apa Saja yang Dibuat?](#a-overview)
- [B. Langkah 1: Buat App Django](#b-langkah-1-buat-app-django)
- [C. Langkah 2: Daftarkan App](#c-langkah-2-daftarkan-app)
- [D. Langkah 3: Buat Model (Database)](#d-langkah-3-buat-model)
- [E. Langkah 4: Buat Form](#e-langkah-4-buat-form)
- [F. Langkah 5: Buat Views (CBV)](#f-langkah-5-buat-views)
- [G. Langkah 6: Buat URL Routing](#g-langkah-6-buat-url-routing)
- [H. Langkah 7: Daftarkan URL di config](#h-langkah-7-daftarkan-url-di-config)
- [I. Langkah 8: Buat Template HTML](#i-langkah-8-buat-template-html)
- [J. Langkah 9: Tambahkan ke Sidebar Menu](#j-langkah-9-tambahkan-ke-sidebar)
- [K. Langkah 10: Daftarkan Permission](#k-langkah-10-daftarkan-permission)
- [L. Langkah 11: Migrasi & Test](#l-langkah-11-migrasi--test)
- [M. Checklist Final](#m-checklist-final)

### Bagian 2: SUBCRUD — Model Parent-Child dengan Formset
- [N. Konsep SUBCRUD dan Perbedaannya dengan CRUD](#n-konsep-subcrud)
- [O. Peta Semua CRUD & SUBCRUD di ERP](#o-peta-semua-crud-subcrud)

### Bagian 3: Fitur-Fitur Tambahan
- [P. Export Excel & PDF (Frontend JavaScript)](#p-export-excel-pdf)
- [Q. Filter Kolom & DataTables](#q-filter-kolom-datatables)
- [R. Log Aktivitas (Audit Trail)](#r-log-aktivitas)
- [S. Fitur Absensi & Face Recognition](#s-fitur-absensi)
- [T. Bot Telegram — Notifikasi Otomatis](#t-bot-telegram)
- [U. POS (Point of Sale) — Kasir](#u-pos-point-of-sale)
- [V. Laporan & Report Views](#v-laporan-report)

---

**Skenario:** Kita akan membuat modul **"Catatan"** (Notes) — sebuah modul sederhana untuk mencatat memo/catatan kerja.

---

## A. Overview: Apa Saja yang Dibuat?

```
Untuk 1 modul baru, kita perlu membuat/edit 8-10 file:

1. apps/catatan/              ← Folder app baru
   ├── __init__.py            ← File kosong (penanda package Python)
   ├── apps.py                ← Konfigurasi app
   ├── models.py              ← Model database
   ├── forms.py               ← Form class
   ├── views.py               ← View class (CBV)
   └── urls.py                ← URL routing app

2. templates/catatan/         ← Template HTML
   ├── catatan_list.html      ← Halaman daftar catatan
   └── catatan_form.html      ← Halaman form tambah/edit

3. File yang di-EDIT (sudah ada):
   ├── config/settings.py     ← Daftarkan app baru
   ├── config/urls.py         ← Include URL app baru
   └── sidebar menu JSON/HTML ← Tambah menu sidebar
```

---

## B. Langkah 1: Buat App Django

```bash
# Di terminal, dari root project:
python manage.py startapp catatan apps/catatan

# Apa yang terjadi:
# Django membuat folder apps/catatan/ dengan struktur default:
#
# apps/catatan/
# ├── __init__.py      ← File kosong
# ├── admin.py         ← Admin panel config (tidak kita pakai)
# ├── apps.py          ← Konfigurasi app
# ├── migrations/      ← Folder migrasi database
# │   └── __init__.py  ← File kosong
# ├── models.py        ← Model (KOSONG)
# ├── tests.py         ← Tests (tidak kita pakai saat ini)
# └── views.py         ← Views (KOSONG)
```

### Edit `apps.py`:

```python
# apps/catatan/apps.py

from django.apps import AppConfig

class CatatanConfig(AppConfig):
    """
    Konfigurasi app Catatan.
    
    default_auto_field: Tipe primary key default → BigAutoField (integer besar)
    name: Path LENGKAP app → 'apps.catatan' (bukan hanya 'catatan')
    verbose_name: Nama yang tampil di Django Admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catatan'          # ← PENTING: harus include 'apps.'
    verbose_name = 'Catatan'       # Nama yang ditampilkan di admin
```

---

## C. Langkah 2: Daftarkan App

```python
# config/settings.py

INSTALLED_APPS = [
    # ... app bawaan Django ...
    
    # App proyek:
    'apps.core',
    'apps.produk',
    'apps.inventory',
    # ... app lainnya ...
    
    'apps.catatan',  # ← TAMBAHKAN INI
]
```

**Kenapa harus didaftarkan?**
- Agar Django tahu app ini ada
- Agar `makemigrations` bisa membuat migrasi untuk model app ini
- Agar template loader bisa menemukan template app ini

---

## D. Langkah 3: Buat Model (Database)

```python
# apps/catatan/models.py

"""
==========================================================================
 MODEL CATATAN — Definisi Tabel Database
 Setiap class = 1 tabel di database
==========================================================================
"""

from django.db import models              # Framework ORM Django
from django.contrib.auth.models import User  # Model User bawaan Django

class Catatan(models.Model):
    """
    Tabel: catatan_catatan (nama_app + nama_model, lowercase)
    
    Field-field:
    - judul:       Judul catatan (maks 200 karakter)
    - isi:         Isi catatan (teks panjang, bisa kosong)
    - prioritas:   Pilihan: rendah/sedang/tinggi
    - selesai:     Status sudah dikerjakan atau belum
    - dibuat_oleh: Siapa yang membuat (relasi ke User)
    - dibuat_pada: Otomatis saat record dibuat
    - diupdate_pada: Otomatis saat record diubah
    """
    
    # ═══ PILIHAN (CHOICES) ═══
    PRIORITAS_CHOICES = [
        ('rendah', 'Rendah'),
        ('sedang', 'Sedang'),
        ('tinggi', 'Tinggi'),
    ]
    # Format: ('nilai_di_database', 'Label_yang_ditampilkan')
    # Di database tersimpan: 'rendah'
    # Di template ditampilkan: 'Rendah'
    
    # ═══ FIELD DEFINITIONS ═══
    judul = models.CharField(
        max_length=200,          # Maks 200 karakter
        verbose_name='Judul',    # Label di form/admin
        help_text='Judul singkat catatan'
    )
    # Output SQL: judul VARCHAR(200) NOT NULL
    
    isi = models.TextField(
        blank=True,              # Boleh kosong di FORM (tidak wajib diisi)
        default='',              # Nilai default: string kosong
        verbose_name='Isi Catatan'
    )
    # Output SQL: isi TEXT DEFAULT ''
    
    prioritas = models.CharField(
        max_length=10,
        choices=PRIORITAS_CHOICES,
        default='sedang',        # Default: sedang
        verbose_name='Prioritas'
    )
    # Output SQL: prioritas VARCHAR(10) DEFAULT 'sedang'
    # Di form otomatis jadi dropdown
    
    selesai = models.BooleanField(
        default=False,           # Default: belum selesai
        verbose_name='Sudah Selesai'
    )
    # Output SQL: selesai BOOLEAN DEFAULT FALSE
    # Di form otomatis jadi checkbox
    
    dibuat_oleh = models.ForeignKey(
        User,                    # Relasi ke tabel auth_user
        on_delete=models.CASCADE, # Jika user dihapus → catatan juga dihapus
        related_name='catatan',  # Akses balik: user.catatan.all()
        null=True,               # Boleh NULL di database
        blank=True,              # Boleh kosong di form
        verbose_name='Dibuat Oleh'
    )
    # Output SQL: dibuat_oleh_id INTEGER REFERENCES auth_user(id)
    
    dibuat_pada = models.DateTimeField(
        auto_now_add=True        # Otomatis isi saat CREATE (sekali saja)
    )
    # Tidak bisa diubah setelah record dibuat
    
    diupdate_pada = models.DateTimeField(
        auto_now=True            # Otomatis isi saat SAVE (setiap kali)
    )
    # Update otomatis setiap kali .save() dipanggil
    
    class Meta:
        """
        Pengaturan tambahan model:
        - ordering: Default urutan query → terbaru dulu
        - verbose_name_plural: Nama jamak di admin
        """
        ordering = ['-dibuat_pada']   # Minus = descending (terbaru dulu)
        verbose_name = 'Catatan'
        verbose_name_plural = 'Catatan'
    
    def __str__(self):
        """
        Representasi string model.
        Dipanggil saat: print(), template {{ catatan }}, dropdown select
        """
        return self.judul
    
    @property
    def prioritas_badge(self):
        """
        Property untuk menentukan warna badge berdasarkan prioritas.
        Digunakan di template: {{ catatan.prioritas_badge }}
        """
        badges = {
            'rendah': 'bg-label-info',
            'sedang': 'bg-label-warning',
            'tinggi': 'bg-label-danger',
        }
        return badges.get(self.prioritas, 'bg-label-secondary')
```

---

## E. Langkah 4: Buat Form

```python
# apps/catatan/forms.py

"""
==========================================================================
 FORM CATATAN — Validasi dan Widget
==========================================================================
"""

from django import forms
from .models import Catatan   # Import model dari file models.py yang sama folder

class CatatanForm(forms.ModelForm):
    """
    ModelForm = form yang otomatis di-generate dari model.
    
    Kenapa ModelForm, bukan Form biasa?
    → Otomatis mengikuti field dari model
    → Otomatis validasi (max_length, required, dll)
    → Otomatis save ke database: form.save()
    """
    
    class Meta:
        model = Catatan          # ← Model yang dipakai
        fields = [               # ← Field yang ditampilkan di form
            'judul',
            'isi',
            'prioritas',
            'selesai',
        ]
        # Field yang TIDAK ada:
        # - dibuat_oleh → diisi otomatis di view (dari request.user)
        # - dibuat_pada → auto_now_add (otomatis)
        # - diupdate_pada → auto_now (otomatis)
        
        widgets = {
            # Widget = bagaimana field ditampilkan di HTML
            'judul': forms.TextInput(attrs={
                'class': 'form-control',       # ← Class Sneat Bootstrap
                'placeholder': 'Judul catatan',
                'autofocus': True,             # Fokus otomatis ke field ini
            }),
            'isi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,                     # Tinggi textarea
                'placeholder': 'Tulis isi catatan...',
            }),
            'prioritas': forms.Select(attrs={
                'class': 'form-select',        # ← Class Sneat untuk <select>
            }),
            'selesai': forms.CheckboxInput(attrs={
                'class': 'form-check-input',   # ← Class Sneat untuk checkbox
            }),
        }
        
        labels = {
            # Custom label (override verbose_name dari model)
            'judul': 'Judul Catatan',
            'isi': 'Isi / Detail',
            'selesai': 'Tandai Sudah Selesai',
        }
```

---

## F. Langkah 5: Buat Views (CBV)

```python
# apps/catatan/views.py

"""
==========================================================================
 VIEWS CATATAN — CRUD Operations
 List, Create, Update, Delete menggunakan Class-Based Views (CBV)
==========================================================================
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy        # URL resolver untuk redirect
from django.contrib import messages          # Flash messages
from django.http import JsonResponse         # Response JSON (untuk AJAX delete)
from web_project import TemplateLayout       # Layout engine Sneat
from apps.core.mixins import SubModulePermissionMixin  # Permission check
from .models import Catatan
from .forms import CatatanForm


class CatatanListView(SubModulePermissionMixin, ListView):
    """
    Halaman daftar catatan.
    
    Inheritance:
    SubModulePermissionMixin ← Cek permission sebelum akses
    ListView ← Ambil semua data dari database, kirim ke template
    
    URL: /catatan/list/
    Template: templates/catatan/catatan_list.html
    """
    model = Catatan                        # Model yang di-query
    template_name = 'catatan/catatan_list.html'  # Path template
    context_object_name = 'catatan_list'   # Nama variabel di template
    
    # Permission settings:
    permission_module = 'catatan'          # Nama modul di RBAC
    permission_sub_module = 'catatan'      # Nama sub-modul
    permission_action = 'read'             # Aksi: read/create/update/delete
    
    def get_queryset(self):
        """
        Override get_queryset untuk optimasi query.
        select_related = JOIN tabel dibuat_oleh (menghindari N+1)
        """
        return Catatan.objects.select_related('dibuat_oleh')
    
    def get_context_data(self, **kwargs):
        """
        Tambahkan data extra ke context template.
        
        WAJIB: TemplateLayout.init(self, ...) ← menginisialisasi layout Sneat
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # ↑ super().get_context_data(**kwargs) = context default Django
        # ↑ TemplateLayout.init() = tambah variabel layout (sidebar, navbar, dll)
        
        context['total_catatan'] = self.get_queryset().count()
        context['total_selesai'] = self.get_queryset().filter(selesai=True).count()
        return context


class CatatanCreateView(SubModulePermissionMixin, CreateView):
    """
    Halaman tambah catatan baru.
    
    URL: /catatan/add/
    Template: templates/catatan/catatan_form.html
    Setelah sukses: redirect ke /catatan/list/
    """
    model = Catatan
    form_class = CatatanForm
    template_name = 'catatan/catatan_form.html'
    success_url = reverse_lazy('catatan:list')  # Redirect setelah berhasil
    # reverse_lazy = resolve URL name → URL path saat dibutuhkan
    # 'catatan:list' = namespace:url_name (lihat urls.py)
    
    permission_module = 'catatan'
    permission_sub_module = 'catatan'
    permission_action = 'create'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = 'Tambah Catatan'   # Judul di template
        context['submit_text'] = 'Simpan'
        return context
    
    def form_valid(self, form):
        """
        Dipanggil JIKA form valid (semua validasi lolos).
        
        Kita override untuk:
        1. Set dibuat_oleh = user yang login
        2. Tampilkan pesan sukses
        """
        form.instance.dibuat_oleh = self.request.user
        # form.instance = objek Catatan yang BELUM disave
        # self.request.user = user yang sedang login
        
        messages.success(self.request, 'Catatan berhasil ditambahkan!')
        # Pesan ini akan muncul di halaman redirect (list)
        
        return super().form_valid(form)
        # super().form_valid() = save ke database + redirect


class CatatanUpdateView(SubModulePermissionMixin, UpdateView):
    """
    Halaman edit catatan.
    
    URL: /catatan/<int:pk>/edit/
    Template: templates/catatan/catatan_form.html (SAMA dengan create!)
    """
    model = Catatan
    form_class = CatatanForm
    template_name = 'catatan/catatan_form.html'  # Template yang sama!
    success_url = reverse_lazy('catatan:list')
    
    permission_module = 'catatan'
    permission_sub_module = 'catatan'
    permission_action = 'write'     # 'write' = aksi edit (bukan 'update'!)
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = f'Edit Catatan: {self.object.judul}'
        context['submit_text'] = 'Update'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Catatan berhasil diupdate!')
        return super().form_valid(form)


class CatatanDeleteView(SubModulePermissionMixin, DeleteView):
    """
    Hapus catatan via AJAX.
    
    URL: /catatan/<int:pk>/delete/
    Method: DELETE (AJAX dari JavaScript)
    Response: JSON (bukan redirect HTML)
    """
    model = Catatan
    
    permission_module = 'catatan'
    permission_sub_module = 'catatan'
    permission_action = 'delete'
    
    def delete(self, request, *args, **kwargs):
        """
        Override delete untuk return JSON response.
        Kenapa JSON? Karena dipanggil via AJAX (tanpa reload halaman).
        """
        try:
            catatan = self.get_object()     # Ambil objek berdasarkan pk
            nama = catatan.judul            # Simpan nama sebelum dihapus
            catatan.delete()                # HAPUS dari database
            return JsonResponse({
                'success': True,
                'message': f'Catatan "{nama}" berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Gagal menghapus: {str(e)}'
            }, status=400)
```

---

## G. Langkah 6: Buat URL Routing

```python
# apps/catatan/urls.py

"""
==========================================================================
 URL ROUTING CATATAN
 Mendaftarkan URL pattern untuk setiap view
==========================================================================
"""

from django.urls import path
from . import views    # Import views dari folder yang sama

# app_name = namespace untuk URL reverse
# Dengan ini, kita bisa pakai: {% url 'catatan:list' %}
app_name = 'catatan'

urlpatterns = [
    # ═══ LIST ═══
    # URL: /catatan/list/
    # View: CatatanListView
    # Name: 'catatan:list'
    path('list/', views.CatatanListView.as_view(), name='list'),
    
    # ═══ CREATE ═══
    # URL: /catatan/add/
    path('add/', views.CatatanCreateView.as_view(), name='add'),
    
    # ═══ UPDATE ═══
    # URL: /catatan/5/edit/ (5 = pk/id catatan)
    # <int:pk> = tangkap integer dari URL, kirim sebagai parameter 'pk'
    path('<int:pk>/edit/', views.CatatanUpdateView.as_view(), name='edit'),
    
    # ═══ DELETE ═══
    # URL: /catatan/5/delete/
    path('<int:pk>/delete/', views.CatatanDeleteView.as_view(), name='delete'),
]
```

---

## H. Langkah 7: Daftarkan URL di config

```python
# config/urls.py

from django.urls import path, include

urlpatterns = [
    # ... URL lainnya ...
    
    path("produk/", include("apps.produk.urls")),
    path("inventory/", include("apps.inventory.urls")),
    
    # ═══ TAMBAHKAN INI ═══
    path("catatan/", include("apps.catatan.urls")),
    # Semua URL di apps/catatan/urls.py akan diawali /catatan/
    # Contoh: /catatan/list/, /catatan/add/, /catatan/5/edit/
    
    # ... URL lainnya ...
]
```

---

## I. Langkah 8: Buat Template HTML

### Template List (`catatan_list.html`):

```html
{# templates/catatan/catatan_list.html #}

{% extends 'layout/layout_vertical.html' %}
{% load static %}

{% block title %}Catatan{% endblock %}

{% block vendor_css %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'vendor/libs/datatables-bs5/datatables.bootstrap5.css' %}" />
{% endblock %}

{% block vendor_js %}
{{ block.super }}
<script src="{% static 'vendor/libs/datatables-bs5/datatables-bootstrap5.js' %}"></script>
{% endblock %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    {# ═══ HEADER ═══ #}
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h4 class="mb-1">
                <i class="ri-sticky-note-line me-2"></i>Catatan
            </h4>
            <p class="text-muted mb-0">Kelola catatan dan memo kerja</p>
        </div>
        <a href="{% url 'catatan:add' %}" class="btn btn-primary">
            <i class="ri-add-line me-1"></i>Tambah Catatan
        </a>
    </div>

    {# ═══ STATISTIK CARDS ═══ #}
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body d-flex align-items-center">
                    <div class="avatar me-3">
                        <span class="avatar-initial rounded bg-label-primary">
                            <i class="ri-sticky-note-line ri-24px"></i>
                        </span>
                    </div>
                    <div>
                        <h4 class="mb-0">{{ total_catatan }}</h4>
                        <span class="text-muted">Total Catatan</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-body d-flex align-items-center">
                    <div class="avatar me-3">
                        <span class="avatar-initial rounded bg-label-success">
                            <i class="ri-checkbox-circle-line ri-24px"></i>
                        </span>
                    </div>
                    <div>
                        <h4 class="mb-0">{{ total_selesai }}</h4>
                        <span class="text-muted">Selesai</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {# ═══ TABEL DATA ═══ #}
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Daftar Catatan</h5>
        </div>
        <div class="card-datatable table-responsive">
            <table class="table table-hover" id="catatanTable">
                <thead>
                    <tr>
                        <th>Judul</th>
                        <th>Prioritas</th>
                        <th>Status</th>
                        <th>Dibuat Oleh</th>
                        <th>Tanggal</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in catatan_list %}
                    <tr>
                        <td><strong>{{ c.judul }}</strong></td>
                        <td>
                            <span class="badge {{ c.prioritas_badge }}">
                                {{ c.get_prioritas_display }}
                            </span>
                            {# get_prioritas_display = tampilkan label, bukan value #}
                            {# 'tinggi' → 'Tinggi' #}
                        </td>
                        <td>
                            {% if c.selesai %}
                                <span class="badge bg-label-success">Selesai</span>
                            {% else %}
                                <span class="badge bg-label-warning">Belum</span>
                            {% endif %}
                        </td>
                        <td>{{ c.dibuat_oleh.username|default:"-" }}</td>
                        <td>{{ c.dibuat_pada|date:"d M Y H:i" }}</td>
                        <td>
                            <a href="{% url 'catatan:edit' c.pk %}" class="btn btn-sm btn-label-warning">
                                <i class="ri-edit-line"></i>
                            </a>
                            <button class="btn btn-sm btn-label-danger"
                                    onclick="confirmDelete({{ c.pk }}, '{{ c.judul }}')">
                                <i class="ri-delete-bin-line"></i>
                            </button>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="6" class="text-center py-5">
                            <i class="ri-sticky-note-line ri-3x text-muted d-block mb-2"></i>
                            <p class="text-muted">Belum ada catatan</p>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {# ═══ MODAL HAPUS ═══ #}
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
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
                    <p class="text-muted">Catatan: <strong id="deleteName"></strong></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-label-secondary" data-bs-dismiss="modal">Batal</button>
                    <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                        <i class="ri-delete-bin-line me-1"></i>Ya, Hapus
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% csrf_token %}
{% endblock %}

{% block page_js %}
<script>
$(document).ready(function() {
    {% if catatan_list %}
    $('#catatanTable').DataTable({
        language: {
            sEmptyTable: "Tidak ada data",
            sLengthMenu: "Tampilkan _MENU_ data",
            sZeroRecords: "Data tidak ditemukan",
            sInfo: "Menampilkan _START_-_END_ dari _TOTAL_",
            sSearch: "Cari:",
            oPaginate: { sPrevious: "Sebelumnya", sNext: "Selanjutnya" }
        },
        order: [[4, 'desc']],   // Urutkan tanggal terbaru
        pageLength: 25,
        columnDefs: [{ orderable: false, targets: [5] }]
    });
    {% endif %}
});

let deleteId = null;

function confirmDelete(id, nama) {
    deleteId = id;
    document.getElementById('deleteName').textContent = nama;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    if (!deleteId) return;
    
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Menghapus...';
    
    fetch(`/catatan/${deleteId}/delete/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) location.reload();
        else alert(data.message);
    });
});
</script>
{% endblock %}
```

### Template Form (`catatan_form.html`):

```html
{# templates/catatan/catatan_form.html #}

{% extends 'layout/layout_vertical.html' %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container-xxl flex-grow-1 container-p-y">
    <h4 class="mb-4">
        <i class="ri-sticky-note-line me-2"></i>{{ title }}
    </h4>

    <form method="POST">
        {% csrf_token %}
        
        <div class="card">
            <div class="card-body">
                <div class="row g-3">
                    {# ═══ JUDUL ═══ #}
                    <div class="col-md-8">
                        <label class="form-label" for="id_judul">{{ form.judul.label }}</label>
                        {{ form.judul }}
                        {% if form.judul.errors %}
                        <div class="text-danger small mt-1">{{ form.judul.errors.0 }}</div>
                        {% endif %}
                    </div>
                    
                    {# ═══ PRIORITAS ═══ #}
                    <div class="col-md-4">
                        <label class="form-label" for="id_prioritas">{{ form.prioritas.label }}</label>
                        {{ form.prioritas }}
                    </div>
                    
                    {# ═══ ISI ═══ #}
                    <div class="col-12">
                        <label class="form-label" for="id_isi">{{ form.isi.label }}</label>
                        {{ form.isi }}
                    </div>
                    
                    {# ═══ CHECKBOX SELESAI ═══ #}
                    <div class="col-12">
                        <div class="form-check">
                            {{ form.selesai }}
                            <label class="form-check-label" for="id_selesai">
                                {{ form.selesai.label }}
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card-footer text-end">
                <a href="{% url 'catatan:list' %}" class="btn btn-label-secondary me-2">
                    <i class="ri-close-line me-1"></i>Batal
                </a>
                <button type="submit" class="btn btn-primary">
                    <i class="ri-save-line me-1"></i>{{ submit_text|default:"Simpan" }}
                </button>
            </div>
        </div>
    </form>
</div>
{% endblock %}
```

---

## J. Langkah 9: Tambahkan ke Sidebar Menu

Edit file JSON atau HTML sidebar untuk menambahkan menu "Catatan":

```json
// Dalam file konfigurasi sidebar menu (VERTICAL_MENU)
{
    "name": "Catatan",
    "icon": "ri-sticky-note-line",
    "slug": "catatan",
    "url": "/catatan/list/",
    "module": "catatan",
    "sub_module": "catatan",
    "permission_action": "read"
}
```

Lokasi perlu dicek: biasanya di `templates/layout/partials/menu/vertical/vertical_menu.html` atau di database/JSON config.

---

## K. Langkah 10: Daftarkan Permission

Agar modul Catatan ter-proteksi RBAC, pastikan:

1. **Tambah ke daftar modul** di Admin RBAC:
   - Module name: `catatan`
   - Sub module: `catatan`
   - Actions: `read`, `create`, `update`, `delete`

2. **Assign ke Role** yang sesuai:
   - Admin → centang semua action
   - User biasa → centang `read` saja (misalnya)

---

## L. Langkah 11: Migrasi & Test

```bash
# ═══ LANGKAH 1: Buat file migrasi ═══
python manage.py makemigrations catatan
# Output:
# Migrations for 'catatan':
#   apps/catatan/migrations/0001_initial.py
#     - Create model Catatan

# ═══ LANGKAH 2: Jalankan migrasi ═══
python manage.py migrate
# Output:
# Running migrations:
#   Applying catatan.0001_initial... OK

# ═══ LANGKAH 3: Jalankan server ═══
python manage.py runserver
# Buka: http://127.0.0.1:8000/catatan/list/

# ═══ LANGKAH 4: Test manual di browser ═══
# 1. Cek halaman list muncul tanpa error
# 2. Klik "Tambah Catatan" → isi form → Simpan
# 3. Cek data muncul di list
# 4. Klik Edit → ubah data → Update
# 5. Klik Hapus → konfirmasi → cek data terhapus
```

---

## M. Checklist Final

```
✅ Checklist Modul Baru:
─────────────────────────────
[ ] 1. Buat app: python manage.py startapp
[ ] 2. Edit apps.py: set name = 'apps.catatan'
[ ] 3. Daftarkan di config/settings.py INSTALLED_APPS
[ ] 4. Buat models.py: definisi tabel database
[ ] 5. Buat forms.py: definisi form + widget Sneat
[ ] 6. Buat views.py: CBV (List, Create, Update, Delete)
[ ] 7. Buat urls.py: URL pattern dengan namespace
[ ] 8. Daftarkan di config/urls.py: include()
[ ] 9. Buat templates: list + form HTML
[ ] 10. Tambah sidebar menu
[ ] 11. Daftarkan permission RBAC
[ ] 12. makemigrations + migrate
[ ] 13. Test di browser (CRUD lengkap)
```

---

**Selamat!** Kamu sudah belajar membuat modul CRUD dasar. Selanjutnya kita pelajari **SUBCRUD, Export, Filter, dan fitur-fitur lanjutan** yang ada di ERP.

---

# BAGIAN 2: SUBCRUD & PETA MODUL ERP

---

## N. Konsep SUBCRUD dan Perbedaannya dengan CRUD

### Apa itu SUBCRUD?

```
CRUD Biasa (Flat):
┌──────────────┐
│   Kategori   │  ← 1 model, 1 tabel, CRUD mandiri
│  List/Add/   │
│  Edit/Delete │
└──────────────┘

SUBCRUD (Parent-Child / Master-Detail):
┌──────────────────────────────────────────┐
│ Sales Order (PARENT)                     │
│  ├── nomor_so, tanggal, customer         │
│  │                                       │
│  └── Items (CHILD — banyak baris)        │
│       ├── Produk A x 5  = Rp 500.000    │
│       ├── Produk B x 3  = Rp 300.000    │
│       └── Produk C x 1  = Rp 100.000    │
│                                          │
│  Total: Rp 900.000                       │
└──────────────────────────────────────────┘
```

**Perbedaan utama:**

| Aspek | CRUD | SUBCRUD |
|-------|------|---------|
| Model | 1 model | 2+ model (parent + child) |
| Form | 1 ModelForm | 1 ModelForm + **Formset** |
| Relasi | Tidak ada / FK sederhana | ForeignKey parent→child |
| Template | 1 form biasa | Form + tabel dinamis (tambah/hapus baris) |
| JavaScript | Minimal | **Wajib** (tambah/hapus baris formset) |
| Contoh | Kategori, Satuan, Departemen | Sales Order+Items, PO+Items, Transfer+Items |

### Model SUBCRUD — Parent-Child

```python
# ═══ MODEL PARENT ═══
class SalesOrder(models.Model):
    nomor_so = models.CharField(max_length=50, unique=True)
    tanggal = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    gudang = models.ForeignKey(Gudang, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    diskon = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pajak = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_harga = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

# ═══ MODEL CHILD (Items) ═══
class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,    # Hapus parent → hapus semua child
        related_name='items'         # Akses: sales_order.items.all()
    )
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah = models.DecimalField(max_digits=15, decimal_places=2)
    harga = models.DecimalField(max_digits=15, decimal_places=2)
    diskon = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Hitung subtotal otomatis saat save
    def save(self, *args, **kwargs):
        self.subtotal = (self.harga * self.jumlah) - self.diskon
        super().save(*args, **kwargs)
```

### Formset — Form untuk Banyak Child Sekaligus

```python
# apps/penjualan/forms.py

from django.forms import inlineformset_factory

# inlineformset_factory = factory untuk membuat FormSet dari relasi parent-child
SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder,          # Parent model
    SalesOrderItem,      # Child model
    fields=['produk', 'jumlah', 'harga', 'diskon'],  # Field yang ditampilkan
    extra=1,             # Jumlah form kosong default
    can_delete=True,     # Boleh hapus baris
    widgets={
        'produk': forms.Select(attrs={'class': 'form-select select2'}),
        'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        'harga': forms.NumberInput(attrs={'class': 'form-control'}),
        'diskon': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
    }
)
```

### View SUBCRUD — Simpan Parent + Child Bersamaan

```python
# apps/penjualan/views.py — SalesOrderCreateView

class SalesOrderCreateView(SubModulePermissionMixin, CreateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'penjualan/sales_order_form.html'
    permission_module = 'penjualan'
    permission_sub_module = 'sales_order'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # ↓ Kirim formset ke template (kosong untuk create)
        if self.request.POST:
            context['formset'] = SalesOrderItemFormSet(self.request.POST)
        else:
            context['formset'] = SalesOrderItemFormSet()
        context['title'] = 'Buat Sales Order'
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            # 1. Simpan parent (Sales Order)
            form.instance.dibuat_oleh = self.request.user
            self.object = form.save()
            
            # 2. Hubungkan formset ke parent, lalu simpan semua child
            formset.instance = self.object
            formset.save()
            
            # 3. Hitung ulang total dari semua items
            self.object.subtotal = sum(item.subtotal for item in self.object.items.all())
            self.object.total_harga = self.object.subtotal - self.object.diskon + self.object.pajak
            self.object.save()
            
            # 4. Kirim notifikasi Telegram
            from apps.automation.signals import kirim_notifikasi_sales_order
            kirim_notifikasi_sales_order(self.object)
            
            messages.success(self.request, 'Sales Order berhasil dibuat!')
            return redirect('penjualan:sales_order')
        else:
            return self.render_to_response(self.get_context_data(form=form))
```

### Template SUBCRUD — Tabel Dinamis dengan JavaScript

```html
{# Template: penjualan/sales_order_form.html #}

{# ═══ FORM PARENT ═══ #}
<form method="POST" id="soForm">
    {% csrf_token %}
    <div class="row g-3">
        <div class="col-md-4">
            {{ form.nomor_so }}    {# Nomor SO (editable) #}
        </div>
        <div class="col-md-4">
            {{ form.customer }}    {# Dropdown customer #}
        </div>
        <div class="col-md-4">
            {{ form.gudang }}      {# Dropdown gudang #}
        </div>
    </div>
    
    {# ═══ TABEL ITEMS (CHILD) ═══ #}
    {{ formset.management_form }}   {# WAJIB! Data internal Django formset #}
    
    <table class="table" id="itemsTable">
        <thead>
            <tr>
                <th>Produk</th>
                <th>Jumlah</th>
                <th>Harga</th>
                <th>Diskon</th>
                <th>Subtotal</th>
                <th>Aksi</th>
            </tr>
        </thead>
        <tbody>
            {% for item_form in formset %}
            <tr class="item-row">
                {{ item_form.id }}    {# Hidden: primary key child #}
                <td>{{ item_form.produk }}</td>
                <td>{{ item_form.jumlah }}</td>
                <td>{{ item_form.harga }}</td>
                <td>{{ item_form.diskon }}</td>
                <td class="subtotal">Rp 0</td>
                <td>
                    <button type="button" class="btn btn-sm btn-danger remove-row">
                        <i class="ri-delete-bin-line"></i>
                    </button>
                    {{ item_form.DELETE }}  {# Checkbox hapus (hidden) #}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <button type="button" id="addRow" class="btn btn-outline-primary">
        <i class="ri-add-line me-1"></i>Tambah Produk
    </button>
</form>

<script>
// ═══ JAVASCRIPT FORMSET: Tambah & Hapus Baris ═══
const totalForms = document.getElementById('id_items-TOTAL_FORMS');
const tbody = document.querySelector('#itemsTable tbody');

// Template baris baru (clone dari baris pertama, ganti index)
document.getElementById('addRow').addEventListener('click', function() {
    const formCount = parseInt(totalForms.value);
    const firstRow = tbody.querySelector('.item-row');
    const newRow = firstRow.cloneNode(true);
    
    // Ganti semua "items-0-" menjadi "items-{formCount}-"
    newRow.innerHTML = newRow.innerHTML.replace(/items-\d+-/g, `items-${formCount}-`);
    
    // Kosongkan value input
    newRow.querySelectorAll('input, select').forEach(input => {
        if (input.type !== 'hidden') input.value = '';
    });
    
    tbody.appendChild(newRow);
    totalForms.value = formCount + 1;  // Update TOTAL_FORMS
});

// Hapus baris — set checkbox DELETE, sembunyikan row
document.addEventListener('click', function(e) {
    if (e.target.closest('.remove-row')) {
        const row = e.target.closest('.item-row');
        const deleteCheckbox = row.querySelector('input[name*="-DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = true;  // Tandai untuk dihapus
            row.style.display = 'none';     // Sembunyikan dari UI
        }
    }
});
</script>
```

### Perbedaan Permission CRUD vs SUBCRUD

```python
# CRUD biasa — 1 level permission:
class KategoriListView(SubModulePermissionMixin, ListView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'   # ← Sub-modul = bagian dari produk
    permission_action = 'read'

# SUBCRUD — permission_sub_module menentukan akses granular:
# Di halaman Role Permission, admin bisa centang:
#   ☑ produk.kategori.read     → Lihat daftar kategori
#   ☑ produk.kategori.create   → Tambah kategori baru
#   ☑ produk.kategori.write    → Edit kategori
#   ☑ produk.kategori.delete   → Hapus kategori
#   ☑ produk.satuan.read       → Lihat daftar satuan
#   ☐ produk.satuan.delete     → TIDAK bisa hapus satuan
```

---

## O. Peta Semua CRUD & SUBCRUD di ERP

### Daftar Lengkap 17 Modul

```
ERP System — Peta Modul & Fitur Lengkap
═══════════════════════════════════════════

📦 1. PRODUK (apps/produk/)
   ├── SUBCRUD: Kategori      → List/Create/Update/Delete
   ├── SUBCRUD: Satuan         → List/Create/Update/Delete
   └── SUBCRUD: Produk         → List/Create/Update/Delete
       Fitur khusus: Gambar produk, harga beli/jual, stok otomatis

📦 2. INVENTORY (apps/inventory/)
   ├── SUBCRUD: Gudang         → List/Create/Update/Delete
   └── SUBCRUD: Transfer Stok  → List/Create/Update/Delete + Items (Formset)
       Fitur khusus: Transfer antar gudang, auto update stok

💰 3. PENJUALAN (apps/penjualan/)
   ├── SUBCRUD: Customer       → List/Create/Update/Delete
   ├── SUBCRUD: Sales Order    → List/Create/Update/Delete + Items (Formset)
   └── SUBCRUD: Transaksi POS  → List/Detail (view dari penjualan)
       Fitur khusus: Formset items, auto hitung total, notif Telegram

🛒 4. PEMBELIAN (apps/pembelian/)
   ├── SUBCRUD: Supplier       → List/Create/Update/Delete
   └── SUBCRUD: Purchase Order → List/Create/Update/Delete + Items (Formset)
       Fitur khusus: Auto buat produk baru dari PO, update stok masuk

💸 5. BIAYA (apps/biaya/)
   ├── SUBCRUD: Kategori Biaya → List/Create/Update/Delete
   └── SUBCRUD: Transaksi Biaya → List/Create/Update/Delete
       Fitur khusus: Metode pembayaran, notif Telegram

🏪 6. POS (apps/pos/)
   ├── Kasir (Grid Produk + Keranjang)
   ├── Invoice List / Detail / Print
   └── API: create-transaction, check-stock, search-products, get-stocks
       Fitur khusus: Full AJAX, atomic transaction, auto stok keluar

👥 7. HR (apps/hr/) — Modul Terbesar (1896 baris views!)
   ├── Dashboard HR            → Statistik karyawan, absensi, gaji
   ├── SUBCRUD: Departemen     → List/Create/Update/Delete
   ├── SUBCRUD: Jabatan        → List/Create/Update/Delete
   ├── SUBCRUD: Karyawan       → List/Create/Update/Delete
   ├── SUBCRUD: Absensi        → List/Create/Update/Delete + Clock In/Out API
   ├── SUBCRUD: Penggajian     → List/Create/Update/Delete + Generate Massal
   └── Pengaturan Absensi      → CRUD (jam masuk, toleransi, GPS, hari kerja)
       Fitur khusus: Face recognition, validasi GPS, slip gaji massal

👤 8. USER MANAGEMENT (apps/user_management/)
   └── CRUD: User              → List/Create/Update/Delete/Detail

🔐 9. PERMISSION / ROLES (apps/permission_management/)
   └── CRUD: Role              → List/Create/Update/Delete
       Fitur khusus: Checkbox permission per modul/sub-modul/action

📊 10. LAPORAN (apps/laporan/)
    ├── Laporan Produk          → Read-only + detail per produk
    ├── Laporan Stok            → Read-only
    ├── Laporan Penjualan       → Read-only (SO + POS gabungan)
    ├── Laporan Pembelian       → Read-only
    └── Laporan Keuangan        → Read-only (laba/rugi)
        Fitur: Filter tanggal, summary cards, detail view

📋 11. ACTIVITY LOG (apps/activity_log/)
    └── Log Aktivitas           → Read-only (auto-catat semua aksi user)
        15 jenis aksi: login, logout, create, update, delete, view,
        export, import, approve, reject, stock_in, stock_out, dll

🤖 12. AUTOMATION (apps/automation/)
    ├── Pengaturan Telegram     → Singleton config (1 record)
    ├── Template Pesan          → List/Update per jenis transaksi
    └── Log Notifikasi          → Read-only (riwayat kirim)
        Fitur: Bot token, chat_id, toggle per transaksi, test kirim

📈 13. DASHBOARD (apps/dashboard/)
    └── Dashboard Utama         → Read-only (statistik agregat semua modul)
        Fitur: ApexCharts, Swiper carousel, summary cards

⚙️ 14. PENGATURAN (apps/pengaturan/)
    └── Company Settings        → Singleton (nama, alamat, logo, NPWP)
        + Template Cetak (struk, invoice)
        + Export template settings

📄 15. PAGES (apps/pages/)
    └── Static pages            → Halaman statis (Terms, Privacy, etc)

🧪 16. SAMPLE (apps/sample/)
    └── Contoh/Demo views       → Untuk development dan testing
```

### Tabel Ringkasan Jumlah Views per Modul

| Modul | CRUD Views | SUBCRUD Views | API/FBV | Total |
|-------|-----------|---------------|---------|-------|
| Produk | — | 12 (Kategori+Satuan+Produk) | 1 (AJAX search) | 13 |
| Inventory | — | 8 (Gudang+Transfer) | — | 8 |
| Penjualan | — | 12 (Customer+SO+POS) | — | 12 |
| Pembelian | — | 8 (Supplier+PO) | — | 8 |
| Biaya | — | 8 (KategoriBiaya+Transaksi) | — | 8 |
| POS | 4 (Invoice CRUD) | — | 4 (API) | 8 |
| HR | 20 (6 SUBCRUD x CRUD) | Dashboard | 2 (clock in/out) | 22+ |
| Laporan | — | — | 7 (read-only) | 7 |
| Activity Log | — | — | 1 (read-only) | 1 |
| Automation | — | 4 (pengaturan+template+log) | 3 (test+deteksi+reset) | 7 |

---

# BAGIAN 3: FITUR-FITUR TAMBAHAN

---

## P. Export Excel & PDF (Frontend JavaScript)

### Konsep: Export dari Frontend, Bukan Backend

```
Pendekatan ERP ini:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Tabel HTML  │ →  │  JavaScript  │ →  │  File Excel  │
│  (di browser)│    │  (baca DOM)  │    │  (.xls)      │
└─────────────┘    └──────────────┘    └─────────────┘

Kenapa dari frontend?
✅ Tidak perlu endpoint backend tambahan
✅ Data yang di-export = persis yang dilihat user (termasuk filter)
✅ Bisa include tfoot/ringkasan langsung
✅ Lebih cepat (tidak perlu request ke server)
```

### Pattern Export Excel — HTML Table → .xls

```javascript
// ═══ PATTERN EXPORT EXCEL (digunakan di SEMUA halaman list) ═══

function exportExcel() {
    // 1. Ambil tabel dari DOM
    const table = document.querySelector('#dataTable');
    
    // 2. Buat HTML table string untuk Excel
    let html = '<table border="1">';
    
    // 3. Header (thead)
    const thead = table.querySelector('thead');
    thead.querySelectorAll('tr').forEach(row => {
        html += '<tr>';
        row.querySelectorAll('th').forEach((th, index) => {
            // Skip kolom terakhir (Aksi) karena tidak perlu di-export
            if (index < row.children.length - 1) {
                html += `<th style="background-color: #696CFF; color: #FFFFFF; 
                          font-weight: bold;">${th.textContent.trim()}</th>`;
            }
        });
        html += '</tr>';
    });
    
    // 4. Body (tbody)
    const tbody = table.querySelector('tbody');
    tbody.querySelectorAll('tr').forEach(row => {
        html += '<tr>';
        row.querySelectorAll('td').forEach((td, index) => {
            if (index < row.children.length - 1) {
                const text = td.textContent.trim().replace(/\s+/g, ' ');
                html += `<td>${text}</td>`;
            }
        });
        html += '</tr>';
    });
    
    // 5. Ringkasan (tfoot) — PENTING untuk laporan
    const tfoot = table.querySelector('tfoot');
    if (tfoot) {
        const tfootRow = tfoot.querySelector('tr');
        if (tfootRow) {
            html += '<tr style="background-color: #f8f9fa; font-weight: bold;">';
            tfootRow.querySelectorAll('td').forEach(td => {
                const text = td.textContent.trim().replace(/\s+/g, ' ');
                const colspan = td.getAttribute('colspan') || 1;
                html += `<td colspan="${colspan}">${text}</td>`;
            });
            html += '</tr>';
        }
    }
    
    html += '</table>';
    
    // 6. Download sebagai file .xls
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'data_export.xls';
    link.click();
}
```

### Pattern Export PDF — pdfMake

```javascript
// ═══ PATTERN EXPORT PDF (pdfMake library) ═══

function exportPDF() {
    const table = document.querySelector('#dataTable');
    
    // 1. Ambil header
    const headers = [];
    table.querySelectorAll('thead th').forEach((th, i) => {
        if (i < table.querySelectorAll('thead th').length - 1) {
            headers.push({ text: th.textContent.trim(), style: 'tableHeader' });
        }
    });
    
    // 2. Ambil data rows
    const body = [headers];
    table.querySelectorAll('tbody tr').forEach(row => {
        const rowData = [];
        row.querySelectorAll('td').forEach((td, i) => {
            if (i < row.children.length - 1) {
                rowData.push(td.textContent.trim());
            }
        });
        if (rowData.length > 0) body.push(rowData);
    });
    
    // 3. Definisi dokumen PDF
    const docDefinition = {
        pageOrientation: 'landscape',
        content: [
            { text: 'NAMA PERUSAHAAN', style: 'companyName' },
            { text: 'Laporan Data Export', style: 'reportTitle' },
            { text: `Tanggal: ${new Date().toLocaleDateString('id-ID')}`, 
              style: 'reportDate' },
            {
                table: {
                    headerRows: 1,
                    body: body
                },
                layout: 'lightHorizontalLines'
            }
        ],
        styles: {
            companyName: { fontSize: 16, bold: true, alignment: 'center' },
            reportTitle: { fontSize: 12, alignment: 'center', margin: [0, 5] },
            tableHeader: { bold: true, fillColor: '#696CFF', color: '#FFFFFF' }
        }
    };
    
    pdfMake.createPdf(docDefinition).download('laporan.pdf');
}
```

### Tombol Export di Template

```html
{# Pattern tombol export di setiap halaman list CRUD #}
<div class="card-header d-flex justify-content-between align-items-center">
    <h5 class="mb-0">Daftar Produk</h5>
    <div>
        <button onclick="exportExcel()" class="btn btn-sm btn-success me-1">
            <i class="ri-file-excel-2-line me-1"></i>Excel
        </button>
        <button onclick="exportPDF()" class="btn btn-sm btn-danger">
            <i class="ri-file-pdf-2-line me-1"></i>PDF
        </button>
    </div>
</div>
```

---

## Q. Filter Kolom & DataTables

### Inisialisasi DataTables dengan Bahasa Indonesia

```javascript
// ═══ PATTERN DATATABLES (digunakan di SEMUA halaman list) ═══

$(document).ready(function() {
    $('#dataTable').DataTable({
        // Bahasa Indonesia
        language: {
            sEmptyTable:   "Tidak ada data",
            sInfo:         "Menampilkan _START_ - _END_ dari _TOTAL_ data",
            sInfoEmpty:    "Menampilkan 0 - 0 dari 0 data",
            sInfoFiltered: "(disaring dari _MAX_ total data)",
            sLengthMenu:   "Tampilkan _MENU_ data",
            sSearch:       "Cari:",
            sZeroRecords:  "Tidak ditemukan data yang cocok",
            oPaginate: {
                sFirst:    "Pertama",
                sLast:     "Terakhir",
                sPrevious: "Sebelumnya",
                sNext:     "Selanjutnya"
            }
        },
        order: [[0, 'desc']],    // Urutan default kolom pertama descending
        pageLength: 25,          // 25 data per halaman
        responsive: true,        // Responsive di mobile
        columnDefs: [
            { orderable: false, targets: [-1] }  // Kolom terakhir (Aksi) tidak bisa di-sort
        ]
    });
});
```

### Filter Dropdown di Backend (Django QuerySet)

```python
# ═══ PATTERN FILTER DI GET_QUERYSET ═══
# Contoh dari ActivityLogIndexView:

def get_queryset(self):
    queryset = super().get_queryset()
    
    # Filter dari URL query: ?start=2026-01-01&end=2026-01-31&action=create&user=5
    start_date = self.request.GET.get('start')
    end_date = self.request.GET.get('end')
    action = self.request.GET.get('action')
    user_id = self.request.GET.get('user')
    
    if start_date:
        queryset = queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__date__lte=end_date)
    if action:
        queryset = queryset.filter(action=action)
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    return queryset
```

### Template Filter — Form dengan Dropdown + Datepicker

```html
{# ═══ PATTERN FILTER SECTION DI TEMPLATE LIST ═══ #}

<div class="card mb-4">
    <div class="card-body">
        <form method="GET" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Dari Tanggal</label>
                <input type="date" name="start" value="{{ request.GET.start }}" 
                       class="form-control">
            </div>
            <div class="col-md-3">
                <label class="form-label">Sampai Tanggal</label>
                <input type="date" name="end" value="{{ request.GET.end }}" 
                       class="form-control">
            </div>
            <div class="col-md-3">
                <label class="form-label">Aksi</label>
                <select name="action" class="form-select">
                    <option value="">Semua</option>
                    {% for value, label in action_choices %}
                    <option value="{{ value }}" 
                            {% if request.GET.action == value %}selected{% endif %}>
                        {{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
                <button type="submit" class="btn btn-primary me-2">
                    <i class="ri-filter-line me-1"></i>Filter
                </button>
                <a href="{% url 'activity_log:index' %}" class="btn btn-outline-secondary">
                    <i class="ri-refresh-line me-1"></i>Reset
                </a>
            </div>
        </form>
    </div>
</div>
```

---

## R. Log Aktivitas (Audit Trail)

### Arsitektur Sistem Log

```
Alur Pencatatan Otomatis:
═════════════════════════

User melakukan aksi (Create/Update/Delete)
        │
        ▼
┌─────────────────────────┐
│    Django Signals        │  ← Auto-trigger saat model.save() / model.delete()
│    (signals.py)          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Middleware            │  ← Ambil request info (IP, User Agent)
│    (middleware.py)       │  ← Simpan di thread-local storage
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  UserActivity.create()  │  ← Record baru di tabel activity_log
│  (models.py)            │
└─────────────────────────┘
```

### Model UserActivity — 15 Jenis Aksi

```python
# apps/activity_log/models.py

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),          ('logout', 'Logout'),
        ('create', 'Tambah Data'),   ('update', 'Edit Data'),
        ('delete', 'Hapus Data'),    ('view', 'Lihat Data'),
        ('export', 'Export Data'),   ('import', 'Import Data'),
        ('approve', 'Approve'),      ('reject', 'Reject'),
        # Stok-specific:
        ('stock_in', 'Stok Masuk'),  ('stock_out', 'Stok Keluar'),
        ('stock_adjustment', 'Penyesuaian Stok'),
        ('stock_transfer_in', 'Transfer Masuk'),
        ('stock_transfer_out', 'Transfer Keluar'),
    ]
    
    # ═══ DATA UTAMA ═══
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)    # Nama model: 'Produk'
    object_id = models.CharField(max_length=100)     # ID record: '42'
    object_repr = models.CharField(max_length=200)   # Representasi: 'Laptop ASUS'
    description = models.TextField()                  # Deskripsi lengkap
    
    # ═══ DETAIL PERUBAHAN (JSON) ═══
    changes = models.TextField()  # {"nama": {"old": "Laptop", "new": "Laptop Pro"}}
    
    # ═══ TRACKING STOK ═══
    source_type = models.CharField(max_length=20)    # 'purchase', 'sales', 'pos'
    quantity_before = models.DecimalField(...)        # Stok sebelum: 100
    quantity_after = models.DecimalField(...)         # Stok sesudah: 95
    quantity_change = models.DecimalField(...)        # Perubahan: -5
    gudang_name = models.CharField(max_length=100)   # Nama gudang
    
    # ═══ REQUEST INFO ═══
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Cara Membaca Log di Template

```html
{# templates/activity_log/index.html #}
{% for activity in activities %}
<tr>
    <td>{{ activity.timestamp|date:"d/m/Y H:i" }}</td>
    <td>{{ activity.user.username }}</td>
    <td>
        <span class="badge bg-label-{{ activity.action|badge_color }}">
            {{ activity.get_action_display }}
        </span>
    </td>
    <td>{{ activity.model_name }}</td>
    <td>{{ activity.object_repr }}</td>
    <td>{{ activity.description }}</td>
    {% if activity.is_stock_action %}
    <td>{{ activity.get_quantity_display }}</td>
    {% endif %}
</tr>
{% endfor %}
```

---

## S. Fitur Absensi & Face Recognition

### Arsitektur Modul Absensi

```
Modul HR Absensi — Komponen:
════════════════════════════

1. PengaturanAbsensi (Konfigurasi)
   ├── jam_masuk / jam_pulang (08:00 / 17:00)
   ├── toleransi_terlambat (menit)
   ├── hari_kerja (Senin-Jumat CSV: "0,1,2,3,4")
   ├── zona_waktu (WIB/WITA/WIT)
   ├── radius_kantor (meter, untuk GPS)
   └── latitude/longitude kantor

2. FotoWajah (Face Recognition Data)
   ├── foto (ImageField)
   ├── encoding (TextField—vector JSON)
   └── karyawan (FK → Karyawan)

3. Absensi (Record Kehadiran)
   ├── karyawan + tanggal (unique_together)
   ├── jam_masuk / jam_keluar
   ├── status (hadir/terlambat/izin/sakit/alpha)
   ├── foto_masuk / foto_keluar (bukti)
   ├── lokasi (GPS coordinates)
   └── keterangan
```

### API Clock In / Clock Out

```python
# apps/hr/views.py — absensi_clock_in (FBV)

@login_required
def absensi_clock_in(request):
    """
    API endpoint: POST /hr/absensi/clock-in/
    Input: karyawan_id, foto (optional)
    
    Alur:
    1. Ambil karyawan dari POST data
    2. Cek apakah sudah clock in hari ini
    3. Jika belum → buat record absensi baru
       - Jam masuk < jam_masuk_setting → status 'hadir'
       - Jam masuk >= jam_masuk + toleransi → status 'terlambat'
    4. Jika sudah → return error
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    karyawan_id = request.POST.get('karyawan_id')
    karyawan = get_object_or_404(Karyawan, pk=karyawan_id)
    
    # Cek sudah absen hari ini?
    today = timezone.now().date()
    existing = Absensi.objects.filter(karyawan=karyawan, tanggal=today).first()
    
    if existing:
        return JsonResponse({
            'success': False,
            'message': f'{karyawan.nama} sudah clock in hari ini'
        })
    
    # Tentukan status berdasarkan jam
    now = timezone.now().time()
    pengaturan = PengaturanAbsensi.get_active()
    
    if pengaturan and now > pengaturan.jam_masuk:
        status = 'terlambat'
    else:
        status = 'hadir'
    
    # Buat record absensi
    absensi = Absensi.objects.create(
        karyawan=karyawan,
        tanggal=today,
        jam_masuk=now,
        status=status,
        foto_masuk=request.FILES.get('foto'),
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Clock In berhasil — {karyawan.nama} ({status})'
    })
```

### Halaman Absensi Deteksi Wajah

```
Alur Face Recognition:
═══════════════════════

1. Buka kamera browser (navigator.mediaDevices.getUserMedia)
2. Capture foto wajah
3. Kirim ke backend via AJAX POST (multipart/form-data)
4. Backend bandingkan dengan FotoWajah.encoding yang tersimpan
5. Jika cocok (persentase > threshold) → clock in/out otomatis
6. Jika tidak cocok → tolak, minta coba lagi

Catatan: Face Recognition menggunakan library face_recognition (opsional).
Dikontrol via flag FACE_RECOGNITION_ENABLED di settings.
Jika disabled, absensi dilakukan manual (pilih karyawan + clock in).
```

---

## T. Bot Telegram — Notifikasi Otomatis

### Arsitektur Sistem Notifikasi

```
Alur Notifikasi Telegram:
═════════════════════════

User buat transaksi (POS/SO/PO/Biaya)
        │
        ▼
┌──────────────────────┐
│  views.py            │  ← Setelah form.save() berhasil
│  (pos/penjualan/dll) │
└──────────┬───────────┘
           │ panggil langsung
           ▼
┌──────────────────────┐
│  signals.py          │  ← Format data transaksi ke dict
│  kirim_notifikasi_*  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│  telegram_service.py     │
│  kirim_notifikasi_async()│  ← Thread baru (daemon=True)
│       │                  │     Tidak blokir proses utama!
│       ▼                  │
│  _kirim_notifikasi_sync()│
│       │                  │
│       ├── Load PengaturanTelegram (token, chat_id)
│       ├── Cek toggle aktif/nonaktif
│       ├── Load TemplatePesan sesuai jenis
│       ├── Render template dengan data
│       ▼                  │
│  kirim_pesan_telegram()  │  ← HTTP POST ke api.telegram.org
│       │                  │     Menggunakan urllib (bukan requests)
│       ▼                  │
│  LogNotifikasi.create()  │  ← Catat sukses/gagal
└──────────────────────────┘
```

### 3 Model Automation

```python
# 1. PengaturanTelegram — Singleton (1 record saja)
class PengaturanTelegram(models.Model):
    bot_token = models.CharField(max_length=200)     # Token dari @BotFather
    chat_id = models.CharField(max_length=100)       # Chat ID tujuan
    aktif = models.BooleanField(default=False)       # Master toggle
    # Toggle per jenis transaksi:
    notif_pos = models.BooleanField(default=True)
    notif_sales_order = models.BooleanField(default=True)
    notif_purchase_order = models.BooleanField(default=True)
    notif_biaya = models.BooleanField(default=True)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

# 2. TemplatePesan — Template per jenis transaksi
class TemplatePesan(models.Model):
    JENIS_CHOICES = [
        ('pos', 'Transaksi POS'),
        ('sales_order', 'Sales Order'),
        ('purchase_order', 'Purchase Order'),
        ('biaya', 'Transaksi Biaya'),
    ]
    jenis = models.CharField(max_length=30, choices=JENIS_CHOICES, unique=True)
    nama = models.CharField(max_length=100)
    template_pesan = models.TextField()  # Menggunakan {{variabel}} placeholder
    aktif = models.BooleanField(default=True)

# 3. LogNotifikasi — Riwayat sukses/gagal
class LogNotifikasi(models.Model):
    jenis = models.CharField(max_length=30)
    nomor_referensi = models.CharField(max_length=100)
    pesan = models.TextField()
    status = models.CharField(max_length=10)  # 'sukses' atau 'gagal'
    error_message = models.TextField(null=True)
    dikirim_pada = models.DateTimeField(auto_now_add=True)
```

### Contoh Template Pesan dan Render

```
Template SO (tersimpan di database):
────────────────────────────────────
🛒 *SALES ORDER BARU*
━━━━━━━━━━━━━━━━━
📋 No: {{nomor_so}}
📅 Tanggal: {{tanggal}}
👤 Customer: {{customer}}
🏭 Gudang: {{gudang}}

📦 *Detail Items:*
{{detail_items}}

💰 Subtotal: Rp {{subtotal}}
🏷️ Diskon: Rp {{diskon}}
📊 Pajak: Rp {{pajak}}
💵 *TOTAL: Rp {{total}}*
━━━━━━━━━━━━━━━━━
📌 Status: {{status}}
👤 Dibuat: {{dibuat_oleh}}

Setelah di-render dengan data:
────────────────────────────────────
🛒 *SALES ORDER BARU*
━━━━━━━━━━━━━━━━━
📋 No: SO-20260001
📅 Tanggal: 21/02/2026 15:30
👤 Customer: Toko Maju Jaya
🏭 Gudang: Gudang Utama

📦 *Detail Items:*
  1. Laptop ASUS x2 = Rp 20.000.000
  2. Mouse Logitech x5 = Rp 750.000

💰 Subtotal: Rp 20.750.000
🏷️ Diskon: Rp 0
📊 Pajak: Rp 2.282.500
💵 *TOTAL: Rp 23.032.500*
━━━━━━━━━━━━━━━━━
📌 Status: Draft
👤 Dibuat: admin
```

---

## U. POS (Point of Sale) — Kasir

### Arsitektur POS

```
Halaman POS (Single Page Application-like):
════════════════════════════════════════════

┌──────────────────────────────────────────────────────┐
│  NAVBAR: Pilih Gudang | Cari Produk (AJAX search)    │
├──────────────────────────┬───────────────────────────┤
│                          │                           │
│   GRID PRODUK            │   KERANJANG (Cart)        │
│   ┌──────┐ ┌──────┐     │   ┌─────────────────────┐ │
│   │ 📦   │ │ 📦   │     │   │ Laptop ASUS   x2    │ │
│   │Laptop│ │Mouse │     │   │ Rp 20.000.000       │ │
│   │Stok:5│ │Stok:20│    │   ├─────────────────────┤ │
│   └──────┘ └──────┘     │   │ Mouse Logi    x5    │ │
│   ┌──────┐ ┌──────┐     │   │ Rp 750.000          │ │
│   │ 📦   │ │ 📦   │     │   ├─────────────────────┤ │
│   │Kabel │ │SSD   │     │   │ Subtotal: 20.750.000│ │
│   │Stok:50│ │Stok:8│    │   │ Diskon:   0         │ │
│   └──────┘ └──────┘     │   │ Pajak:    2.282.500 │ │
│                          │   │ TOTAL:   23.032.500 │ │
│  Tab: [Semua][Elektronik]│   ├─────────────────────┤ │
│        [Aksesoris][...]  │   │ [BAYAR & SIMPAN]    │ │
│                          │   └─────────────────────┘ │
└──────────────────────────┴───────────────────────────┘
```

### 4 API Endpoint POS

```python
# apps/pos/views.py — Semua endpoint return JSON

# 1. create_transaction — Buat transaksi + kurangi stok
#    POST /pos/api/create-transaction/
#    Input: { items: [...], gudang_id, nama_customer, metode, diskon, pajak }
#    Proses: atomic transaction (rollback jika error)

# 2. check_stock — Cek stok produk di gudang tertentu
#    GET /pos/api/check-stock/<produk_id>/?gudang_id=1
#    Return: { success, stok, satuan }

# 3. search_products — Autocomplete pencarian produk
#    GET /pos/api/search-products/?q=keyword&gudang_id=1
#    Return: [{ id, nama, harga, stok, gambar }, ...]

# 4. get_stocks_by_gudang — Semua stok per gudang
#    GET /pos/api/get-stocks-by-gudang/?gudang_id=1
#    Return: { produk_id: { jumlah, satuan }, ... }
```

### Alur Transaksi POS (Atomic)

```python
# Simplified flow dari create_transaction():

@login_required
def create_transaction(request):
    with transaction.atomic():  # ← Semua atau tidak sama sekali
        # 1. Parse JSON body
        data = json.loads(request.body)
        
        # 2. Buat header transaksi
        trx = POSTransaction.objects.create(
            nomor_transaksi=generate_nomor(),   # Auto: POS-20260001
            kasir=request.user,
            gudang=gudang,
            nama_customer=data.get('nama_customer', 'Walk-in'),
        )
        
        # 3. Loop setiap item di keranjang
        for item_data in data['items']:
            produk = Produk.objects.get(pk=item_data['id'])
            
            # Buat item transaksi
            POSTransactionItem.objects.create(
                transaksi=trx,
                produk=produk,
                jumlah=item_data['qty'],
                harga=item_data['price'],
                subtotal=item_data['qty'] * item_data['price']
            )
            
            # Kurangi stok (otomatis via signal atau langsung)
            stok = Stok.objects.get(produk=produk, gudang=gudang)
            stok.jumlah -= item_data['qty']
            stok.save()
        
        # 4. Hitung total
        trx.subtotal = sum(i.subtotal for i in trx.items.all())
        trx.total_harga = trx.subtotal - trx.diskon + trx.pajak
        trx.save()
        
        # 5. Kirim notifikasi Telegram
        kirim_notifikasi_pos(trx)
        
        return JsonResponse({
            'success': True,
            'invoice_url': f'/pos/invoice/{trx.pk}/'
        })
```

---

## V. Laporan & Report Views

### Jenis Laporan yang Tersedia

```
Semua laporan bersifat READ-ONLY (tidak ada create/update/delete).
Semua view menggunakan SubModulePermissionMixin untuk akses kontrol.

┌───────────────────┬────────────────────────────────────────────┐
│ Laporan           │ Data yang ditampilkan                      │
├───────────────────┼────────────────────────────────────────────┤
│ Laporan Produk    │ Daftar produk + nilai aset + qty terjual   │
│ Laporan Stok      │ Stok per produk per gudang + stok rendah   │
│ Laporan Penjualan │ SO + POS gabungan + total keuntungan       │
│ Laporan Pembelian │ PO list + total pembelian + pajak          │
│ Laporan Keuangan  │ Pendapatan - Pengeluaran = Laba/Rugi       │
│ Detail Produk     │ Info lengkap + riwayat stok + activity log │
│ Detail SO/PO      │ Header + items + status                    │
└───────────────────┴────────────────────────────────────────────┘
```

### Pattern View Laporan

```python
# apps/laporan/views.py — Contoh LaporanKeuanganView

class LaporanKeuanganView(SubModulePermissionMixin, TemplateView):
    template_name = 'laporan/keuangan.html'
    permission_module = 'laporan'
    permission_sub_module = 'laporan_keuangan'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Filter tanggal dari URL query
        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')
        
        # ═══ PENDAPATAN ═══
        # Dari Sales Order (status != cancelled)
        so_qs = SalesOrder.objects.exclude(status='cancelled')
        if start: so_qs = so_qs.filter(tanggal__date__gte=start)
        if end: so_qs = so_qs.filter(tanggal__date__lte=end)
        total_so = so_qs.aggregate(total=Sum('total_harga'))['total'] or 0
        
        # Dari POS Transaction
        pos_qs = POSTransaction.objects.all()
        if start: pos_qs = pos_qs.filter(dibuat_pada__date__gte=start)
        if end: pos_qs = pos_qs.filter(dibuat_pada__date__lte=end)
        total_pos = pos_qs.aggregate(total=Sum('total_harga'))['total'] or 0
        
        total_pendapatan = total_so + total_pos
        
        # ═══ PENGELUARAN ═══
        # Dari Purchase Order
        po_total = PurchaseOrder.objects.filter(...).aggregate(...)['total'] or 0
        # Dari Transaksi Biaya
        biaya_total = TransaksiBiaya.objects.filter(...).aggregate(...)['total'] or 0
        total_pengeluaran = po_total + biaya_total
        
        # ═══ LABA/RUGI ═══
        laba_rugi = total_pendapatan - total_pengeluaran
        
        context.update({
            'total_pendapatan': total_pendapatan,
            'total_pengeluaran': total_pengeluaran,
            'laba_rugi': laba_rugi,
            'total_so': total_so,
            'total_pos': total_pos,
            # ... data lainnya untuk grafik/tabel
        })
        return context
```

### Summary Cards di Laporan

```html
{# Pattern summary cards yang dipakai di semua halaman laporan #}
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="avatar me-3">
                        <span class="avatar-initial rounded bg-label-success">
                            <i class="ri-money-dollar-circle-line ri-24px"></i>
                        </span>
                    </div>
                    <div>
                        <h4 class="mb-0">Rp {{ total_pendapatan|rupiah }}</h4>
                        <span class="text-muted">Total Pendapatan</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {# Ulangi pola yang sama untuk kartu lainnya #}
</div>
```

---

## Kesimpulan

Dokumen ini mencakup panduan lengkap **dari A sampai Z** tentang cara kerja CRUD, SUBCRUD, dan semua fitur utama di sistem ERP:

| Bagian | Topik | Section |
|--------|-------|---------|
| **Bagian 1** | Membuat modul CRUD baru dari nol | A–M |
| **Bagian 2** | SUBCRUD (Parent-Child + Formset) + Peta modul | N–O |
| **Bagian 3** | Export, Filter, Log, Absensi, Telegram, POS, Laporan | P–V |

**Pola yang konsisten di seluruh ERP:**
1. **Model** → `models.py` (definisi tabel + relasi)
2. **Form** → `forms.py` (validasi + widget Sneat)
3. **View** → `views.py` (CBV + mixin permission)
4. **URL** → `urls.py` (namespace routing)
5. **Template** → `templates/` (Sneat layout + DataTables + AJAX delete)
6. **Permission** → `SubModulePermissionMixin` (RBAC granular)
7. **Notifikasi** → `automation/` (Telegram async thread)
