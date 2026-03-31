/**
 * ==========================================================================
 *  MODAL EDIT ROLE — Handler untuk Edit Role dan Permission
 * ==========================================================================
 *  File ini menangani proses edit role yang sudah ada, termasuk:
 *  1. Load data role dan permission dari server via AJAX
 *  2. Render checkbox permission di dalam modal
 *  3. Populate checkbox sesuai permission yang sudah ada
 *  4. Submit perubahan ke server via AJAX
 *
 *  Optimisasi v2.0:
 *  - Checkbox hanya di-render sekali (tidak double render)
 *  - Loading state ditampilkan saat mengambil data
 *  - Guard variable untuk mencegah re-render yang tidak perlu
 *
 *  Alur kerja edit role:
 *  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
 *  │ User klik    │    │ AJAX GET     │    │ Render       │    │ AJAX POST    │
 *  │ tombol Edit  │───→│ ambil data   │───→│ checkbox &   │───→│ simpan       │
 *  │ di tabel     │    │ role dari    │    │ centang sesuai│    │ perubahan    │
 *  └──────────────┘    │ server       │    │ data server  │    └──────────────┘
 *                      └──────────────┘    └──────────────┘
 *
 *  Terhubung dengan:
 *  - templates/access/roles.html → Template yang memuat modal edit
 *  - permission_management.js → Fungsi renderPermissionCheckboxes() (shared)
 *  - apps/user_management/views.py → Endpoint:
 *    /access/roles/ajax/{role_code}/data/ (GET data)
 *    /access/roles/ajax/{role_code}/update/ (POST update)
 *  - apps/core/models.py → Model RolePermission di database
 *
 *  Dependensi:
 *  - Bootstrap 5 (Modal) → Popup form edit
 *  - SweetAlert2 (Swal) → Notifikasi toast
 * ==========================================================================
 */

