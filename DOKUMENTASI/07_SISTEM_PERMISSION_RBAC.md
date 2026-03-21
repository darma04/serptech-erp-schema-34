# 🔐 07 — Sistem Permission RBAC — Penjelasan Sangat Detail

## A. Apa itu RBAC? Kenapa Perlu?

### Masalah Tanpa RBAC:
Semua user punya akses yang SAMA — kasir bisa hapus produk, staff gudang bisa lihat gaji, semua orang bisa akses data sensitif.

### Solusi RBAC (Role-Based Access Control):
**Akses ditentukan oleh PERAN (role)** pengguna. Setiap role punya **hak akses yang berbeda**.

```
SUPERUSER → Akses SEMUA (bypass semua pengecekan)
ADMIN     → Akses banyak fitur, tapi bisa dibatasi
USER      → Hanya bisa lihat data tertentu
KASIR     → Hanya bisa akses POS / kasir
STAFF_GUDANG → Hanya bisa akses inventory (custom role)
```

### Alur Lengkap RBAC:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  User "Budi" (role: KASIR) buka /produk/list/                   │
│                                                                   │
│  LANGKAH 1: Django terima HTTP request                           │
│  LANGKAH 2: AuthenticationMiddleware set request.user = Budi     │
│  LANGKAH 3: URL match → ProdukListView                          │
│  LANGKAH 4: SubModulePermissionMixin.dispatch() dipanggil        │
│      → permission_module = 'produk'                              │
│      → permission_sub_module = 'daftar_produk'                   │
│      → permission_action = 'read'                                │
│  LANGKAH 5: has_permission() dipanggil                           │
│      → Ambil profile Budi: role = 'KASIR'                       │
│      → Cek: role == 'SUPERUSER'? TIDAK → lanjut cek             │
│      → Query: RolePermission.objects.get(                        │
│            role='KASIR', module='produk',                        │
│            sub_module='daftar_produk')                           │
│      → Hasil: can_view=False                                     │
│  LANGKAH 6: can_view=False → raise PermissionDenied             │
│  LANGKAH 7: Django tampilkan halaman 403 FORBIDDEN              │
│                                                                   │
│  ═══════════════════════════════════════════════                  │
│                                                                   │
│  User "Admin" (role: ADMIN) buka /produk/list/                   │
│  → Query: role='ADMIN', module='produk', can_view=True           │
│  → DIIZINKAN → Halaman Daftar Produk ditampilkan                │
│                                                                   │
│  User "Super" (role: SUPERUSER) buka halaman APAPUN              │
│  → role=='SUPERUSER' → BYPASS semua cek → SELALU diizinkan      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## B. Model RolePermission — Baris per Baris

