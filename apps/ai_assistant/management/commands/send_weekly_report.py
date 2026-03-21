"""
==========================================================================
 SEND WEEKLY REPORT — Management Command
==========================================================================
 Mengirim laporan mingguan otomatis setiap Senin pagi.
 Gunakan dengan Task Scheduler (Windows) atau crontab (Linux):

 Windows Task Scheduler:
   Action: python manage.py send_weekly_report
   Trigger: Weekly, Monday 07:00

 Linux crontab:
   0 7 * * 1 cd /path/to/project && python manage.py send_weekly_report
==========================================================================
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate dan kirim laporan mingguan otomatis (dijalankan setiap Senin pagi)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--print-only',
            action='store_true',
            help='Hanya cetak laporan ke stdout tanpa mengirim'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 Generating laporan mingguan...'))

        today = timezone.now().date()
        # Minggu lalu: Senin - Minggu
        week_end = today - timedelta(days=today.weekday() + 1)  # Minggu kemarin
        week_start = week_end - timedelta(days=6)  # Senin kemarin

        report = self._generate_report(week_start, week_end)

        if options['print_only']:
            self.stdout.write(report)
        else:
            # Simpan ke ChatHistory sebagai system report
            self._save_report(report, week_start, week_end)

        self.stdout.write(self.style.SUCCESS(
            f'✅ Laporan minggu {week_start.strftime("%d/%m")} - '
            f'{week_end.strftime("%d/%m/%Y")} berhasil digenerate!'
        ))

    def _generate_report(self, week_start, week_end):
        """Generate laporan mingguan dari data ERP."""
        from apps.penjualan.models import SalesOrder, SalesOrderItem
        from apps.pos.models import POSTransaction
        from apps.produk.models import Produk, Stok

        # Revenue
        so_rev = float(SalesOrder.objects.filter(
            status__in=['confirmed', 'delivered', 'completed'],
            tanggal__date__gte=week_start, tanggal__date__lte=week_end
        ).aggregate(t=Sum('total_harga'))['t'] or 0)

        pos_rev = float(POSTransaction.objects.filter(
            status='paid',
            tanggal__date__gte=week_start, tanggal__date__lte=week_end
        ).aggregate(t=Sum('total_harga'))['t'] or 0)

        total_rev = so_rev + pos_rev

        # Transaksi
        so_count = SalesOrder.objects.filter(
            status__in=['confirmed', 'delivered', 'completed'],
            tanggal__date__gte=week_start, tanggal__date__lte=week_end
        ).count()
        pos_count = POSTransaction.objects.filter(
            status='paid',
            tanggal__date__gte=week_start, tanggal__date__lte=week_end
        ).count()

        # Minggu sebelumnya untuk perbandingan
        prev_end = week_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=6)
        prev_so = float(SalesOrder.objects.filter(
            status__in=['confirmed', 'delivered', 'completed'],
            tanggal__date__gte=prev_start, tanggal__date__lte=prev_end
        ).aggregate(t=Sum('total_harga'))['t'] or 0)
        prev_pos = float(POSTransaction.objects.filter(
            status='paid',
            tanggal__date__gte=prev_start, tanggal__date__lte=prev_end
        ).aggregate(t=Sum('total_harga'))['t'] or 0)
        prev_total = prev_so + prev_pos
        growth = round(((total_rev - prev_total) / prev_total * 100), 1) if prev_total > 0 else 0

        # Top 5 produk
        top_items = SalesOrderItem.objects.filter(
            sales_order__status__in=['confirmed', 'delivered', 'completed'],
            sales_order__tanggal__date__gte=week_start,
            sales_order__tanggal__date__lte=week_end
        ).values('produk__nama').annotate(
            total_qty=Sum('jumlah'), total_rev=Sum('subtotal')
        ).order_by('-total_rev')[:5]

        top_lines = []
        for i, item in enumerate(top_items, 1):
            top_lines.append(
                f"  {i}. {item['produk__nama']}: "
                f"{int(item['total_qty'])} unit (Rp {float(item['total_rev']):,.0f})"
            )

        # Stok kritis
        produk_ids_stok = list(Stok.objects.filter(jumlah__gt=0).values_list('produk_id', flat=True))
        stok_habis = Produk.objects.filter(aktif=True).exclude(id__in=produk_ids_stok).count()
        stok_rendah = Stok.objects.values('produk_id').annotate(
            total=Sum('jumlah')
        ).filter(total__gt=0, total__lt=10).count()

        report = f"""
╔══════════════════════════════════════════════════╗
║       📊 LAPORAN MINGGUAN SERPTECH ERP           ║
║  Periode: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}          ║
╚══════════════════════════════════════════════════╝

💰 REVENUE:
  Total Revenue  : Rp {total_rev:,.0f}
  Sales Order    : Rp {so_rev:,.0f} ({so_count} transaksi)
  POS            : Rp {pos_rev:,.0f} ({pos_count} transaksi)
  Growth vs minggu lalu: {'+' if growth >= 0 else ''}{growth}%

🏆 TOP 5 PRODUK TERLARIS:
{chr(10).join(top_lines) if top_lines else '  - Tidak ada data'}

📦 STATUS STOK:
  Stok Habis     : {stok_habis} produk
  Stok Rendah (<10): {stok_rendah} produk

📈 PERBANDINGAN:
  Minggu ini     : Rp {total_rev:,.0f}
  Minggu lalu    : Rp {prev_total:,.0f}
  Selisih        : Rp {total_rev - prev_total:,.0f}

Generated: {timezone.now().strftime('%d/%m/%Y %H:%M')}
"""
        return report

    def _save_report(self, report, week_start, week_end):
        """Simpan laporan sebagai ChatHistory."""
        from apps.ai_assistant.models import ChatHistory
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Simpan untuk semua superuser
        superusers = User.objects.filter(is_superuser=True, is_active=True)
        for user in superusers:
            ChatHistory.objects.create(
                user=user,
                role='assistant',
                message=report,
                intent='laporan_terjadwal',
                source='system',
            )
            logger.info(f"[Weekly Report] Saved report for user: {user.username}")
