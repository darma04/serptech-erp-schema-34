"""
==========================================================================
PENGATURAN VIEWS - View Settings/Konfigurasi Sistem ERP
==========================================================================
File ini berisi views untuk modul pengaturan sistem:

PROFIL USER:
    ProfilView → Edit profil pengguna (nama, avatar, telepon)

PERUSAHAAN (Singleton):
    PerusahaanView → Pengaturan perusahaan + sistem + SMTP email
    Menggunakan PengaturanPerusahaan.load() (singleton pattern)

METODE PEMBAYARAN CRUD:
    MetodePembayaranListView/Create/Update/Detail/Delete
    toggle_metode_pembayaran() → Toggle aktif/nonaktif via AJAX
    Detail: menampilkan statistik penggunaan (POS, biaya, PO)

TEMPLATE CETAK CRUD:
    TemplateCetakListView/Create/Update
    Konfigurasi header, footer, tanda tangan untuk cetak dokumen

MANAJEMEN DATA (⚠ KRITIS):
    ManajemenDataView → Statistik seluruh database + riwayat backup
    backup_data() → Export seluruh DB ke JSON (dumpdata)
    restore_data() → Import DB dari JSON (loaddata)
    reset_data() → HAPUS SEMUA TRANSAKSI, pertahankan master data
    hapus_riwayat_backup() → Hapus record riwayat backup

⚠ PERHATIAN:
- backup/restore/reset memerlukan permission superuser atau create/delete
- reset_data() membutuhkan konfirmasi ketik 'RESET'
- reset_data() juga mereset stok produk ke 0
==========================================================================
"""

import os
import json
import tempfile
from datetime import datetime

# Import dari framework Django
from django.shortcuts import render
from django.db.models import ProtectedError
from django.shortcuts import redirect, get_object_or_404
# Import dari framework Django
from django.contrib.auth.decorators import login_required
# Import dari framework Django
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
# Import dari framework Django
from django.utils.decorators import method_decorator
# Import dari framework Django
from django.urls import reverse_lazy
# Import dari framework Django
from django.contrib import messages
# Import dari framework Django
from django.http import JsonResponse, HttpResponse
# Import dari framework Django
from django.contrib.auth import get_user_model
# Import dari framework Django
from django.core.management import call_command
# Import dari framework Django
from django.conf import settings
# Import dari framework Django
from django.views.decorators.http import require_POST

from web_project import TemplateLayout
# Import dari modul internal proyek
from apps.pos.models import MetodePembayaran
# Import dari modul internal proyek
from .models import TemplateCetak, PengaturanPerusahaan, BackupHistory
# Import dari modul internal proyek
from apps.core.mixins import ReadPermissionMixin, CreatePermissionMixin, UpdatePermissionMixin, DeletePermissionMixin
# Import dari modul internal proyek
from apps.core.permissions import has_permission
from django.db import transaction

User = get_user_model()


class ProfilView(ReadPermissionMixin, TemplateView):
    """
    Edit Profil User - nama, avatar, telepon.
    URL: /pengaturan/profil/
    GET: tampilkan form profil, POST: simpan perubahan (termasuk avatar upload/hapus)
    """
    template_name = 'pengaturan/profil.html'
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        context['user'] = user
        # Pastikan profile ada
        if not hasattr(user, 'profile'):
            from auth.models import Profile
            Profile.objects.create(user=user, email=user.email)
        context['profile'] = user.profile
        return context


    def post(self, request, *args, **kwargs):


        user = request.user

        # Update field User
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        # Update field Profile
        profile = user.profile
        profile.phone = request.POST.get('phone', '')

        # Tangani upload avatar
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        # Tangani penghapusan avatar
        if request.POST.get('remove_avatar') == '1':
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None

        profile.save()

        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('pengaturan:profil')


class PerusahaanView(UpdatePermissionMixin, UpdateView):
    """
    Pengaturan Perusahaan - data perusahaan, sistem, SMTP email (singleton).
    URL: /pengaturan/perusahaan/
    Menggunakan PengaturanPerusahaan.load() untuk singleton pattern.
    """
    model = PengaturanPerusahaan
    template_name = 'pengaturan/perusahaan.html'
    permission_module = 'pengaturan'
    fields = [
        # Company Identity
        'nama_perusahaan', 'logo', 'alamat', 'telepon', 'email', 'website', 'pajak_default',
        # System Settings
        'system_title', 'system_description', 'system_keywords', 'system_logo', 'system_favicon',
        'maintenance_mode', 'maintenance_message',
        # Email/SMTP
        'email_smtp_host', 'email_smtp_port', 'email_smtp_user', 'email_smtp_password', 'email_use_tls',
        # Email Templates
        'email_header', 'email_footer',
        'forgot_password_subject', 'forgot_password_message',
        'register_subject', 'register_message'
    ]
    success_url = reverse_lazy('pengaturan:perusahaan')

    def get_object(self):
        """Mendapatkan objek berdasarkan parameter URL."""
        return PengaturanPerusahaan.load()

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


    def form_valid(self, form):
        """
        Simpan pengaturan perusahaan dan hapus cache agar perubahan
        meta sistem (judul, deskripsi, keywords, favicon, dll) langsung
        terasa di semua halaman tanpa menunggu cache 60 detik expired.
        """
        from django.core.cache import cache
        # Hapus cache context processor agar data terbaru langsung dimuat
        cache.delete('ctx_pengaturan_perusahaan')
        messages.success(self.request, 'Pengaturan perusahaan berhasil diperbarui!')
        return super().form_valid(form)


