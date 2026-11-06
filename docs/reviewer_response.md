# Tanggapan atas enam persoalan — Versi 3

## CRITICAL 1 — Kesetiaan spesifikasi

Ditambahkan tabel **Original FPoR specification versus audit model** dalam manuskrip: bagian, halaman, kutipan pendek, klasifikasi status, dan pilihan audit untuk enam unsur. Full exclusion diklasifikasikan sebagai pembacaan preskriptif Bagian 3.3 yang cakupan operasionalnya ambigu ketika dibaca bersama Bagian 3.5.1. Asumsi inisialisasi seragam dan event ordering diberi label analitis. Judul diperhalus menjadi audit terhadap selection rules. Tidak dinyatakan bahwa implementasi asli pasti mengalami masalah ini.

## CRITICAL 2 — Liveness

Ditambahkan definisi state/transition, formation liveness, dan block liveness. Selection deadlock adalah properti submodel dengan eligibility/scores tetap dan hanya transisi seleksi diizinkan. Consensus stall adalah interval observasi tanpa commit. Permanent liveness violation memerlukan eksekusi tak berhingga yang memenuhi asumsi lingkungan tetapi tidak pernah melayani request. Proposition 2 hanya membuktikan keadaan pembentukan komite yang gagal dalam model tersebut. Recovery atau perubahan eligibility dapat mengubah hasil; tidak ada klaim bahwa view change PBFT telah diuji.

## MAJOR 3 — Probabilitas dan interval

200 lintasan solver dipertahankan sebagai witness generation. Ditambahkan **4.000 lintasan probabilistik**, 200 per konfigurasi, dengan sampler uniform terkondisi yang didefinisikan matematis. Rejection dan exact grouped fallback menghasilkan distribusi yang sama; solver tidak pernah memasok sampel. Kasus kehabisan anggaran sampling memiliki label terpisah. Run final tidak memiliki sampling-censored trajectories; fallback eksak dipakai 149 kali. Frekuensi dan interval Wilson pointwise 95% tersedia per konfigurasi. Tidak ada pooling hasil 10/25 dengan data probabilistik baru.

## MAJOR 4 — Klaim Byzantine

Dipilih jalur yang diizinkan reviewer: fokus tetap pada analisis seleksi. Certificate witness dipertahankan dengan pembatasan eksplisit bahwa tidak ada pre-prepare/prepare/commit, view change, transport asinkron, atau pemeriksaan state replication. Tidak ada probabilitas serangan PBFT operasional yang diklaim. Pengujian tersebut tetap pekerjaan terpisah jika lingkup penelitian kelak diperluas.

## MAJOR 5 — Sensitivitas

Ditambahkan **216 populasi**: n=64/128/256; k=log2(n), n/8, n/4; reputasi continuous uniform, lognormal, dan hasil 200 siklus reward/penalty sintetis; delapan seed populasi. Masing-masing memiliki 500 sampel komite. Fraksi adversarial .10/.25/.40 dan penempatan high-weight/random menghasilkan **1.296 evaluasi**. Semua populasi tersimpan. Wilson digunakan pada satu populasi; interval t aproksimasi menggunakan delapan populasi sebagai unit independen. Tidak diklaim bahwa generator histori adalah implementasi FPoR. Jain dan TV empiris dilabeli plug-in.

## MAJOR 6 — Reproducibility publik

Paket publik berisi kode, dependency, konfigurasi solver, seed, oracle, score arrays, traces, hasil CSV/JSON, dan checksum. Pengunggahan hanya mencakup artefak penelitian: tidak menyertakan PDF publisher, attachment review pribadi, atau kredensial. Repository publik sudah tersedia di https://github.com/giantfor/fpor-selection-audit dan commit tetap dicantumkan dalam Data and Code Availability. Akses tanpa login, replay, dan regenerasi eksperimen dari clone baru berhasil diverifikasi; enam output utama cocok dengan checksum rilis.

## Pemeriksaan

- Replay independen memeriksa **53.400 transisi** probabilistik dan **1.400 terminasi** berlabel infeasible.
- Pemeriksaan lama 3.335 transisi solver tetap tersedia.
- Hasil bukan skor reviewer baru dan tidak menjamin penerimaan publikasi.
