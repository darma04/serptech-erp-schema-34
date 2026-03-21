"""
==========================================================================
 ACTIVITY LOG MIDDLEWARE - Middleware Pencatatan Aktivitas
==========================================================================
 File ini berisi middleware dan utility function yang KRITIS untuk
 sistem logging aktivitas. Tanpa middleware ini, signals tidak bisa
 mengetahui USER MANA yang melakukan perubahan data.

 Apa itu Middleware di Django?
 - Middleware adalah "lapisan tengah" antara request dan response
 - Setiap HTTP request melewati SEMUA middleware secara berurutan
 - Digunakan untuk: autentikasi, logging, CORS, dll
 - Didaftarkan di settings.py → MIDDLEWARE = [...]

 Alur kerja middleware ini:
 ┌─────────────┐    ┌──────────────────┐    ┌──────────┐
 │ HTTP Request │───▶│ process_request  │───▶│ View/API │
 │  masuk       │    │ Simpan request   │    │ diproses │
 └─────────────┘    │ ke thread-local  │    └──────────┘
                    └──────────────────┘         │
 ┌─────────────┐    ┌──────────────────┐         │
 │ HTTP Response│◀──│ process_response │◀────────┘
 │ keluar       │    │ Hapus thread-local│
 └─────────────┘    └──────────────────┘

 Apa itu Thread-Local Storage?
 - Variabel yang unik per thread (setiap request = 1 thread)
 - Aman untuk multi-user concurrent — data tidak tercampur
 - Digunakan agar signals (yang tidak menerima request) bisa
   mengakses info request/user saat ini

 Terhubung dengan:
 - signals.py → Memanggil get_current_request() untuk mendapat user
 - settings.py → MIDDLEWARE list (harus terdaftar)
==========================================================================
"""
from django.utils.deprecation import MiddlewareMixin
# Import dari modul internal proyek
from .models import UserActivity
from threading import local


# Thread-local storage: variabel global yang unik per thread/request
# Setiap user yang mengakses aplikasi mendapat "ruang" tersendiri
_thread_locals = local()


def get_current_request():
    """
    Mengambil objek request HTTP yang sedang aktif dari thread-local.
    Dipanggil oleh signals.py untuk mengetahui user yang sedang login.
    Return None jika tidak ada request aktif.
    """
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """
    Menyimpan objek request ke thread-local storage.
    Dipanggil saat request masuk (process_request).
    """
    _thread_locals.request = request


class ActivityLogMiddleware(MiddlewareMixin):
    """
    Middleware utama untuk sistem logging aktivitas.

    Tugas utama:
    1. Menyimpan request ke thread-local saat request masuk
    2. Membersihkan thread-local saat response keluar
    3. Menyediakan static method log_activity() untuk manual logging dari views
    """

    def process_request(self, request):
        """
        Dipanggil otomatis SETIAP request masuk (sebelum view diproses).
        Menyimpan request di thread-local agar bisa diakses oleh signals.
        """
        set_current_request(request)
        request._activity_logged = False  # Flag anti-duplikasi log
        return None

    def process_response(self, request, response):
        """
        Dipanggil otomatis SETIAP response keluar (setelah view selesai).
        Membersihkan thread-local agar tidak bocor ke request berikutnya.
        """
        set_current_request(None)
        return response

    def get_client_ip(self, request):
        """
        Mengambil IP address client dari HTTP headers.
        Mendukung reverse proxy (X-Forwarded-For) dan koneksi langsung.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Ambil IP pertama dari chain proxy
        else:
            ip = request.META.get('REMOTE_ADDR')  # IP langsung dari koneksi
        return ip

    @staticmethod
    def log_activity(request, action, model_name=None, object_id=None, object_repr=None, description=None, changes=None):
        """
        Static method untuk mencatat aktivitas secara manual dari views.
        Digunakan ketika auto-logging via signals tidak cukup
        (contoh: export data, approve transaksi, dll).

        Parameter:
        - request: HTTP request object (wajib)
        - action: Jenis aksi ('create', 'update', 'delete', 'export', dll)
        - model_name: Nama model yang terlibat (opsional)
        - object_id: ID objek yang diubah (opsional)
        - object_repr: Representasi string objek (opsional)
        - description: Deskripsi aktivitas (opsional)
        - changes: Dict perubahan field {field: {old: x, new: y}} (opsional)
        """
        if not request.user.is_authenticated:
            return

        # Cegah duplikasi log — satu request hanya boleh log 1x via method ini
        if hasattr(request, '_activity_logged') and request._activity_logged:
            return

        # Blok penanganan error — coba jalankan kode di bawah
        try:
            # Buat record baru di database
            activity = UserActivity.objects.create(
                user=request.user,
                action=action,
                model_name=model_name,
                object_id=str(object_id) if object_id else None,
                object_repr=object_repr,
                description=description,
                ip_address=ActivityLogMiddleware().get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )

            # Simpan detail perubahan (JSON) jika ada
            if changes:
                activity.set_changes(changes)
                activity.save()

            request._activity_logged = True  # Tandai bahwa log sudah dibuat
        # Tangkap error Exception — lanjutkan tanpa crash
        except Exception as e:
            # Silent fail — jangan ganggu proses utama user
            # Logging gagal tidak boleh menyebabkan error di fitur utama
            pass
