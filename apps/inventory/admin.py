"""
==========================================================================
 INVENTORY ADMIN - Registrasi model ke Django Admin
==========================================================================
 File ini sengaja dikosongkan karena model inventory dikelola
 melalui halaman CRUD custom (bukan Django Admin).
==========================================================================
"""

from django.contrib import admin

# Model inventory (TransferStok, AdjustmentStok) tidak didaftarkan ke Django Admin
# karena sudah memiliki halaman CRUD custom di apps/inventory/views.py.
# Jika perlu debugging via admin, bisa didaftarkan di sini.