class MetodePembayaranListView(ReadPermissionMixin, ListView):
    paginate_by = 50
    """Daftar semua metode pembayaran (tunai, transfer, QRIS, dll)."""
    model = MetodePembayaran
    template_name = 'pengaturan/metode_pembayaran_list.html'
    context_object_name = 'metode_list'
    ordering = ['nama']
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Hitung ringkasan untuk footer tabel
        from django.db.models import Sum
        metode_list = context.get('metode_list', [])
        total_saldo = 0
        total_pendapatan = 0
        total_pengeluaran = 0
        total_transaksi = 0
        for m in metode_list:
            total_saldo += m.saldo_terhitung
            total_pendapatan += m.total_pendapatan
            total_pengeluaran += m.total_pengeluaran
            total_transaksi += m.total_transaksi_count
        context['ringkasan_saldo'] = total_saldo
        context['ringkasan_pendapatan'] = total_pendapatan
        context['ringkasan_pengeluaran'] = total_pengeluaran
        context['ringkasan_transaksi'] = total_transaksi

        return context


class MetodePembayaranCreateView(CreatePermissionMixin, CreateView):
    """Tambah metode pembayaran baru."""
    model = MetodePembayaran
    template_name = 'pengaturan/metode_pembayaran_form.html'
    fields = ['nama', 'nama_pemilik', 'kode', 'deskripsi', 'gambar', 'saldo', 'aktif']
    success_url = reverse_lazy('pengaturan:metode_pembayaran_list')
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['action'] = 'Tambah'
        return context


    def form_valid(self, form):

        messages.success(self.request, 'Metode pembayaran berhasil ditambahkan!')
        return super().form_valid(form)


class MetodePembayaranUpdateView(UpdatePermissionMixin, UpdateView):
    """Edit metode pembayaran yang sudah ada."""
    model = MetodePembayaran
    template_name = 'pengaturan/metode_pembayaran_form.html'
    fields = ['nama', 'nama_pemilik', 'kode', 'deskripsi', 'gambar', 'saldo', 'aktif']
    success_url = reverse_lazy('pengaturan:metode_pembayaran_list')
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['action'] = 'Edit'
        return context


    def form_valid(self, form):

        messages.success(self.request, 'Metode pembayaran berhasil diperbarui!')
        return super().form_valid(form)



class MetodePembayaranDetailView(ReadPermissionMixin, DetailView):
    """Detail metode pembayaran + statistik penggunaan (POS, biaya, PO)."""
    model = MetodePembayaran
    template_name = 'pengaturan/metode_pembayaran_detail.html'
    context_object_name = 'metode'
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Hitung jumlah transaksi yang menggunakan metode ini
        from apps.pos.models import POSTransaction
        # Import dari modul internal proyek
        from apps.biaya.models import TransaksiBiaya
        # Import dari modul internal proyek
        from apps.pembelian.models import PurchaseOrder
        # Import dari modul internal proyek
        from apps.penjualan.models import SalesOrder
        # Import dari framework Django
        from django.db.models import Sum, Max

        # Statistik POS
        context['total_transaksi_pos'] = POSTransaction.objects.filter(metode_pembayaran=self.object).count()
        context['transaksi_lunas'] = POSTransaction.objects.filter(metode_pembayaran=self.object, status='paid').count()

        # Statistik SO
        context['total_transaksi_so'] = SalesOrder.objects.filter(metode_pembayaran=self.object).count()

        # Total transaksi keseluruhan (POS + SO + Biaya + PO)
        context['total_transaksi'] = (
            context['total_transaksi_pos'] + 
            context['total_transaksi_so'] + 
            TransaksiBiaya.objects.filter(metode_pembayaran=self.object).count() +
            PurchaseOrder.objects.filter(metode_pembayaran=self.object).count()
        )

        # Hitung total pendapatan dari POS + SO (gunakan property model)
        context['total_pendapatan'] = self.object.total_pendapatan

        # Hitung total pengeluaran dari Biaya + PO (gunakan property model)
        context['total_pengeluaran'] = self.object.total_pengeluaran

        # Saldo terhitung (dinamis) - bisa negatif
        context['saldo_terhitung'] = self.object.saldo_terhitung

        # Pendapatan tertinggi (POS atau SO)
        pos_max = POSTransaction.objects.filter(
            metode_pembayaran=self.object, status='paid'
        ).aggregate(max_val=Max('total_harga'))['max_val'] or 0
        so_max = SalesOrder.objects.filter(
            metode_pembayaran=self.object, status__in=['confirmed', 'delivered', 'completed']
        ).aggregate(max_val=Max('total_harga'))['max_val'] or 0
        context['pendapatan_tertinggi'] = max(pos_max, so_max)

        # Pengeluaran tertinggi (Biaya atau PO)
        biaya_max = TransaksiBiaya.objects.filter(
            metode_pembayaran=self.object, status='approved'
        ).aggregate(max_val=Max('jumlah'))['max_val'] or 0
        po_max = PurchaseOrder.objects.filter(
            metode_pembayaran=self.object, status='received'
        ).aggregate(max_val=Max('total_harga'))['max_val'] or 0
        context['pengeluaran_tertinggi'] = max(biaya_max, po_max)

        return context


class MetodePembayaranDeleteView(DeletePermissionMixin, DeleteView):
    """Hapus metode pembayaran (JSON response untuk AJAX)."""
    model = MetodePembayaran
    success_url = reverse_lazy('pengaturan:metode_pembayaran_list')
    permission_module = 'pengaturan'

    def delete(self, request, *args, **kwargs):
        """Hapus data - return JSON response untuk AJAX."""
        from django.http import JsonResponse
        self.object = self.get_object()

        try:
            metode_name = self.object.nama
            self.object.delete()
            return JsonResponse({
                'success': True, 
                'message': f'Metode pembayaran {metode_name} berhasil dihapus'
            })
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'Data tidak dapat dihapus karena sedang digunakan atau terkait dengan data lain.'}, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Gagal menghapus metode pembayaran: {str(e)}'
            }, status=400)

