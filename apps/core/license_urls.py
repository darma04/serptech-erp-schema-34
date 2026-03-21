"""
URL patterns untuk halaman aktivasi lisensi.
"""
from django.urls import path
from apps.core.license_views import license_activation_view, license_status_view

urlpatterns = [
    path('license/', license_activation_view, name='license_activation'),
    path('license/status/', license_status_view, name='license_status'),
]
