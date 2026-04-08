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

        # Update spacing on the logo image. 
        # xhtml2pdf can sometimes ignore margin-right on images. Using padding-right instead, and maybe a non-breaking space
        
        # 1. Update CSS
        content = re.sub(r'\.company-logo\s*\{[^}]*\}', '.company-logo { height: 26px; width: auto; margin-right: 12px; padding-right: 10px; vertical-align: middle; }', content)
        
        # 2. Update the HTML to include an explicit &nbsp; to guarantee spacing in the PDF safely.
        old_img_tag = 'class="company-logo">\n                        {% endif %}'
        new_img_tag = 'class="company-logo">&nbsp;&nbsp;\n                        {% endif %}'
        content = content.replace(old_img_tag, new_img_tag)

        # Check if the thermal template needs skipping for &nbsp; if it's different. Invoice thermal does not have company-name layout like this typically.
        # But if it does, it'll apply. Just rely on the strict matching.

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modifikasi sukses: {file}")
    else:
        print(f"Gagal menemukan: {file}")
