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

        # Revert corrupted table badges back to original <span> format
        # Pattern: <table cellpadding="0" cellspacing="0" style="display: inline-block; margin-top: 5px;"><tr><td class="XXX">TEXT</td></tr></table>
        # Replace with: <span class="XXX">TEXT</span>
        content = re.sub(
            r'<table cellpadding="0" cellspacing="0" style="display: inline-block; margin-top: 5px;"><tr><td class="([^"]+)">(.*?)</td></tr></table>',
            r'<span class="\1">\2</span>',
            content
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Reverted badges to <span> in: {file}")
    else:
        print(f"File not found: {file}")
