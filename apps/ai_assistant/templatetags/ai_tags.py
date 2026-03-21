"""
==========================================================================
 AI ASSISTANT — Template Tags (Custom Django Template Tags)
==========================================================================
 Template tag kustom untuk AI Assistant. Digunakan di template HTML
 agar bisa mengambil data konfigurasi AI tanpa melalui views.

 PEMAKAIAN DI TEMPLATE:
   {% load ai_tags %}
   {% get_ai_name as ai_name %}
   <h1>{{ ai_name }}</h1>

 MENGAPA DIPERLUKAN:
 - Nama AI (misal "SERPTECH AI") perlu ditampilkan di chat widget
   yang ada di setiap halaman (via base template).
 - Tidak praktis menambahkan context dari setiap view,
   jadi pakai template tag agar otomatis tersedia.

 TERHUBUNG DENGAN:
 - Model: AIAssistantConfig.ai_name (field di database)
 - Widget: templates/partials/ai_chat_widget.html → menampilkan nama AI
 - Settings: templates/ai_assistant/pengaturan.html → mengatur nama AI
==========================================================================
"""
from django import template
from apps.ai_assistant.models import AIAssistantConfig

# Register library template tag — Django mencari file di folder templatetags/
register = template.Library()


@register.simple_tag
def get_ai_name():
    """
    Mengembalikan nama AI dari konfigurasi database (AIAssistantConfig).

    Cara kerja:
    1. Load singleton config dari database (AIAssistantConfig.load())
    2. Ambil field ai_name (misal: "SERPTECH AI", "Business Assistant")
    3. Jika kosong atau error → fallback ke 'AI Assistant'

    Returns:
        str: Nama AI yang dikonfigurasi, atau 'AI Assistant' sebagai default
    """
    try:
        config = AIAssistantConfig.load()
        return config.ai_name or 'AI Assistant'
    except Exception:
        return 'AI Assistant'
