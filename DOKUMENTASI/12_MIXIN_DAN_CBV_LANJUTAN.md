# 🧩 12 — Mixin, CBV, FBV — Panduan Detail Lengkap

## DAFTAR ISI
- [A. Apa itu Mixin?](#a-apa-itu-mixin)
- [B. Method Resolution Order (MRO)](#b-method-resolution-order-mro)
- [C. Semua Mixin di Project ERP](#c-semua-mixin-di-project-erp)
- [D. Class-Based Views (CBV) — Lengkap](#d-class-based-views-cbv)
- [E. Function-Based Views (FBV) — Perbandingan](#e-function-based-views-fbv)
- [F. CBV vs FBV — Kapan Pakai Mana?](#f-cbv-vs-fbv)
- [G. Lifecycle CBV — Step by Step](#g-lifecycle-cbv)
- [H. Cara Kerja Backend → Frontend (Request-Response)](#h-cara-kerja-backend--frontend)
- [I. Model Django — Panduan Detail](#i-model-django)
- [J. Form Django — Panduan Detail](#j-form-django)

---

## A. Apa itu Mixin?

### Definisi Sederhana:

```
Mixin = POTONGAN FITUR yang bisa DITEMPELKAN ke class lain.

Analogi kehidupan nyata:
┌──────────────────────────────────────────────────────┐
│ Mixin ≈ TOPPING ES KRIM                             │
│                                                      │
│ Es Krim (class dasar):                               │
│   - ListView = Es krim vanilla (bisa list data)     │
│   - CreateView = Es krim coklat (bisa buat data)    │
│                                                      │
│ Topping/Mixin:                                       │
│   - SubModulePermissionMixin = Sprinkle cek akses   │
│   - LoginRequiredMixin = Choco chip cek login       │
│                                                      │
│ Hasil akhir:                                         │
│   class MyView(PermissionMixin, ListView):           │
│   → Es krim vanilla + sprinkle                      │
│   → Bisa list data + cek permission sebelum akses   │
└──────────────────────────────────────────────────────┘
```

### Kenapa Mixin, Bukan Inheritance Biasa?

```python
# ═══ TANPA Mixin — Inheritance Tunggal ═══
# Masalah: Python hanya support 1 parent class langsung

# Cara JELEK: duplikasi kode
class KategoriListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        # Copy-paste kode permission check DI SETIAP VIEW!
        if not has_permission(request.user, 'read', 'produk'):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

class ProdukListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        # Copy-paste LAGI! 
        if not has_permission(request.user, 'read', 'produk'):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

# ═══ DENGAN Mixin — Multiple Inheritance ═══
# Solusi: tulis SEKALI, pakai di SEMUA

class SubModulePermissionMixin:
    """Kode permission check — ditulis 1x saja"""
    def dispatch(self, request, *args, **kwargs):
        if not has_permission(request.user, self.permission_action, self.permission_module):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

# Tinggal TEMPEL ke view manapun:
class KategoriListView(SubModulePermissionMixin, ListView):
    permission_module = 'produk'
    permission_action = 'read'

class ProdukListView(SubModulePermissionMixin, ListView):
    permission_module = 'produk'
    permission_action = 'read'
```

---

## B. Method Resolution Order (MRO)

### Apa itu MRO?

MRO = urutan Python mencari method saat dipanggil di class yang punya banyak parent.

```python
class KategoriListView(SubModulePermissionMixin, ListView):
    ...

# Saat dispatch() dipanggil:
# Python cari dispatch() sesuai urutan MRO:
#
# 1. KategoriListView ← cek di sini dulu
# 2. SubModulePermissionMixin ← KETEMU! Ada dispatch()
#    ↓ dispatch() cek permission
#    ↓ Jika OK → panggil super().dispatch()
# 3. ListView ← super() memanggil dispatch() di sini
#    ↓ Jalankan logic list data
# 4. View ← base class Django
# 5. object ← base class Python
```

### Kenapa Mixin Harus di KIRI?

```python
# ═══ BENAR ═══
class MyView(SubModulePermissionMixin, ListView):  # Mixin di KIRI
# MRO: MyView → SubModulePermissionMixin → ListView → View
# dispatch() dicari dari kiri ke kanan:
#   SubModulePermissionMixin.dispatch() → cek permission DULU
#   super().dispatch() → ListView.dispatch() → tampilkan halaman

# ═══ SALAH ═══
class MyView(ListView, SubModulePermissionMixin):  # Mixin di KANAN
# MRO: MyView → ListView → SubModulePermissionMixin → View
# dispatch() dicari dari kiri ke kanan:
#   ListView.dispatch() → LANGSUNG tampilkan halaman!
#   SubModulePermissionMixin.dispatch() TIDAK PERNAH dipanggil!
#   → Permission check TIDAK AKTIF → BUG KEAMANAN!
```

---

## C. Semua Mixin di Project ERP

Semua mixin didefinisikan di **`apps/core/mixins.py`** (292 baris).

### 1. SubModulePermissionMixin (UTAMA — Paling Sering Dipakai):

```python
class SubModulePermissionMixin:
    """
    Apa: Cek permission modul + sub-modul sebelum view diakses
    Kapan: Di SEMUA view CRUD (list, create, update, delete)
    Jika gagal: Raise PermissionDenied → halaman 403
    """
    permission_module = None       # Wajib: 'produk', 'inventory', dll
    permission_sub_module = None   # Opsional: 'kategori', 'gudang', dll
    permission_action = 'read'     # 'read', 'create', 'write', 'delete'
    
    def dispatch(self, request, *args, **kwargs):
        # 1. Superuser bypass semua cek (langsung masuk)
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # 2. Cek permission:
        #    has_permission(user, 'read', 'produk', 'kategori')
        #    → Cek apakah role user punya akses read di produk.kategori
        if not has_permission(
            request.user,
            self.permission_action,
            self.permission_module,
            self.permission_sub_module
        ):
            raise PermissionDenied("Akses ditolak")
        
        # 3. OK, lanjut ke view
        return super().dispatch(request, *args, **kwargs)
```

**Contoh penggunaan:**

```python
# View LIST — cek permission READ
class KategoriListView(SubModulePermissionMixin, ListView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'read'         # ← Cek akses BACA

# View CREATE — cek permission CREATE
class KategoriCreateView(SubModulePermissionMixin, CreateView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'create'       # ← Cek akses TAMBAH

# View UPDATE — cek permission WRITE
class KategoriUpdateView(SubModulePermissionMixin, UpdateView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'write'        # ← Cek akses EDIT

# View DELETE — cek permission DELETE
class KategoriDeleteView(SubModulePermissionMixin, DeleteView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'delete'       # ← Cek akses HAPUS
```

### 2. Mixin Spesifik per Aksi (Alternatif):

```python
# Cara ringkas — langsung spesifik per aksi:

class ReadPermissionMixin:      # Cek can_view
class CreatePermissionMixin:    # Cek can_create
class UpdatePermissionMixin:    # Cek can_edit (action='write')
class DeletePermissionMixin:    # Cek can_delete

# Pakai:
class MyListView(ReadPermissionMixin, ListView):
    permission_module = 'produk'
    # Tidak perlu set permission_action — sudah otomatis 'read'
```

### 3. Mixin Legacy (Lama):

```python
class AdminOrSuperuserMixin:
    """Hanya admin atau superuser yang boleh akses (cek is_staff)"""
    # Jika ditolak → redirect ke dashboard (bukan 403)

class SuperuserRequiredMixin:
    """Hanya superuser yang boleh akses"""
    # Lebih ketat dari AdminOrSuperuserMixin
```

### Tabel Ringkasan Mixin:

| Mixin | Cek Apa | Jika Ditolak | Digunakan Di |
|-------|---------|--------------|--------------|
| `SubModulePermissionMixin` | RBAC modul+sub | 403 Forbidden | Semua CRUD view |
| `ModulePermissionMixin` | RBAC modul saja | Redirect dashboard | View sederhana |
| `ReadPermissionMixin` | can_view | 403 | ListView |
| `CreatePermissionMixin` | can_create | 403 | CreateView |
| `UpdatePermissionMixin` | can_edit | 403 | UpdateView |
| `DeletePermissionMixin` | can_delete | 403 | DeleteView |
| `AdminOrSuperuserMixin` | is_staff/superuser | Redirect | Legacy views |
| `SuperuserRequiredMixin` | is_superuser | Redirect | Admin panel |

---

## D. Class-Based Views (CBV) — Lengkap

### Apa itu CBV?

```
CBV = View yang dibuat sebagai CLASS Python.
→ Terorganisir, bisa di-inherit, bisa pakai mixin
→ Django menyediakan CBV bawaan untuk operasi umum (CRUD)

Kebalikan dari FBV (Function-Based Views)
→ View yang dibuat sebagai FUNCTION biasa
```

### CBV Bawaan Django yang Dipakai di Project:

| CBV | Kegunaan | Method HTTP | Template Default |
|-----|----------|-------------|-----------------|
| `TemplateView` | Tampilkan template statis | GET | template_name |
| `ListView` | List semua data | GET | model_list.html |
| `DetailView` | Detail 1 data | GET | model_detail.html |
| `CreateView` | Form tambah baru | GET + POST | model_form.html |
| `UpdateView` | Form edit data | GET + POST | model_form.html |
| `DeleteView` | Hapus data | POST/DELETE | model_confirm_delete.html |
| `FormView` | Form custom | GET + POST | template_name |

### ListView — Detail Lengkap:

```python
class ProdukListView(SubModulePermissionMixin, ListView):
    """
    Inheritance chain:
    ProdukListView
      └── SubModulePermissionMixin (cek permission)
          └── ListView (ambil data dari DB)
              └── MultipleObjectMixin (query + pagination)
                  └── ContextMixin (context data)
                      └── TemplateResponseMixin (render template)
                          └── View (dispatch HTTP methods)
    """
    
    # ═══ ATRIBUT WAJIB ═══
    model = Produk                           # Model yang di-query
    template_name = 'produk/produk_list.html'  # Template HTML
    context_object_name = 'produk_list'      # Nama variabel di template
    
    # ═══ ATRIBUT OPSIONAL ═══
    paginate_by = 25                         # 25 per halaman (auto pagination)
    ordering = ['-created_at']               # Urutkan terbaru dulu
    
    # ═══ METHOD YANG BISA DI-OVERRIDE ═══
    
    def get_queryset(self):
        """
        Customize QUERY yang dijalankan.
        Default: self.model.objects.all()
        
        Override untuk: filter, annotate, select_related
        """
        qs = Produk.objects.select_related('kategori').all()
        
        # Contoh: filter berdasarkan parameter URL
        kategori = self.request.GET.get('kategori')
        if kategori:
            qs = qs.filter(kategori_id=kategori)
        
        return qs
    
    def get_context_data(self, **kwargs):
        """
        Tambahkan DATA EXTRA ke context template.
        
        WAJIB panggil TemplateLayout.init() untuk Sneat!
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Tambah data statistik
        context['total_produk'] = self.get_queryset().count()
        context['total_stok'] = self.get_queryset().aggregate(Sum('stok'))['stok__sum']
        context['kategori_list'] = Kategori.objects.all()  # Untuk filter dropdown
        
        return context
```

### CreateView — Detail Lengkap:

```python
class ProdukCreateView(SubModulePermissionMixin, CreateView):
    """Halaman form TAMBAH produk baru."""
    
    model = Produk
    form_class = ProdukForm
    template_name = 'produk/produk_form.html'
    success_url = reverse_lazy('produk:list')
    
    # Permission:
    permission_module = 'produk'
    permission_sub_module = 'daftar_produk'
    permission_action = 'create'
    
    def get_context_data(self, **kwargs):
        """Tambah konteks untuk template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = 'Tambah Produk'
        context['submit_text'] = 'Simpan'
        return context
    
    def form_valid(self, form):
        """
        Dipanggil saat form VALID (semua validasi lolos).
        
        Lifecycle:
        1. User isi form → klik Submit
        2. Browser POST data ke server
        3. Django cek CSRF token
        4. Django construct ProdukForm dengan POST data
        5. form.is_valid() → True
        6. form_valid() dipanggil ← KITA DI SINI
        7. Kita bisa manipulasi data SEBELUM save
        8. super().form_valid() → form.save() → INSERT ke DB → redirect
        """
        # Set field yang tidak ada di form:
        form.instance.dibuat_oleh = self.request.user
        
        # Flash message
        messages.success(self.request, f'Produk "{form.instance.nama}" berhasil ditambahkan!')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Dipanggil saat form TIDAK VALID (ada error validasi).
        
        Lifecycle:
        1. User isi form → klik Submit
        2. form.is_valid() → False
        3. form_invalid() dipanggil ← KITA DI SINI
        4. Re-render template DENGAN error messages
        """
        messages.error(self.request, 'Data gagal disimpan. Periksa form di bawah.')
        return super().form_invalid(form)
```

### UpdateView — Detail Lengkap:

```python
class ProdukUpdateView(SubModulePermissionMixin, UpdateView):
    """
    Halaman form EDIT produk.
    
    Perbedaan dengan CreateView:
    - Otomatis ambil data existing berdasarkan pk di URL
    - Form auto-filled dengan data yang ada
    - Save = UPDATE (bukan INSERT)
    """
    
    model = Produk
    form_class = ProdukForm
    template_name = 'produk/produk_form.html'  # Template SAMA dengan create!
    success_url = reverse_lazy('produk:list')
    
    permission_action = 'write'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['title'] = f'Edit Produk: {self.object.nama}'
        # self.object = instance Produk yang sedang di-edit
        context['submit_text'] = 'Update'
        return context
```

### DeleteView — AJAX Pattern (Project Kita):

```python
class ProdukDeleteView(SubModulePermissionMixin, DeleteView):
    """
    Hapus produk via AJAX (tidak render template HTML).
    
    Di project ini, delete TIDAK pakai template confirm_delete.html.
    Konfirmasi hapus ditangani di FRONTEND (modal JavaScript).
    Backend hanya terima request DELETE → return JSON.
    """
    model = Produk
    permission_action = 'delete'
    
    def delete(self, request, *args, **kwargs):
        """Override delete untuk return JSON, bukan redirect."""
        try:
            obj = self.get_object()
            nama = str(obj)
            obj.delete()
            return JsonResponse({
                'success': True,
                'message': f'{nama} berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
```

---

## E. Function-Based Views (FBV) — Perbandingan

### FBV = View sebagai FUNCTION biasa:

```python
# ═══ FBV: List Produk ═══
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required                    # Decorator: harus login dulu
def produk_list(request):
    """Function view untuk list produk."""
    
    produk = Produk.objects.select_related('kategori').all()
    
    # Filter dari GET parameter
    kategori = request.GET.get('kategori')
    if kategori:
        produk = produk.filter(kategori_id=kategori)
    
    context = {
        'produk_list': produk,
        'total_produk': produk.count(),
        'kategori_list': Kategori.objects.all(),
    }
    return render(request, 'produk/produk_list.html', context)


# ═══ FBV: Create + Update (Gabung) ═══
@login_required
def produk_form(request, pk=None):
    """
    Function view untuk create DAN update.
    pk=None → create baru
    pk=integer → edit existing
    """
    
    # Ambil instance jika edit, None jika create
    instance = None
    if pk:
        instance = get_object_or_404(Produk, pk=pk)
    
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            produk = form.save(commit=False)
            if not pk:  # Create baru
                produk.dibuat_oleh = request.user
            produk.save()
            messages.success(request, 'Produk berhasil disimpan!')
            return redirect('produk:list')
        else:
            messages.error(request, 'Data tidak valid!')
    else:
        # GET request: tampilkan form kosong / terisi
        form = ProdukForm(instance=instance)
    
    context = {
        'form': form,
        'title': 'Edit Produk' if pk else 'Tambah Produk',
    }
    return render(request, 'produk/produk_form.html', context)


# ═══ FBV: Delete via AJAX ═══
@login_required
def produk_delete(request, pk):
    """Delete produk via AJAX."""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        produk = get_object_or_404(Produk, pk=pk)
        nama = produk.nama
        produk.delete()
        return JsonResponse({'success': True, 'message': f'{nama} dihapus!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
```

### URL FBV:

```python
# urls.py untuk FBV
urlpatterns = [
    path('list/', produk_list, name='list'),
    path('add/', produk_form, name='add'),
    path('<int:pk>/edit/', produk_form, name='edit'),  # pk diteruskan
    path('<int:pk>/delete/', produk_delete, name='delete'),
]
# Perhatikan: FBV langsung pakai nama_function, bukan .as_view()
```

---

## F. CBV vs FBV — Kapan Pakai Mana?

| Aspek | CBV | FBV |
|-------|-----|-----|
| **Kode** | Lebih sedikit (inheritance) | Lebih banyak (eksplisit) |
| **Mixin** | ✅ Bisa pakai mixin | ❌ Harus decorator |
| **Reuse** | ✅ Tinggi (override method) | ❌ Rendah (copy-paste) |
| **Baca kode** | Sulit (banyak "magic") | Mudah (langsung terlihat) |
| **Logic kompleks** | Override method yang tepat | Tulis semuanya manual |
| **Kasus sederhana** | Overkill (terlalu banyak class) | Ideal |
| **Permission** | Mixin | Decorator |

### Di Project ERP Ini:
- **95% menggunakan CBV** → karena CRUD repetitif, mixin permission efektif
- **5% FBV** → untuk endpoint AJAX sederhana, edge cases

---

## G. Lifecycle CBV — Step by Step

### ListView Lifecycle:

```
User mengetik URL: /produk/list/ dan tekan Enter

1. Browser kirim HTTP GET ke server
2. Django URL resolver cocokkan: path('list/', ProdukListView.as_view())
3. as_view() membuat instance view
4. dispatch(request) dipanggil
   ↓ SubModulePermissionMixin.dispatch() → Cek permission
   ↓ Jika OK → super().dispatch() → ListView.dispatch()
5. dispatch() tentukan method → GET → panggil get()
6. get() dipanggil:
   a. get_queryset() → Produk.objects.all()
   b. get_context_data() → {'produk_list': queryset, ...}
   c. TemplateLayout.init() → Tambah data sidebar, navbar
   d. render_to_response(context) → Render template ke HTML
7. HTML dikirim ke browser
8. Browser render halaman
```

### CreateView Lifecycle (POST):

```
User isi form dan klik "Simpan"

1. Browser kirim HTTP POST dengan data form + CSRF token
2. URL resolver cocokkan → ProdukCreateView.as_view()
3. dispatch() → Mixin cek permission → OK
4. dispatch() → method = POST → panggil post()
5. post() dipanggil:
   a. get_form_class() → ProdukForm
   b. get_form() → ProdukForm(request.POST, request.FILES)
   c. form.is_valid()
      → True → form_valid(form) → form.save() → redirect
      → False → form_invalid(form) → re-render form + errors
6. Jika valid: redirect ke success_url → /produk/list/
7. Browser GET ke /produk/list/ → ListView berjalan
```

---

## H. Cara Kerja Backend → Frontend (Request-Response)

### Diagram Lengkap:

```
                           FRONTEND                    BACKEND
                        (Browser/HTML)              (Django/Python)
                              │                          │
                              │                          │
  1. User klik link    ───────┤                          │
     /produk/list/            │                          │
                              │──── HTTP GET ──────────→ │
                              │                          │
                              │                     2. urls.py:
                              │                        path('list/', 
                              │                         ProdukListView.as_view())
                              │                          │
                              │                     3. Mixin: cek permission ✅
                              │                          │
                              │                     4. views.py:
                              │                        get_queryset()
                              │                        → DB query: SELECT *
                              │                          │
                              │                     5. get_context_data()
                              │                        → {'produk_list': [..]}
                              │                          │
                              │                     6. Template engine:
                              │                        Render produk_list.html
                              │                        {% for p in produk_list %}
                              │                          │
                              │←── HTML Response ────────│
                              │                          │
  7. Browser render    ───────┤                          │
     HTML → tampilkan         │                          │
     tabel produk             │                          │
                              │                          │
  8. DataTables init   ───────┤                          │
     JavaScript               │                          │
     Sort, Search, etc        │                          │
                              │                          │
  9. User klik Hapus   ──────┤                          │
                              │──── AJAX DELETE ────────→│
                              │     /produk/5/delete/    │
                              │     X-CSRFToken: abc     │
                              │                     10. DeleteView:
                              │                         produk.delete()
                              │                          │
                              │←── JSON Response ────────│
                              │    {success: true}       │
                              │                          │
  11. JavaScript:      ───────┤                          │
      location.reload()       │                          │
```

### Data dari Python → HTML Template:

```python
# ═══ DI VIEWS.PY (Python) ═══
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['total_produk'] = 150        # Integer
    context['nama_toko'] = 'Toko ABC'    # String
    context['produk_list'] = queryset    # QuerySet (list of objects)
    context['form'] = ProdukForm()       # Form instance
    context['is_admin'] = True           # Boolean
    return context
```

```html
{# ═══ DI TEMPLATE (HTML) — Cara akses data dari Python ═══ #}

{# Variabel biasa: #}
<h4>Total: {{ total_produk }}</h4>     {# Output: Total: 150 #}
<h4>Toko: {{ nama_toko }}</h4>          {# Output: Toko: Toko ABC #}

{# Loop (for): #}
{% for p in produk_list %}
    <tr>
        <td>{{ p.nama }}</td>           {# Akses field model #}
        <td>{{ p.kategori.nama }}</td>  {# Akses relasi FK #}
        <td>{{ p.harga_jual|floatformat:0 }}</td>  {# Filter format #}
    </tr>
{% empty %}
    <tr><td colspan="3">Tidak ada data</td></tr>
{% endfor %}

{# Kondisi (if): #}
{% if is_admin %}
    <button class="btn btn-danger">Hapus</button>
{% else %}
    {# Tombol hapus tidak ditampilkan #}
{% endif %}

{# Form: #}
<form method="POST">
    {% csrf_token %}                  {# Token keamanan WAJIB #}
    {{ form.nama }}                   {# Render input field #}
    {{ form.nama.errors }}            {# Render error message #}
</form>
```

### Data dari Python → JavaScript (Charts):

```python
# views.py — Kirim data untuk chart
context['sales_data'] = [150000, 200000, 180000]  # List angka
context['sales_labels'] = ['1 Jan', '2 Jan', '3 Jan']
```

```html
{# Template — Bridge data Python → JavaScript #}

{# Cara 1: json_script (AMAN — recommended) #}
{{ sales_data|json_script:"sales-data" }}
{# Output HTML: <script id="sales-data" type="application/json">[150000,200000,180000]</script> #}

<script>
// JavaScript ambil data:
const data = JSON.parse(document.getElementById('sales-data').textContent);
// data = [150000, 200000, 180000]
</script>

{# Cara 2: Langsung di template (HATI-HATI — rentan XSS) #}
<script>
const labels = [{% for l in sales_labels %}'{{ l }}'{% if not forloop.last %},{% endif %}{% endfor %}];
// labels = ['1 Jan', '2 Jan', '3 Jan']
</script>
```

---

## I. Model Django — Panduan Detail

### Tipe Field (Kolom Database):

| Django Field | SQL | Contoh | Keterangan |
|-------------|-----|--------|------------|
| `CharField(max_length=N)` | VARCHAR(N) | Nama, SKU | Teks pendek, wajib max_length |
| `TextField()` | TEXT | Deskripsi | Teks panjang, tanpa max_length |
| `IntegerField()` | INTEGER | Stok, qty | Bilangan bulat |
| `DecimalField(max_digits, decimal_places)` | DECIMAL | Harga | Angka desimal presisi |
| `FloatField()` | FLOAT | Persentase | Angka desimal (kurang presisi) |
| `BooleanField()` | BOOLEAN | Status aktif | True/False |
| `DateField()` | DATE | Tanggal lahir | Tanggal saja |
| `DateTimeField()` | DATETIME | Created at | Tanggal + waktu |
| `EmailField()` | VARCHAR(254) | Email | Validasi format email |
| `URLField()` | VARCHAR(200) | Website | Validasi format URL |
| `FileField()` | VARCHAR(100) | Lampiran | Path file upload |
| `ImageField()` | VARCHAR(100) | Foto | Path gambar (validasi image) |
| `JSONField()` | JSON | Metadata | Data JSON bebas |
| `ForeignKey()` | INTEGER + FK | Kategori | Relasi ke tabel lain (1:N) |
| `ManyToManyField()` | Tabel pivot | Tags | Relasi N:N |
| `OneToOneField()` | INTEGER + FK UNIQUE | Profil | Relasi 1:1 |

### Opsi Field yang Penting:

```python
class Produk(models.Model):
    nama = models.CharField(
        max_length=200,           # Maks karakter
        unique=True,              # Tidak boleh duplikat
        verbose_name='Nama Produk',  # Label di form/admin
        help_text='Nama unik produk',  # Teks bantuan
        db_index=True,            # Index database (pencarian cepat)
    )
    
    deskripsi = models.TextField(
        blank=True,               # Boleh KOSONG di FORM (tidak wajib)
        default='',               # Nilai default di DATABASE
    )
    # blank vs null:
    # blank=True  → Form boleh kosong (validasi)
    # null=True   → Database boleh NULL (storage)
    # Untuk CharField/TextField: gunakan blank=True, JANGAN null=True
    # Untuk ForeignKey/DateField: bisa null=True + blank=True
    
    harga = models.DecimalField(
        max_digits=15,            # Total digit (termasuk desimal)
        decimal_places=2,         # Digit setelah koma
        default=0,
    )
    # Contoh valid: 9999999999999.99 (13 digit + 2 desimal)
    
    kategori = models.ForeignKey(
        'Kategori',               # String reference (jika model belum didefinisikan)
        on_delete=models.CASCADE, # ← APA YANG TERJADI jika parent DIHAPUS
        # CASCADE = ikut terhapus
        # PROTECT = error (tidak bisa hapus parent)
        # SET_NULL = set ke NULL (perlu null=True)
        # SET_DEFAULT = set ke default value
        related_name='produk_set',  # Akses balik: kategori.produk_set.all()
        null=True,
        blank=True,
    )
    
    gambar = models.ImageField(
        upload_to='produk/',      # Disimpan di MEDIA_ROOT/produk/
        null=True,
        blank=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)  # Otomatis saat CREATE
    updated_at = models.DateTimeField(auto_now=True)      # Otomatis saat SAVE
```

### Method dan Property Model:

```python
class Produk(models.Model):
    # ... fields ...
    
    class Meta:
        ordering = ['-created_at']         # Default sort: terbaru dulu
        verbose_name = 'Produk'
        verbose_name_plural = 'Produk'
        indexes = [
            models.Index(fields=['nama']),  # Index untuk query cepat
        ]
    
    def __str__(self):
        """String representation — tampil di dropdown, admin, dll."""
        return self.nama
    
    @property
    def total_nilai(self):
        """Property (bukan field) — dihitung, bukan disimpan di DB."""
        return self.harga * self.stok
    # Akses: produk.total_nilai (TANPA parenthesis)
    # Di template: {{ produk.total_nilai }}
    
    def get_absolute_url(self):
        """URL detail produk — convention Django."""
        from django.urls import reverse
        return reverse('produk:detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        """Override save untuk logic custom sebelum/sesudah simpan."""
        # Sebelum save:
        self.nama = self.nama.strip().upper()  # Uppercase nama
        
        # Save ke database:
        super().save(*args, **kwargs)
        
        # Sesudah save:
        # Contoh: update total stok gudang
```

---

## J. Form Django — Panduan Detail

### ModelForm vs Form:

```python
# ═══ ModelForm — OTOMATIS dari Model ═══
# Gunakan ini untuk CRUD standar (95% kasus)

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama', 'sku', 'harga', 'stok', 'kategori']
        # Otomatis:
        # - Field type sesuai model (CharField → TextInput)
        # - Validasi max_length, required, unique
        # - form.save() langsung simpan ke DB
    
    def clean_nama(self):
        """Validasi CUSTOM untuk field 'nama'."""
        nama = self.cleaned_data.get('nama')
        if len(nama) < 3:
            raise forms.ValidationError('Nama minimal 3 karakter')
        return nama
    
    def clean(self):
        """Validasi CROSS-FIELD (melibatkan lebih dari 1 field)."""
        cleaned = super().clean()
        harga_beli = cleaned.get('harga_beli')
        harga_jual = cleaned.get('harga_jual')
        if harga_jual and harga_beli and harga_jual < harga_beli:
            raise forms.ValidationError('Harga jual tidak boleh < harga beli')
        return cleaned


# ═══ Form Biasa — MANUAL ═══
# Gunakan untuk form yang TIDAK terkait model

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))
    remember_me = forms.BooleanField(required=False)
    # required=False → checkbox tidak wajib dicentang
```

### Widget — Tampilan Field di HTML:

```python
class ProdukForm(forms.ModelForm):
    class Meta:
        widgets = {
            # TextInput → <input type="text">
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama produk',
                'autofocus': True,
            }),
            
            # NumberInput → <input type="number">
            'harga': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '100',
            }),
            
            # Select → <select><option>
            'kategori': forms.Select(attrs={
                'class': 'form-select',  # Sneat dropdown
            }),
            
            # Textarea → <textarea>
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
            }),
            
            # CheckboxInput → <input type="checkbox">
            'aktif': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            
            # DateInput → <input type="date">
            'tanggal': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            
            # FileInput → <input type="file">
            'gambar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            
            # HiddenInput → <input type="hidden">
            'dibuat_oleh': forms.HiddenInput(),
        }
```

### Menampilkan Form di Template:

```html
{# ═══ CARA 1: Render manual per field (RECOMMENDED) ═══ #}
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    
    <div class="row g-3">
        <div class="col-md-6">
            <label class="form-label" for="{{ form.nama.id_for_label }}">
                {{ form.nama.label }} 
                {% if form.nama.field.required %}<span class="text-danger">*</span>{% endif %}
            </label>
            {{ form.nama }}
            {# Output: <input type="text" class="form-control" name="nama" ...> #}
            
            {% if form.nama.errors %}
            <div class="text-danger small mt-1">
                {{ form.nama.errors.0 }}
            </div>
            {% endif %}
            
            {% if form.nama.help_text %}
            <div class="form-text">{{ form.nama.help_text }}</div>
            {% endif %}
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary">Simpan</button>
</form>

{# enctype="multipart/form-data" → WAJIB jika ada file upload (ImageField) #}


{# ═══ CARA 2: Loop otomatis (cepat tapi kurang kontrol layout) ═══ #}
<form method="POST">
    {% csrf_token %}
    {% for field in form %}
    <div class="mb-3">
        <label class="form-label">{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}
        <div class="text-danger">{{ field.errors.0 }}</div>
        {% endif %}
    </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Simpan</button>
</form>
```

---

*Lanjut ke [13_API_DAN_AJAX.md](13_API_DAN_AJAX.md) →*
