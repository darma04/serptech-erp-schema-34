import os
import re

files = [
    'templates/pos/invoice_print.html',
    'templates/pos/invoice_print_thermal.html',
    'templates/penjualan/sales_order_print.html',
    'templates/pembelian/purchase_order_print.html',
    'templates/hr/penggajian_print.html',
    'templates/biaya/transaksi_biaya_print.html'
]

basedir = 'c:/SERPTECH-Full-Version-32-New-10-03-2026/SERPTECH-Software-39'

for file in files:
    path = os.path.join(basedir, file)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Revert divs back to spans for status badges
        replacements = [
            ('<div class="invoice-status', '<span class="invoice-status'),
            ('<div class="order-status', '<span class="order-status'),
            ('<div class="po-status', '<span class="po-status'),
            ('<div class="slip-status', '<span class="slip-status'),
            ('<div class="biaya-status', '<span class="biaya-status'),
        ]
        
        for old_div, new_span in replacements:
            if old_div in content:
                content = content.replace(old_div, new_span)
                
        # Revert the closing </div> to </span> for these badges
        # Regex to find these specific badge DIVs and change closing tag
        content = re.sub(r'(<span class=\"(?:invoice|order|po|slip|biaya)-status[^\"]*\".*?>.*?)</div>', r'\1</span>', content, flags=re.DOTALL)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Reverted to span in: {file}")
