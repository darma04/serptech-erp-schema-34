# 🔌 13 — API & AJAX di Project ERP — Panduan Lengkap

## DAFTAR ISI
- [A. Apa itu API?](#a-apa-itu-api)
- [B. Apakah ERP Kita Punya API?](#b-apakah-erp-kita-punya-api)
- [C. Pola AJAX di Project ERP](#c-pola-ajax-di-project-erp)
- [D. CSRF Token — Keamanan Form & AJAX](#d-csrf-token)
- [E. Contoh Lengkap: AJAX Delete](#e-contoh-lengkap-ajax-delete)
- [F. Contoh Lengkap: AJAX Search (Select2)](#f-contoh-lengkap-ajax-search)
- [G. json_script — Bridge Data Python → JavaScript](#g-json_script)
- [H. Membuat Endpoint AJAX Baru](#h-membuat-endpoint-ajax-baru)

---

## A. Apa itu API?

### Definisi:

```
API = Application Programming Interface
    = Cara 2 program BERKOMUNIKASI satu sama lain

Analogi:
┌────────────────────────────────────────────────────────┐
│ API ≈ PELAYAN RESTORAN                                │
│                                                        │
│ Kamu (Frontend)      → Pesan makanan (request)        │
│ Pelayan (API)        → Antar pesanan ke dapur         │
│ Dapur (Backend/DB)   → Masak makanan (proses data)    │
│ Pelayan (API)        → Antar makanan kembali (response)│
│ Kamu                 → Makan (tampilkan data)         │
│                                                        │
│ Kamu TIDAK PERNAH masuk ke dapur langsung!            │
│ Selalu melalui pelayan (API).                         │
└────────────────────────────────────────────────────────┘
```

### Jenis API:

```
1. REST API (RESTful)
   → Endpoint URL yang return DATA (JSON/XML)
   → Contoh: GET /api/produk/ → return JSON list produk
   → Framework populer: Django REST Framework (DRF)
   → Biasa dipakai untuk: Mobile app, SPA (React/Vue), integrasi

2. Internal AJAX Endpoint
   → URL yang return JSON, tapi BUKAN REST API formal
   → Tidak ada autentikasi token (pakai session cookie)
   → Tidak ada versioning (/api/v1/...)
   → Dipakai oleh JavaScript di halaman yang SAMA
   → ← INI yang dipakai di project ERP kita!

3. GraphQL API
   → Query language untuk API (tidak digunakan di project ini)
```

---

## B. Apakah ERP Kita Punya API?

### Jawaban: TIDAK punya REST API formal, TAPI punya AJAX endpoints.

```
Project ERP ini = Server-Side Rendered (SSR):
→ Django render HTML di server → kirim ke browser
→ BUKAN Single Page Application (SPA)
→ BUKAN Mobile App yang butuh REST API

TAPI ada "mini API" dalam bentuk AJAX endpoints:
→ URL yang return JsonResponse (bukan HTML)
→ Dipanggil oleh JavaScript di browser
→ Contoh: hapus data, search produk, update status
```

### Semua AJAX Endpoints di Project:

| URL | Method | Fungsi | File |
|-----|--------|--------|------|
| `/produk/<id>/delete/` | DELETE | Hapus produk | `apps/produk/views.py` |
| `/produk/kategori/<id>/delete/` | DELETE | Hapus kategori | `apps/produk/views.py` |
| `/penjualan/so/<id>/delete/` | DELETE | Hapus Sales Order | `apps/penjualan/views.py` |
| `/pembelian/po/<id>/delete/` | DELETE | Hapus Purchase Order | `apps/pembelian/views.py` |
| `/inventory/transfer/<id>/delete/` | DELETE | Hapus transfer stok | `apps/inventory/views.py` |
| `/inventory/gudang/<id>/delete/` | DELETE | Hapus gudang | `apps/inventory/views.py` |
| `/hr/karyawan/<id>/delete/` | DELETE | Hapus karyawan | `apps/hr/views.py` |
| `/biaya/<id>/delete/` | DELETE | Hapus biaya | `apps/biaya/views.py` |
| `/access/roles/<id>/delete/` | POST | Hapus role | `apps/permission_management/views_roles.py` |
| `/pos/complete/` | POST | Selesaikan POS | `apps/pos/views.py` |
| `/produk/search/` | GET | Search produk (Select2) | `apps/produk/views.py` |

---

## C. Pola AJAX di Project ERP

### Apa itu AJAX?

```
AJAX = Asynchronous JavaScript And XML
     = Teknik kirim/terima data TANPA reload halaman

Tanpa AJAX:
1. User klik hapus → Browser reload → Server proses → Kirim HTML baru → Render ulang
   (Layar putih sebentar — UX buruk)

Dengan AJAX:
1. User klik hapus → JavaScript kirim request di background
2. Server proses → Kirim response JSON (kecil)
3. JavaScript update halaman TANPA reload
   (Halaman tidak berkedip — UX bagus)
```

### Pola Standar AJAX di Project:

```
┌──────────── FRONTEND ─────────────┐    ┌──────── BACKEND ────────┐
│                                    │    │                          │
│ 1. User klik "Hapus"              │    │                          │
│    ↓                               │    │                          │
│ 2. confirmDelete(id, nama)        │    │                          │
│    → Tampilkan modal konfirmasi   │    │                          │
│    ↓                               │    │                          │
│ 3. User klik "Ya, Hapus"         │    │                          │
│    ↓                               │    │                          │
│ 4. fetch('/produk/5/delete/', {   │──→ │ 5. DeleteView.delete()  │
│        method: 'DELETE',           │    │    → produk.delete()     │
│        headers: {                  │    │    → return JsonResponse │
│          'X-CSRFToken': token      │    │      {success: true}     │
│        }                           │    │                          │
│    })                              │    │                          │
│    ↓                               │ ←──│                          │
│ 6. .then(response => {            │    │                          │
│       if (data.success)            │    │                          │
│         location.reload()          │    │                          │
│       else                         │    │                          │
│         alert(data.message)        │    │                          │
│    })                              │    │                          │
└────────────────────────────────────┘    └──────────────────────────┘
```

---

## D. CSRF Token — Keamanan Form & AJAX

### Apa itu CSRF?

```
CSRF = Cross-Site Request Forgery
     = Serangan di mana website LAIN mengirimkan request
       ke server KITA atas nama user yang sedang login.

Contoh serangan:
1. User login ke ERP kita (session aktif)
2. User buka website jahat di tab lain
3. Website jahat punya form tersembunyi:
   <form action="https://erp-kita.com/produk/5/delete/" method="POST">
   <script>document.forms[0].submit()</script>
4. Browser kirim request KE SERVER KITA dengan cookie user!
5. Server kira ini request sah → data TERHAPUS!

CSRF Token mencegah ini:
→ Setiap form punya token RAHASIA yang hanya diketahui server
→ Website lain TIDAK tahu token ini → request ditolak
```

### Cara Pakai di Form HTML:

```html
<form method="POST">
    {% csrf_token %}
    {# Output: <input type="hidden" name="csrfmiddlewaretoken" value="abc123..."> #}
    ... field-field form ...
</form>
```

### Cara Pakai di AJAX:

```javascript
// Cara 1: Ambil dari hidden input (jika ada {% csrf_token %} di halaman)
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Cara 2: Ambil dari cookie
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Kirim di header request:
fetch('/produk/5/delete/', {
    method: 'DELETE',
    headers: {
        'X-CSRFToken': csrfToken,      // ← Header wajib untuk POST/PUT/DELETE
        'Content-Type': 'application/json',
    }
});
```

---

## E. Contoh Lengkap: AJAX Delete

### Backend (Python):

```python
# apps/produk/views.py

class ProdukDeleteView(SubModulePermissionMixin, DeleteView):
    model = Produk
    permission_module = 'produk'
    permission_sub_module = 'daftar_produk'
    permission_action = 'delete'
    
    def delete(self, request, *args, **kwargs):
        try:
            produk = self.get_object()       # Ambil produk berdasarkan pk di URL
            nama = produk.nama
            
            # Cek apakah produk memiliki relasi yang menghalangi delete
            if produk.salesorderitem_set.exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Tidak bisa menghapus "{nama}" — masih ada di Sales Order'
                }, status=400)
            
            produk.delete()
            return JsonResponse({
                'success': True,
                'message': f'Produk "{nama}" berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Gagal: {str(e)}'
            }, status=500)
```

### Frontend (JavaScript):

```javascript
// ═══ DI TEMPLATE HTML ═══

// Tombol hapus di setiap row tabel:
// <button onclick="confirmDelete({{ produk.pk }}, '{{ produk.nama }}')">Hapus</button>

let deleteId = null;

function confirmDelete(id, nama) {
    deleteId = id;
    document.getElementById('deleteName').textContent = nama;
    // Buka modal konfirmasi Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Event listener tombol "Ya, Hapus" di modal
document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    if (!deleteId) return;
    
    const btn = this;
    // Disable tombol + tampilkan spinner (mencegah double-click)
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Menghapus...';
    
    // Kirim AJAX DELETE request
    fetch(`/produk/${deleteId}/delete/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Berhasil → reload halaman
            location.reload();
        } else {
            // Gagal → tampilkan error
            alert(data.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="ri-delete-bin-line me-1"></i>Ya, Hapus';
        }
    })
    .catch(error => {
        alert('Terjadi kesalahan jaringan');
        btn.disabled = false;
    });
});
```

---

## F. Contoh Lengkap: AJAX Search (Select2)

### Backend — Search Endpoint:

```python
# apps/produk/views.py

class ProdukSearchView(SubModulePermissionMixin, ListView):
    """
    AJAX endpoint untuk search produk (dipakai oleh Select2 dropdown).
    
    URL: /produk/search/?q=keyword
    Response: JSON list produk yang cocok
    """
    permission_module = 'produk'
    permission_action = 'read'
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        produk = Produk.objects.filter(
            nama__icontains=query      # Case-insensitive LIKE '%query%'
        )[:20]                         # Limit 20 hasil
        
        # Format untuk Select2:
        results = [
            {
                'id': p.pk,
                'text': p.nama,
                'sku': p.sku,
                'harga': float(p.harga_jual),
                'stok': p.stok,
            }
            for p in produk
        ]
        
        return JsonResponse({
            'results': results,
            'pagination': {'more': False}
        })
```

### Frontend — Select2 AJAX:

```javascript
// Inisialisasi Select2 dengan AJAX search
$('#produk-dropdown').select2({
    placeholder: 'Cari produk...',
    minimumInputLength: 2,          // Mulai search setelah 2 karakter
    
    ajax: {
        url: '/produk/search/',     // URL endpoint backend
        dataType: 'json',
        delay: 300,                 // Tunggu 300ms sebelum request (debounce)
        
        data: function(params) {
            return { q: params.term };  // Kirim keyword sebagai ?q=keyword
        },
        
        processResults: function(data) {
            return { results: data.results };
        }
    },
    
    // Custom format tampilan hasil search:
    templateResult: function(item) {
        if (!item.id) return item.text;
        return $(`
            <div class="d-flex justify-content-between">
                <span><strong>${item.text}</strong> (${item.sku})</span>
                <span class="text-muted">Stok: ${item.stok}</span>
            </div>
        `);
    }
});
```

---

## G. json_script — Bridge Data Python → JavaScript

### Kenapa Pakai json_script?

```
Masalah: Bagaimana mengirim data dari Python ke JavaScript?

Cara LAMA (rentan XSS):
  <script>
  var data = "{{ data_python }}";
  // Jika data mengandung </script> → RUSAK!
  // Jika data mengandung ' atau " → RUSAK!
  </script>

Cara AMAN (json_script):
  {{ data|json_script:"my-data" }}
  → Django auto-escape semua karakter berbahaya
  → Aman dari XSS attack
```

### Cara Pakai:

```python
# views.py — kirim data
context['chart_data'] = [100, 200, 300, 400]
context['chart_labels'] = ['Jan', 'Feb', 'Mar', 'Apr']
context['user_info'] = {'nama': 'Admin', 'role': 'Super Admin'}
```

```html
{# template.html — bridge ke JavaScript #}

{# Langkah 1: Inject data sebagai JSON di HTML #}
{{ chart_data|json_script:"chart-data" }}
{{ chart_labels|json_script:"chart-labels" }}
{{ user_info|json_script:"user-info" }}

{# Output HTML (aman!): #}
{# <script id="chart-data" type="application/json">[100, 200, 300, 400]</script> #}
{# <script id="chart-labels" type="application/json">["Jan", "Feb", "Mar", "Apr"]</script> #}
{# <script id="user-info" type="application/json">{"nama": "Admin", "role": "Super Admin"}</script> #}

{# Langkah 2: Baca dari JavaScript #}
<script>
const chartData = JSON.parse(document.getElementById('chart-data').textContent);
// chartData = [100, 200, 300, 400]

const chartLabels = JSON.parse(document.getElementById('chart-labels').textContent);
// chartLabels = ['Jan', 'Feb', 'Mar', 'Apr']

const userInfo = JSON.parse(document.getElementById('user-info').textContent);
// userInfo = {nama: 'Admin', role: 'Super Admin'}
</script>
```

---

## H. Membuat Endpoint AJAX Baru

### Langkah-Langkah:

```python
# ═══ LANGKAH 1: Buat view yang return JsonResponse ═══
# apps/produk/views.py

from django.http import JsonResponse

class ProdukToggleAktifView(SubModulePermissionMixin, UpdateView):
    """Toggle status aktif/nonaktif produk via AJAX."""
    model = Produk
    permission_module = 'produk'
    permission_action = 'write'
    
    def post(self, request, *args, **kwargs):
        produk = self.get_object()
        produk.aktif = not produk.aktif   # Toggle boolean
        produk.save()
        return JsonResponse({
            'success': True,
            'aktif': produk.aktif,
            'message': f'{produk.nama} {"diaktifkan" if produk.aktif else "dinonaktifkan"}'
        })


# ═══ LANGKAH 2: Tambah URL ═══
# apps/produk/urls.py

path('<int:pk>/toggle-aktif/', views.ProdukToggleAktifView.as_view(), name='toggle_aktif'),


# ═══ LANGKAH 3: Panggil dari JavaScript ═══
```

```javascript
// Di template:
function toggleAktif(id) {
    fetch(`/produk/${id}/toggle-aktif/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            // Update badge di tabel tanpa reload
            const badge = document.querySelector(`#status-${id}`);
            if (data.aktif) {
                badge.className = 'badge bg-label-success';
                badge.textContent = 'Aktif';
            } else {
                badge.className = 'badge bg-label-danger';
                badge.textContent = 'Nonaktif';
            }
        }
    });
}
```

---

*Lanjut ke [14_TEMPLATE_TAGS_DAN_FILTERS.md](14_TEMPLATE_TAGS_DAN_FILTERS.md) →*
