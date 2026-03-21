"""
==========================================================================
 AI ASSISTANT URLS - Routing untuk Chat API & Halaman Pengaturan AI
==========================================================================
 File ini mendefinisikan URL patterns untuk modul AI Assistant.

 URL yang tersedia:
 ┌──────────────────┬──────────┬──────────────────────────────────────────┐
 │ URL              │ Method   │ Fungsi                                   │
 ├──────────────────┼──────────┼──────────────────────────────────────────┤
 │ /ai/             │ GET      │ Halaman pengaturan AI (provider, API key)│
 │ /ai/dashboard/   │ GET      │ Dashboard analitik AI (skor kesehatan)   │
 │ /ai/chat/        │ POST     │ API chat AI (AJAX dari widget chat)      │
 │ /ai/insight/     │ GET      │ Auto insight bisnis harian               │
 │ /ai/feedback/    │ POST     │ Simpan feedback 👍/👎 respons AI         │
 │ /ai/history/     │ GET      │ Load riwayat chat user (JSON)            │
 │ /ai/clear/       │ POST     │ Hapus semua riwayat chat user            │
 └──────────────────┴──────────┴──────────────────────────────────────────┘

 Cara kerja URL routing Django:
 - URL didaftarkan di config/urls.py: path('ai/', include('apps.ai_assistant.urls'))
 - Prefix '/ai/' ditambahkan otomatis oleh include()
 - app_name digunakan untuk namespace ({% url 'ai_assistant:chat' %})

 Terhubung dengan:
 - config/urls.py → include() mendaftarkan urls ini dengan prefix /ai/
 - views.py → Setiap path() mengarahkan ke view function/class
 - templates → Menggunakan {% url 'ai_assistant:nama' %} untuk link
 - JavaScript → AJAX call ke /ai/chat/, /ai/feedback/, dll
==========================================================================
"""

# Import fungsi path dari Django untuk mendefinisikan URL patterns
from django.urls import path

# Import views dari modul yang sama (apps/ai_assistant/views.py)
from . import views

# Namespace untuk URL reversal — digunakan di template dan views:
# Contoh: {% url 'ai_assistant:chat' %} → '/ai/chat/'
# Contoh Python: reverse('ai_assistant:dashboard') → '/ai/dashboard/'
app_name = 'ai_assistant'

# ═══ DAFTAR URL PATTERNS ═══
# Setiap path() mendaftarkan 1 URL → 1 view → 1 name (untuk reversal)
urlpatterns = [
    # Halaman utama AI Assistant — pengaturan provider, API key, model
    # Class-Based View (CBV) → perlu .as_view() untuk konversi ke fungsi
    path('', views.AIAssistantSettingsView.as_view(), name='index'),

    # Dashboard analitik AI — skor kesehatan bisnis, prediksi revenue, anomali
    # Hanya bisa diakses user dengan permission ai_assistant.dashboard_ai.read
    path('dashboard/', views.AIDashboardView.as_view(), name='dashboard'),

    # API endpoint chat AI — menerima POST dari widget chat (AJAX)
    # Request: { message: "berapa penjualan hari ini?" }
    # Response: { reply: "...", intent: "penjualan", source: "groq" }
    path('chat/', views.ai_chat_api, name='chat'),

    # Auto insight — generate insight bisnis otomatis dari data terkini
    # Dipanggil saat widget chat baru dibuka untuk tampilkan insight awal
    path('insight/', views.auto_insight, name='insight'),

    # Feedback API — simpan rating 👍/👎 untuk respons AI
    # Request: { feedback: "up" atau "down", message_text: "..." }
    path('feedback/', views.chat_feedback, name='feedback'),

    # Riwayat chat — load 50 pesan terakhir user dalam format JSON
    # Dipanggil saat widget chat dibuka untuk menampilkan percakapan lama
    path('history/', views.chat_history_api, name='history'),

    # Hapus riwayat — menghapus SEMUA riwayat chat user yang login
    # Dipanggil saat user klik tombol "Hapus Riwayat" di widget chat
    path('clear/', views.clear_history, name='clear'),
]