```python
# File: apps/core/models.py

class RolePermission(models.Model):
    """
    Model ini adalah JANTUNG sistem RBAC.
    Menyimpan: "Role X punya akses apa di modul Y, sub-modul Z?"
    
    Satu record = SATU aturan permission.
    Contoh: role=ADMIN, module=produk, sub_module=kategori, can_view=True, can_create=True
    Artinya: ADMIN bisa MELIHAT dan MEMBUAT data di sub-modul Kategori Produk
    """
    
    ROLE_CHOICES = [
        ('SUPERUSER', 'Superuser'),   # Akses penuh (bypass semua)
        ('ADMIN', 'Admin'),           # Admin (dikontrol via permission)
        ('USER', 'User'),             # User biasa
        ('KASIR', 'Kasir'),           # Kasir (fokus POS)
    ]
    # ↑ Daftar role BAWAAN
    # Tapi bisa ditambah role KUSTOM via halaman Permission Management
    # Contoh: ('STAFF_GUDANG', 'Staff Gudang')
    # Bagaimana? Method get_all_roles() menggabungkan choices + role dari DB
    
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('produk', 'Produk'),
        ('inventory', 'Inventory'),
        ('pembelian', 'Pembelian'),
        ('penjualan', 'Penjualan'),
        ('pos', 'POS'),
        ('biaya', 'Biaya'),
        ('laporan', 'Laporan'),
        ('hr', 'HR Management'),
        ('automation', 'Automation'),
        ('pengaturan', 'Pengaturan'),
        ('access', 'Access Management'),
        ('users', 'User Management'),
        ('ai_assistant', 'AI Manajemen'),
    ]
    # ↑ Daftar semua modul ERP yang bisa dikontrol aksesnya
    
    SUB_MODULE_CHOICES = {
        'produk': [
            ('kategori', 'Kategori'),
            ('satuan', 'Satuan'),
            ('daftar_produk', 'Daftar Produk'),
        ],
        'inventory': [
            ('gudang', 'Gudang'),
            ('stok', 'Stok'),
            ('transfer', 'Transfer Stok'),
            ('adjustment', 'Adjustment Stok'),
        ],
        # ... sub-modul untuk modul lainnya
        'ai_assistant': [
            ('dashboard_ai', 'AI Dashboard'),
            ('pengaturan_ai', 'AI Assistant'),
        ],
    }
    # ↑ Setiap modul bisa punya SUB-MODUL
    # Contoh: Modul "Produk" punya sub-modul: Kategori, Satuan, Daftar Produk
    # Akses dikontrol per sub-modul (granular control)
    
    # ═══ FIELDS ═══
    role = models.CharField(max_length=50)
    # ↑ Role yang diatur: 'ADMIN', 'KASIR', 'STAFF_GUDANG', dll
    
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    # ↑ Modul yang diatur: 'produk', 'inventory', 'pembelian', dll
    
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    # ↑ Sub-modul (opsional): 'kategori', 'daftar_produk', dll
    # Jika NULL → permission berlaku untuk SELURUH modul
    
    can_view = models.BooleanField(default=True)
    # ↑ Boleh MELIHAT data? (menu muncul di sidebar)
    # True → menu muncul, halaman bisa diakses, data bisa dilihat
    # False → menu TERSEMBUNYI, halaman return 403
    
    can_create = models.BooleanField(default=False)
    # ↑ Boleh MENAMBAH data baru?
    # True → tombol "Tambah" muncul, form create bisa diakses
    # False → tombol "Tambah" TERSEMBUNYI, form create return 403
    
    can_edit = models.BooleanField(default=False)
    # ↑ Boleh MENGEDIT data yang ada?
    # True → tombol "Edit" muncul, form edit bisa diakses
    # False → tombol "Edit" TERSEMBUNYI, form edit return 403
    
    can_delete = models.BooleanField(default=False)
    # ↑ Boleh MENGHAPUS data?
    # True → tombol "Hapus" muncul, delete endpoint bisa diakses
    # False → tombol "Hapus" TERSEMBUNYI, delete return 403
    
    class Meta:
        unique_together = ('role', 'module', 'sub_module')
        # ↑ Kombinasi role + module + sub_module harus UNIK
        # Tidak boleh ada 2 record: ADMIN + produk + kategori
        # Ini mencegah data duplikat
```

**Contoh data di database:**
```
┌────┬────────┬──────────┬───────────────┬──────────┬────────────┬──────────┬────────────┐
│ id │ role   │ module   │ sub_module    │ can_view │ can_create │ can_edit │ can_delete │
├────┼────────┼──────────┼───────────────┼──────────┼────────────┼──────────┼────────────┤
│ 1  │ ADMIN  │ produk   │ kategori      │ ✅ True  │ ✅ True    │ ✅ True  │ ✅ True    │
│ 2  │ ADMIN  │ produk   │ daftar_produk │ ✅ True  │ ✅ True    │ ✅ True  │ ❌ False   │
│ 3  │ KASIR  │ pos      │ NULL          │ ✅ True  │ ✅ True    │ ❌ False │ ❌ False   │
│ 4  │ KASIR  │ produk   │ daftar_produk │ ✅ True  │ ❌ False   │ ❌ False │ ❌ False   │
│ 5  │ USER   │ produk   │ daftar_produk │ ✅ True  │ ❌ False   │ ❌ False │ ❌ False   │
│ 6  │ USER   │ dashboard│ NULL          │ ✅ True  │ ❌ False   │ ❌ False │ ❌ False   │
└────┴────────┴──────────┴───────────────┴──────────┴────────────┴──────────┴────────────┘

Artinya:
- ADMIN bisa CRUD lengkap di Kategori Produk
- ADMIN bisa lihat/tambah/edit Produk, tapi TIDAK bisa hapus
- KASIR bisa lihat & buat transaksi POS, tapi tidak bisa edit/hapus
- KASIR bisa MELIHAT daftar produk (untuk cari harga), tapi tidak bisa tambah/edit/hapus
- USER hanya bisa lihat produk dan dashboard
```

---

## C. SubModulePermissionMixin — Cara Kerja Internal

