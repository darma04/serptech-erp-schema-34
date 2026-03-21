"""
==========================================================================
 USER MANAGEMENT URLS - Routing URL Manajemen User
==========================================================================
 Peta URL modul user management:

 - /access/users/              → Daftar semua user
 - /access/users/add/          → Tambah user baru
 - /access/users/detail/<id>/  → Detail user
 - /access/users/detail/<id>/ajax/ → Detail user via AJAX (JSON)
 - /access/users/edit/<id>/    → Edit user
 - /access/users/delete/<id>/  → Hapus user

 Didaftarkan di config/urls.py: path('access/users/', include('apps.user_management.urls'))
==========================================================================
"""
from django.urls import path
from . import views

app_name = 'user_management'  # Namespace URL — {% url 'user_management:index' %}

urlpatterns = [
    # ── CRUD User ─────────────────────────────────────────────
    path('', views.UserManagementIndexView.as_view(), name='index'),
    # URL: /user_management/add/ — user_add
    path('add/', views.UserAddView.as_view(), name='user_add'),
    # URL: /user_management/detail/<int:pk>/ — user_detail
    path('detail/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    # URL: /user_management/detail/<int:pk>/ajax/ — user_detail_ajax
    path('detail/<int:pk>/ajax/', views.UserDetailAjaxView.as_view(), name='user_detail_ajax'),
    # URL: /user_management/edit/<int:pk>/ — user_edit
    path('edit/<int:pk>/', views.UserEditView.as_view(), name='user_edit'),
    # URL: /user_management/delete/<int:pk>/ — user_delete
    path('delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
    # URL: /user_management/toggle-status/<int:pk>/ — user_toggle_status
    path('toggle-status/<int:pk>/', views.user_toggle_status, name='user_toggle_status'),
]
