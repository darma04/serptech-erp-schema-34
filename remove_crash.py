import os

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

        # Remove the attribute selector that crashes xhtml2pdf
        if ', [class*="status-"] {' in content:
            content = content.replace(', [class*="status-"] {', ' {')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed CSS in: {file}")
            
        # Also let's ensure spacing is correct from previous step:
        # User complained spacing was TOO FAR.
        # Ensure company-logo has NO margin or padding:
        import re
        content = re.sub(r'\.company-logo\s*\{[^}]*\}', '.company-logo { height: 26px; width: auto; vertical-align: middle; }', content)
        
        # Ensure only a single &nbsp; is used, and no space compounding
        content = content.replace('class="company-logo">&nbsp;&nbsp;\n', 'class="company-logo">&nbsp;\n')
        content = content.replace('class="company-logo"> &nbsp;\n', 'class="company-logo">&nbsp;\n')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Selesai memperbaiki semua file.')