```python
# File: apps/core/mixins.py

class SubModulePermissionMixin:
    """
    Mixin yang dicampur ke View untuk mengecek permission SEBELUM view dijalankan.
    
    Apa itu Mixin?
    Mixin = class yang TIDAK berdiri sendiri, tapi dicampur (mixed-in) ke class lain.
    Mixin menambah fungsionalitas tanpa mengubah class utama.
    
    Analogi: View = kopi. Mixin = gula.
    Kopi bisa diminum tanpa gula (view tanpa mixin = tanpa cek permission)
    Kopi + gula = kopi manis (view + mixin = view dengan cek permission)
    """
    
    permission_module = None       # WAJIB diisi oleh view: 'produk', 'inventory', dll
    permission_sub_module = None   # Opsional: 'kategori', 'daftar_produk', dll
    permission_action = 'read'     # Default: 'read' (can_view)
    # Mapping action → field:
    #   'read'   → cek can_view
    #   'create' → cek can_create
    #   'write'  → cek can_edit
    #   'delete' → cek can_delete
    
    def dispatch(self, request, *args, **kwargs):
        """
        dispatch() = method pertama yang dipanggil saat request masuk.
        Ini "pintu gerbang" sebelum get() atau post() dijalankan.
        
        Alur:
        1. dispatch() dipanggil
        2. Cek permission
        3a. Jika DIIZINKAN → lanjut ke get()/post() → render halaman
        3b. Jika DITOLAK → return 403 Forbidden (halaman error)
        """
        # Cek apakah user login punya permission
        if not has_permission(
            request.user,                # User yang sedang login
            self.permission_action,      # Aksi yang dilakukan
            self.permission_module,      # Modul yang diakses
            self.permission_sub_module   # Sub-modul (opsional)
        ):
            raise PermissionDenied  # HTTP 403 Forbidden
            # ↑ Django menangkap exception ini dan menampilkan halaman 403
        
        # Jika permission OK → lanjut ke method view (get/post/put/delete)
        return super().dispatch(request, *args, **kwargs)
```

### Contoh Penggunaan di View:
```python
# Daftar Kategori — butuh permission READ
class KategoriListView(SubModulePermissionMixin, ListView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'read'        # → cek can_view
    # ...

# Tambah Kategori — butuh permission CREATE
class KategoriCreateView(SubModulePermissionMixin, CreateView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'create'      # → cek can_create
    # ...

# Edit Kategori — butuh permission WRITE (edit)
class KategoriUpdateView(SubModulePermissionMixin, UpdateView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'write'       # → cek can_edit
    # ...

# Hapus Kategori — butuh permission DELETE
class KategoriDeleteView(SubModulePermissionMixin, DeleteView):
    permission_module = 'produk'
    permission_sub_module = 'kategori'
    permission_action = 'delete'      # → cek can_delete
    # ...
```

### Mixin CRUD Shorthand (Versi Ringkas)

Selain `SubModulePermissionMixin` yang serba-guna, tersedia juga **4 mixin shorthand** yang lebih ringkas — masing-masing sudah otomatis set action-nya:

```python
# File: apps/core/mixins.py

# ═══ ReadPermissionMixin — cek can_view ═══
class SupplierListView(ReadPermissionMixin, ListView):
    permission_module = 'pembelian'
    permission_sub_module = 'supplier'   # Opsional
    # Tidak perlu set permission_action = 'read' → sudah otomatis!

# ═══ CreatePermissionMixin — cek can_create ═══
class SupplierCreateView(CreatePermissionMixin, CreateView):
    permission_module = 'pembelian'
    # Tidak perlu set permission_action = 'create' → sudah otomatis!

# ═══ UpdatePermissionMixin — cek can_edit ═══
class SupplierUpdateView(UpdatePermissionMixin, UpdateView):
    permission_module = 'pembelian'
    # Tidak perlu set permission_action = 'write' → sudah otomatis!

# ═══ DeletePermissionMixin — cek can_delete ═══
class SupplierDeleteView(DeletePermissionMixin, DeleteView):
    permission_module = 'pembelian'
    permission_sub_module = 'supplier'   # Opsional
    # Tidak perlu set permission_action = 'delete' → sudah otomatis!
```

**Kapan pakai yang mana?**
| Mixin | Action | Cocok untuk |
|-------|--------|-------------|
| `SubModulePermissionMixin` | Bisa diatur | View yang butuh fleksibilitas |
| `ReadPermissionMixin` | `read` (otomatis) | ListView, DetailView |
| `CreatePermissionMixin` | `create` (otomatis) | CreateView |
| `UpdatePermissionMixin` | `write` (otomatis) | UpdateView |
| `DeletePermissionMixin` | `delete` (otomatis) | DeleteView |

---

## D. Fungsi has_permission() — Logic Inti (Versi Terbaru + Caching)

