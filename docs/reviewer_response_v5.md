# Respons revisi Versi 5

1. **Klaim dan implementasi asli.** Judul, abstrak, kesimpulan, dan batasan menyatakan audit kondisional atas model seleksi yang dilengkapi secara eksplisit. Tidak ada verifikasi prototype FPoR asli, pengujian serangan PBFT, atau pembuktian kegagalan universal protokol.
2. **Reproduksi.** Commit V3 yang dahulu dirujuk berhasil direproduksi dalam venv baru: 37 checksum rilis dan 17 keluaran CSV/JSON cocok. Ketidakcocokan awal disebabkan konversi LF/CRLF oleh Git; checkout tanpa konversi menyelesaikannya. Rilis V5 memakai `.gitattributes` untuk mempertahankan byte. Commit V5 dalam manuskrip harus sesuai hasil 40 populasi; laporan reproduksi disediakan terpisah. Ini reproduksi otomatis sisi penulis pada host yang sama, bukan audit independen oleh pihak eksternal.
3. **Referensi.** Dari katalog 89, manuskrip mempertahankan 56 rujukan dengan peran langsung pada asumsi, metode, reputasi, fairness, atau perbandingan terdekat. Sebanyak 33 rujukan konteks umum dipindahkan dari daftar sitasi aktif. Katalog lengkap tetap tersedia. Audit struktur metadata tidak menemukan field inti atau pengenal sumber hilang maupun DOI duplikat; tidak diklaim sebagai pembacaan ulang seluruh full text atau verifikasi Scopus.
4. **Paired effect size.** Seluruh 81 konfigurasi dianalisis menggunakan 40 selisih populasi berpasangan; sembilan ditampilkan pada n=128,k=16. CI t approximate pointwise menggunakan df=39. Komite yang sama dipakai untuk high versus random; tidak ada pooling 20.000 komite sebagai unit independen. Ini efek placement, bukan efek recovery. Tidak ada simulasi baru.
5. **Recovery.** Batas bukti diperjelas: feasibility saja tidak menjamin fairness atau keamanan recovery. Tidak mengklaim kebijakan pemulihan aman.
6. **Penulis dan deklarasi.** Djarot Hindarto sebagai penulis pertama/korespondensi; Eko Mulyanto Yuniarno sebagai penulis kedua (ITS); Sari Ningsih sebagai penulis ketiga (Universitas Nasional). CRediT sesuai keterangan penulis: Djarot konseptualisasi, software, draf; Eko review/editing; Sari bahasa/presentasi. Tidak ada pendanaan eksternal dan konflik kepentingan menurut konfirmasi pengguna. Disclosure Codex mencakup penulisan dan proses riset; tidak mengarang pernyataan bahwa semua penulis telah memvalidasi seluruh hasil.

## Pemeriksaan sebelum submission
Seluruh penulis tetap perlu menyetujui isi final, urutan authorship dan tanggung jawab ilmiah; persetujuan tersebut tidak dibuktikan oleh proses kompilasi. Kesetiaan ke prototype asli dan reproduksi oleh pihak eksternal tetap batasan. Tidak ada jaminan skor 9,8/10 atau penerimaan jurnal.

## Sumber kebijakan deklarasi
https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
https://www.elsevier.com/about/policies-and-standards/publishing-ethics
Panduan khusus ICT Express tidak dapat diambil melalui akses web saat revisi (403); layout dua kolom menggunakan CAS yang sudah tersedia, bukan klaim pemeriksaan seluruh ketentuan submission terkini.