@login_required
def toggle_metode_pembayaran(request, pk):
    """Toggle status aktif/nonaktif metode pembayaran via AJAX"""
    if request.method == 'POST':
        metode = get_object_or_404(MetodePembayaran, pk=pk)
        metode.aktif = not metode.aktif
        metode.save()
        return JsonResponse({
            'success': True,
            'aktif': metode.aktif,
            'message': f'Metode pembayaran {"diaktifkan" if metode.aktif else "dinonaktifkan"}'
        })
    return JsonResponse({'success': False}, status=400)


# ╔══════════════════════════════════════════════════════════════╗
# ║  TEMPLATE CETAK CRUD - konfigurasi cetak dokumen             ║
# ║  Header, footer, tanda tangan untuk invoice/PO/SO/expense    ║
# ╚══════════════════════════════════════════════════════════════╝


class TemplateCetakListView(ReadPermissionMixin, ListView):
    paginate_by = 50
    """Daftar template cetak (invoice, PO, SO, expense, dll)."""
    model = TemplateCetak
    template_name = 'pengaturan/template_cetak_list.html'
    context_object_name = 'templates'
    ordering = ['jenis']
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['total_template'] = TemplateCetak.objects.count()
        context['total_aktif'] = TemplateCetak.objects.filter(aktif=True).count()
        context['total_nonaktif'] = TemplateCetak.objects.filter(aktif=False).count()
        return context



class TemplateCetakUpdateView(UpdatePermissionMixin, UpdateView):
    """Edit template cetak - konfigurasi header, footer, tanda tangan."""
    model = TemplateCetak
    template_name = 'pengaturan/template_cetak_form.html'
    permission_module = 'pengaturan'
    fields = [
        'nama', 'jenis', 'header_nama_perusahaan', 'header_alamat', 
        'header_telepon', 'header_email', 'header_website',
        'footer_ucapan', 'footer_keterangan', 'footer_copyright',
        'signature_kiri_label', 'signature_kanan_label',
        'tampilkan_logo', 'tampilkan_website', 'aktif'
    ]
    success_url = reverse_lazy('pengaturan:template_cetak_list')

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['action'] = 'Edit'
        return context


    def form_valid(self, form):

        messages.success(self.request, 'Template cetak berhasil diperbarui!')
        return super().form_valid(form)



class TemplateCetakCreateView(CreatePermissionMixin, CreateView):
    """Buat template cetak baru untuk jenis dokumen tertentu."""
    model = TemplateCetak
    template_name = 'pengaturan/template_cetak_form.html'
    permission_module = 'pengaturan'
    fields = [
        'nama', 'jenis', 'header_nama_perusahaan', 'header_alamat', 
        'header_telepon', 'header_email', 'header_website',
        'footer_ucapan', 'footer_keterangan', 'footer_copyright',
        'signature_kiri_label', 'signature_kanan_label',
        'tampilkan_logo', 'tampilkan_website', 'aktif'
    ]
    success_url = reverse_lazy('pengaturan:template_cetak_list')

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['action'] = 'Tambah'
        return context


    def form_valid(self, form):

        messages.success(self.request, 'Template cetak berhasil ditambahkan!')
        return super().form_valid(form)


class TemplateCetakDeleteView(DeletePermissionMixin, DeleteView):
    """Hapus template cetak - return JSON untuk AJAX."""
    model = TemplateCetak
    success_url = reverse_lazy('pengaturan:template_cetak_list')
    permission_module = 'pengaturan'

    def delete(self, request, *args, **kwargs):
        """Hapus data - return JSON response untuk AJAX."""
        self.object = self.get_object()
        try:
            nama = self.object.nama
            self.object.delete()
            return JsonResponse({
                'success': True,
                'message': f'Template cetak {nama} berhasil dihapus'
            })
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'Data tidak dapat dihapus karena sedang digunakan atau terkait dengan data lain.'}, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Gagal menghapus template cetak: {str(e)}'
            }, status=400)


# ╔══════════════════════════════════════════════════════════════╗
                # ║  MANAJEMEN DATA - backup/restore/reset database              ║
                # ║  ⚠ OPERASI KRITIS: memerlukan superuser atau permission      ║
# ╚══════════════════════════════════════════════════════════════╝