```python
# File: apps/core/permissions.py

def has_permission(user, action, module=None, sub_module=None):
    """
    Fungsi inti RBAC — mengecek apakah user punya permission.
    
    Parameter (URUTAN PENTING!):
    - user: objek User (dari request.user)
    - action: string aksi ('create', 'read'/'view', 'update'/'write', 'delete')
    - module: string nama modul ('produk', 'inventory', 'access-control')
    - sub_module: string sub-modul opsional (contoh: 'kategori', 'gudang')
    
    Return: True jika diizinkan, False jika ditolak
    
    OPTIMASI: Semua permission untuk sebuah role di-load SEKALI dari DB
    dan di-cache selama 30 detik. Satu page load hanya 1 DB query,
    bukan 20-40+ query seperti versi lama.
    """
    
    # LANGKAH 1: Ambil role user (via get_user_role helper)
    role = get_user_role(user)
    if not role:
        return False  # Belum login → tolak
    
    # LANGKAH 2: SUPERUSER selalu diizinkan (bypass semua!)
    if role == 'SUPERUSER':
        return True
    # ↑ Kenapa? SUPERUSER = owner sistem, harus bisa akses SEMUA
    
    # LANGKAH 3: Cek di CACHE permission (bukan query langsung!)
    if module:
        # Normalisasi: 'access-control' → 'access_control'
        module_normalized = module.replace('-', '_').lower()
        
        # Mapping aksi ke field database
        action_map = {
            'create': 'can_create',
            'read': 'can_view',
            'view': 'can_view',     # Alias untuk 'read'
            'update': 'can_edit',
            'write': 'can_edit',    # Alias untuk 'update'
            'delete': 'can_delete'
        }
        perm_field = action_map.get(action)
        if not perm_field:
            return False
        
        # Ambil cache permission (1 query per role, 30 detik)
        perms_cache = _get_role_permissions_cache(role)
        
        # CEK SUB-MODULE DULU (lebih spesifik)
        if sub_module:
            sub_key = (module_normalized, sub_module.lower())
            if sub_key in perms_cache:
                return perms_cache[sub_key].get(perm_field, False)
            # Jika sub-module tidak ditemukan → fallback ke module level
        
        # CEK MODULE LEVEL (fallback)
        mod_key = (module_normalized, None)
        if mod_key in perms_cache:
            return perms_cache[mod_key].get(perm_field, False)
        
        # Tidak ada permission record → DITOLAK
        return False
    
    return False
```

### Sistem Caching Permission — Optimasi Performa

Tanpa caching, **setiap pengecekan permission = 1 query database**. Satu halaman bisa mengecek 20-40 permission (sidebar, tombol, form). Itu berarti 20-40 query HANYA untuk cek permission!

```python
# File: apps/core/permissions.py

def _get_role_permissions_cache(role):
    """
    Load SEMUA permissions untuk sebuah role dalam 1 query dan cache.
    Return: Dict {(module, sub_module): {can_view, can_create, can_edit, can_delete}}
    Cache TTL: 30 detik
    """
    from django.core.cache import cache
    
    cache_key = f'role_perms_{role}'  # Contoh: 'role_perms_ADMIN'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached  # Cache HIT → tidak perlu query DB
    
    # Cache MISS → query SEMUA permission untuk role ini
    from apps.core.models import RolePermission
    perms_dict = {}
    
    all_perms = RolePermission.objects.filter(
        role__iexact=role
    ).values('module', 'sub_module', 'can_view', 'can_create', 'can_edit', 'can_delete')
    
    for p in all_perms:
        mod = p['module'].lower() if p['module'] else ''
        sub = p['sub_module'].lower() if p['sub_module'] else None
        key = (mod, sub)  # Contoh: ('produk', 'kategori') atau ('pos', None)
        perms_dict[key] = {
            'can_view': p['can_view'],
            'can_create': p['can_create'],
            'can_edit': p['can_edit'],
            'can_delete': p['can_delete'],
        }
    
    cache.set(cache_key, perms_dict, 30)  # Cache 30 detik
    return perms_dict
```

**Perbandingan performa:**
```
SEBELUM (tanpa caching):
  Halaman Produk List → 25 query permission (sidebar + tombol + tabel)
  Waktu: ~50ms hanya untuk permission check
  
SESUDAH (dengan caching):
  Request pertama → 1 query (load semua permission role)
  Request ke-2 s/d 30 detik → 0 query (dari cache)
  Waktu: ~2ms untuk permission check
```

---

## E. Permission di Template — Kontrol Tampilan UI

### Sidebar Menu — Sembunyikan Menu yang Tidak Punya Akses

```html
<!-- File: templates/layout/partials/menu/vertical/partials/menu_collapsible_template.html -->

{% for menu_item in menu_items %}
    {% with has_module_view=can_view|attr:item.slug %}
    {% with accessible_list=accessible_subs|attr:item.slug %}
    <!-- ↑ can_view|attr:item.slug → cek apakah user bisa akses modul ini
         accessible_subs|attr:item.slug → daftar sub-modul yang bisa diakses
         Jika can_view=False DAN tidak ada accessible sub → menu TIDAK DIRENDER
         User dengan role KASIR tidak akan melihat menu Produk di sidebar -->
    
    {% if has_module_view or accessible_list %}
    <li class="menu-item">
        <a href="{{ menu_item.url }}" class="menu-link">
            <i class="{{ menu_item.icon }}"></i>
            <div>{{ menu_item.name }}</div>
        </a>
        
        {% if menu_item.submenu %}
        <ul class="menu-sub">
            {% for sub in menu_item.submenu %}
                {% if sub.sub_module in accessible_list %}
                <li class="menu-item">
                    <a href="{{ sub.url }}" class="menu-link">{{ sub.name }}</a>
                </li>
                {% endif %}
            {% endfor %}
        </ul>
        {% endif %}
    </li>
    {% endif %}
    {% endwith %}
    {% endwith %}
{% endfor %}
```

