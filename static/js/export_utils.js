/**
 * ==========================================================================
 *  EXPORT UTILITIES - Fungsi Ekspor Tabel ke Excel (CSV) dan PDF
 *  + UNIVERSAL DOWNLOAD HELPER untuk Capacitor WebView
 * ==========================================================================
 *  File ini berisi:
 *  1. _downloadBlob()    → Download file universal (browser + Capacitor WebView)
 *  2. exportTableToExcel() → Ekspor tabel ke file CSV (bisa dibuka di Excel)
 *  3. exportTableToPDF()   → Ekspor tabel ke file PDF (membutuhkan pdfMake)
 *
 *  ===== MASALAH YANG DISELESAIKAN =====
 *  Di Capacitor WebView (Android), metode download standar TIDAK berfungsi:
 *  - createElement('a').click() → GAGAL (WebView blokir navigasi blob:/data:)
 *  - window.open(dataUri) → GAGAL (popup diblokir)
 *  - pdfMake.download() → GAGAL (internal link.click())
 *
 *  Solusi:
 *  1. navigator.share() Web Share API → Buka native Android share sheet
 *  2. Blob URL + link.click() → Untuk browser biasa
 *  3. Overlay manual download → Fallback terakhir dengan <a download> tag
 *
 *  Dependensi:
 *  - pdfMake library (hanya untuk fungsi PDF) — dimuat dari CDN/vendor
 * ==========================================================================
 */

// ── DETEKSI MOBILE WEBVIEW ────────────────────────────────────────────────
/**
 * Cek apakah berjalan di WebView (Capacitor / Android WebView / iOS WKWebView).
 * Di WebView, Blob URL + link.click() TIDAK berfungsi untuk download.
 */
function _isWebView() {
    var ua = navigator.userAgent || '';
    if (window.Capacitor) return true;
    if (/wv|WebView/i.test(ua)) return true;
    if (/Android.*Version\/[\d.]+/i.test(ua) && !/Chrome\/[\d.]+/i.test(ua)) return true;
    if (/iPhone|iPad|iPod/i.test(ua) && !/Safari/i.test(ua)) return true;
    return false;
}

// ── UNIVERSAL FILE DOWNLOAD ──────────────────────────────────────────────
/**
 * Download file dari Blob — kompatibel browser biasa DAN WebView.
 *
 * Strategi (berurutan):
 * 1. WebView → navigator.share() (native Android share sheet)
 * 2. WebView fallback → overlay manual download <a download>
 * 3. Browser biasa → createObjectURL + link.click() (standar)
 *
 * @param {Blob}   blob     - File data dalam bentuk Blob
 * @param {string} filename - Nama file dengan ekstensi
 */
function _downloadBlob(blob, filename) {
    if (_isWebView()) {
        // ================================================================
        // MODE WEBVIEW (CAPACITOR / ANDROID WEBVIEW)
        // ================================================================
        _downloadBlobWebView(blob, filename);
    } else {
        // ================================================================
        // MODE BROWSER BIASA
        // ================================================================
        _downloadBlobBrowser(blob, filename);
    }
}

/**
 * Download di WebView menggunakan navigator.share() atau fallback overlay.
 */
function _downloadBlobWebView(blob, filename) {
    // Strategi 1: navigator.share() — Native Android Share Sheet
    // Tersedia di Android Chrome WebView 75+ dan iOS Safari 15+
    if (navigator.share && navigator.canShare) {
        try {
            var file = new File([blob], filename, { type: blob.type });
            var shareData = { files: [file], title: filename };

            if (navigator.canShare(shareData)) {
                navigator.share(shareData)
                    .then(function() {
                        console.log('File berhasil di-share/download via native share');
                    })
                    .catch(function(err) {
                        // User cancelled share atau error lain
                        if (err.name !== 'AbortError') {
                            console.warn('Share gagal, mencoba fallback:', err);
                            _showManualDownloadLink(blob, filename);
                        }
                    });
                return; // navigator.share() berhasil dipanggil
            }
        } catch (e) {
            console.warn('navigator.share error:', e);
        }
    }

    // Strategi 2: Buat <a> dengan Blob URL langsung di overlay
    // Ini bekerja di beberapa WebView karena user melakukan tap langsung (bukan programmatic click)
    _showManualDownloadLink(blob, filename);
}