class ManajemenDataView(ReadPermissionMixin, TemplateView):
    """Halaman utama Manajemen Data - statistik, riwayat, dan aksi backup/restore/reset"""
    template_name = 'pengaturan/manajemen_data.html'
    permission_module = 'pengaturan'

    def get_context_data(self, **kwargs):
        """Menambahkan data konteks tambahan ke template."""
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Import SEMUA model untuk statistik menyeluruh
        from apps.produk.models import Produk, Kategori, Satuan, Gudang, Stok, KonversiSatuan
        # Import dari modul internal proyek
        from apps.pos.models import POSTransaction, POSTransactionItem, MetodePembayaran
        # Import dari modul internal proyek
        from apps.penjualan.models import SalesOrder, SalesOrderItem, Customer
        # Import dari modul internal proyek
        from apps.pembelian.models import PurchaseOrder, PurchaseOrderItem, Supplier
        # Import dari modul internal proyek
        from apps.inventory.models import TransferStok, TransferStokItem, AdjustmentStok
        # Import dari modul internal proyek
        from apps.biaya.models import TransaksiBiaya, KategoriBiaya
        # Import dari modul internal proyek
        from apps.hr.models import Karyawan, Departemen, Jabatan, Absensi, Penggajian
        # Import dari modul internal proyek
        from apps.activity_log.models import UserActivity
        # Import dari modul internal proyek
        from apps.automation.models import LogNotifikasi, PengaturanTelegram, TemplatePesan
        # Import dari modul internal proyek
        from apps.ai_assistant.models import AIAssistantConfig, ChatHistory, ChatFeedback
        # Import dari modul internal proyek
        from apps.core.models import RolePermission
        from auth.models import Profile
        # Import model Fraud Detection - untuk statistik anomali & rekonsiliasi kas
        from apps.fraud_detection.models import FraudAlert, CashReconciliation

        # Statistik Database - SEMUA model
        context['stats'] = {
            # Master Data Produk
            'produk': Produk.objects.count(),
            'kategori': Kategori.objects.count(),
            'satuan': Satuan.objects.count(),
            'gudang': Gudang.objects.count(),
            'stok': Stok.objects.count(),
            'konversi_satuan': KonversiSatuan.objects.count(),
            # Transaksi
            'pos': POSTransaction.objects.count(),
            'pos_item': POSTransactionItem.objects.count(),
            'sales_order': SalesOrder.objects.count(),
            'sales_order_item': SalesOrderItem.objects.count(),
            'purchase_order': PurchaseOrder.objects.count(),
            'purchase_order_item': PurchaseOrderItem.objects.count(),
            'transfer_stok': TransferStok.objects.count(),
            'transfer_stok_item': TransferStokItem.objects.count(),
            'adjustment_stok': AdjustmentStok.objects.count(),
            'biaya': TransaksiBiaya.objects.count(),
            'kategori_biaya': KategoriBiaya.objects.count(),
            # Relasi Bisnis
            'customer': Customer.objects.count(),
            'supplier': Supplier.objects.count(),
            'metode_pembayaran': MetodePembayaran.objects.count(),
            # HR
            'karyawan': Karyawan.objects.count(),
            'departemen': Departemen.objects.count(),
            'jabatan': Jabatan.objects.count(),
            'absensi': Absensi.objects.count(),
            'penggajian': Penggajian.objects.count(),
            # User & Akun
            'user': User.objects.count(),
            'profile': Profile.objects.count(),
            'role_permission': RolePermission.objects.count(),
            # Log & Aktivitas
            'activity_log': UserActivity.objects.count(),
            'log_notifikasi': LogNotifikasi.objects.count(),
            # AI Assistant
            'chat_history': ChatHistory.objects.count(),
            'chat_feedback': ChatFeedback.objects.count(),
            # Fraud Detection - anomali kecurangan & rekonsiliasi kas
            'fraud_alert': FraudAlert.objects.count(),
            'cash_reconciliation': CashReconciliation.objects.count(),
            # Pengaturan
            'template_cetak': TemplateCetak.objects.count(),
            'backup_history': BackupHistory.objects.count(),
        }

        # Total seluruh record database
        context['total_record'] = sum(context['stats'].values())

        # Total transaksi
        context['total_transaksi'] = (
            context['stats']['pos'] + context['stats']['sales_order'] + 
            context['stats']['purchase_order'] + context['stats']['biaya'] +
            context['stats']['transfer_stok'] + context['stats']['adjustment_stok']
        )

        # Total master data
        context['total_master'] = (
            context['stats']['produk'] + context['stats']['kategori'] + 
            context['stats']['satuan'] + context['stats']['gudang'] +
            context['stats']['customer'] + context['stats']['supplier'] +
            context['stats']['karyawan'] + context['stats']['departemen']
        )

        # Riwayat Backup
        context['riwayat_list'] = BackupHistory.objects.select_related('dibuat_oleh').all()[:50]

        # Ukuran database - real-time dari file SQLite
        db_path = settings.BASE_DIR / 'db.sqlite3'
        if db_path.exists():
            db_size = os.path.getsize(db_path)
            if db_size < 1024:
                context['db_size'] = f"{db_size} B"
            elif db_size < 1024 * 1024:
                context['db_size'] = f"{db_size / 1024:.1f} KB"
            else:
                context['db_size'] = f"{db_size / (1024 * 1024):.1f} MB"
            context['db_size_bytes'] = db_size
        else:
            context['db_size'] = '0 B'
            context['db_size_bytes'] = 0

        # Backup terakhir
        last_backup = BackupHistory.objects.filter(jenis='backup', status='sukses').first()
        context['last_backup'] = last_backup

        return context


@login_required
@require_POST
def backup_data(request):
    """Export seluruh database ke file JSON"""
    # Permission check
    if not request.user.is_superuser and not has_permission(request.user, 'create', 'pengaturan'):
        messages.error(request, 'Anda tidak memiliki izin untuk melakukan backup data.')
        return redirect('pengaturan:manajemen_data')

    try:
        # Generate nama file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nama_file = f"backup_{timestamp}.json"

        # Backup menggunakan dumpdata
        from io import StringIO
        output = StringIO()
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            '--exclude=admin.logentry',
            '--exclude=sessions.session',
            '--indent=2',
            stdout=output
        )

        json_data = output.getvalue()
        file_size = len(json_data.encode('utf-8'))

        # Simpan riwayat
        BackupHistory.objects.create(
            nama_file=nama_file,
            ukuran_file=file_size,
            jenis='backup',
            status='sukses',
            catatan=f"Backup seluruh database ({file_size / 1024:.1f} KB)",
            dibuat_oleh=request.user
        )

        # Kembalikan file unduhan
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{nama_file}"'
        return response

    except ProtectedError:
        return JsonResponse({'success': False, 'message': 'Data tidak dapat dihapus karena sedang digunakan atau terkait dengan data lain.'}, status=400)
    except Exception as e:
        # Simpan riwayat gagal
        BackupHistory.objects.create(
            nama_file=f"backup_gagal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            ukuran_file=0,
            jenis='backup',
            status='gagal',
            catatan=f"Error: {str(e)}",
            dibuat_oleh=request.user
        )
        messages.error(request, f'Backup gagal: {str(e)}')
        return redirect('pengaturan:manajemen_data')


