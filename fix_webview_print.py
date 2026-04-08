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
        
        # Pastikan tidak ada karakter aneh
        content = content.replace("!isAndroidWebView && typeof window.print === 'function'", "typeof window.print === 'function'")
        # For desktop fallback (already window.print)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modifikasi sukses: {file}")
    else:
        print(f"Gagal menemukan: {file}")
