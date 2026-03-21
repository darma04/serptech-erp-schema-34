"""
Management command untuk seed data konversi satuan default.
Jalankan: python manage.py seed_konversi_satuan

Mendukung 7 kategori satuan:
1. Jumlah (PCS, Unit, Buah, Set, Pack, Box, Dus, Karton, Roll, Lembar, Pasang, Rim, Lusin, Kodi, Pallet)
2. Berat (mg, Gram, Kilogram, Ons, Kuintal/Kwintal, Ton)
3. Volume Cairan (ML, Liter, Galon, Drum, Jerigen)
4. Panjang (mm, CM, Meter, Inch, Km)
5. Luas (M², CM², Hektar, Are)
6. Volume Padat (M³, CM³)
7. Satuan Khusus Retail/Industri (Set, Bundle, Paket, Tray, Slop, Sachet, Strip,
   Tablet, Botol, Kaleng, Sak, Tabung, Batang, Karung)
"""
from django.core.management.base import BaseCommand
from apps.produk.models import Satuan, KonversiSatuan


class Command(BaseCommand):
    help = 'Seed data semua satuan dan konversi default (global)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Memulai seed satuan dan konversi...'))

        # ============================================================
        # LANGKAH 1: Buat/temukan semua record Satuan
        # ============================================================
        satuan_data = [
            # ── A. Satuan Unit (Barang Satuan) ──
            ('Pieces', 'pcs'),
            ('Unit', 'unit'),
            ('Buah', 'buah'),
            ('Set', 'set'),
            ('Pack', 'pack'),
            ('Box', 'box'),
            ('Dus', 'dus'),
            ('Karton', 'karton'),
            ('Roll', 'roll'),
            ('Lembar', 'lembar'),
            ('Pasang', 'pasang'),
            ('Rim', 'rim'),
            ('Lusin', 'lusin'),
            ('Kodi', 'kodi'),
            ('Pallet', 'pallet'),

            # ── B. Satuan Berat ──
            ('Milligram', 'mg'),
            ('Gram', 'gram'),
            ('Kilogram', 'kg'),
            ('Ons', 'ons'),
            ('Kuintal', 'kuintal'),
            ('Ton', 'ton'),

            # ── C. Satuan Panjang ──
            ('Millimeter', 'mm'),
            ('Centimeter', 'cm'),
            ('Meter', 'meter'),
            ('Kilometer', 'km'),
            ('Inch', 'inch'),

            # ── D. Satuan Volume ──
            ('Mililiter', 'ml'),
            ('Liter', 'liter'),
            ('Galon', 'galon'),
            ('Meter Kubik', 'm³'),

            # ── E. Satuan Luas ──
            ('Meter Persegi', 'm²'),
            ('Centimeter Persegi', 'cm²'),
            ('Hektar', 'ha'),
            ('Are', 'are'),

            # ── F. Satuan Industri / Khusus ──
            ('Tabung', 'tabung'),
            ('Sak', 'sak'),
            ('Drum', 'drum'),
            ('Jerigen', 'jerigen'),
            ('Batang', 'batang'),
            ('Karung', 'karung'),
            ('Tray', 'tray'),
            ('Slop', 'slop'),
            ('Sachet', 'sachet'),
            ('Strip', 'strip'),
            ('Tablet', 'tablet'),
            ('Botol', 'botol'),
            ('Kaleng', 'kaleng'),
            ('Bundle', 'bundle'),
            ('Paket', 'paket'),
        ]

        satuan_map = {}
        new_satuan_count = 0

        for nama, singkatan in satuan_data:
            # Cari existing berdasarkan singkatan (case insensitive)
            existing = Satuan.objects.filter(singkatan__iexact=singkatan).first()
            if not existing:
                # Coba cari berdasarkan nama (case insensitive)
                existing = Satuan.objects.filter(nama__iexact=nama).first()
            if existing:
                satuan_map[singkatan.lower()] = existing
            else:
                obj = Satuan.objects.create(nama=nama, singkatan=singkatan)
                satuan_map[singkatan.lower()] = obj
                new_satuan_count += 1
                self.stdout.write(f'  + Satuan baru: {obj.nama} ({obj.singkatan})')

        self.stdout.write(f'\n  {new_satuan_count} satuan baru ditambahkan.\n')

        # ============================================================
        # LANGKAH 2: Buat data konversi global
        # Format: (dari_singkatan, ke_singkatan, faktor_konversi)
        # Artinya: 1 [dari] = [faktor] [ke]
        # ============================================================
        konversi_data = [
            # ── A. Satuan Unit / Jumlah ──
            ('lusin', 'pcs', 12),          # 1 lusin = 12 pcs
            ('lusin', 'buah', 12),         # 1 lusin = 12 buah
            ('kodi', 'pcs', 20),           # 1 kodi = 20 pcs
            ('rim', 'lembar', 500),        # 1 rim = 500 lembar
            ('rim', 'pcs', 500),           # 1 rim = 500 pcs (kertas)
            ('pack', 'pcs', 6),            # 1 pack = 6 pcs (default, bisa override per produk)
            ('box', 'pcs', 12),            # 1 box = 12 pcs (default, bisa override per produk)
            ('dus', 'pcs', 24),            # 1 dus = 24 pcs (default)
            ('karton', 'pcs', 24),         # 1 karton = 24 pcs (default, bisa override per produk)
            ('karton', 'box', 2),          # 1 karton = 2 box (default)
            ('karton', 'dus', 1),          # 1 karton = 1 dus (default)
            ('pallet', 'karton', 40),      # 1 pallet = 40 karton (default)
            ('pallet', 'pcs', 960),        # 1 pallet = 960 pcs (40x24)
            ('slop', 'pcs', 10),           # 1 slop = 10 pcs (rokok)
            ('pasang', 'pcs', 2),          # 1 pasang = 2 pcs

            # ── B. Satuan Berat ──
            ('ton', 'kg', 1000),           # 1 ton = 1000 kg
            ('ton', 'gram', 1000000),      # 1 ton = 1.000.000 gram
            ('kuintal', 'kg', 100),        # 1 kuintal = 100 kg
            ('kuintal', 'gram', 100000),   # 1 kuintal = 100.000 gram
            ('kg', 'gram', 1000),          # 1 kg = 1000 gram
            ('kg', 'mg', 1000000),         # 1 kg = 1.000.000 mg
            ('kg', 'ons', 10),             # 1 kg = 10 ons
            ('ons', 'gram', 100),          # 1 ons = 100 gram
            ('gram', 'mg', 1000),          # 1 gram = 1000 mg
            ('sak', 'kg', 50),             # 1 sak = 50 kg (semen, default)
            ('karung', 'kg', 50),          # 1 karung = 50 kg (beras, default)

            # ── C. Satuan Volume ──
            ('liter', 'ml', 1000),         # 1 liter = 1000 ml
            ('galon', 'liter', 19),        # 1 galon = 19 liter (Indonesia)
            ('galon', 'ml', 19000),        # 1 galon = 19.000 ml
            ('drum', 'liter', 200),        # 1 drum = 200 liter
            ('drum', 'ml', 200000),        # 1 drum = 200.000 ml
            ('jerigen', 'liter', 20),      # 1 jerigen = 20 liter (default)
            ('jerigen', 'ml', 20000),      # 1 jerigen = 20.000 ml
            ('m³', 'liter', 1000),         # 1 m³ = 1000 liter
            ('m³', 'ml', 1000000),         # 1 m³ = 1.000.000 ml

            # ── D. Satuan Panjang ──
            ('km', 'meter', 1000),         # 1 km = 1000 meter
            ('km', 'cm', 100000),          # 1 km = 100.000 cm
            ('meter', 'cm', 100),          # 1 meter = 100 cm
            ('meter', 'mm', 1000),         # 1 meter = 1000 mm
            ('cm', 'mm', 10),              # 1 cm = 10 mm
            ('inch', 'cm', 2.54),          # 1 inch = 2.54 cm
            ('meter', 'inch', 39.37),      # 1 meter = 39.37 inch
            ('roll', 'meter', 50),         # 1 roll = 50 meter (default, bisa override)

            # ── E. Satuan Luas ──
            ('m²', 'cm²', 10000),          # 1 m² = 10.000 cm²
            ('ha', 'm²', 10000),           # 1 hektar = 10.000 m²
            ('are', 'm²', 100),            # 1 are = 100 m²
            ('ha', 'are', 100),            # 1 hektar = 100 are

            # ── F. Satuan Khusus ──
            ('tray', 'pcs', 30),           # 1 tray = 30 pcs (telur, default)
            ('tray', 'buah', 30),          # 1 tray = 30 buah (telur)
        ]

        created_count = 0
        skipped_count = 0

        for dari_key, ke_key, faktor in konversi_data:
            dari = satuan_map.get(dari_key)
            ke = satuan_map.get(ke_key)

            if dari and ke:
                _, created = KonversiSatuan.objects.get_or_create(
                    dari_satuan=dari,
                    ke_satuan=ke,
                    produk=None,  # Global (berlaku untuk semua produk)
                    defaults={'faktor_konversi': faktor}
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  + 1 {dari.singkatan} = {faktor} {ke.singkatan}')
                else:
                    skipped_count += 1
            else:
                missing = []
                if not dari:
                    missing.append(dari_key)
                if not ke:
                    missing.append(ke_key)
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Satuan tidak ditemukan: {", ".join(missing)}'
                ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Selesai! {created_count} konversi baru ditambahkan, '
            f'{skipped_count} sudah ada (dilewati).'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total satuan tersedia: {Satuan.objects.count()}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total konversi global: {KonversiSatuan.objects.filter(produk__isnull=True).count()}'
        ))
