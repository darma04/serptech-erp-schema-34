"""
==========================================================================
 PEMBELIAN ADMIN - Registrasi model ke Django Admin
==========================================================================
 Model pembelian (Supplier, PurchaseOrder) tidak didaftarkan ke Admin
 karena sudah memiliki halaman CRUD custom di apps/pembelian/views.py.
==========================================================================
"""

# Import dari framework Django
from django.contrib import admin

# Model pembelian dikelola melalui CRUD custom, bukan Django Admin.
