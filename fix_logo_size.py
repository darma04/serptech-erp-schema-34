import os

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
        
        # Replace existing CSS for logo to make height match 24px and align properly
        # Find exactly the right CSS string. Let's do it intelligently.
        import re
        content = re.sub(r'\.company-logo\s*\{[^}]*\}', '.company-logo { height: 24px; width: auto; margin-right: 8px; vertical-align: bottom; }', content)
        
        # Ensure right side aligns perfectly with left side. 
        # By setting vertical-align: top on the table cells (td), and letting the text size dictate the height, it should be fine. But user complained it wasn't.
        # Let's adjust header-table text align and vertical-align
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modifikasi CSS sukses: {file}")
    else:
        print(f"Gagal menemukan: {file}")