/**
 * Download di browser biasa menggunakan Blob URL + link.click().
 */
function _downloadBlobBrowser(blob, filename) {
    try {
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        setTimeout(function () {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 300);
    } catch (e) {
        console.error('Download browser gagal:', e);
        // Fallback ke overlay manual
        _showManualDownloadLink(blob, filename);
    }
}

/**
 * Tampilkan overlay premium dengan link download manual.
 * User tap tombol download secara langsung (bukan programmatic) —
 * ini membuat <a download> bekerja bahkan di beberapa WebView.
 *
 * @param {Blob}   blob     - Blob data untuk di-download
 * @param {string} filename - Nama file
 */
function _showManualDownloadLink(blob, filename) {
    // Buat Blob URL untuk link
    var blobUrl = URL.createObjectURL(blob);

    var overlay = document.createElement('div');
    overlay.className = 'download-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;';
    overlay.innerHTML =
        '<div style="background:#fff;border-radius:16px;padding:28px 24px;text-align:center;max-width:360px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3);">' +
            '<div style="width:60px;height:60px;margin:0 auto 16px;background:linear-gradient(135deg,#e8e8ff,#d0d0ff);border-radius:50%;display:flex;align-items:center;justify-content:center;">' +
                '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#696cff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' +
            '</div>' +
            '<h5 style="margin:0 0 8px;color:#333;font-size:1.1rem;font-weight:700;">File Siap Diunduh</h5>' +
            '<p style="color:#697a8d;font-size:0.85rem;margin-bottom:20px;line-height:1.4;">Ketuk tombol di bawah untuk menyimpan file <strong>' + filename + '</strong></p>' +
            '<a id="_dl_link" href="' + blobUrl + '" download="' + filename + '" ' +
                'style="display:block;background:linear-gradient(135deg,#696cff,#5f61e6);color:#fff;padding:14px 24px;border-radius:10px;text-decoration:none;font-weight:600;font-size:0.95rem;margin-bottom:12px;">' +
                '📥 Download ' + filename +
            '</a>' +
            '<button id="_dl_close" style="background:none;border:none;color:#697a8d;cursor:pointer;font-size:0.8rem;padding:8px 16px;">Tutup</button>' +
        '</div>';

    // Event: tutup overlay
    overlay.querySelector('#_dl_close').addEventListener('click', function () {
        overlay.remove();
        URL.revokeObjectURL(blobUrl);
    });
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
            overlay.remove();
            URL.revokeObjectURL(blobUrl);
        }
    });

    // Event: setelah user klik download, tutup overlay otomatis
    overlay.querySelector('#_dl_link').addEventListener('click', function () {
        setTimeout(function () {
            overlay.remove();
            // Jangan revokeObjectURL terlalu cepat agar download selesai
            setTimeout(function () { URL.revokeObjectURL(blobUrl); }, 5000);
        }, 1000);
    });

    document.body.appendChild(overlay);
}

// Pastikan fungsi tersedia secara global
window._downloadBlob = _downloadBlob;
window._isWebView = _isWebView;
window._showManualDownloadLink = _showManualDownloadLink;

// ── EXPORT TABLE TO EXCEL ────────────────────────────────────────────────
/**
 * Ekspor tabel HTML ke file Excel (format CSV).
 *
 * @param {string} tableId  - ID elemen tabel HTML (contoh: "produkTable")
 * @param {string} filename - Nama file yang didownload (tanpa ekstensi)
 */
