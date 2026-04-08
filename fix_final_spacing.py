import os
import re

files = [
    'templates/pos/invoice_print.html',
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

        # Fix the spacing overlap by removing excessive CSS margins/paddings 
        # and relying simply on a single &nbsp; to render 1 space gap universally.
        # This will perfectly align browser print spacing and xhtml2pdf spacing.
        
        # 1. Update the CSS for company-logo to remove margin/padding
        content = re.sub(
            r'\.company-logo\s*\{[^}]*\}', 
            '.company-logo { height: 26px; width: auto; vertical-align: middle; }', 
            content
        )
        
        # 2. Clean up any existing &nbsp;&nbsp; or other tags and replace with exactly one &nbsp;
        # Before: class="company-logo">&nbsp;&nbsp; ... or something like that.
        content = content.replace('class="company-logo">&nbsp;&nbsp;\n', 'class="company-logo">&nbsp;\n')
        content = content.replace('class="company-logo">\n', 'class="company-logo">&nbsp;\n')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Memperbaiki spacing di: {file}")
    else:
        print(f"Gagal menemukan: {file}")
