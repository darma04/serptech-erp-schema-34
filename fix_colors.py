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

        inject_css = """
            .invoice-status, .order-status, .po-status, .slip-status, [class*="status-"] {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
"""
        
        # Add to @media print
        if '@media print {' in content:
            # Check if we already injected to prevent duplication
            if 'print-color-adjust: exact !important;' not in content or 'invoice-status' not in content:
                content = content.replace('@media print {', '@media print {' + inject_css)
        
        # For Telegram PDF (xhtml2pdf), we need background colors explicitly set if it sometimes drops them.
        # But xhtml2pdf normally respects them unless blocked.
        # The user said: "pdf yang di kirim ke telegram memiliki border berbentuk button dengan warna background relevan misal lunas hijau dll, seperti milik slip gaji"
        # Let's ensure border-radius is respected by rendering a table or standard borders if we want, but xhtml2pdf handles border, background-color on span/div fine.
        
        # In xhtml2pdf, border-radius on span doesn't work well, but it falls back to a squared button.
        # However, to be 100% sure it looks like a button, let's make sure it has padding.
        # We already have padding: 6px 20px; in the css.
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modifikasi print-color-adjust sukses: {file}")
    else:
        print(f"Gagal menemukan: {file}")