// IIFE — membungkus kode agar variabel tidak bocor ke scope global
(function() {
    'use strict';  // Mode ketat JavaScript

    // ═══════════════════════════════════════════════════════
    // VARIABEL STATE — Melacak status rendering checkbox
    // ═══════════════════════════════════════════════════════

    // Guard variable: apakah checkbox sudah pernah di-render?
    // Mencegah double render yang menyebabkan checkbox duplikat
    let checkboxesRendered = false;

    // Role code yang sedang diedit (misal: "KASIR", "ADMIN")
    // Digunakan untuk mengirim data ke endpoint yang benar
    let currentRoleCode = null;

    // ═══════════════════════════════════════════════════════
    // INISIALISASI — Setup event listener setelah DOM siap
    // ═══════════════════════════════════════════════════════
    document.addEventListener('DOMContentLoaded', function() {
        const modal = document.getElementById('editRoleModal');
        const form = document.getElementById('editRoleForm');

        if (!modal || !form) return;  // Skip jika elemen tidak ada

        // ─── EVENT MODAL DIBUKA ───
        // 'show.bs.modal' = event Bootstrap saat modal AKAN ditampilkan
        // event.relatedTarget = tombol yang memicu pembukaan modal
        // Atribut data-role-code = kode role yang akan diedit
        modal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;  // Tombol "Edit" yang diklik

            if (button) {
                // Ambil role_code dari atribut data-role-code di tombol
                // Contoh HTML: <button data-role-code="KASIR">Edit</button>
                var roleCode = button.getAttribute('data-role-code');
                if (roleCode) {
                    console.log('[EditRole] Loading data for role:', roleCode);
                    loadRoleDataForEdit(roleCode);  // Muat data dari server
                }
            }
        });

        // ─── EVENT MODAL DITUTUP ───
        // 'hidden.bs.modal' = event setelah modal selesai tertutup
        // Reset currentRoleCode tapi JANGAN reset checkboxesRendered
        // (agar checkbox yang sudah di-render bisa di-reuse)
        modal.addEventListener('hidden.bs.modal', function() {
            currentRoleCode = null;
            // Catatan: Tidak mereset checkboxesRendered agar DOM checkbox
            // yang sudah ada bisa digunakan kembali (lebih efisien)
        });

        // ─── EVENT SUBMIT FORM ───
        form.addEventListener('submit', function(e) {
            e.preventDefault();        // Cegah submit bawaan browser
            submitEditRole(form);      // Kirim via AJAX
        });
    });

    // ─────────────────────────────────────────────────────────
    // LOAD ROLE DATA — Muat Data Role dari Server untuk Edit
    // ─────────────────────────────────────────────────────────
    // Mengambil data role (nama + daftar permission) dari server
    // via AJAX GET, lalu mengisi form edit dengan data tersebut.
    //
    // Alur:
    // 1. Set role_code di hidden input
    // 2. Cek apakah checkbox sudah di-render sebelumnya
    // 3. Jika belum → tampilkan loading spinner
    // 4. Jika sudah → uncheck semua checkbox (reset)
    // 5. Fetch data dari server
    // 6. Render checkbox jika belum ada
    // 7. Centang checkbox sesuai permission dari server
    //
    // Parameter:
    //   roleCode (string) — Kode role yang diedit (misal: "KASIR")
    // ─────────────────────────────────────────────────────────
    function loadRoleDataForEdit(roleCode) {
        // Referensi ke elemen-elemen form
        const roleCodeInput = document.getElementById('editRoleCode');     // Hidden input untuk role_code
        const roleNameInput = document.getElementById('editRoleName');     // Input nama role
        const container = document.getElementById('editPermissionCheckboxContainer');  // Container checkbox

        if (!roleCodeInput) return;

        // Set role code di hidden input (akan dikirim saat submit)
        roleCodeInput.value = roleCode;
        currentRoleCode = roleCode;

        // Cek apakah checkbox sudah pernah di-render (ada checkbox di container?)
        const alreadyRendered = container && container.querySelectorAll('input[type="checkbox"]').length > 0;

        if (!alreadyRendered && container) {
            // ─── PERTAMA KALI: Tampilkan Loading ───
            // Ganti isi container dengan spinner loading
            container.innerHTML = '<div class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Memuat permissions...</div>';
        } else if (alreadyRendered) {
            // ─── SUDAH ADA: Uncheck Semua ───
            // Reset semua checkbox ke unchecked sebelum mengisi data baru
            container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        }

        // ─── FETCH DATA DARI SERVER ───
        // GET request ke endpoint Django yang mengembalikan JSON:
        // { success: true, role_display: "Kasir", permissions: [...] }
        fetch(`/access/roles/ajax/${roleCode}/data/`)
            .then(response => response.json())
            .then(data => {
                console.log('[EditRole] Data loaded:', data);

                if (data.success) {
                    // Set nama role di input text
                    if (roleNameInput) {
                        // Jika server mengirim role_display, gunakan itu
                        // Jika tidak, konversi role_code: "KEPALA_GUDANG" → "Kepala Gudang"
                        roleNameInput.value = data.role_display || roleCode.replace(/_/g, ' ');
                    }

                    // Render checkbox hanya jika belum pernah di-render
                    // renderPermissionCheckboxes() = fungsi global dari file lain
                    if (!alreadyRendered && typeof renderPermissionCheckboxes === 'function') {
                        renderPermissionCheckboxes('editPermissionCheckboxContainer', 'edit');
                    }

                    // ─── POPULATE CHECKBOX ───
                    // requestAnimationFrame() = menunggu browser selesai render DOM
                    // Diperlukan karena checkbox baru saja di-render dan mungkin
                    // belum ada di DOM pada saat ini (async rendering)
                    requestAnimationFrame(function() {
                        populatePermissionCheckboxes(data.permissions || []);
                    });
                } else {
                    // Server mengembalikan error
                    showAlert('error', data.message || 'Gagal memuat data role');
                    if (container) {
                        container.innerHTML = '<div class="alert alert-danger">Gagal memuat data permission</div>';
                    }
                }
            })
            .catch(error => {
                // Error jaringan (koneksi terputus, server down, dll)
                console.error('[EditRole] Error loading role data:', error);
                showAlert('error', 'Gagal memuat data role dari server');
                if (container) {
                    container.innerHTML = '<div class="alert alert-danger">Gagal memuat data permission</div>';
                }
            });
    }

    // ─────────────────────────────────────────────────────────
    // POPULATE PERMISSION CHECKBOXES — Centang Checkbox Sesuai Data
    // ─────────────────────────────────────────────────────────
    // Menerima array permission dari server dan mencentang checkbox
    // yang sesuai di form edit.
    //
    // Struktur data permission dari server:
    // [
    //   { module: "produk", sub_module: null, can_view: true, can_create: true, ... },
    //   { module: "produk", sub_module: "kategori", can_view: true, ... },
    // ]
    //
    // Logika:
    // - Jika sub_module ada → checkbox ID: edit_{module}_{sub_module}_view
    // - Jika sub_module null → checkbox ID: edit_{module}_{action}
    //
    // Parameter:
    //   permissions (Array) — Array objek permission dari server
    // ─────────────────────────────────────────────────────────
    function populatePermissionCheckboxes(permissions) {
        if (!Array.isArray(permissions)) return;

        // Uncheck SEMUA checkbox di form terlebih dahulu
        // Agar permission yang sudah dihapus di server juga ter-uncheck
        document.querySelectorAll('#editRoleForm input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });

        // Loop setiap permission dan centang checkbox yang sesuai
        permissions.forEach(perm => {
            const module = perm.module;         // Nama modul (misal: "produk")
            const subModule = perm.sub_module;  // Nama sub-modul (misal: "kategori") atau null

            if (subModule) {
                // ─── SUB-MODULE PERMISSION ───
                // Sub-modul hanya punya 1 checkbox: "Tampilkan" (view)
                // ID format: edit_{module}_{sub_module}_view
                // Contoh: edit_produk_kategori_view
                const cb = document.getElementById(`edit_${module}_${subModule}_view`);
                if (cb && perm.can_view) {
                    cb.checked = true;
                }
            } else {
                // ─── MODULE-LEVEL PERMISSION ───
                // Modul utama punya 4 checkbox CRUD: view, create, edit, delete
                // ID format: edit_{module}_{action}
                // Contoh: edit_produk_view, edit_produk_create
                const idPrefix = `edit_${module}_`;
                const actions = ['view', 'create', 'edit', 'delete'];

                actions.forEach(action => {
                    // Mapping action ke field name di data server
                    // 'view' → 'can_view', 'create' → 'can_create', dst
                    const fieldName = action === 'view' ? 'can_view' :
                                      action === 'create' ? 'can_create' :
                                      action === 'edit' ? 'can_edit' : 'can_delete';

                    // Centang jika permission bernilai true
                    if (perm[fieldName]) {
                        const cb = document.getElementById(`${idPrefix}${action}`);
                        if (cb) {
                            cb.checked = true;
                        }
                    }
                });
            }
        });

        console.log(`[EditRole] Populated ${permissions.length} permission records`);
    }

    // ─────────────────────────────────────────────────────────
    // SUBMIT EDIT ROLE — Kirim Perubahan ke Server
    // ─────────────────────────────────────────────────────────
    // Mengirim form edit role ke server via AJAX POST.
    // Menggunakan FormData yang secara otomatis mengumpulkan
    // semua input termasuk checkbox yang tercentang.
    //
    // Parameter:
    //   form (HTMLFormElement) — Form edit yang di-submit
    // ─────────────────────────────────────────────────────────
    function submitEditRole(form) {
        // FormData otomatis mengumpulkan semua field dari form
        const formData = new FormData(form);
        const roleCode = document.getElementById('editRoleCode').value;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;

        // Loading state — disable tombol dan tampilkan spinner
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Menyimpan...';

        // CSRF token untuk autentikasi request Django
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Kirim AJAX POST ke endpoint update
        // URL: /access/roles/ajax/{role_code}/update/
        fetch(`/access/roles/ajax/${roleCode}/update/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Header CSRF (wajib untuk POST di Django)
            },
            body: formData  // FormData dikirim sebagai multipart/form-data
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // ─── BERHASIL ───
                showAlert('success', data.message || 'Permissions berhasil diupdate!');

                // Tutup modal
                const modalEl = document.getElementById('editRoleModal');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) modalInstance.hide();

                // Reload halaman setelah 1.5 detik agar perubahan terlihat
                setTimeout(() => location.reload(), 1500);
            } else {
                // ─── GAGAL (dari server) ───
                showAlert('error', data.message || 'Gagal mengupdate permissions');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        })
        .catch(error => {
            // ─── ERROR JARINGAN ───
            console.error('[EditRole] Error saving role:', error);
            showAlert('error', 'Terjadi kesalahan saat menyimpan. Coba lagi.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    }

    // ─────────────────────────────────────────────────────────
    // SHOW ALERT — Tampilkan Notifikasi
    // ─────────────────────────────────────────────────────────
    // Menggunakan SweetAlert2 untuk notifikasi.
    // Perbedaan dengan showToast di file lain:
    // - Success: auto-close setelah 2 detik (lebih pendek)
    // - Error: TIDAK auto-close (user harus klik tombol)
    //
    // Parameter:
    //   type (string) — Tipe: 'success' atau 'error'
    //   message (string) — Pesan yang ditampilkan
    // ─────────────────────────────────────────────────────────
    function showAlert(type, message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: type === 'success' ? 'success' : 'error',
                title: type === 'success' ? 'Berhasil!' : 'Error!',
                text: message,
                timer: type === 'success' ? 2000 : undefined,       // Success: auto-tutup 2 detik. Error: tidak auto-tutup
                showConfirmButton: type !== 'success'                 // Error: tampilkan tombol OK
            });
        } else {
            // Fallback jika SweetAlert2 tidak tersedia
            alert(message);
        }
    }

})();  // Akhir IIFE
