# 📝 06 — Form & Validasi — Dokumentasi Lengkap & Detail

## DAFTAR ISI
- [A. Apa itu Django Form?](#a-apa-itu-django-form)
- [B. Jenis-Jenis Form Django](#b-jenis-jenis-form-django)
- [C. ModelForm — Anatomi Lengkap](#c-modelform--anatomi-lengkap)
- [D. Semua Jenis Widget](#d-semua-jenis-widget)
- [E. Custom Validasi — 3 Level](#e-custom-validasi--3-level)
- [F. Formset & InlineFormSet](#f-formset--inlineformset)
- [G. Form di View (CBV) — Alur Lengkap](#g-form-di-view-cbv--alur-lengkap)
- [H. Render Form di Template](#h-render-form-di-template)
- [I. File & Image Upload](#i-file--image-upload)
- [J. AJAX Form Submit](#j-ajax-form-submit)
- [K. Studi Kasus: Semua Form di ERP](#k-studi-kasus-semua-form-di-erp)
- [L. Kesalahan Umum & Best Practice](#l-kesalahan-umum--best-practice)

---

## A. Apa itu Django Form?

### Fungsi Utama
Django Form = **"penjaga gerbang"** antara data dari user (browser) dan database.

```
USER (Browser)                    SERVER (Django)                  DATABASE
┌──────────┐    HTTP POST     ┌─────────────────┐    SQL       ┌──────────┐
│ Form HTML │ ──────────────► │  Django Form     │ ──────────► │  Tabel   │
│           │                 │  ┌─────────────┐ │             │          │
│ nama: ... │                 │  │ Validasi    │ │             │  INSERT  │
│ harga: .. │                 │  │ Sanitasi    │ │             │  UPDATE  │
│ gambar: . │                 │  │ Konversi    │ │             │          │
└──────────┘                  │  └─────────────┘ │             └──────────┘
                              └─────────────────┘
```

### Kenapa File forms.py Penting?

| Tanpa forms.py | Dengan forms.py |
|----------------|-----------------|
| Parsing POST manual | Otomatis dari model |
| Validasi tulis sendiri | Validasi bawaan + custom |
| Rawan SQL injection | Aman otomatis |
| Widget HTML manual | Widget otomatis + CSS |
| Error handling manual | Error otomatis per field |

### Kapan Digunakan?
- **Setiap halaman yang menerima input user** (Create, Update)
- **Import data** (file upload + parsing)
- **Filter/search** (form GET untuk filtering)
- **Login, Register** (AuthenticationForm)
- **Settings/Pengaturan** (form konfigurasi)

### Masalah Tanpa Form:
```python
# ❌ TANPA Form — harus parsing manual (BAHAYA!)
def produk_create(request):
    nama = request.POST.get('nama')        # Bisa kosong
    harga = request.POST.get('harga')      # Bisa string "abc"!
    # Tidak ada validasi → rawan error & SQL injection
    Produk.objects.create(nama=nama, harga_jual=harga)  # ERROR!
```

### Solusi Django Form:
```python
# ✅ DENGAN Form — validasi otomatis, aman
class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama', 'harga_jual']

def produk_create(request):
    form = ProdukForm(request.POST)
    if form.is_valid():        # Semua validasi dicek otomatis!
        form.save()             # Aman → INSERT INTO produk
    else:
        print(form.errors)      # {'harga_jual': ['Enter a number.']}
```

---

## B. Jenis-Jenis Form Django

### 1. `forms.Form` — Form Manual (Tanpa Model)

**Kapan pakai:** Form yang TIDAK terhubung ke database (login, search, filter, generate).

```python
from django import forms

class LoginForm(forms.Form):
    """Form login — tidak ada model, hanya validasi input."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(required=False)
```

```python
# Contoh nyata: Form generate penggajian bulanan (apps/hr/forms.py)
class GeneratePenggajianForm(forms.Form):
    """Form untuk generate penggajian — tidak simpan ke DB langsung."""
    periode_bulan = forms.ChoiceField(
        choices=[
            (1, 'Januari'), (2, 'Februari'), (3, 'Maret'),
            (4, 'April'), (5, 'Mei'), (6, 'Juni'),
            (7, 'Juli'), (8, 'Agustus'), (9, 'September'),
            (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    periode_tahun = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tunjangan_makan = forms.DecimalField(
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '500000'
        })
    )
```

### 2. `forms.ModelForm` — Form dari Model (Paling Umum!)

**Kapan pakai:** Form yang SIMPAN/EDIT data ke database. **90% form di project ini.**

```python
from django import forms
from apps.produk.models import Produk

class ProdukForm(forms.ModelForm):
    """Form otomatis dari Model Produk."""
    class Meta:
        model = Produk          # Basis model
        fields = ['nama', 'harga_jual']  # Field yang ditampilkan
    # form.save() → langsung INSERT/UPDATE ke tabel produk_produk
```

**Perbedaan Form vs ModelForm:**

| Aspek | `forms.Form` | `forms.ModelForm` |
|-------|-------------|-------------------|
| Basis | Field manual | Field dari Model |
| `save()` | ❌ Tidak ada | ✅ Simpan ke DB |
| Validasi | Manual semua | Otomatis dari model |
| Kapan pakai | Login, filter, generate | CRUD database |
| Contoh di ERP | GeneratePenggajianForm | ProdukForm, SupplierForm |

### 3. `BaseInlineFormSet` — Kumpulan Form Child (Parent-Child)

**Kapan pakai:** Form yang mengelola **banyak child records** sekaligus, seperti:
- PurchaseOrder → PurchaseOrderItem (banyak item per PO)
- TransferStok → TransferStokItem (banyak produk per transfer)
- SalesOrder → SalesOrderItem (banyak item per SO)

```python
from django.forms import inlineformset_factory

# ═══ CONTOH NYATA: apps/inventory/forms.py ═══
TransferStokItemFormSet = inlineformset_factory(
    TransferStok,            # Parent model
    TransferStokItem,        # Child model
    form=TransferStokItemForm,  # Form per-item
    extra=0,                 # 0 form kosong (user klik "Tambah")
    can_delete=True,         # User bisa hapus item
    min_num=1,               # Minimal 1 item
    validate_min=True,       # Enforce minimum
)

# ═══ CONTOH NYATA: apps/pembelian/forms.py ═══
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,           # Parent model
    PurchaseOrderItem,       # Child model
    fields=['produk', 'jumlah', 'harga_satuan', 'catatan'],
    extra=1,                 # 1 form kosong untuk tambah
    can_delete=True,         # Bisa hapus item
    widgets={
        'produk': forms.Select(attrs={'class': 'form-select select2-item'}),
        'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)
```

**Visualisasi Parent-Child Form:**
```
┌─────────────────────────────────────────┐
│ PURCHASE ORDER FORM (Parent)            │
│ ┌──────────────┐ ┌──────────────┐       │
│ │ Supplier ▼   │ │ Gudang ▼     │       │
│ └──────────────┘ └──────────────┘       │
│ ┌──────────────┐ ┌──────────────┐       │
│ │ Tanggal      │ │ Status ▼     │       │
│ └──────────────┘ └──────────────┘       │
│                                         │
│ ═══ ITEMS FORMSET (Children) ═══        │
│ ┌──────────┬────────┬────────┬───────┐  │
│ │ Produk ▼ │ Jumlah │ Harga  │ Hapus │  │
│ ├──────────┼────────┼────────┼───────┤  │
│ │ Beras    │ 100    │ 12000  │  🗑   │  │
│ │ Gula     │ 50     │ 15000  │  🗑   │  │
│ │ [Kosong] │        │        │       │  │ ← extra=1
│ └──────────┴────────┴────────┴───────┘  │
│ [+ Tambah Item]                         │
│                                         │
│ [💾 Simpan PO]                          │
└─────────────────────────────────────────┘
```

---

## C. ModelForm — Anatomi Lengkap

### Class Meta — Semua Opsi Konfigurasi

```python
# ═══ CONTOH LENGKAP: apps/produk/forms.py ═══
class ProdukForm(forms.ModelForm):
    """
    Form untuk menambah dan mengedit produk.
    Menggunakan ModelForm → field otomatis dari model Produk.
    """

    class Meta:
        # ─── 1. MODEL (WAJIB) ───
        model = Produk
        # Form ini berdasarkan model Produk
        # Django membaca SEMUA field dari model ini

        # ─── 2. FIELDS (WAJIB — pilih salah satu) ───
        fields = ['sku', 'barcode', 'nama', 'kategori', 'satuan',
                  'cabang', 'harga_beli', 'harga_jual', 'deskripsi',
                  'gambar', 'aktif']
        # Opsi lain:
        # fields = '__all__'           # Semua field (TIDAK DISARANKAN!)
        # exclude = ['dibuat_pada']    # Semua KECUALI yang di-exclude

        # ─── 3. WIDGETS (opsional) ───
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',      # CSS Bootstrap
                'placeholder': 'Nama Produk', # Teks hint
                'id': 'productName',           # ID untuk JavaScript
                'required': True               # HTML5 required
            }),
            'kategori': forms.Select(attrs={
                'class': 'select2 form-select form-select-lg',
                'data-allow-clear': 'true'     # Select2 clear button
            }),
            'harga_beli': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',                    # Minimal 0
                'step': '0.01'                 # Desimal 2 digit
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4'                    # Tinggi 4 baris
            }),
            'gambar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'            # Hanya file gambar
            }),
            'aktif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        # ─── 4. LABELS (opsional) ───
        labels = {
            'gudang_asal': 'Dari Gudang',
            'gudang_tujuan': 'Ke Gudang',
            'catatan': 'Catatan',
        }
        # Alternatif: set di __init__ (lebih fleksibel)

        # ─── 5. HELP_TEXTS (opsional) ───
        help_texts = {
            'sku': 'Kode unik produk. Kosongkan untuk auto-generate.',
            'barcode': 'Scan atau ketik barcode produk.',
        }

        # ─── 6. ERROR_MESSAGES (opsional) ───
        error_messages = {
            'nama': {
                'required': 'Nama produk wajib diisi!',
                'max_length': 'Nama produk maksimal 200 karakter.',
            },
        }
```

### Method `__init__` — Kustomisasi Dinamis

```python
def __init__(self, *args, **kwargs):
    """
    Constructor — dipanggil saat form dibuat.

    Kapan override __init__?
    - Mengubah label/required secara dinamis
    - Filter queryset dropdown berdasarkan kondisi
    - Menambah CSS class berdasarkan context
    """
    super().__init__(*args, **kwargs)
    # ↑ WAJIB panggil parent dulu!

    # ═══ SET REQUIRED ═══
    self.fields['sku'].required = False       # Auto-generate
    self.fields['barcode'].required = False
    self.fields['gambar'].required = False

    # ═══ SET LABEL (Bahasa Indonesia) ═══
    self.fields['nama'].label = 'Nama Produk'
    self.fields['harga_beli'].label = 'Harga Beli'
    self.fields['harga_jual'].label = 'Harga Jual'

    # ═══ FILTER QUERYSET (hanya data aktif) ═══
    # Contoh dari PurchaseOrderForm:
    self.fields['supplier'].queryset = Supplier.objects.filter(aktif=True)
    self.fields['gudang'].queryset = Gudang.objects.filter(aktif=True)

    # ═══ SET EMPTY LABEL (placeholder dropdown) ═══
    self.fields['supplier'].empty_label = 'Pilih Supplier'
    self.fields['gudang'].empty_label = 'Pilih Gudang'

    # ═══ FORMAT TANGGAL EDIT (dari PurchaseOrderForm) ═══
    if self.instance and self.instance.pk and self.instance.tanggal:
        from django.utils import timezone
        local_time = timezone.localtime(self.instance.tanggal)
        self.initial['tanggal'] = local_time.strftime('%Y-%m-%dT%H:%M')
```

---

## D. Semua Jenis Widget

### Apa itu Widget?
Widget = **cara field form dirender menjadi HTML**. Setiap field model punya widget DEFAULT, tapi bisa di-override.

### Mapping Model Field → Widget Default → HTML Output:

| Model Field | Widget Default | HTML Output |
|-------------|---------------|-------------|
| `CharField` | `TextInput` | `<input type="text">` |
| `TextField` | `Textarea` | `<textarea>` |
| `IntegerField` | `NumberInput` | `<input type="number">` |
| `DecimalField` | `NumberInput` | `<input type="number">` |
| `BooleanField` | `CheckboxInput` | `<input type="checkbox">` |
| `DateField` | `DateInput` | `<input type="text">` |
| `DateTimeField` | `DateTimeInput` | `<input type="text">` |
| `EmailField` | `EmailInput` | `<input type="email">` |
| `FileField` | `FileInput` | `<input type="file">` |
| `ImageField` | `FileInput` | `<input type="file">` |
| `ForeignKey` | `Select` | `<select>` |
| `ChoiceField` | `Select` | `<select>` |

### Widget yang Digunakan di Project ERP:

#### 1. TextInput — Input Teks Pendek
```python
'nama': forms.TextInput(attrs={
    'class': 'form-control',           # Bootstrap styling
    'placeholder': 'Nama Produk',      # Hint text
    'id': 'productName',               # ID untuk JavaScript
    'required': True,                  # HTML5 required
    'maxlength': '200',                # Max karakter
    'autocomplete': 'off',             # Matikan autocomplete browser
})
# Output HTML:
# <input type="text" name="nama" class="form-control"
#        placeholder="Nama Produk" id="productName" required maxlength="200">
```

#### 2. NumberInput — Input Angka
```python
'harga_beli': forms.NumberInput(attrs={
    'class': 'form-control',
    'min': '0',           # Tidak boleh negatif
    'step': '0.01',       # Desimal 2 digit (10.50, 100.00)
    'placeholder': '0',
})
# Output: <input type="number" min="0" step="0.01">
```

#### 3. Select — Dropdown (ForeignKey)
```python
'kategori': forms.Select(attrs={
    'class': 'select2 form-select form-select-lg',
    # 'select2' → Plugin Select2 (searchable dropdown)
    # 'form-select' → Bootstrap dropdown styling
    # 'form-select-lg' → Ukuran besar
    'data-allow-clear': 'true',   # Select2: bisa kosongkan pilihan
})
# Output: <select class="select2 form-select form-select-lg">
#   <option value="">---------</option>
#   <option value="1">Makanan</option>
#   <option value="2">Minuman</option>
# </select>
```

#### 4. Textarea — Input Teks Panjang
```python
'deskripsi': forms.Textarea(attrs={
    'class': 'form-control h-px-100',   # h-px-100 = custom height
    'rows': 4,                          # Tinggi 4 baris
    'placeholder': 'Deskripsi produk...',
})
# Output: <textarea rows="4" class="form-control">...</textarea>
```

#### 5. DateInput & DateTimeInput — Tanggal
```python
# DateInput — hanya tanggal (apps/biaya/forms.py)
'tanggal': forms.DateInput(attrs={
    'class': 'form-control',
    'type': 'date',        # HTML5 date picker
})
# Output: <input type="date" class="form-control">

# DateTimeInput — tanggal + waktu (apps/pembelian/forms.py)
tanggal = forms.DateTimeField(
    widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local',   # HTML5 datetime picker
        'class': 'form-control',
    }),
    label='Tanggal PO',
    required=False,
)
# Output: <input type="datetime-local" class="form-control">
```

#### 6. TimeInput — Waktu (apps/hr/forms.py)
```python
'jam_masuk': forms.TimeInput(attrs={
    'class': 'form-control',
    'type': 'time',        # HTML5 time picker
})
# Output: <input type="time" class="form-control">
```

#### 7. FileInput — Upload File
```python
'gambar': forms.FileInput(attrs={
    'class': 'form-control',
    'accept': 'image/*',   # Hanya gambar (jpg, png, gif, webp)
})
# Output: <input type="file" accept="image/*" class="form-control">

# Untuk upload dokumen (foto/PDF):
'bukti': forms.FileInput(attrs={
    'class': 'form-control',
    # Tanpa accept → terima semua jenis file
})
```

#### 8. CheckboxInput — Checkbox Boolean
```python
'aktif': forms.CheckboxInput(attrs={
    'class': 'form-check-input',   # Bootstrap checkbox
    'id': 'productActive',
})
# Output: <input type="checkbox" class="form-check-input" checked>
```

#### 9. CheckboxSelectMultiple — Multi-Pilihan (apps/hr/forms.py)
```python
# Contoh: Pilih hari kerja (Senin-Jumat)
hari_kerja_checkboxes = forms.MultipleChoiceField(
    choices=[
        ('0', 'Senin'), ('1', 'Selasa'), ('2', 'Rabu'),
        ('3', 'Kamis'), ('4', 'Jumat'), ('5', 'Sabtu'), ('6', 'Minggu'),
    ],
    widget=forms.CheckboxSelectMultiple(attrs={
        'class': 'form-check-input'
    }),
    required=False,
)
# Output: Multiple <input type="checkbox" value="0"> Senin
#                   <input type="checkbox" value="1"> Selasa ...
```

#### 10. EmailInput — Input Email
```python
'email': forms.EmailInput(attrs={
    'class': 'form-control',
    'placeholder': 'email@supplier.com',
})
# Output: <input type="email" class="form-control">
# Browser otomatis validasi format email
```

#### 11. PasswordInput — Input Password
```python
'password': forms.PasswordInput(attrs={
    'class': 'form-control',
    'placeholder': '********',
})
# Output: <input type="password"> → karakter disembunyikan (●●●●)
```

---

## E. Custom Validasi — 3 Level

### Kenapa Perlu Validasi?
```
USER mengirim data  →  Level 1: Browser  →  Level 2: Django  →  Level 3: Custom
                       (bisa di-bypass!)     (otomatis)         (logika bisnis)
```

### Level 1: Validasi HTML/Browser (Client-Side)
```html
<input type="number" min="0" required>
<!-- Browser mencegah submit jika kosong atau < 0 -->
<!-- ⚠ TAPI: user bisa disable via DevTools → TIDAK AMAN sendiri! -->
```

### Level 2: Validasi Django Otomatis (Server-Side)
```python
# Otomatis dari definisi model field:
nama = CharField(max_length=200)    # Max 200 karakter
# → form.errors: {'nama': ['max 200 characters']}

email = EmailField(unique=True)     # Format email + unik
# → {'email': ['Enter a valid email address.']}
# → {'email': ['This email already exists.']}

harga = DecimalField()              # Harus angka
# → {'harga': ['Enter a number.']}
```

### Level 3: Validasi Custom (Logika Bisnis)

#### 3a. `clean_<field>()` — Validasi Per Field

```python
# ═══ CONTOH: Validasi harga jual > harga beli ═══
class ProdukForm(forms.ModelForm):
    def clean_harga_jual(self):
        """
        clean_<field_name>() → validasi khusus untuk satu field.
        Dipanggil OTOMATIS oleh is_valid() setelah validasi dasar.

        Konvensi: clean_ + nama_field
        HARUS return nilai yang sudah divalidasi.
        """
        harga_jual = self.cleaned_data.get('harga_jual')
        harga_beli = self.cleaned_data.get('harga_beli')

        if harga_jual and harga_beli and harga_jual < harga_beli:
            raise forms.ValidationError(
                'Harga jual (Rp %(jual)s) tidak boleh lebih kecil '
                'dari harga beli (Rp %(beli)s)!',
                params={'jual': harga_jual, 'beli': harga_beli}
            )

        return harga_jual  # WAJIB return!
```

#### 3b. `clean()` — Validasi Multiple Fields

```python
# ═══ CONTOH NYATA: apps/inventory/forms.py ═══
class TransferStokForm(forms.ModelForm):
    def clean(self):
        """
        clean() tanpa nama field → validasi ANTAR field.
        Dipanggil setelah SEMUA clean_<field>() selesai.
        """
        cleaned_data = super().clean()
        gudang_asal = cleaned_data.get('gudang_asal')
        gudang_tujuan = cleaned_data.get('gudang_tujuan')

        # Validasi: gudang asal dan tujuan TIDAK BOLEH SAMA
        if gudang_asal and gudang_tujuan and gudang_asal == gudang_tujuan:
            raise forms.ValidationError(
                'Gudang asal dan tujuan tidak boleh sama!'
            )

        return cleaned_data
```

#### 3c. `validators=[]` — Validator Reusable

```python
from django.core.validators import MinValueValidator, MaxValueValidator

class TransaksiBiayaForm(forms.ModelForm):
    jumlah = forms.DecimalField(
        validators=[
            MinValueValidator(0, message='Jumlah tidak boleh negatif!'),
            MaxValueValidator(999999999, message='Jumlah terlalu besar!'),
        ]
    )
```

### Alur Validasi Lengkap:
```
form.is_valid() dipanggil
    │
    ├── 1. Per-field validation (tipe data, max_length, dll)
    │       → Gagal? → error masuk form.errors['field_name']
    │
    ├── 2. clean_<field>() dipanggil untuk setiap field
    │       → ValidationError? → error masuk form.errors['field_name']
    │
    ├── 3. clean() dipanggil (cross-field validation)
    │       → ValidationError? → error masuk form.non_field_errors
    │
    └── 4. Result:
            → Semua lolos → is_valid() = True → cleaned_data tersedia
            → Ada error → is_valid() = False → form.errors berisi detail
```

### Output Error di Template:
```html
<!-- Error per field (dari clean_harga_jual) -->
{% if form.harga_jual.errors %}
<div class="invalid-feedback d-block">
    {% for error in form.harga_jual.errors %}
        <span>{{ error }}</span>
    {% endfor %}
</div>
{% endif %}
<!-- Output: "Harga jual (Rp 5000) tidak boleh lebih kecil dari harga beli (Rp 10000)!" -->

<!-- Error non-field (dari clean()) -->
{% if form.non_field_errors %}
<div class="alert alert-danger">
    {% for error in form.non_field_errors %}
        <p>{{ error }}</p>
    {% endfor %}
</div>
{% endif %}
<!-- Output: "Gudang asal dan tujuan tidak boleh sama!" -->
```

---

## F. Formset & InlineFormSet

### Apa itu Formset?
Formset = **kumpulan form** yang dikelola bersama. Digunakan untuk pola **Parent-Child** (1 PO → banyak Item).

### Kenapa Formset Penting?
```
Tanpa Formset:                         Dengan Formset:
┌────────────────────┐                 ┌────────────────────┐
│ Save PO dulu       │                 │ Save PO + Items    │
│ → Redirect ke      │                 │ dalam 1 kali       │
│   halaman items    │ ← Ribet!       │ submit form        │ ← Simpel!
│ → Tambah item 1    │                 │                    │
│ → Tambah item 2    │                 │ [Tambah Item] btn  │
│ → ...              │                 │ JavaScript handle  │
└────────────────────┘                 └────────────────────┘
```

### `inlineformset_factory()` — Parameter Lengkap

```python
from django.forms import inlineformset_factory

# ═══ CONTOH: apps/inventory/forms.py ═══
TransferStokItemFormSet = inlineformset_factory(
    TransferStok,              # Parent model
    TransferStokItem,          # Child model (punya FK ke parent)
    form=TransferStokItemForm, # Form class yang sudah dikustomisasi
    extra=0,                   # Berapa form kosong saat pertama dibuka
    #   0 → Tidak ada (user klik "Tambah Produk" untuk nambah)
    #   1 → 1 form kosong (default PO)
    can_delete=True,           # User bisa hapus item (checkbox DELETE)
    min_num=1,                 # Minimal harus ada 1 item
    validate_min=True,         # Enforce minimal (ValidationError jika < 1)
)

# ═══ CONTOH: apps/pembelian/forms.py ═══
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    fields=['produk', 'jumlah', 'harga_satuan', 'catatan'],
    extra=1,                   # 1 form kosong extra
    can_delete=True,
    widgets={                  # Kustomisasi widget langsung
        'produk': forms.Select(attrs={'class': 'form-select select2-item'}),
        'jumlah': forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01', 'min': '0',
        }),
        'harga_satuan': forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01', 'min': '0',
        }),
    }
)
```

### Cara Pakai Formset di View:

```python
class TransferStokCreateView(CreateView):
    model = TransferStok
    form_class = TransferStokForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # Saat POST: isi formset dengan data POST
            context['formset'] = TransferStokItemFormSet(self.request.POST)
        else:
            # Saat GET: formset kosong
            context['formset'] = TransferStokItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            # Simpan parent dulu
            self.object = form.save(commit=False)
            self.object.dibuat_oleh = self.request.user
            self.object.save()
            # Set parent untuk semua child, lalu simpan
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(context)
```

### Management Form (WAJIB di Template):
```html
<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}

    <!-- WAJIB: Management form untuk formset -->
    {{ formset.management_form }}
    <!--
    Output hidden inputs:
    <input type="hidden" name="items-TOTAL_FORMS" value="3">
    <input type="hidden" name="items-INITIAL_FORMS" value="2">
    <input type="hidden" name="items-MIN_NUM_FORMS" value="1">
    <input type="hidden" name="items-MAX_NUM_FORMS" value="1000">

    Tanpa management_form → Django TOLAK formset (ManagementForm error)!
    -->

    {% for item_form in formset %}
    <div class="formset-row">
        {{ item_form.produk }}
        {{ item_form.jumlah }}
        {{ item_form.DELETE }}  <!-- Checkbox hapus -->
    </div>
    {% endfor %}
</form>
```

---

## G. Form di View (CBV) — Alur Lengkap

### CreateView — Buat Data Baru

```python
# ═══ apps/produk/views.py ═══
class ProdukCreateView(SubModulePermissionMixin, CreateView):
    model = Produk
    form_class = ProdukForm       # Pakai form yang sudah dikustomisasi
    template_name = 'produk/produk_form.html'
    success_url = reverse_lazy('produk:list')

    # Method yang di-override:
    def form_valid(self, form):
        """Dipanggil jika form VALID → simpan ke DB."""
        form.instance.dibuat_oleh = self.request.user  # Set pembuat
        return super().form_valid(form)
```

### UpdateView — Edit Data

```python
class ProdukUpdateView(SubModulePermissionMixin, UpdateView):
    model = Produk
    form_class = ProdukForm
    template_name = 'produk/produk_form.html'
    success_url = reverse_lazy('produk:list')
    # Django otomatis:
    # 1. Ambil Produk berdasarkan pk dari URL
    # 2. Isi form dengan data existing (instance=produk)
    # 3. Saat submit: update data, bukan create baru
```

### Alur Lengkap Saat User Submit Form:
```
1. User buka /produk/tambah/    → GET request
2. CreateView.get() dipanggil
3. Django buat ProdukForm()     → form kosong
4. Template render form HTML    → ditampilkan di browser

5. User mengisi form, klik "Simpan" → POST request
6. CreateView.post() dipanggil
7. Django buat ProdukForm(request.POST, request.FILES)
   ↑ request.POST  = data form (nama, harga, dll)
   ↑ request.FILES = file upload (gambar)

8. form.is_valid() dipanggil
   → Cek CharField max_length
   → Cek DecimalField format angka
   → Cek required fields
   → Cek unique constraints
   → Jalankan semua clean_*() methods

9a. VALID → form_valid() → form.save() → INSERT INTO → Redirect
9b. INVALID → form_invalid() → Re-render form + error messages
```

---

## H. Render Form di Template

### Form Lengkap dengan Validasi Error:
```html
<form method="POST" enctype="multipart/form-data"
      action="{% url 'produk:tambah' %}">

    <!-- CSRF Token — WAJIB untuk setiap form POST! -->
    {% csrf_token %}
    <!--
    Apa itu CSRF?
    Cross-Site Request Forgery = serangan website jahat
    yang submit form "atas nama" user yang login.

    Cara kerja proteksi:
    1. Django generate token unik per session
    2. Token jadi hidden input di form
    3. Saat submit → Django cek token cocok atau tidak
    4. Token tidak cocok → 403 Forbidden
    Tanpa {% csrf_token %} → form POST DITOLAK (403)!
    -->

    <!-- Non-field errors (dari clean()) -->
    {% if form.non_field_errors %}
    <div class="alert alert-danger">
        {% for error in form.non_field_errors %}
            <p>{{ error }}</p>
        {% endfor %}
    </div>
    {% endif %}

    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label" for="{{ form.nama.id_for_label }}">
                {{ form.nama.label }}
            </label>
            <!-- Output: <label for="id_nama">Nama Produk</label> -->

            {{ form.nama }}
            <!-- Output: <input type="text" name="nama" class="form-control"
                         placeholder="Nama Produk" id="productName" required> -->

            {% if form.nama.errors %}
            <div class="invalid-feedback d-block">
                {% for error in form.nama.errors %}
                    <span>{{ error }}</span>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>

    <button type="submit" class="btn btn-primary">
        <i class="ri-save-line me-1"></i>Simpan
    </button>
</form>
```

### Kenapa `enctype="multipart/form-data"`?
```
Tanpa enctype:                          Dengan enctype:
┌──────────────────┐                   ┌──────────────────┐
│ POST Data:       │                   │ POST Data:       │
│ nama=Beras       │                   │ nama=Beras       │
│ harga=12000      │                   │ harga=12000      │
│ gambar=          │ ← KOSONG!        │ gambar=[binary]  │ ← FILE!
└──────────────────┘                   └──────────────────┘

enctype="multipart/form-data" WAJIB jika ada upload file (ImageField/FileField)
Tanpa ini → request.FILES akan KOSONG!
```

---

## I. File & Image Upload

### Setup di Model:
```python
class Produk(models.Model):
    gambar = models.ImageField(
        upload_to='produk/',       # Disimpan di: media/produk/
        blank=True, null=True      # Opsional
    )
    # Membutuhkan: pip install Pillow
```

### Setup di Settings:
```python
# config/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Setup di URLs:
```python
# config/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Di Template:
```html
<!-- Upload form WAJIB enctype multipart -->
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.gambar }}
</form>

<!-- Menampilkan gambar -->
{% if produk.gambar %}
    <img src="{{ produk.gambar.url }}" alt="{{ produk.nama }}" class="img-fluid">
{% else %}
    <img src="{% static 'img/no-image.png' %}" alt="No Image">
{% endif %}
```

### Di View (PENTING — jangan lupa `request.FILES`!):
```python
# CBV: otomatis handle request.FILES
class ProdukCreateView(CreateView):
    form_class = ProdukForm  # Otomatis handle FILES

# FBV: harus manual!
def produk_create(request):
    form = ProdukForm(request.POST, request.FILES)  # ← FILES!
    # Tanpa request.FILES → gambar tidak terupload!
```

---

## J. AJAX Form Submit

### Kapan Pakai AJAX?
- Submit tanpa reload halaman (experience lebih smooth)
- Validasi real-time saat user mengetik
- Form dalam modal/popup

### Contoh: AJAX Delete dengan SweetAlert2
```javascript
// ═══ Dari project ERP — delete with confirmation ═══
function deleteItem(url, itemName) {
    Swal.fire({
        title: 'Hapus ' + itemName + '?',
        text: 'Data yang dihapus tidak bisa dikembalikan!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ya, Hapus!',
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Terhapus!', data.message, 'success');
                    location.reload();
                }
            });
        }
    });
}
```

### Contoh: Select2 AJAX Search Product (apps/inventory)
```javascript
// ═══ Dropdown pencarian produk via AJAX ═══
$('.select2-product').select2({
    ajax: {
        url: '/api/produk/search/',
        dataType: 'json',
        delay: 250,        // Tunggu 250ms setelah user berhenti ketik
        data: function(params) {
            return { q: params.term };  // Kirim keyword pencarian
        },
        processResults: function(data) {
            return {
                results: data.map(function(item) {
                    return { id: item.id, text: item.nama };
                })
            };
        },
    },
    placeholder: 'Cari produk...',
    minimumInputLength: 2,   // Minimal 2 karakter untuk mulai cari
});
```

---

## K. Studi Kasus: Semua Form di ERP

### Peta Semua Form dalam Sistem:

| File | Form Class | Jenis | Kegunaan |
|------|-----------|-------|----------|
| `produk/forms.py` | `ProdukForm` | ModelForm | CRUD Produk |
| `pembelian/forms.py` | `SupplierForm` | ModelForm | CRUD Supplier |
| `pembelian/forms.py` | `PurchaseOrderForm` | ModelForm | Form utama PO |
| `pembelian/forms.py` | `PurchaseOrderItemFormSet` | InlineFormSet | Items PO |
| `penjualan/forms.py` | `CustomerForm` | ModelForm | CRUD Customer |
| `penjualan/forms.py` | `SalesOrderForm` | ModelForm | Form utama SO |
| `penjualan/forms.py` | `SalesOrderItemFormSet` | InlineFormSet | Items SO |
| `inventory/forms.py` | `TransferStokForm` | ModelForm + clean() | Transfer + validasi gudang |
| `inventory/forms.py` | `TransferStokItemFormSet` | InlineFormSet | Items transfer |
| `inventory/forms.py` | `AdjustmentStokForm` | ModelForm | Koreksi stok |
| `biaya/forms.py` | `KategoriBiayaForm` | ModelForm | CRUD kategori biaya |
| `biaya/forms.py` | `TransaksiBiayaForm` | ModelForm | Catat pengeluaran |
| `hr/forms.py` | `DepartemenForm` | ModelForm | CRUD departemen |
| `hr/forms.py` | `JabatanForm` | ModelForm | CRUD jabatan |
| `hr/forms.py` | `KaryawanForm` | ModelForm | CRUD karyawan |
| `hr/forms.py` | `AbsensiForm` | ModelForm | Catat absensi |
| `hr/forms.py` | `PenggajianForm` | ModelForm | Detail gaji |
| `hr/forms.py` | `GeneratePenggajianForm` | Form (non-model) | Generate gaji bulanan |
| `hr/forms.py` | `PengaturanAbsensiForm` | ModelForm + save() | Setting absensi |
| `hr/forms.py` | `FotoWajahForm` | ModelForm | Upload foto face recognition |

### Studi Kasus: TransferStokForm (Validasi Cross-Field)

**Problem:** User bisa memilih gudang asal dan tujuan yang SAMA → transfer ke diri sendiri.

**Solusi:** Override `clean()` untuk validasi antar field:
```python
class TransferStokForm(forms.ModelForm):
    class Meta:
        model = TransferStok
        fields = ['gudang_asal', 'gudang_tujuan', 'catatan']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hanya tampilkan gudang aktif
        self.fields['gudang_asal'].queryset = Gudang.objects.filter(aktif=True)
        self.fields['gudang_tujuan'].queryset = Gudang.objects.filter(aktif=True)

    def clean(self):
        cleaned_data = super().clean()
        asal = cleaned_data.get('gudang_asal')
        tujuan = cleaned_data.get('gudang_tujuan')
        if asal and tujuan and asal == tujuan:
            raise forms.ValidationError('Gudang asal dan tujuan tidak boleh sama!')
        return cleaned_data
```

### Studi Kasus: PengaturanAbsensiForm (Override save())

**Problem:** Multi-checkbox hari kerja (Senin-Jumat) perlu disimpan sebagai CSV string.

```python
class PengaturanAbsensiForm(forms.ModelForm):
    HARI_CHOICES = [
        ('0', 'Senin'), ('1', 'Selasa'), ('2', 'Rabu'),
        ('3', 'Kamis'), ('4', 'Jumat'), ('5', 'Sabtu'), ('6', 'Minggu'),
    ]
    hari_kerja_checkboxes = forms.MultipleChoiceField(
        choices=HARI_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    def save(self, commit=True):
        """Override save — konversi list checkbox ke CSV string."""
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('hari_kerja_checkboxes', [])
        instance.hari_kerja = ','.join(selected)  # ['0','1','4'] → '0,1,4'
        if commit:
            instance.save()
        return instance
```

---

## L. Kesalahan Umum & Best Practice

### ❌ Kesalahan Umum

#### 1. Lupa `request.FILES` untuk File Upload
```python
# ❌ SALAH — gambar tidak terupload!
form = ProdukForm(request.POST)

# ✅ BENAR
form = ProdukForm(request.POST, request.FILES)
```

#### 2. Lupa `enctype` di HTML Form
```html
<!-- ❌ SALAH — file tidak terkirim -->
<form method="POST">

<!-- ✅ BENAR -->
<form method="POST" enctype="multipart/form-data">
```

#### 3. Lupa `{% csrf_token %}` di Form POST
```html
<!-- ❌ SALAH — 403 Forbidden! -->
<form method="POST">
    <input type="text" name="nama">
</form>

<!-- ✅ BENAR -->
<form method="POST">
    {% csrf_token %}
    <input type="text" name="nama">
</form>
```

#### 4. Pakai `fields = '__all__'`
```python
# ❌ BAHAYA — expose semua field termasuk yang sensitif!
class Meta:
    fields = '__all__'

# ✅ AMAN — whitelist field yang boleh diedit
class Meta:
    fields = ['nama', 'harga_jual', 'kategori']
```

#### 5. Lupa `return` di `clean_<field>()`
```python
# ❌ SALAH — field jadi None!
def clean_nama(self):
    nama = self.cleaned_data.get('nama')
    if len(nama) < 3:
        raise forms.ValidationError('Minimal 3 karakter!')
    # Lupa return!

# ✅ BENAR
def clean_nama(self):
    nama = self.cleaned_data.get('nama')
    if len(nama) < 3:
        raise forms.ValidationError('Minimal 3 karakter!')
    return nama  # ← WAJIB!
```

#### 6. Lupa `management_form` di Formset
```html
<!-- ❌ SALAH — ManagementForm error! -->
{% for form in formset %}
    {{ form.as_p }}
{% endfor %}

<!-- ✅ BENAR -->
{{ formset.management_form }}
{% for form in formset %}
    {{ form.as_p }}
{% endfor %}
```

### ✅ Best Practice Production

| # | Practice | Contoh |
|---|----------|--------|
| 1 | Selalu whitelist fields | `fields = ['nama', 'harga']` |
| 2 | Filter queryset di `__init__` | `self.fields['supplier'].queryset = Supplier.objects.filter(aktif=True)` |
| 3 | Set label Bahasa Indonesia | `self.fields['nama'].label = 'Nama Produk'` |
| 4 | Gunakan `empty_label` | `self.fields['kategori'].empty_label = 'Pilih Kategori'` |
| 5 | Validasi logika bisnis di `clean()` | Gudang asal ≠ tujuan, harga jual ≥ harga beli |
| 6 | Pakai `commit=False` untuk set field sebelum save | `obj = form.save(commit=False); obj.user = request.user; obj.save()` |
| 7 | Gunakan Select2 untuk dropdown besar | `'class': 'select2 form-select'` |
| 8 | Default value untuk record baru | `if not self.instance.pk: self.fields['tanggal'].initial = date.today()` |
| 9 | Pakai `select_related` di queryset form | `Produk.objects.filter(aktif=True).select_related('satuan')` |
| 10 | Consistent widget styling | Semua input pakai `'class': 'form-control'` |

---

*Lanjut ke [07_SISTEM_PERMISSION_RBAC.md](07_SISTEM_PERMISSION_RBAC.md) →*
