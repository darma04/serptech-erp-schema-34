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

        # Fix nested table issue that breaks spacing in xhtml2pdf
        old_table = """                    <table cellpadding="0" cellspacing="0">
                        <tr>
                            {% if template.tampilkan_logo and perusahaan.logo %}
                            <td style="vertical-align: middle; padding-right: 8px;">
                                <img src="{{ perusahaan.logo.url }}" alt="{{ template.header_nama_perusahaan }}" class="company-logo">
                            </td>
                            {% endif %}
                            <td style="vertical-align: middle;">
                                <div class="company-name">{{ template.header_nama_perusahaan }}</div>
                            </td>
                        </tr>
                    </table>"""

        new_div = """                    <div class="company-name">
                        {% if template.tampilkan_logo and perusahaan.logo %}
                        <img src="{{ perusahaan.logo.url }}" alt="{{ template.header_nama_perusahaan }}" class="company-logo">
                        {% endif %}
                        {{ template.header_nama_perusahaan }}
                    </div>"""

        if old_table in content:
            content = content.replace(old_table, new_div)
            print(f"Diganti table layout di: {file}")
        
        # Modify CSS for company-logo to ensure vertical alignment
        # Previous: .company-logo { height: 24px; width: auto; margin-right: 8px; vertical-align: bottom; }
        # Better for xhtml2pdf: height: 28px; width: auto; margin-right: 8px; vertical-align: text-bottom;
        content = re.sub(r'\.company-logo\s*\{[^}]*\}', '.company-logo { height: 26px; width: auto; margin-right: 8px; vertical-align: middle; }', content)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modifikasi sukses: {file}")
    else:
        print(f"Gagal menemukan: {file}")