@login_required
@require_POST
def restore_data(request):
    """
    Restore data dari file backup JSON.
    -------- Strategi --------
    Strategi:
    1. SIMPAN user admin yang sedang login (jangan hapus!) → agar session tetap valid
    2. Hapus SEMUA data lain (termasuk profile admin, agar loaddata bisa recreate)
    3. Matikan FK constraints saat loaddata → cegah FOREIGN KEY error
    4. Load data dari backup
    5. Nyalakan kembali FK constraints
    6. Pastikan admin tetap punya profile setelah restore
    """
    # Permission check
    if not request.user.is_superuser and not has_permission(request.user, 'create', 'pengaturan'):
        messages.error(request, 'Anda tidak memiliki izin untuk restore data.')
        return redirect('pengaturan:manajemen_data')

    if 'backup_file' not in request.FILES:
        messages.error(request, 'File backup tidak ditemukan. Pilih file .json untuk restore.')
        return redirect('pengaturan:manajemen_data')

    backup_file = request.FILES['backup_file']

    # Validasi ekstensi file
    if not backup_file.name.endswith('.json'):
        messages.error(request, 'Format file tidak valid. Hanya file .json yang diperbolehkan.')
        return redirect('pengaturan:manajemen_data')

    tmp_path = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        # Import dari framework Django
        from django.db import connection
        from io import StringIO

        # Baca file content
        content = backup_file.read().decode('utf-8')
        file_size = len(content.encode('utf-8'))

        # Validasi JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            messages.error(request, 'File JSON tidak valid atau rusak.')
            return redirect('pengaturan:manajemen_data')

        # Validasi bahwa data adalah list (format dumpdata Django)
        if not isinstance(data, list):
            messages.error(request, 'Format file backup tidak valid. File harus berisi data dumpdata Django.')
            return redirect('pengaturan:manajemen_data')

        if len(data) == 0:
            messages.error(request, 'File backup kosong, tidak ada data untuk di-restore.')
            return redirect('pengaturan:manajemen_data')

        # Filter data: hapus contenttypes, auth.permission, admin.logentry, sessions
        excluded_models = {
            'contenttypes.contenttype',
            'auth.permission',
            'admin.logentry',
            'sessions.session'
        }
        filtered_data = [
            item for item in data
            if item.get('model') not in excluded_models
        ]

        logger.info("[RESTORE] File: %s, ukuran: %d bytes, total objek: %d, setelah filter: %d",
                    backup_file.name, file_size, len(data), len(filtered_data))

        # Simpan user & admin info sebelum flush
        current_user = request.user
        current_user_pk = current_user.pk
        current_username = current_user.username

        # Simpan data yang sudah difilter ke temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(filtered_data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name

        # === LANGKAH 1: FLUSH SEMUA DATA LAMA ===
        # Bypass fraud signals agar bulk delete tidak diblokir oleh FRAUD_BLOCK
        from apps.fraud_detection import signals as fraud_signals
        fraud_signals._BYPASS_FRAUD_SIGNALS = True
        logger.info("[RESTORE] Langkah 1: Menghapus semua data lama...")

        # Import dari modul internal proyek
        from apps.pos.models import POSTransaction, POSTransactionItem, MetodePembayaran
        from apps.penjualan.models import SalesOrder, SalesOrderItem, Customer
        from apps.pembelian.models import PurchaseOrder, PurchaseOrderItem, Supplier
        from apps.produk.models import Produk, Stok, Gudang, Kategori, Satuan, KonversiSatuan
        from apps.inventory.models import TransferStok, TransferStokItem, AdjustmentStok
        from apps.biaya.models import TransaksiBiaya, KategoriBiaya
        from apps.hr.models import Karyawan, Departemen, Jabatan, Absensi, Penggajian
        from apps.activity_log.models import UserActivity
        from apps.automation.models import LogNotifikasi, TemplatePesan
        from apps.ai_assistant.models import ChatHistory, ChatFeedback
        from apps.core.models import RolePermission
        from auth.models import Profile
        from apps.fraud_detection.models import FraudAlert, CashReconciliation, FraudRule

        # Hapus transaksi (child tables dulu, lalu parent)
        POSTransactionItem.objects.all().delete()
        POSTransaction.objects.all().delete()
        SalesOrderItem.objects.all().delete()
        SalesOrder.objects.all().delete()
        PurchaseOrderItem.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        TransferStokItem.objects.all().delete()
        TransferStok.objects.all().delete()
        AdjustmentStok.objects.all().delete()
        TransaksiBiaya.objects.all().delete()
        KategoriBiaya.objects.all().delete()

        # Hapus data Fraud Detection
        FraudAlert.objects.all().delete()
        CashReconciliation.objects.all().delete()

        # Hapus master data produk
        Stok.objects.all().delete()
        KonversiSatuan.objects.all().delete()
        Produk.objects.all().delete()
        Kategori.objects.all().delete()
        Satuan.objects.all().delete()
        Gudang.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        MetodePembayaran.objects.all().delete()

        # Hapus HR data
        Penggajian.objects.all().delete()
        Absensi.objects.all().delete()
        try:
            from apps.hr.models import FotoWajah
            FotoWajah.objects.all().delete()
        except Exception:
            pass
        Karyawan.objects.all().delete()
        Jabatan.objects.all().delete()
        Departemen.objects.all().delete()

        # Hapus AI & log data
        ChatFeedback.objects.all().delete()
        ChatHistory.objects.all().delete()
        UserActivity.objects.all().delete()
        LogNotifikasi.objects.all().delete()

        # Hapus pengaturan
        TemplatePesan.objects.all().delete()
        TemplateCetak.objects.all().delete()
        BackupHistory.objects.all().delete()
        RolePermission.objects.all().delete()

        # Hapus user LAIN (bukan admin yang sedang login!) + profile admin
        # → User admin TETAP ADA agar session tidak rusak
        # → Profile admin dihapus agar loaddata bisa recreate tanpa UNIQUE error
        Profile.objects.all().delete()  # Hapus SEMUA profile (termasuk admin)
        User.objects.exclude(pk=current_user_pk).delete()  # Hapus user LAIN saja

        # Hapus singleton configs
        PengaturanPerusahaan.objects.all().delete()
        try:
            from apps.automation.models import PengaturanTelegram
            PengaturanTelegram.objects.all().delete()
        except Exception:
            pass
        try:
            from apps.ai_assistant.models import AIAssistantConfig
            AIAssistantConfig.objects.all().delete()
        except Exception:
            pass
        try:
            from apps.hr.models import PengaturanAbsensi
            PengaturanAbsensi.objects.all().delete()
        except Exception:
            pass
        try:
            FraudRule.objects.all().delete()
        except Exception:
            pass

        logger.info("[RESTORE] Langkah 1 selesai: Semua data lama berhasil dihapus.")

        # === LANGKAH 2: LOAD DATA DARI BACKUP ===
        logger.info("[RESTORE] Langkah 2: Memuat data dari backup...")

        # MATIKAN FK CONSTRAINTS sebelum loaddata
        # Ini mencegah FOREIGN KEY constraint failed saat urutan insert tidak sempurna
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
        logger.info("[RESTORE] FK constraints dimatikan sementara.")

        load_success = False
        load_error_msg = ""

        # Percobaan 1: loaddata langsung
        try:
            stderr_output = StringIO()
            call_command(
                'loaddata',
                tmp_path,
                '--ignorenonexistent',
                verbosity=1,
                stderr=stderr_output
            )
            load_success = True
            load_error_msg = ""
            logger.info("[RESTORE] Langkah 2 sukses: loaddata berhasil.")
        except Exception as load_err:
            load_success = False
            load_error_msg = str(load_err)
            stderr_msg = stderr_output.getvalue()
            logger.error("[RESTORE] Loaddata gagal (percobaan 1): %s | stderr: %s", load_err, stderr_msg)

        # Percobaan 2: item-by-item jika loaddata langsung gagal
        if not load_success:
            logger.info("[RESTORE] Percobaan 2: load item per item")
            success_count = 0
            error_count = 0
            error_models = []

            for item in filtered_data:
                single_tmp = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as stmp:
                        json.dump([item], stmp, ensure_ascii=False)
                        single_tmp = stmp.name

                    call_command('loaddata', single_tmp, '--ignorenonexistent', verbosity=0, stderr=StringIO())
                    success_count += 1
                except Exception as item_err:
                    error_count += 1
                    model_name = item.get('model', 'unknown')
                    if model_name not in error_models:
                        error_models.append(model_name)
                        logger.warning("[RESTORE] Gagal memuat model %s: %s", model_name, str(item_err)[:100])
                finally:
                    if single_tmp and os.path.exists(single_tmp):
                        try:
                            os.unlink(single_tmp)
                        except OSError:
                            pass

            if success_count > 0:
                load_success = True
                load_error_msg = f"Dimuat {success_count} objek, {error_count} gagal"
                if error_models:
                    load_error_msg += f" (model gagal: {', '.join(error_models[:5])})"
                logger.info("[RESTORE] Item-by-item: %s", load_error_msg)

        # NYALAKAN kembali FK constraints
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")
        logger.info("[RESTORE] FK constraints diaktifkan kembali.")

        # === LANGKAH 3: PASTIKAN ADMIN TETAP PUNYA PROFILE ===
        # Jika backup tidak mengandung profile untuk user admin saat ini,
        # buat profile baru agar admin bisa tetap mengakses sistem.
        try:
            if not Profile.objects.filter(user=current_user).exists():
                Profile.objects.create(
                    user=current_user,
                    role='pemilik',
                    email=current_user.email or ''
                )
                logger.info("[RESTORE] Profile admin '%s' dibuat ulang.", current_username)
        except Exception as profile_err:
            logger.warning("[RESTORE] Gagal membuat profile admin: %s", profile_err)

        # Pastikan admin tetap superuser
        try:
            current_user.refresh_from_db()
            if not current_user.is_superuser:
                current_user.is_superuser = True
                current_user.is_staff = True
                current_user.save(update_fields=['is_superuser', 'is_staff'])
        except Exception:
            pass

        # === LANGKAH 4: VACUUM DATABASE ===
        try:
            with connection.cursor() as cursor:
                cursor.execute("VACUUM")
            logger.info("[RESTORE] VACUUM database selesai.")
        except Exception as vac_err:
            logger.warning("[RESTORE] VACUUM gagal (tidak fatal): %s", vac_err)

        if load_success:
            # Simpan riwayat sukses
            try:
                BackupHistory.objects.create(
                    nama_file=backup_file.name,
                    ukuran_file=file_size,
                    jenis='restore',
                    status='sukses',
                    catatan=f"Restore dari {backup_file.name} ({file_size / 1024:.1f} KB) - {len(filtered_data)} objek. {load_error_msg}",
                    dibuat_oleh=current_user
                )
            except Exception:
                pass
            messages.success(request, f'Data berhasil di-restore dari "{backup_file.name}"! ({len(filtered_data)} objek dimuat) {load_error_msg}')
        else:
            raise Exception(f"Semua metode restore gagal: {load_error_msg}")

    except ProtectedError:
        messages.error(request, 'Data tidak dapat dihapus karena sedang digunakan atau terkait dengan data lain.')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("[RESTORE] Error: %s", e, exc_info=True)

        try:
            BackupHistory.objects.create(
                nama_file=backup_file.name,
                ukuran_file=0,
                jenis='restore',
                status='gagal',
                catatan=f"Error: {str(e)}",
                dibuat_oleh=request.user
            )
        except Exception:
            pass
        messages.error(request, f'Restore gagal: {str(e)}')

    finally:
        # Selalu kembalikan fraud signals ke aktif
        try:
            from apps.fraud_detection import signals as fraud_signals
            fraud_signals._BYPASS_FRAUD_SIGNALS = False
        except Exception:
            pass
        # Selalu pastikan FK constraints aktif
        try:
            from django.db import connection as conn
            with conn.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON")
        except Exception:
            pass
        # Hapus temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    return redirect('pengaturan:manajemen_data')


