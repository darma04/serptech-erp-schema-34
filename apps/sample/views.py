"""
==========================================================================
 SAMPLE VIEWS - View Contoh/Template Bawaan Starter Kit
==========================================================================
 Modul sample adalah template bawaan dari starter kit.
 Menyediakan contoh view dasar menggunakan TemplateLayout.
 Dapat digunakan sebagai referensi untuk membuat modul baru.

 Terhubung dengan:
 - web_project → TemplateLayout untuk inisialisasi layout global
 - sample/urls.py → Routing halaman contoh
==========================================================================
"""
from django.views.generic import TemplateView
from web_project import TemplateLayout


class SampleView(TemplateView):
    """
    View contoh bawaan starter kit.
    Template ditentukan via parameter di urls.py.
    """
    # Menambahkan data konteks tambahan ke template
    def get_context_data(self, **kwargs):
        # Inisialisasi layout global (tema, warna, sidebar, dll)
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
