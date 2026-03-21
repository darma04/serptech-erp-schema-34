"""
==========================================================================
 AI ASSISTANT — Admin Configuration (Django Admin)
==========================================================================
 Registrasi model AI Assistant ke panel Django Admin (/admin/).
 Memungkinkan superadmin untuk mengelola:
 1. AIAssistantConfig → Konfigurasi API key, provider, model AI
 2. ChatHistory       → Riwayat percakapan user dengan AI
 3. ChatFeedback      → Feedback (👍/👎) dari user terhadap respons AI

 TERHUBUNG DENGAN:
 - Model: apps/ai_assistant/models.py (AIAssistantConfig, ChatHistory, ChatFeedback)
 - Views: apps/ai_assistant/views.py (ai_chat_api, chat_feedback, chat_history_api)
 - Template: templates/ai_assistant/ (halaman pengaturan AI)
 - URL: apps/ai_assistant/urls.py (/ai/...)
==========================================================================
"""
from django.contrib import admin
from .models import AIAssistantConfig, ChatHistory, ChatFeedback


# ═══════════════════════════════════════════════════════════════
# Konfigurasi AI Assistant — Singleton (hanya 1 record)
# Berisi: provider (gemini/openai/groq), API key, model, temperature
# ═══════════════════════════════════════════════════════════════
@admin.register(AIAssistantConfig)
class AIAssistantConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'model_name', 'aktif', 'diupdate_pada')


# ═══════════════════════════════════════════════════════════════
# Riwayat Chat — Semua pesan user ↔ AI tersimpan di sini
# Role: 'user' (pesan dari user) atau 'assistant' (respons AI)
# Intent: kategori pertanyaan (penjualan, stok, produk, dll)
# Source: asal respons (gemini, openai, groq, fallback, local)
# ═══════════════════════════════════════════════════════════════
@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'short_message', 'intent', 'source', 'created_at')
    list_filter = ('role', 'intent', 'user', 'created_at')   # Filter sidebar di admin
    search_fields = ('message', 'user__username')              # Pencarian teks pesan
    readonly_fields = ('created_at',)                          # Waktu tidak bisa diedit
    ordering = ('-created_at',)                                # Terbaru di atas

    def short_message(self, obj):
        """Tampilkan pesan terpotong (maks 80 karakter) di list admin."""
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Pesan'


# ═══════════════════════════════════════════════════════════════
# Feedback Chat — Penilaian user terhadap kualitas respons AI
# feedback: 'up' (👍 bagus) atau 'down' (👎 kurang bagus)
# Digunakan untuk monitoring kualitas AI dari waktu ke waktu
# ═══════════════════════════════════════════════════════════════
@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback', 'short_text', 'created_at')
    list_filter = ('feedback', 'user', 'created_at')
    ordering = ('-created_at',)

    def short_text(self, obj):
        """Tampilkan teks respons AI terpotong (maks 80 karakter) di list admin."""
        return obj.message_text[:80] + '...' if len(obj.message_text) > 80 else obj.message_text
    short_text.short_description = 'Teks AI'