@login_required
@require_POST
def reset_data(request):
    """Reset SEMUA data database - hapus seluruh data kecuali user admin yang sedang login"""
    # Permission check: harus punya delete permission
    if not request.user.is_superuser and not has_permission(request.user, 'delete', 'pengaturan'):
        return JsonResponse({'success': False, 'message': 'Anda tidak memiliki izin untuk reset data.'}, status=403)

    # Validasi konfirmasi
    konfirmasi = request.POST.get('konfirmasi', '')
    if konfirmasi != 'HAPUS SEMUA':
        messages.error(request, 'Konfirmasi tidak valid. Ketik "HAPUS SEMUA" untuk melanjutkan.')
        return redirect('pengaturan:manajemen_data')

    try:
        # Import dari framework Django
        from django.db import connection
        # Bypass fraud signals agar bulk delete tidak diblokir oleh FRAUD_BLOCK
        from apps.fraud_detection import signals as fraud_signals
        fraud_signals._BYPASS_FRAUD_SIGNALS = True
        # Import SEMUA model
        from apps.pos.models import POSTransaction, POSTransactionItem, MetodePembayaran
        # Import dari modul internal proyek
        from apps.penjualan.models import SalesOrder, SalesOrderItem, Customer
        # Import dari modul internal proyek
        from apps.pembelian.models import PurchaseOrder, PurchaseOrderItem, Supplier
        # Import dari modul internal proyek
        from apps.inventory.models import TransferStok, TransferStokItem, AdjustmentStok
        # Import dari modul internal proyek
        from apps.biaya.models import TransaksiBiaya, KategoriBiaya
        # Import dari modul internal proyek
        from apps.produk.models import Produk, Kategori, Satuan, Gudang, Stok, KonversiSatuan
        # Import dari modul internal proyek
        from apps.hr.models import Karyawan, Departemen, Jabatan, Absensi, Penggajian
        # Import dari modul internal proyek
        from apps.activity_log.models import UserActivity
        # Import dari modul internal proyek
        from apps.automation.models import LogNotifikasi, PengaturanTelegram, TemplatePesan
        # Import dari modul internal proyek
        from apps.ai_assistant.models import AIAssistantConfig, ChatHistory, ChatFeedback
        # Import dari modul internal proyek
        from apps.core.models import RolePermission
        from auth.models import Profile
        # Import model Fraud Detection - untuk hapus data fraud saat reset
        from apps.fraud_detection.models import FraudAlert, CashReconciliation, FraudRule

        # Simpan info user yang sedang login
        current_user = request.user
        current_user_pk = current_user.pk

        # Hitung SEMUA data yang akan dihapus
        counts = {
            'POS Transaction': POSTransaction.objects.count(),
            'POS Item': POSTransactionItem.objects.count(),
            'Sales Order': SalesOrder.objects.count(),
            'Sales Order Item': SalesOrderItem.objects.count(),
            'Purchase Order': PurchaseOrder.objects.count(),
            'Purchase Order Item': PurchaseOrderItem.objects.count(),
            'Transfer Stok': TransferStok.objects.count(),
            'Transfer Stok Item': TransferStokItem.objects.count(),
            'Adjustment Stok': AdjustmentStok.objects.count(),
            'Transaksi Biaya': TransaksiBiaya.objects.count(),
            'Kategori Biaya': KategoriBiaya.objects.count(),
            'Produk': Produk.objects.count(),
            'Stok': Stok.objects.count(),
            'Kategori': Kategori.objects.count(),
            'Satuan': Satuan.objects.count(),
            'Gudang': Gudang.objects.count(),
            'Konversi Satuan': KonversiSatuan.objects.count(),
            'Customer': Customer.objects.count(),
            'Supplier': Supplier.objects.count(),
            'Metode Pembayaran': MetodePembayaran.objects.count(),
            'Karyawan': Karyawan.objects.count(),
            'Departemen': Departemen.objects.count(),
            'Jabatan': Jabatan.objects.count(),
            'Absensi': Absensi.objects.count(),
            'Penggajian': Penggajian.objects.count(),
            'Activity Log': UserActivity.objects.count(),
            'Log Notifikasi': LogNotifikasi.objects.count(),
            'Chat History': ChatHistory.objects.count(),
            'Chat Feedback': ChatFeedback.objects.count(),
            # Fraud Detection - data anomali & rekonsiliasi kas
            'Fraud Alert': FraudAlert.objects.count(),
            'Cash Reconciliation': CashReconciliation.objects.count(),
            'User Lain': User.objects.exclude(pk=current_user_pk).count(),
            'Role Permission': RolePermission.objects.count(),
            'Riwayat Backup': BackupHistory.objects.count(),
        }

        total_deleted = sum(counts.values())

        # ===== HAPUS SEMUA DATA (urutan penting: child dulu, lalu parent) =====

        # 1. Hapus transaksi (items dulu)
        POSTransactionItem.objects.all().delete()
        POSTransaction.objects.all().delete()
        SalesOrderItem.objects.all().delete()
        SalesOrder.objects.all().delete()
        PurchaseOrderItem.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        TransferStokItem.objects.all().delete()
        TransferStok.objects.all().delete()
        AdjustmentStok.objects.all().delete()
        TransaksiBiaya.objects.all().delete()
        KategoriBiaya.objects.all().delete()

        # 2. Hapus stok & produk
        Stok.objects.all().delete()
        KonversiSatuan.objects.all().delete()
        Produk.objects.all().delete()
        Kategori.objects.all().delete()
        Satuan.objects.all().delete()
        Gudang.objects.all().delete()

        # 3. Hapus relasi bisnis
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        MetodePembayaran.objects.all().delete()

        # 4. Hapus HR data (child dulu)
        Penggajian.objects.all().delete()
        Absensi.objects.all().delete()
        try:
            # Import dari modul internal proyek
            from apps.hr.models import FotoWajah
            FotoWajah.objects.all().delete()
        except Exception:
            pass
        Karyawan.objects.all().delete()
        Jabatan.objects.all().delete()
        Departemen.objects.all().delete()

        # 5. Hapus data Fraud Detection (sebelum AI dan log)
        FraudAlert.objects.all().delete()
        CashReconciliation.objects.all().delete()

        # 6. Hapus AI data
        ChatFeedback.objects.all().delete()
        ChatHistory.objects.all().delete()

        # 7. Hapus log & notifikasi
        UserActivity.objects.all().delete()
        LogNotifikasi.objects.all().delete()

        # 7. Hapus pengaturan
        TemplatePesan.objects.all().delete()
        TemplateCetak.objects.all().delete()
        BackupHistory.objects.all().delete()
        RolePermission.objects.all().delete()

        # 8. Hapus user lain kecuali admin yang sedang login
        Profile.objects.exclude(user_id=current_user_pk).delete()
        User.objects.exclude(pk=current_user_pk).delete()

        # 9. Reset singleton pengaturan ke default
        PengaturanPerusahaan.objects.all().delete()
        try:
            PengaturanTelegram.objects.all().delete()
        except Exception:
            pass
        try:
            AIAssistantConfig.objects.all().delete()
        except Exception:
            pass
        try:
            # Import dari modul internal proyek
            from apps.hr.models import PengaturanAbsensi
            PengaturanAbsensi.objects.all().delete()
        except Exception:
            pass
        try:
            # Reset singleton Fraud Detection - mengembalikan pengaturan fraud ke default
            FraudRule.objects.all().delete()
        except Exception:
            pass

        # 10. VACUUM database untuk mengecilkan ukuran file
        with connection.cursor() as cursor:
            cursor.execute("VACUUM")

        # Buat detail catatan
        detail_parts = [f"{name}: {count}" for name, count in counts.items() if count > 0]
        detail_str = ", ".join(detail_parts) if detail_parts else "Tidak ada data"

        # Simpan riwayat reset
        BackupHistory.objects.create(
            nama_file='reset_semua_data',
            ukuran_file=0,
            jenis='reset',
            status='sukses',
            catatan=f"Hapus SEMUA {total_deleted} record database. Detail: {detail_str}",
            dibuat_oleh=current_user
        )

        messages.success(request, f'Semua data berhasil dihapus! {total_deleted} record dihapus dari database. Hanya akun admin Anda yang dipertahankan.')

    except ProtectedError:
        return JsonResponse({'success': False, 'message': 'Data tidak dapat dihapus karena sedang digunakan atau terkait dengan data lain.'}, status=400)
    except Exception as e:
        try:
            BackupHistory.objects.create(
                nama_file='reset_semua_data',
                ukuran_file=0,
                jenis='reset',
                status='gagal',
                catatan=f"Error: {str(e)}",
                dibuat_oleh=request.user
            )
        except Exception:
            pass
        messages.error(request, f'Reset gagal: {str(e)}')
    finally:
        # Selalu kembalikan fraud signals ke aktif
        try:
            from apps.fraud_detection import signals as fraud_signals
            fraud_signals._BYPASS_FRAUD_SIGNALS = False
        except Exception:
            pass

    return redirect('pengaturan:manajemen_data')


