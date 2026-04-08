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

        # xhtml2pdf drops padding, top/bottom borders on <span> tags because they are inline.
        # By changing them to <div> tags, xhtml2pdf handles padding and backgrounds perfectly.
        # We need to replace only the spans that contain status classes.
        
        # A quick replacement strategy
        replacements = [
            ('<span class="invoice-status', '<div class="invoice-status'),
            ('<span class="order-status', '<div class="order-status'),
            ('<span class="po-status', '<div class="po-status'),
            ('<span class="slip-status', '<div class="slip-status'),
            ('<span class="biaya-status', '<div class="biaya-status'), # if it exists
        ]
        
        for old_span, new_div in replacements:
            if old_span in content:
                content = content.replace(old_span, new_div)
                
        # Now we need to also replace the closing </span> for these specific wrappers.
        # We can't just replace ALL </span>, but we can replace them sequentially or via regex.
        import re
        # Find all <div class="xxx-status ...">...</span>
        content = re.sub(r'(<div class=\"(?:invoice|order|po|slip|biaya)-status[^\"]*\".*?>.*?)</span>', r'\1</div>', content, flags=re.DOTALL)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed Badge HTML in: {file}")
