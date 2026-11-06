# Audit spesifikasi primer — 6 November 2026

Sumber: PDF lokal `../../Refrence/FPoR - Fair proof-of-reputation consensus for blockchain.pdf`, DOI https://doi.org/10.1016/j.icte.2022.11.007. Nomor halaman berikut adalah nomor cetak artikel.

| Unsur | Bukti primer | Keputusan model |
|---|---|---|
| Eksklusi | Bagian 3.3, hlm. 47, butir terakhir: larangan memilih node pada grup konsensus yang memproses dua blok berurutan | Full-membership exclusion adalah pembacaan literal; tidak dianggap satu-satunya implementasi |
| Alternatif | Bagian 3.5.1, hlm. 48, Prevention of over-control membahas proposal dua blok berurutan | Varian proposer-only diuji terpisah |
| Ambang | Persamaan (2) dan (3), hlm. 47 membandingkan mean grup dengan mean semua kandidat | Cooldown tidak menghapus identitas dari populasi mean; ini asumsi eksplisit |
| Pembaruan | Bagian 3.5.1, hlm. 48: current bertambah 2^gamma kali reward, lalu cumulative bertambah current yang telah diperbarui | Hanya anggota komite jujur memperoleh pembaruan; nonanggota tetap |
| Parameter | Bagian 4.1, hlm. 48–49: reward 1, gamma 3 lalu 2, alpha .6 beta .4; inisialisasi 120/110/100 | Jadwal diperluas setelah putaran 10 dengan gamma 2; itu pilihan eksperimen |
| Inisialisasi sama | Nilai awal diberikan lewat collateral, tetapi aturan rinci pemetaannya tidak dispesifikasikan | Equal initialization diperbolehkan dalam model; tidak diklaim identik dengan eksperimen asli |
| Sampling | Persamaan (1) memberi bobot per-node; prosedur sampling subset terkondisi tidak lengkap | Product weighting dan MILP adalah model audit yang dibedakan dengan jelas |
| Prototipe | Bagian 4.1 menyatakan proof of concept Python; tidak ada tautan kode pada PDF | Penelusuran publik bertarget belum menemukan repository penulis yang dapat diverifikasi |

Implikasi: proposisi baru membuktikan reachability dalam state machine yang didefinisikan di manuskrip, bukan kerusakan terverifikasi pada kode asli. Mengubah cakupan reward, saat menghitung mean, atau anggota populasi kandidat dapat mengubah hasil.
