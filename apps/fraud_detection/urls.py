"""
==========================================================================
 FRAUD DETECTION URLS — Routing URL untuk Modul Fraud Detection
==========================================================================
 Semua URL di file ini di-include dari urls.py utama (config/urls.py)
 dengan prefix '/fraud/', sehingga URL lengkap menjadi:

 ┌────────────────────────────────────────────────────────────────────────┐
 │ URL                             │ View                    │ Name      │
 ├─────────────────────────────────┼─────────────────────────┼───────────┤
 │ /fraud/                         │ FraudDashboardView      │ dashboard │
 │ /fraud/alerts/                  │ FraudAlertListView      │ alert_list│
 │ /fraud/alerts/<pk>/             │ FraudAlertDetailView    │ detail    │
 │ /fraud/alerts/<pk>/update-status│ fraud_alert_update_stat │ update    │
 │ /fraud/alerts/export/           │ export_fraud_alerts_xls │ export    │
 │ /fraud/alerts/<pk>/delete/      │ fraud_alert_delete      │ delete    │
 │ /fraud/cash/                    │ CashReconListView       │ cash_list │
 │ /fraud/cash/create/             │ CashReconCreateView     │ create    │
 │ /fraud/cash/<pk>/edit/          │ cash_recon_edit          │ edit      │
 │ /fraud/cash/<pk>/review/        │ cash_recon_review        │ review    │
 │ /fraud/cash/<pk>/delete/        │ cash_recon_delete         │ delete    │
 │ /fraud/settings/                │ FraudSettingsView        │ settings  │
 └────────────────────────────────────────────────────────────────────────┘

 app_name = 'fraud_detection' → digunakan sebagai namespace untuk {% url %}
 Contoh di template: {% url 'fraud_detection:alert_list' %}
 Contoh di Python:   reverse('fraud_detection:dashboard')

 Terhubung dengan:
 → config/urls.py — include('apps.fraud_detection.urls') dengan prefix '/fraud/'
 → views.py — semua view class dan function didefinisikan di sana
 → templates/fraud_detection/ — template HTML untuk setiap halaman
 → ai_assistant/views.py — AI system prompt menyimpan URL ini untuk quick action
==========================================================================
"""

# Import path() dari Django untuk mendefinisikan URL patterns
from django.urls import path
# Import semua views dari file views.py di folder yang sama
from . import views

# Namespace — agar nama URL unik saat digunakan dengan {% url %} di template
# Contoh: {% url 'fraud_detection:alert_list' %} → /fraud/alerts/
app_name = 'fraud_detection'

urlpatterns = [
    # ═══════════════════════════════════════════════════════
    # DASHBOARD — Halaman utama Fraud Detection
    # ═══════════════════════════════════════════════════════
    # Menampilkan ringkasan: total anomali, potensi kerugian, grafik tren,
    # distribusi jenis anomali, karyawan berisiko, rekonsiliasi terbaru
    path('', views.FraudDashboardView.as_view(), name='dashboard'),

    # ═══════════════════════════════════════════════════════
    # FRAUD ALERTS — Daftar & Detail Anomali Kecurangan
    # ═══════════════════════════════════════════════════════
    # Daftar semua anomali dengan filter status/jenis/severity/user
    path('alerts/', views.FraudAlertListView.as_view(), name='alert_list'),
    # Detail 1 anomali + data snapshot + riwayat activity + aksi konfirmasi
    path('alerts/<int:pk>/', views.FraudAlertDetailView.as_view(), name='alert_detail'),
    # Update status anomali via AJAX POST (pending → investigated → cleared/rejected)
    path('alerts/<int:pk>/update-status/', views.fraud_alert_update_status, name='alert_update_status'),
    # Export semua anomali ke file Excel (.xls)
    path('alerts/export/', views.export_fraud_alerts_excel, name='alert_export'),
    # Hapus anomali via AJAX POST — return JSON response
    path('alerts/<int:pk>/delete/', views.fraud_alert_delete, name='alert_delete'),

    # ═══════════════════════════════════════════════════════
    # CASH RECONCILIATION — Rekonsiliasi Kas (Blind Cash Closing)
    # ═══════════════════════════════════════════════════════
    # Daftar semua rekonsiliasi kas + ringkasan (total selisih, shortage, overage)
    path('cash/', views.CashReconciliationListView.as_view(), name='cash_list'),
    # Form buat rekonsiliasi baru — kasir input uang fisik, sistem hitung expected
    path('cash/create/', views.CashReconciliationCreateView.as_view(), name='cash_create'),
    # Edit uang fisik via AJAX POST — hanya jika status masih 'closed' (belum reviewed)
    path('cash/<int:pk>/edit/', views.cash_recon_edit, name='cash_edit'),
    # Review/setujui rekonsiliasi via AJAX POST — bisa + catatan + biaya kerugian
    path('cash/<int:pk>/review/', views.cash_recon_review, name='cash_review'),
    # Hapus rekonsiliasi via AJAX POST — return JSON response
    path('cash/<int:pk>/delete/', views.cash_recon_delete, name='cash_delete'),

    # ═══════════════════════════════════════════════════════
    # SETTINGS — Pengaturan Fraud Prevention
    # ═══════════════════════════════════════════════════════
    # Form konfigurasi: blokir hapus lunas, blokir stok minus, batas diskon, jam ops
    path('settings/', views.FraudSettingsView.as_view(), name='settings'),
]
