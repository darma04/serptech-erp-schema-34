"""
==========================================================================
 ACTIVITY LOG VIEWS - Halaman Log Aktivitas User
==========================================================================
 File ini berisi view untuk menampilkan halaman log aktivitas user.
 Hanya ada 1 view: ActivityLogIndexView — daftar semua aktivitas.

 Pola yang digunakan:
 - ListView (Django CBV) → Menampilkan daftar data dengan pagination otomatis
 - ReadPermissionMixin → Cek permission 'read' pada modul 'activity_log'
 - @login_required → Hanya user yang sudah login yang bisa akses
 - TemplateLayout.init() → Menambahkan data sidebar, navbar, tema ke context

 Fitur filtering via URL query string:
 - ?start=2026-01-01 → Filter mulai tanggal
 - ?end=2026-01-31 → Filter sampai tanggal
 - ?action=create → Filter jenis aksi
 - ?user=5 → Filter berdasarkan user ID

 URL: /activity-log/ → name='activity_log:index'
==========================================================================
"""
from django.shortcuts import render
# Import dari framework Django
from django.contrib.auth.decorators import login_required
# Import dari framework Django
from django.views.generic import ListView
# Import dari framework Django
from django.utils.decorators import method_decorator
from web_project import TemplateLayout
# Import dari modul internal proyek
from .models import UserActivity
# Import dari framework Django
from django.contrib.auth.models import User
# Import dari modul internal proyek
from apps.core.mixins import ReadPermissionMixin


# ╔══════════════════════════════════════════════════════════════╗
# ║ VIEW: Daftar Log Aktivitas (Read-only)                      ║
# ╚══════════════════════════════════════════════════════════════╝
@method_decorator(login_required, name='dispatch')
class ActivityLogIndexView(ReadPermissionMixin, ListView):
    """
    View untuk menampilkan daftar log aktivitas user.

    Atribut CBV yang dikonfigurasi:
    - model: Model yang akan di-query (UserActivity)
    - template_name: File HTML yang digunakan
    - context_object_name: Nama variabel di template ('activities')
    - paginate_by: Jumlah item per halaman (25)
    - ordering: Urutan data (terbaru dulu)
    - permission_module: Modul yang dicek permission-nya
    """
    model = UserActivity
    template_name = 'activity_log/index.html'
    context_object_name = 'activities'
    paginate_by = 25                    # Tampilkan 25 record per halaman
    ordering = ['-timestamp']           # Urutkan dari yang terbaru
    permission_module = 'activity_log'  # Cek permission modul 'activity_log'

    def get_queryset(self):
        """
        Override get_queryset() untuk menambahkan filter dinamis.
        Filter diambil dari URL query parameter (?start=...&end=...&action=...&user=...).
        Setiap filter bersifat opsional — hanya diterapkan jika nilainya ada.
        """
        queryset = super().get_queryset()

        # Ambil parameter filter dari URL query string
        start_date = self.request.GET.get('start')   # Tanggal mulai
        end_date = self.request.GET.get('end')        # Tanggal akhir
        action = self.request.GET.get('action')       # Jenis aksi (login, create, dll)
        user_id = self.request.GET.get('user')        # ID user tertentu

        # Terapkan filter jika parameter tersedia
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)  # >= tanggal mulai
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)    # <= tanggal akhir
        if action:
            queryset = queryset.filter(action=action)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Override get_context_data() untuk menambahkan data tambahan ke template.
        TemplateLayout.init() menambahkan data sidebar, navbar, dan tema.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Data untuk dropdown filter di template
        context['user_list'] = User.objects.all().order_by('username')
        context['action_choices'] = UserActivity.ACTION_CHOICES
        # Metrik ringkasan total aktivitas (setelah filter)
        queryset = self.get_queryset()
        context['total_activities'] = queryset.count()
        return context
