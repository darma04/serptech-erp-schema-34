"""
==========================================================================
 AI ASSISTANT — Django App Configuration
==========================================================================
 Konfigurasi aplikasi Django untuk modul AI Assistant.

 FUNGSI MODUL INI:
 - Chat AI dengan deteksi intent otomatis (penjualan, stok, produk, dll)
 - Multi-provider: Gemini, OpenAI, Groq (Free)
 - Context memory: mengingat 5 percakapan terakhir
 - Auto Insight: ringkasan bisnis otomatis saat buka chat
 - AI Dashboard: skor kesehatan bisnis, anomali, tren revenue
 - Fitur AI lanjutan: Campaign Planner, Business Plan, Content Generator

 TERHUBUNG DENGAN:
 - settings.py → INSTALLED_APPS ('apps.ai_assistant')
 - urls.py → /ai/... (chat, insight, feedback, history, dashboard, pengaturan)
 - Template: templates/ai_assistant/ + templates/partials/ai_chat_widget.html
==========================================================================
"""
from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    """Konfigurasi app AI Assistant — nama dan auto field."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'          # Path ke folder app di struktur project
    verbose_name = 'AI Assistant'       # Nama yang tampil di Django Admin