**Hasil untuk user KASIR:**
```
Sidebar:
├── Dashboard          ✅ (can_view=True)
├── POS                ✅ (can_view=True)
└── (menu lain tidak muncul)

Sidebar untuk ADMIN:
├── Dashboard          ✅
├── Produk             ✅
│   ├── Kategori       ✅
│   ├── Satuan         ✅
│   └── Daftar Produk  ✅
├── Inventory          ✅
├── Pembelian          ✅
├── Penjualan          ✅
├── POS                ✅
├── Laporan            ✅
└── Pengaturan         ✅
```

### Button Aksi — Sembunyikan Berdasarkan Permission

```html
<div class="card-header">
    <h5>Daftar Produk</h5>
    
    {% if can_create.produk %}
        <a href="{% url 'produk:tambah' %}" class="btn btn-primary">
            <i class="ri-add-line"></i> Tambah Produk
        </a>
        <!-- Tombol ini HANYA muncul jika user punya can_create=True -->
    {% endif %}
</div>

<table>
    {% for p in produk_list %}
    <tr>
        <td>{{ p.nama }}</td>
        <td>
            {% if can_edit.produk %}
                <a href="{% url 'produk:edit' pk=p.pk %}" class="btn btn-sm btn-warning">Edit</a>
            {% endif %}
            
            {% if can_delete.produk %}
                <button class="btn btn-sm btn-danger" onclick="hapus({{ p.pk }})">Hapus</button>
            {% endif %}
            
            {% if not can_edit.produk and not can_delete.produk %}
                <span class="text-muted">Tidak ada aksi</span>
                <!-- Jika tidak punya permission edit DAN delete → tampilkan teks info -->
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
```

---

## F. Model Profile — Penghubung User ↔ Role

```python
# File: auth/models.py

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # ↑ OneToOneField = 1 User punya TEPAT 1 Profile
    # CASCADE = jika User dihapus, Profile IKUT dihapus
    # related_name='profile' → bisa akses: user.profile
    
    role = models.CharField(max_length=50, default='USER')
    # ↑ Role RBAC user ini: 'SUPERUSER', 'ADMIN', 'KASIR', 'USER'
    # default='USER' → user baru otomatis role USER (hak akses terbatas)
    
    email = models.EmailField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    email_token = models.CharField(max_length=100, blank=True)
    # ↑ Token verifikasi email (dikirim via email saat register)
    
    forget_password_token = models.CharField(max_length=100, blank=True)
    # ↑ Token reset password (dikirim via email saat lupa password)


# ═══ SIGNAL: Auto-Create Profile ═══
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    SIGNAL = "event listener" di Django.
    
    @receiver(post_save, sender=User)
    Artinya: "Setiap kali objek User di-SAVE (baik create maupun update),
              jalankan fungsi ini."
    
    Parameter:
    - sender: class yang mengirim signal (User)
    - instance: objek User yang baru di-save
    - created: True jika objek BARU DIBUAT, False jika UPDATE
    - **kwargs: argumen tambahan
    
    Kenapa pakai Signal?
    Karena kita TIDAK mengontrol proses pembuatan User.
    User bisa dibuat dari:
    - python manage.py createsuperuser
    - Django Admin panel
    - Form register di website
    - Script import data
    
    Dengan Signal, APAPUN cara User dibuat, Profile PASTI ikut dibuat.
    """
    if created:  # Hanya saat User BARU dibuat (bukan update)
        Profile.objects.create(
            user=instance,          # Hubungkan ke User yang baru dibuat
            email=instance.email    # Salin email dari User
        )
```

## G. Sistem Autentikasi (Authentication) — Login, Register, Forgot Password

### Apa itu Autentikasi vs Otorisasi?

```
AUTENTIKASI (Authentication):        OTORISASI (Authorization):
"SIAPA kamu?"                        "BOLEH akses apa?"
┌─────────────────────────┐          ┌─────────────────────────┐
│ User masukkan:          │          │ User sudah login.       │
│ - Username / Email      │          │ Sekarang cek:           │
│ - Password              │          │ - Apakah boleh buka     │
│                         │          │   halaman ini?          │
│ Sistem cek:             │          │ - Pakai RBAC            │
│ - Apakah ada di DB?     │          │   (RolePermission)      │
│ - Apakah password cocok?│          │                         │
│                         │          │ ← Ini section A-F di    │
│ ← Ini section G-I      │          │   atas                  │
└─────────────────────────┘          └─────────────────────────┘
```

