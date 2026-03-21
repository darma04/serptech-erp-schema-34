"""
==========================================================================
 INVENTORY FORMS - Form Transfer Stok, Items Formset, Adjustment Stok
==========================================================================
 File ini berisi 3 form + 1 formset untuk modul Inventory:

 1. TransferStokForm → Form utama transfer stok (gudang asal/tujuan)
 2. TransferStokItemForm → Form per-item dalam transfer
 3. TransferStokItemFormSet → Kumpulan TransferStokItemForm (inline formset)
 4. AdjustmentStokForm → Form adjustment stok manual

 POLA FORMSET:
 TransferStokForm (parent) → TransferStokItemFormSet (children)
 - Saat create: form parent + formset empty
 - Saat update: form parent + formset diisi data existing
 - FormSet menggunakan inlineformset_factory() dari Django

 Widget: Semua menggunakan Bootstrap 5 classes (form-select, form-control)
         Select2 digunakan untuk dropdown pencarian produk/gudang
==========================================================================
"""

# Import dari framework Django
from django import forms
# Import dari framework Django
from django.forms import inlineformset_factory
# Import dari modul internal proyek
from apps.inventory.models import TransferStok, TransferStokItem, AdjustmentStok
# Import dari modul internal proyek
from apps.produk.models import Gudang, Produk


class TransferStokForm(forms.ModelForm):
    """
    Form utama TRANSFER STOK — pilih gudang asal, gudang tujuan, dan catatan.
    
    Validasi custom:
    - Gudang asal dan tujuan TIDAK BOLEH SAMA
    """
    class Meta:
        """Konfigurasi form TransferStok — field gudang asal/tujuan dan catatan."""
        model = TransferStok
        fields = ['gudang_asal', 'gudang_tujuan', 'catatan']
        # Widget HTML untuk setiap field form (class CSS, placeholder, dll)
        widgets = {
            'gudang_asal': forms.Select(attrs={'class': 'form-select select2'}),
            'gudang_tujuan': forms.Select(attrs={'class': 'form-select select2'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'gudang_asal': 'Dari Gudang',
            'gudang_tujuan': 'Ke Gudang',
            'catatan': 'Catatan',
        }
    
    def __init__(self, *args, **kwargs):
        """Inisialisasi form — filter dropdown gudang hanya yang aktif."""
        super().__init__(*args, **kwargs)
        # Filter hanya gudang yang aktif di dropdown
        self.fields['gudang_asal'].queryset = Gudang.objects.filter(aktif=True)
        # Query database — ambil data self.fields['gudang_tujuan'].queryset yang sesuai filter
        # Set queryset dropdown gudang_tujuan
        self.fields['gudang_tujuan'].queryset = Gudang.objects.filter(aktif=True)
    
    def clean(self):
        """Validasi: gudang asal dan tujuan tidak boleh sama."""
        cleaned_data = super().clean()
        gudang_asal = cleaned_data.get('gudang_asal')
        gudang_tujuan = cleaned_data.get('gudang_tujuan')
        
        if gudang_asal and gudang_tujuan and gudang_asal == gudang_tujuan:
            raise forms.ValidationError('Gudang asal dan tujuan tidak boleh sama!')
        
        return cleaned_data


class TransferStokItemForm(forms.ModelForm):
    """
    Form per-ITEM dalam transfer stok — pilih produk, jumlah, catatan.
    Digunakan dalam formset (TransferStokItemFormSet).
    """
    class Meta:
        """Konfigurasi form item transfer — field produk, jumlah, dan catatan."""
        model = TransferStokItem
        fields = ['produk', 'jumlah', 'catatan']
        # Widget HTML untuk setiap field form (class CSS, placeholder, dll)
        widgets = {
            'produk': forms.Select(attrs={'class': 'form-select select2'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'catatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Catatan item (opsional)'}),
        }
        labels = {
            'produk': 'Produk',
            'jumlah': 'Jumlah',
            'catatan': 'Catatan',
        }
    
    def __init__(self, *args, **kwargs):
        """Inisialisasi form — filter dropdown produk hanya yang aktif dengan optimasi query."""
        super().__init__(*args, **kwargs)
        # Filter hanya produk aktif + optimasi query dengan select_related
        self.fields['produk'].queryset = Produk.objects.filter(aktif=True).select_related('satuan')


# ============================================================
# FORMSET — Kumpulan form items untuk Transfer Stok
# ============================================================
# inlineformset_factory() menghasilkan class FormSet yang:
# - Terhubung ke parent model (TransferStok)
# - Menggunakan child model (TransferStokItem)
# - extra=0 → Tidak ada form kosong (user klik "Tambah Produk")
# - can_delete=True → User bisa hapus item
# - min_num=1 → Minimal harus ada 1 item
# - validate_min=True → Enforce minimal 1 item

TransferStokItemFormSet = inlineformset_factory(
    TransferStok,            # Parent model
    TransferStokItem,        # Child model
    form=TransferStokItemForm,
    extra=0,                 # Tidak ada form kosong extra
    can_delete=True,         # Bisa hapus item
    min_num=1,               # Minimal 1 item
    validate_min=True,       # Enforce minimal
)


class AdjustmentStokForm(forms.ModelForm):
    """
    Form ADJUSTMENT STOK — pilih produk, gudang, tipe (tambah/kurang), jumlah, alasan.
    
    Alasan WAJIB diisi untuk audit trail.
    """
    class Meta:
        """Konfigurasi form AdjustmentStok — field produk, gudang, tipe, jumlah, alasan."""
        model = AdjustmentStok
        fields = ['produk', 'gudang', 'tipe', 'jumlah', 'alasan']
        # Widget HTML untuk setiap field form (class CSS, placeholder, dll)
        widgets = {
            'produk':  forms.Select(attrs={'class': 'form-select select2'}),
            'gudang': forms.Select(attrs={'class': 'form-select select2'}),
            'tipe': forms.Select(attrs={'class': 'form-select'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'alasan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'produk': 'Produk',
            'gudang': 'Gudang',
            'tipe': 'Jenis Adjustment',
            'jumlah': 'Jumlah',
            'alasan': 'Alasan/Keterangan',
        }
    
    def __init__(self, *args, **kwargs):
        """Inisialisasi form — filter dropdown produk dan gudang hanya yang aktif."""
        super().__init__(*args, **kwargs)
        # Filter hanya data aktif
        self.fields['produk'].queryset = Produk.objects.filter(aktif=True)
        # Query database — ambil data self.fields['gudang'].queryset yang sesuai filter
        # Set queryset dropdown gudang
        self.fields['gudang'].queryset = Gudang.objects.filter(aktif=True)
