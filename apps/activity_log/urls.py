"""
==========================================================================
 ACTIVITY LOG URLS - Routing URL Modul Log Aktivitas
==========================================================================
 Peta URL:
 - /activity-log/ → Halaman daftar log aktivitas (ActivityLogIndexView)

 app_name = 'activity_log' → Namespace untuk URL, digunakan di template
 sebagai {% url 'activity_log:index' %}

 Didaftarkan di config/urls.py: path('activity-log/', include('apps.activity_log.urls'))
==========================================================================
"""
from django.urls import path
from . import views

app_name = 'activity_log'  # Namespace URL — agar bisa dipanggil: {% url 'activity_log:index' %}

urlpatterns = [
    # Halaman utama: daftar semua log aktivitas user
    path('', views.ActivityLogIndexView.as_view(), name='index'),
]