### Arsitektur Auth di Project Ini:

```
d:\starter-kit\auth\                   ← Folder autentikasi
├── views.py                           ← AuthView (BASE class)
├── models.py                          ← Profile model
├── helpers.py                         ← Kirim email (verifikasi/reset)
├── urls.py                            ← URL routing auth
├── login\
│   └── views.py                       ← LoginView (POST: authenticate)
├── register\
│   └── views.py                       ← RegisterView (POST: create_user)
├── forgot_password\
│   └── views.py                       ← ForgetPasswordView (POST: send token)
├── reset_password\
│   └── views.py                       ← ResetPasswordView (POST: set_password)
└── verify_email\
    └── views.py                       ← VerifyEmailView (GET: verify token)
```

### Alur Lengkap Semua Fitur Auth:

```
═══════════════════════════════════════════════════════════════
 ALUR 1: LOGIN (Masuk ke Sistem)
═══════════════════════════════════════════════════════════════

User                         Server (Django)                    Database
  │                              │                                │
  │  GET /login/                 │                                │
  │ ──────────────────────────►  │                                │
  │                              │  Cek: user sudah login?       │
  │  ◄── Tampilkan form login    │  Tidak → render form          │
  │                              │                                │
  │  POST /login/                │                                │
  │  email-username: admin       │                                │
  │  password: ****              │                                │
  │ ──────────────────────────►  │                                │
  │                              │  1. Ada '@'? Ya → cari email  │
  │                              │     Tidak → cari username     │
  │                              │ ────────────────────────────►  │
  │                              │                                │
  │                              │  ◄── User object (atau None)  │
  │                              │                                │
  │                              │  2. authenticate(user, pwd)   │
  │                              │     → Hash password input     │
  │                              │     → Bandingkan dengan DB    │
  │                              │                                │
  │                              │  3a. Cocok:                   │
  │                              │     login(request, user)      │
  │                              │     → Buat Session            │
  │  ◄── Redirect /dashboard/   │     → Set Cookie              │
  │                              │                                │
  │                              │  3b. Tidak cocok:             │
  │  ◄── Error "Username/pwd    │                                │
  │       salah"                │                                │
  │                              │                                │

═══════════════════════════════════════════════════════════════
 ALUR 2: REGISTER (Daftar Akun Baru)
═══════════════════════════════════════════════════════════════

User                         Server (Django)                    Database
  │                              │                                │
  │  POST /register/             │                                │
  │  username: budi              │                                │
  │  email: budi@mail.com        │                                │
  │  password: ****              │                                │
  │ ──────────────────────────►  │                                │
  │                              │  1. Cek duplikasi:            │
  │                              │     - Username ada? → error   │
  │                              │     - Email ada? → error      │
  │                              │                                │
  │                              │  2. User.objects.create_user()│
  │                              │     → Password di-HASH        │
  │                              │     (PBKDF2 algorithm)        │
  │                              │ ────────────────────────────►  │
  │                              │     ◄── User created           │
  │                              │                                │
  │                              │  3. Signal post_save:         │
  │                              │     Profile.objects.create()  │
  │                              │     → role = 'USER' (default) │
  │                              │ ────────────────────────────►  │
  │                              │     ◄── Profile created        │
  │                              │                                │
  │                              │  4. Generate token UUID       │
  │                              │  5. Kirim email verifikasi    │
  │                              │                                │
  │  ◄── Redirect /verify-email/ │                                │

═══════════════════════════════════════════════════════════════
 ALUR 3: FORGOT PASSWORD (Lupa Password)
═══════════════════════════════════════════════════════════════

User                         Server (Django)                Email
  │                              │                            │
  │  POST /forgot_password/      │                            │
  │  email: budi@mail.com        │                            │
  │ ──────────────────────────►  │                            │
  │                              │                            │
  │                              │  1. Cari user by email     │
  │                              │  2. Generate token UUID    │
  │                              │  3. Set expiry = 24 jam    │
  │                              │  4. Simpan di Profile      │
  │                              │  5. Kirim email reset ────►│
  │                              │                            │
  │  ◄── "Link reset dikirim"   │                            │
  │                              │                            │
  │                              │                     ┌──────┤
  │  Klik link di email ─────────────────────────────► │      │
  │  /reset-password/{token}/    │                     │      │
  │                              │                     └──────┘
  │  ──────────────────────────► │
  │                              │  6. Cek token valid?       │
  │                              │  7. Cek belum expired?     │
  │  ◄── Form password baru     │                            │
  │                              │                            │
  │  POST new_password: ****     │                            │
  │  ──────────────────────────► │                            │
  │                              │  8. user.set_password()    │
  │                              │  9. Hapus token            │
  │  ◄── Redirect /login/       │                            │
```

