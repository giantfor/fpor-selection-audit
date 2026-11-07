# Respons terhadap review versi 6 — revisi Versi 7

## P0: graphical abstract — diperbaiki

Dua skenario kini berada dalam panel terpisah tanpa panah penghubung. Panel A menyatakan equal initialization, full membership exclusion, dan global reputation thresholds; hasilnya berbunyi “No feasible next committee” dengan syarat tersebut tepat di bawahnya. Panel B berlabel “Separate audit scenario”, menggunakan reputasi dua tingkat, n=16, k=4 dan empat adversary bereputasi tinggi. Angka 0.245→0.336 dan Jain 1.000→0.956 tetap berasal dari skenario B. Tidak ada klaim bahwa skenario A menghasilkan angka B.

## P0: reproduksi independen — belum terpenuhi secara eksternal

Tidak ada peneliti eksternal yang menjalankan audit dalam sesi ini. Menjalankan ulang kode, mengganti environment, atau memakai program pemeriksa kedua tidak memenuhi independensi personal yang diminta reviewer. Paket `Supplement/EXTERNAL_REPRODUCTION.md` menyediakan prosedur lengkap; rekaman operator tetap berstatus `not_performed`. Laporan eksekusi otomatis sisi penulis tetap tersedia dan tidak disamakan dengan pengesahan eksternal.

## P1: Table 7 — diperiksa ulang

Program baru `verify_paired_independent.py` hanya memakai standard library. Program membangun ulang 3.240 pasangan dari 6.480 baris integer risky/samples, memeriksa ID replikasi 0–39 pada masing-masing 81 konfigurasi, dan menghitung mean/varians memakai pecahan rasional. Kuantil Student dihitung melalui integrasi Simpson dan bisection, tanpa mengimpor NumPy, SciPy atau fungsi estimator utama. Semua 81 konfigurasi dan sembilan baris tabel cocok dalam toleransi 1e-10. Ini verifikasi implementasi estimator atas data tersimpan, bukan simulasi ulang independen.

Pada evolved, n=128, k=16, fraksi 0,10, mean=0,00070 dan CI kira-kira [-0,00003216; 0,00143216]. Nol memang termasuk sebelum pembulatan. Tabel sekarang memakai lima desimal; teks membatasi klaim efek kecil, rare-event coverage, multiplicity dan signifikansi praktis. Tidak ditambahkan eksperimen hanya untuk mengejar skor.

## P1: lingkup teorema dan keamanan — dipertahankan dan diperjelas

Judul/abstrak tetap menyebut audit kondisional FPoR-inspired. Tambahan aljabar pendek menjelaskan kelas aturan lebih umum: bila hanya identitas yang dieksklusi memperoleh total kenaikan positif dan tetap masuk rata-rata global, sedangkan semua kandidat eligible mempertahankan skor awal yang sama, satu koordinat wajib saja cukup membuat seleksi berikutnya tidak feasible. Ini konsekuensi model, bukan bukti bahwa protokol lain menerapkan premis itu. Selection deadlock, consensus stall, permanent liveness violation dan Byzantine composition tetap dibedakan.

## P2: editorial — diperiksa dengan batasan

Graphical abstract tersedia sebagai PDF/SVG serta PNG/TIFF 4500×1800, 300 dpi, rasio 2,5:1, font Arial. Panduan umum Elsevier diperiksa; panduan khusus ICT Express tidak dapat diakses (403), sehingga kepatuhan jurnal spesifik tidak diklaim selesai. Metadata sitasi dan kompilasi diperiksa kembali. Deklarasi dan urutan tiga penulis dipertahankan.

## Batas penilaian

Revisi ini menutup salah interpretasi visual dan memverifikasi tabel. Verifikasi prototype asli, bukti operasional PBFT, keamanan recovery dan reproduksi oleh pihak eksternal masih belum tersedia. Tidak ada pernyataan nilai 10/10, penerimaan Q1 atau skor reviewer tertentu telah dicapai.
