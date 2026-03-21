"""
==========================================================================
 SAMPLE URLS - Routing Halaman Contoh Starter Kit
==========================================================================
 URL routing untuk halaman contoh bawaan starter kit.
 Halaman menggunakan SampleView dengan template_name berbeda.
==========================================================================
"""
from django.urls import path
from .views import SampleView


urlpatterns = [
    # URL: /sample/ — 
    path(
        "",
        SampleView.as_view(template_name="index.html"),
        name="index",
    ),
    # URL: /sample/ — 
    path(
        "page_2/",
        SampleView.as_view(template_name="page_2.html"),
        name="page-2",
    ),
]
