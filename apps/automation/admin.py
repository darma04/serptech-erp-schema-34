"""
==========================================================================
 AUTOMATION ADMIN - Registrasi Model ke Django Admin
==========================================================================
 Mendaftarkan model-model automasi ke panel Django Admin (/admin/).
 Ini memungkinkan superuser mengelola data langsung via admin panel:
 - PengaturanTelegram: Konfigurasi bot Telegram
 - TemplatePesan: Template pesan notifikasi
 - LogNotifikasi: Riwayat pengiriman notifikasi
==========================================================================
"""
from django.contrib import admin
# Import dari modul internal proyek
from .models import PengaturanTelegram, TemplatePesan, LogNotifikasi

# Daftarkan model ke Django Admin dengan registrasi sederhana
# Untuk kustomisasi tampilan admin, bisa menggunakan ModelAdmin class
admin.site.register(PengaturanTelegram)
admin.site.register(TemplatePesan)
admin.site.register(LogNotifikasi)