### Session & Cookie — Bagaimana Django "Mengingat" Login:

```python
# Setelah login berhasil, Django melakukan:
login(request, user)

# Apa yang terjadi di balik layar:
# 1. Django buat SESI (session) di database:
#    ┌────────────────────────────────────┬──────────┬────────────┐
#    │ session_key                         │ user_id  │ expire_date│
#    ├────────────────────────────────────┼──────────┼────────────┤
#    │ abc123def456...                     │ 1        │ 2026-02-22 │
#    └────────────────────────────────────┴──────────┴────────────┘
#
# 2. Django kirim COOKIE ke browser:
#    Set-Cookie: sessionid=abc123def456...; Path=/; HttpOnly
#
# 3. Setiap request berikutnya, browser kirim cookie:
#    Cookie: sessionid=abc123def456...
#
# 4. Django Middleware (SessionMiddleware) baca cookie:
#    → Cari session_key di database
#    → Set request.user = User yang login
#
# 5. AuthenticationMiddleware:
#    → request.user sekarang berisi objek User yang login
#    → Bisa diakses di view: request.user.username

# Konfigurasi session di settings.py:
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Simpan di database
SESSION_COOKIE_AGE = 86400     # Expired setelah 24 jam (dalam detik)
SESSION_COOKIE_HTTPONLY = True  # Cookie TIDAK bisa diakses JavaScript (keamanan)
SESSION_COOKIE_SECURE = False  # Set True di production (hanya kirim via HTTPS)
```

### Middleware Pipeline — Alur Request di Django:

```
HTTP Request dari Browser
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. SecurityMiddleware                                   │
│    → Tambah header keamanan (HSTS, X-Content-Type)     │
├────────────────────────────────────────────────────────┤
│ 2. GZipMiddleware                                       │
│    → Kompresi response (ukuran lebih kecil, lebih cepat)│
├────────────────────────────────────────────────────────┤
│ 3. WhiteNoiseMiddleware                                 │
│    → Serve static files (CSS, JS, gambar) langsung     │
│    → Tanpa perlu Nginx di production                   │
├────────────────────────────────────────────────────────┤
│ 4. SessionMiddleware                                    │
│    → Baca cookie sessionid                             │
│    → Load session data dari database                   │
│    → Set request.session                               │
├────────────────────────────────────────────────────────┤
│ 5. LocaleMiddleware                                     │
│    → Deteksi bahasa user (i18n)                        │
├────────────────────────────────────────────────────────┤
│ 6. CommonMiddleware                                     │
│    → Tambah/hapus trailing slash di URL                │
├────────────────────────────────────────────────────────┤
│ 7. CsrfViewMiddleware                                   │
│    → Cek token CSRF (anti serangan Cross-Site Request  │
│      Forgery)                                          │
│    → Setiap form POST WAJIB ada {% csrf_token %}       │
├────────────────────────────────────────────────────────┤
│ 8. AuthenticationMiddleware ← PENTING!                  │
│    → Tambahkan request.user dari session               │
│    → Setelah ini, setiap view bisa akses request.user  │
├────────────────────────────────────────────────────────┤
│ 9. MessageMiddleware                                    │
│    → Support messages.success(), messages.error()      │
│    → Flash message yang tampil 1 kali                  │
├────────────────────────────────────────────────────────┤
│ 10. XFrameOptionsMiddleware                             │
│     → Cegah halaman di-embed di iframe (anti clickjack)│
├────────────────────────────────────────────────────────┤
│ 11. ActivityLogMiddleware ← CUSTOM (buatan kita)        │
│     → Catat request info (IP, user agent)              │
│     → Untuk audit trail (UserActivity model)           │
└────────────────────────────────────────────────────────┘
         │
         ▼
      View (get/post) → Template → Response
```

### Keamanan Password di Django:

```python
# Django TIDAK PERNAH menyimpan password dalam bentuk plain text!
# Password di-hash menggunakan PBKDF2-SHA256:

# Contoh password "admin123" di database:
# pbkdf2_sha256$720000$salt$hash...
#
# Format: <algorithm>$<iterations>$<salt>$<hash>
#
# Proses verify password saat login:
# 1. User input: "admin123"
# 2. Django ambil salt dari database
# 3. Hash "admin123" + salt menggunakan PBKDF2
# 4. Bandingkan hasil hash dengan hash di database
# 5. Jika SAMA → password benar
#
# KENAPA aman?
# - Tidak bisa di-reverse (one-way hashing)
# - Salt unik per user (mencegah rainbow table attack)
# - 720.000 iterasi (brute-force sangat lambat)

# Password Validators di settings.py:
AUTH_PASSWORD_VALIDATORS = [
    # 1. Tidak boleh mirip username/email:
    {"NAME": "...UserAttributeSimilarityValidator"},
    # 2. Minimal 8 karakter:
    {"NAME": "...MinimumLengthValidator"},
    # 3. Tidak boleh password umum ("123456", "password"):
    {"NAME": "...CommonPasswordValidator"},
    # 4. Tidak boleh hanya angka:
    {"NAME": "...NumericPasswordValidator"},
]
```