function exportTableToExcel(tableId, filename) {
    try {
        const table = document.getElementById(tableId);
        if (!table) {
            alert('Tabel tidak ditemukan!');
            return;
        }

        let csv = [];

        // ─── AMBIL HEADER TABEL ───
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            const headers = [];
            headerRow.querySelectorAll('th').forEach(th => {
                headers.push('"' + th.textContent.trim().replace(/"/g, '""') + '"');
            });
            csv.push(headers.join(','));
        }

        // ─── AMBIL DATA BARIS ───
        const tbody = table.querySelector('tbody');
        if (tbody) {
            tbody.querySelectorAll('tr').forEach(tr => {
                const cells = tr.querySelectorAll('td');
                if (cells.length === 0) return;
                if (cells.length === 1 && cells[0].colSpan > 1) return;

                const row = [];
                cells.forEach(td => {
                    let text = td.textContent.trim();
                    text = text.replace(/\s+/g, ' ').replace(/"/g, '""');
                    row.push('"' + text + '"');
                });
                csv.push(row.join(','));
            });
        }

        // ─── AMBIL DATA SUMMARY (TFOOT) ───
        const tfoot = table.querySelector('tfoot');
        if (tfoot) {
            tfoot.querySelectorAll('tr').forEach(tr => {
                const cells = tr.querySelectorAll('td, th');
                if (cells.length === 0) return;
                const row = [];
                cells.forEach(cell => {
                    let text = cell.textContent.trim();
                    text = text.replace(/\s+/g, ' ').replace(/"/g, '""');
                    row.push('"' + text + '"');
                });
                csv.push(row.join(','));
            });
        }

        // ─── BUAT FILE DOWNLOAD ───
        const csvContent = csv.join('\n');
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });

        // Download universal (browser + WebView compatible)
        _downloadBlob(blob, filename + '.csv');

    } catch (error) {
        console.error('Export Excel error:', error);
        alert('Terjadi kesalahan saat export Excel: ' + error.message);
    }
}

// ── EXPORT TABLE TO PDF ──────────────────────────────────────────────────
/**
 * Ekspor tabel HTML ke file PDF.
 *
 * @param {string} tableId     - ID elemen tabel HTML
 * @param {string} filename    - Nama file PDF (tanpa ekstensi)
 * @param {string} title       - Judul dokumen PDF
 * @param {string} orientation - 'portrait' atau 'landscape'
 */
function exportTableToPDF(tableId, filename, title, orientation) {
    orientation = orientation || 'landscape';
    try {
        if (typeof pdfMake === 'undefined') {
            alert('pdfMake library tidak tersedia. Export PDF dibatalkan.');
            return;
        }

        const table = document.getElementById(tableId);
        if (!table) {
            alert('Tabel tidak ditemukan!');
            return;
        }

        // ─── AMBIL HEADER TABEL ───
        const headers = [];
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            headerRow.querySelectorAll('th').forEach(th => {
                headers.push({
                    text: th.textContent.trim(),
                    style: 'tableHeader',
                    fillColor: '#696CFF',
                    color: '#FFFFFF',
                    bold: true
                });
            });
        }

        // ─── AMBIL DATA BARIS ───
        const body = [headers];
        const tbody = table.querySelector('tbody');
        if (tbody) {
            tbody.querySelectorAll('tr').forEach(tr => {
                const cells = tr.querySelectorAll('td');
                if (cells.length === 0) return;
                if (cells.length === 1 && cells[0].colSpan > 1) return;

                const row = [];
                cells.forEach(td => {
                    let text = td.textContent.trim();
                    text = text.replace(/\s+/g, ' ');
                    if (text.length > 100) {
                        text = text.substring(0, 97) + '...';
                    }
                    row.push(text);
                });
                body.push(row);
            });
        }

        // ─── AMBIL DATA SUMMARY (TFOOT) ───
        const tfoot = table.querySelector('tfoot');
        if (tfoot) {
            tfoot.querySelectorAll('tr').forEach(tr => {
                const cells = tr.querySelectorAll('td, th');
                if (cells.length === 0) return;
                const row = [];
                cells.forEach(cell => {
                    let text = cell.textContent.trim();
                    text = text.replace(/\s+/g, ' ');
                    if (text.length > 100) {
                        text = text.substring(0, 97) + '...';
                    }
                    row.push({ text: text, bold: true, fillColor: '#E8E8FF' });
                });
                body.push(row);
            });
        }

        const docDefinition = {
            pageOrientation: orientation,
            pageMargins: [40, 60, 40, 60],
            content: [
                {
                    text: title,
                    style: 'header',
                    margin: [0, 0, 0, 20]
                },
                {
                    table: {
                        headerRows: 1,
                        widths: Array(headers.length).fill('auto'),
                        body: body
                    },
                    layout: {
                        fillColor: function (rowIndex) {
                            return (rowIndex === 0) ? '#696CFF' : ((rowIndex % 2 === 0) ? '#F5F5F9' : null);
                        },
                        hLineWidth: function () { return 0.5; },
                        vLineWidth: function () { return 0.5; },
                        hLineColor: function () { return '#DBDADE'; },
                        vLineColor: function () { return '#DBDADE'; },
                    }
                },
                {
                    text: 'Dicetak pada: ' + new Date().toLocaleString('id-ID'),
                    style: 'footer',
                    margin: [0, 20, 0, 0]
                }
            ],
            styles: {
                header: { fontSize: 18, bold: true, color: '#5F61E6' },
                tableHeader: { bold: true, fontSize: 11, color: '#FFFFFF' },
                footer: { fontSize: 9, italics: true, color: '#697A8D' }
            },
            defaultStyle: { fontSize: 9 }
        };

        // ─── DOWNLOAD PDF ───
        // Di WebView, pdfMake.download() TIDAK berfungsi → gunakan getBlob + _downloadBlob
        var pdfDoc = pdfMake.createPdf(docDefinition);

        if (_isWebView()) {
            pdfDoc.getBlob(function (blob) {
                _downloadBlob(blob, filename + '.pdf');
            });
        } else {
            pdfDoc.download(filename + '.pdf');
        }

    } catch (error) {
        console.error('Export PDF error:', error);
        alert('Terjadi kesalahan saat export PDF: ' + error.message);
    }
}