@login_required
@require_POST
def hapus_riwayat_backup(request, pk):
    """Hapus satu record riwayat backup"""
    if not request.user.is_superuser and not has_permission(request.user, 'delete', 'pengaturan'):
        return JsonResponse({'success': False, 'message': 'Anda tidak memiliki izin.'}, status=403)

    riwayat = get_object_or_404(BackupHistory, pk=pk)
    riwayat.delete()
    messages.success(request, 'Riwayat berhasil dihapus.')
    return redirect('pengaturan:manajemen_data')


@login_required
@require_POST
def bersihkan_log_aktivitas(request):
    """Bersihkan (hapus semua) data log aktivitas user."""
    if not request.user.is_superuser and not has_permission(request.user, 'delete', 'pengaturan'):
        messages.error(request, 'Anda tidak memiliki izin untuk membersihkan log.')
        return redirect('pengaturan:manajemen_data')

    # Import dari modul internal proyek
    from apps.activity_log.models import UserActivity
    jumlah = UserActivity.objects.count()
    UserActivity.objects.all().delete()

    # Catat ke riwayat
    BackupHistory.objects.create(
        jenis='reset',
        nama_file='-',
        ukuran_file=0,
        status='sukses',
        catatan=f'Membersihkan {jumlah} record log aktivitas',
        dibuat_oleh=request.user
    )

    messages.success(request, f'Berhasil membersihkan {jumlah} record log aktivitas.')
    return redirect('pengaturan:manajemen_data')


@login_required
@require_POST
def bersihkan_log_notifikasi(request):
    """Bersihkan (hapus semua) data log notifikasi Telegram."""
    if not request.user.is_superuser and not has_permission(request.user, 'delete', 'pengaturan'):
        messages.error(request, 'Anda tidak memiliki izin untuk membersihkan log.')
        return redirect('pengaturan:manajemen_data')

    # Import dari modul internal proyek
    from apps.automation.models import LogNotifikasi
    jumlah = LogNotifikasi.objects.count()
    LogNotifikasi.objects.all().delete()

    # Catat ke riwayat
    BackupHistory.objects.create(
        jenis='reset',
        nama_file='-',
        ukuran_file=0,
        status='sukses',
        catatan=f'Membersihkan {jumlah} record log notifikasi Telegram',
        dibuat_oleh=request.user
)

    messages.success(request, f'Berhasil membersihkan {jumlah} record log notifikasi Telegram.')
    return redirect('pengaturan:manajemen_data')