---

## H. Decorators & Proteksi View — @login_required & Variasi

### Melindungi View dari User yang Belum Login:

```python
# ═══ CARA 1: Decorator @login_required (untuk Function-Based View) ═══
from django.contrib.auth.decorators import login_required

@login_required
def pos_api_create(request):
    """
    Decorator @login_required:
    - Cek: request.user.is_authenticated?
    - Jika belum login → redirect ke LOGIN_URL (/login/)
    - Jika sudah login → jalankan fungsi
    
    Kenapa ada parameter 'next'?
    - User akses /pos/api/create/ tapi belum login
    - Redirect ke /login/?next=/pos/api/create/
    - Setelah login → redirect kembali ke /pos/api/create/
    """
    pass  # ... logika POS

# ═══ CARA 2: LoginRequiredMixin (untuk Class-Based View) ═══
from django.contrib.auth.mixins import LoginRequiredMixin

class ProdukListView(LoginRequiredMixin, SubModulePermissionMixin, ListView):
    """
    LoginRequiredMixin harus di POSISI PERTAMA (paling kiri).
    
    Alur:
    1. LoginRequiredMixin.dispatch() → cek login
    2. SubModulePermissionMixin.dispatch() → cek RBAC permission
    3. ListView.dispatch() → jalankan get()/post()
    
    Kenapa urutan penting?
    Karena mixin dieksekusi dari KIRI ke KANAN.
    Cek login DULU, baru cek permission.
    """
    pass

# ═══ CARA 3: Di settings.py (untuk SELURUH project) ═══
LOGIN_URL = "/login/"              # URL halaman login
LOGOUT_REDIRECT_URL = "/login/"    # Setelah logout → ke login
LOGIN_REDIRECT_URL = "/"           # Setelah login → ke dashboard
```

### Logout — Menghapus Sesi:

```python
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    # Apa yang terjadi:
    # 1. Session di database DIHAPUS
    # 2. Cookie sessionid di browser DIHAPUS
    # 3. request.user menjadi AnonymousUser
    # 4. Redirect ke LOGOUT_REDIRECT_URL (/login/)
    return redirect("login")
```

---

## I. Integrasi Auth ↔ RBAC — Alur Lengkap End-to-End

```
┌──────── USER BARU ─────────────────────────────────────────────────┐
│                                                                     │
│  1. REGISTER  ──► User created ──► Profile created (role=USER)     │
│                                                                     │
│  2. ADMIN mengubah role:                                           │
│     User Management → Edit User → Set role = KASIR                │
│     → Profile.role = 'KASIR'                                      │
│                                                                     │
│  3. ADMIN mengatur permission:                                     │
│     Permission Management → Role: KASIR                            │
│     → Centang: POS (view ✅, create ✅)                           │
│     → Centang: Produk > Daftar Produk (view ✅ saja)             │
│     → Simpan → RolePermission records dibuat                      │
│                                                                     │
│  4. User LOGIN:                                                    │
│     → Session dibuat                                              │
│     → request.user tersedia di semua view                         │
│                                                                     │
│  5. User AKSES HALAMAN:                                            │
│     GET /produk/list/                                              │
│     → LoginRequiredMixin: sudah login? ✅                         │
│     → SubModulePermissionMixin:                                    │
│       has_permission(user, 'read', 'produk', 'daftar_produk')    │
       → Cache/DB: can_view = True → ✅ DIIZINKAN                │
│                                                                     │
│  6. User COBA TAMBAH PRODUK:                                      │
│     GET /produk/tambah/                                            │
│     → SubModulePermissionMixin:                                    │
│       has_permission(user, 'create', 'produk', 'daftar_produk')  │
       → Cache/DB: can_create = False → ❌ 403 FORBIDDEN          │
│                                                                     │
│  7. SIDEBAR hanya tampilkan menu sesuai permission:                │
│     ├── Dashboard  ✅ (can_view=True)                             │
│     ├── POS        ✅ (can_view=True)                             │
│     └── Produk     ✅ (can_view=True, tapi tanpa tombol Tambah)  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

*Lanjut ke [08_FITUR_MODUL_ERP.md](08_FITUR_MODUL_ERP.md) →*