// ══════════════════════════════════════════════════════════════════════════
//  GLOBAL DOWNLOAD INTERCEPTOR
//  Otomatis menangkap SEMUA download via link.click() di WebView
//  dan redirect ke _downloadBlob() agar berfungsi di Capacitor.
//
//  Ini memperbaiki 30+ template yang masih menggunakan:
//    var link = document.createElement('a');
//    link.href = URL.createObjectURL(blob);
//    link.download = 'filename.xls';
//    link.click();
//
//  Tanpa interceptor ini, link.click() GAGAL DIAM-DIAM di Android WebView.
// ══════════════════════════════════════════════════════════════════════════
(function() {
    'use strict';

    // Hanya aktifkan interceptor di WebView
    if (!_isWebView()) return;

    // Simpan referensi ke click() asli
    var _originalClick = HTMLAnchorElement.prototype.click;

    // Override click() untuk <a> elements
    HTMLAnchorElement.prototype.click = function() {
        // Cek apakah ini adalah download link (punya attribute download DAN href blob:/data:)
        var downloadAttr = this.getAttribute('download');
        var href = this.href || '';

        if (downloadAttr && (href.startsWith('blob:') || href.startsWith('data:'))) {
            // Ini adalah download link — intercept dan gunakan _downloadBlob()
            var filename = downloadAttr || 'download';

            console.log('[DownloadInterceptor] Intercepted download: ' + filename);

            if (href.startsWith('blob:')) {
                // Blob URL — fetch blob lalu download via _downloadBlob
                fetch(href)
                    .then(function(response) { return response.blob(); })
                    .then(function(blob) {
                        _downloadBlob(blob, filename);
                    })
                    .catch(function(err) {
                        console.error('[DownloadInterceptor] Fetch blob gagal:', err);
                        // Fallback: coba click asli
                        _originalClick.call(this);
                    }.bind(this));
            } else if (href.startsWith('data:')) {
                // Data URI — convert ke Blob lalu download
                try {
                    var parts = href.split(',');
                    var meta = parts[0]; // data:mime;base64
                    var raw = parts[1];
                    var mimeMatch = meta.match(/data:([^;]+)/);
                    var mime = mimeMatch ? mimeMatch[1] : 'application/octet-stream';
                    var isBase64 = meta.indexOf('base64') !== -1;

                    var byteString;
                    if (isBase64) {
                        byteString = atob(raw);
                    } else {
                        byteString = decodeURIComponent(raw);
                    }

                    var ab = new ArrayBuffer(byteString.length);
                    var ia = new Uint8Array(ab);
                    for (var i = 0; i < byteString.length; i++) {
                        ia[i] = byteString.charCodeAt(i);
                    }

                    var blob = new Blob([ab], { type: mime });
                    _downloadBlob(blob, filename);
                } catch (e) {
                    console.error('[DownloadInterceptor] Data URI parse gagal:', e);
                    _originalClick.call(this);
                }
            }

            return; // Jangan panggil click() asli
        }

        // Bukan download link — panggil click() asli
        _originalClick.call(this);
    };

    console.log('[ExportUtils] Global download interceptor aktif untuk WebView');
})();
