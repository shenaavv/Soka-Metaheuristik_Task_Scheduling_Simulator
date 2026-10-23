# Perbandingan GA dan MBA untuk Task Scheduling

Repository ini adalah gabungan dua simulator penjadwalan task berbasis
CloudSim Plus:

- **Genetic Algorithm (GA)** pada [`cloudsim-plus-ga/`](cloudsim-plus-ga/)
- **Modified Bat Algorithm (MBA)** pada [`cloudsim-plus-mba/`](cloudsim-plus-mba/)

Keduanya mengikuti desain pada
[`SOKA A_Kelompok 4_DESIGN PROJECT.pdf`](SOKA%20A_Kelompok%204_DESIGN%20PROJECT.pdf).
File source Java, dataset, script, grafik, hasil run, dan PDF dari kedua arsip
dipertahankan. Dataset aktif kedua algoritma disamakan agar perbandingan tidak
bias; dataset asli MBA disimpan sebagai
[`tasks-mba-original.csv`](cloudsim-plus-mba/dataset/tasks-mba-original.csv).

## Anggota Tim

| No | Nama | NRP |
| --- | --- | --- |
| 1 | Kanafira Vanesha Putri | 5027241010 |
| 2 | Tiara Putri Prasetya | 5027241013 |
| 3 | Dina Rahmadani | 5027241065 |
| 4 | Zahra Khaalishah | 5027241070 |
| 5 | S. Farhan Baig | 5027241097 |

## Struktur Project

```text
.
├── run.sh
├── README.md
├── requirements.txt
├── run_scalability_experiment.py
├── SOKA A_Kelompok 4_DESIGN PROJECT.pdf
├── cloudsim-plus-ga/
│   ├── pom.xml
│   ├── dataset/
│   ├── results/
│   └── src/main/java/id/its/cloudtaskscheduling/
│       └── GeneticAlgorithmCloudTaskScheduling.java
└── cloudsim-plus-mba/
    ├── pom.xml
    ├── dataset/
    ├── results/
    └── src/main/java/id/its/cloudtaskscheduling/
        └── MBACloudTaskScheduling.java
```

Folder `results/` berisi mapping, metrik, log eksekusi, dan grafik dari arsip
asal. Folder `target/` akan dibuat ulang oleh Maven bila belum tersedia.

## Arsitektur Cloud

| Komponen | Konfigurasi |
| --- | --- |
| Datacenter | 1 |
| Host | 4 host heterogen, 8/16 PE, RAM 16/32 GB |
| VM | 8 VM dengan 2/4/8 PE dan 1000–2500 MIPS/PE |
| Workload | 100 task Google Cluster Trace yang dipetakan ke schema CloudSim |
| Tujuan | Makespan dan konsumsi energi |

GA memakai populasi 20, 50 generasi, tournament selection, one-point
crossover, mutation rate 0,05, dan elitism. MBA memakai 16 bat, 80 iterasi,
frekuensi, loudness, dan random mutation. Detail implementasi berada di file
Java masing-masing.

## Persyaratan dan Cara Menjalankan

- JDK 17 atau lebih baru
- Apache Maven 3.6 atau lebih baru
- Bash, Git Bash, atau WSL
- Python 3.8+ dan `requirements.txt` hanya untuk eksperimen skalabilitas MBA

Jalankan kedua algoritma dan FCFS baseline dari root:

```bash
bash run.sh
```

Perintah manual:

```bash
cd cloudsim-plus-ga
mvn clean compile exec:java
mvn exec:java -Dexec.args=fcfs

cd ../cloudsim-plus-mba
mvn clean compile exec:java
mvn exec:java -Dexec.args=fcfs
```

Metrik utama tersimpan di:

- [`cloudsim-plus-ga/results/metrics.txt`](cloudsim-plus-ga/results/metrics.txt)
- [`cloudsim-plus-ga/results/fcfs_metrics.txt`](cloudsim-plus-ga/results/fcfs_metrics.txt)
- [`cloudsim-plus-mba/results/metrics.txt`](cloudsim-plus-mba/results/metrics.txt)
- [`cloudsim-plus-mba/results/fcfs_metrics.txt`](cloudsim-plus-mba/results/fcfs_metrics.txt)

## Hasil Eksperimen

Angka berikut diambil dari eksekusi ulang pada 22 Oktober 2026 menggunakan
dataset aktif yang sama (SHA-256:
`605512889143b5fc067f4dafc6c00c93707c1e1066f8f4b5e850b630510f65d2`).

### GA dan MBA

| Metrik | GA | MBA | Observasi |
| --- | ---: | ---: | --- |
| Task selesai | 100 | 100 | Sama |
| Makespan (s) | 273,9825 | 19.830.250.035,1413 | GA jauh lebih kecil pada run ini |
| Energi (J) | 131.769,60 | 44.419.760.078.716,5160 | GA jauh lebih kecil pada run ini |
| Utilisasi CPU/VM | 44,52% | 100,00% | MBA melaporkan utilisasi lebih tinggi |
| Throughput tercetak (task/s) | 0,364987 | 5,042800762612e-09 | MBA memakai notasi ilmiah |

Throughput MBA dihitung sebagai `100 / makespan` dan dicetak dalam notasi
ilmiah agar nilai kecil tersebut tidak berubah menjadi nol secara tampilan.

### Perbandingan Tiga Metode: GA, MBA, dan FCFS

Tabel berikut menampilkan ketiga metode dalam satu perbandingan. FCFS
ditampilkan sebagai dua baseline karena masing-masing project menjalankan
implementasi FCFS pada versi CloudSim Plus dan konfigurasi project-nya sendiri.
Kolom `FCFS (GA)` berasal dari [`cloudsim-plus-ga/results/fcfs_metrics.txt`](cloudsim-plus-ga/results/fcfs_metrics.txt),
sedangkan `FCFS (MBA)` berasal dari [`cloudsim-plus-mba/results/fcfs_metrics.txt`](cloudsim-plus-mba/results/fcfs_metrics.txt).

| Metode | Task selesai | Makespan (s) | Energi (J) | Utilisasi | Throughput (task/s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| GA | 100 | 273,9825 | 131.769,60 | 44,52% | 0,364987 |
| MBA | 100 | 19.830.250.035,1413 | 44.419.760.078.716,5160 | 100,00% | 5,042800762612e-09 |
| FCFS | 100 | 79,4450 (GA) / 56.267.206.489,9020 (MBA) | 38.186,40 (GA) / 76.747.959.251.439,5000 (MBA) | 28,42% (GA) / 54,71% (MBA) | 1,258732 (GA) / 1,777234134023e-09 (MBA) |

Karena baseline FCFS menghasilkan angka berbeda saat dijalankan dari project GA
dan project MBA, rincian sumber angka tersebut ditampilkan berikut ini:

| Metrik | GA | MBA | FCFS (GA) | FCFS (MBA) |
| --- | ---: | ---: | ---: | ---: |
| Task selesai | 100 | 100 | 100 | 100 |
| Makespan (s) | 273,9825 | 19.830.250.035,1413 | 79,4450 | 56.267.206.489,9020 |
| Energi (J) | 131.769,60 | 44.419.760.078.716,5160 | 38.186,40 | 76.747.959.251.439,5000 |
| Utilisasi CPU/VM | 44,52% | 100,00% | 28,42% | 54,71% |
| Throughput (task/s) | 0,364987 | 5,042800762612e-09 | 1,258732 | 1,777234134023e-09 |

Throughput MBA dan FCFS (MBA) ditampilkan dalam notasi ilmiah karena nilainya
sangat kecil. Tidak ada nilai throughput yang diubah menjadi nol.

Jika dibandingkan dengan baseline pada project yang sama:

| Perbandingan | Makespan | Energi | Utilisasi | Throughput |
| --- | ---: | ---: | ---: | ---: |
| GA vs FCFS (GA) | 244,75% lebih tinggi | 245,08% lebih tinggi | +16,10 poin | 71,00% lebih rendah |
| MBA vs FCFS (MBA) | 64,76% lebih rendah | 42,12% lebih rendah | +45,29 poin | 183,99% lebih tinggi* |

Persentase throughput MBA dihitung menggunakan nilai throughput aktual dalam
notasi ilmiah.

### Baseline FCFS

| Metrik | GA FCFS | MBA FCFS |
| --- | ---: | ---: |
| Task selesai | 100 | 100 |
| Makespan (s) | 79,4450 | 56.267.206.489,9020 |
| Energi (J) | 38.186,40 | 76.747.959.251.439,5000 |
| Utilisasi | 28,42% | 54,71% |

### Interpretasi

Pada konfigurasi dan implementasi saat ini, **GA adalah hasil terbaik secara
absolut** untuk makespan dan energi. MBA melaporkan utilisasi 100%, tetapi
makespan dan energi yang sangat besar menunjukkan ada perbedaan skala
waktu/perhitungan pada implementasi MBA yang perlu diaudit sebelum kesimpulan
umum tentang keunggulan MBA dibuat. Versi CloudSim Plus juga berbeda: GA
menggunakan 7.3.3, sedangkan MBA menggunakan 8.0.0.

Hasil ini adalah hasil satu konfigurasi dan satu seed, bukan klaim bahwa GA
selalu lebih baik daripada MBA. Eksperimen lanjutan sebaiknya:

1. menyamakan versi dependency CloudSim Plus;
2. memeriksa konversi `lengthMI`, MIPS, dan satuan waktu pada MBA;
3. mencetak throughput dengan notasi ilmiah atau lebih banyak digit;
4. menjalankan beberapa seed dan melaporkan mean serta standar deviasi.

## Analisis PDF Desain

PDF desain memuat rancangan sistem penjadwalan cloud, arsitektur host/VM,
alur algoritma metaheuristik, dan evaluasi metrik. Implementasi gabungan ini
mempertahankan pembagian source Java, dataset, hasil, dan script sesuai pola
tersebut. README ini menambahkan analisis komparatif GA-vs-MBA sebagai laporan
gabungan.

## Regenerasi Dataset dan Grafik

Dataset dasar dapat dibuat ulang dari trace dengan script pada masing-masing folder:

```bash
python3 cloudsim-plus-ga/dataset/prepare_google_trace.py
python3 cloudsim-plus-mba/dataset/prepare_google_trace.py
```

Trace mentah tersedia di
[`cloudsim-plus-ga/dataset/google-cluster-data-1.csv.gz`](cloudsim-plus-ga/dataset/google-cluster-data-1.csv.gz)
dan disalin ke folder MBA agar kedua project memiliki input reproducible yang
sama. Eksperimen skalabilitas MBA:

```bash
python3 run_scalability_experiment.py --runs 3
```

Perintah tersebut membuat dataset `tasks-100.csv` sampai `tasks-1000.csv` di
kedua folder algoritma, menjalankan GA, MBA, dan baseline FCFS sebanyak tiga
kali untuk setiap ukuran, lalu menghasilkan:

- [`results/scalability_runs.csv`](results/scalability_runs.csv): eksekusi
  yang sudah selesai (42 run lengkap untuk 100–700 task dan 1 run GA untuk
  800 task);
- [`results/scalability_summary.csv`](results/scalability_summary.csv): mean
  dan standar deviasi tiap ukuran;
- grafik SVG `results/scalability_makespan.svg`,
  `results/scalability_energy.svg`, `results/scalability_throughput.svg`, dan
  `results/scalability_utilization.svg`.

Jika `matplotlib` tersedia, runner juga membuat versi PNG dengan nama yang sama.
SVG tetap dibuat tanpa dependency tambahan sehingga grafik selalu tersedia.

### Hasil Skalabilitas Tiga Repetisi

Tabel berikut memakai angka aktual dari
[`results/scalability_summary.csv`](results/scalability_summary.csv). Nilai
adalah rata-rata tiga run. Efisiensi dihitung sebagai
`(FCFS - algoritma) / FCFS × 100%`; nilai negatif berarti algoritma lebih
buruk daripada FCFS. Satuan energi adalah joule.

#### GA vs FCFS

| Jumlah Task | Makespan GA (s) | Makespan FCFS (s) | Efisiensi Makespan | Energi GA (J) | Energi FCFS (J) | Efisiensi Energi | Avg Util GA (%) | Avg Util FCFS (%) | Throughput GA (task/s) | Throughput FCFS (task/s) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 273,9825 | 79,4450 | -244,75% | 131.769,60 | 38.186,40 | -245,08% | 44,52 | — | 0,364987 | 1,258732 |
| 200 | 385,1665 | 146,5350 | -162,85% | 185.133,84 | 70.389,60 | -163,01% | 112,33 | — | 0,519256 | 1,364087 |
| 300 | 386,0575 | 207,5300 | -86,02% | 186.289,20 | 99.667,20 | -86,89% | 233,84 | — | 0,777086 | 1,445579 |
| 400 | 488,1687 | 255,5500 | -91,03% | 234.421,12 | 122.716,80 | -91,03% | 397,42 | — | 0,819389 | 1,565049 |
| 500 | 434,2390 | 342,4450 | -26,80% | 208.715,04 | 164.426,40 | -26,94% | 554,26 | — | 1,151440 | 1,460094 |
| 600 | 484,4109 | 418,0350 | -15,88% | 232.731,84 | 200.709,60 | -15,96% | 726,62 | — | 1,238618 | 1,435763 |
| 700 | 546,5427 | 493,3330 | -10,78% | 262.492,80 | 236.852,64 | -10,82% | 816,50 | — | 1,280778 | 1,419229 |

#### MBA vs FCFS

| Jumlah Task | Makespan MBA (s) | Makespan FCFS (s) | Efisiensi Makespan | Energi MBA (J) | Energi FCFS (J) | Efisiensi Energi | Avg Util MBA (%) | Avg Util FCFS (%) | Throughput MBA (task/s) | Throughput FCFS (task/s) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 19.830.250.035,14 | 56.267.206.489,90 | 64,76% | 44.419.760.078.716,52 | 76.747.959.251.439,50 | 42,12% | 100,00 | — | 5,042800762612e-09 | 1,777234134023e-09 |
| 200 | 89.312.986.124,30 | 86.708.971.865,03 | -3,00% | 200.061.088.918.439,60 | 194.228.096.977.667,16 | -3,00% | 100,00 | — | 2,239316013034e-09 | 2,306566387517e-09 |
| 300 | 194.785.420.841,29 | 165.401.168.754,52 | -17,77% | 436.319.342.684.490,56 | 370.498.618.010.128,50 | -17,77% | 100,00 | — | 1,540156335645e-09 | 1,813771947677e-09 |
| 400 | 338.963.559.820,32 | 247.489.179.947,84 | -36,96% | 759.278.373.997.517,00 | 554.375.763.083.157,70 | -36,96% | 100,00 | — | 1,180067852167e-09 | 1,616232273606e-09 |
| 500 | 515.260.503.082,70 | 405.204.203.864,22 | -27,16% | 1.154.183.526.905.241,50 | 907.657.416.655.852,40 | -27,16% | 100,00 | — | 9,703829364149e-10 | 1,233945737067e-09 |
| 600 | 806.588.523.401,37 | 728.334.308.940,44 | -10,74% | 1.806.758.292.419.060,75 | 1.631.468.851.026.575,20 | -10,74% | 100,00 | — | 7,438737132904e-10 | 8,237975235203e-10 |
| 700 | 1.203.808.412.058,50 | 884.833.464.838,47 | -36,05% | 2.696.530.843.011.030,50 | 1.982.026.961.238.183,00 | -36,05% | 100,00 | — | 5,814878787921e-10 | 7,911093192297e-10 |

Kolom Avg Util FCFS bertanda `—` karena runner sebelumnya belum menyimpan
utilisasi FCFS ke CSV. Runner sudah diperbarui untuk merekam kolom tersebut
pada eksekusi berikutnya; throughput FCFS di atas dihitung dari
`jumlah_task / makespan`.

#### GA vs MBA vs FCFS

Tabel berikut merangkum ketiga metode dalam satu tabel. FCFS yang digunakan
adalah baseline dari project GA agar pembandingnya sama untuk GA dan MBA.
Efisiensi pada tabel ini dihitung terhadap FCFS:
`(FCFS - metode) / FCFS × 100%`. Nilai positif berarti metode lebih baik
daripada FCFS. Nilai `—` pada utilisasi FCFS mengikuti keterbatasan CSV lama.

| Jumlah Task | Makespan GA (s) | Makespan MBA (s) | Makespan FCFS (s) | Efisiensi GA | Efisiensi MBA | Energi GA (J) | Energi MBA (J) | Energi FCFS (J) | Efisiensi Energi GA | Efisiensi Energi MBA | Avg Util GA (%) | Avg Util MBA (%) | Avg Util FCFS (%) | Throughput GA (task/s) | Throughput MBA (task/s) | Throughput FCFS (task/s) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 273,9825 | 19.830.250.035,14 | 79,4450 | -244,87% | -24.960.979.238,08% | 131.769,60 | 44.419.760.078.716,52 | 38.186,40 | -245,07% | -116.323.507.951,86% | 44,52 | 100,00 | — | 0,364987 | 5,042800762612e-09 | 1,258732 |
| 200 | 385,1665 | 89.312.986.124,30 | 146,5350 | -162,85% | -60.949.934.130,25% | 185.133,84 | 200.061.088.918.439,60 | 70.389,60 | -163,01% | -284.219.670.019,51% | 112,33 | 100,00 | — | 0,519256 | 2,239316013034e-09 | 1,364087 |
| 300 | 386,0575 | 194.785.420.841,29 | 207,5300 | -86,02% | -93.858.921.907,08% | 186.289,20 | 436.319.342.684.490,56 | 99.667,20 | -86,91% | -437.776.261.984,71% | 233,84 | 100,00 | — | 0,777086 | 1,540156335645e-09 | 1,445579 |
| 400 | 488,1687 | 338.963.559.820,32 | 255,5500 | -91,03% | -132.640.798.107,91% | 234.421,12 | 759.278.373.997.517,00 | 122.716,80 | -91,03% | -618.724.065.388,60% | 397,42 | 100,00 | — | 0,819389 | 1,180067852167e-09 | 1,565049 |
| 500 | 434,2390 | 515.260.503.082,70 | 342,4450 | -26,81% | -150.465.184.990,36% | 208.715,04 | 1.154.183.526.905.241,50 | 164.426,40 | -26,94% | -701.945.385.133,30% | 554,26 | 100,00 | — | 1,151440 | 9,703829364149e-10 | 1,460094 |
| 600 | 484,4109 | 806.588.523.401,37 | 418,0350 | -15,88% | -192.947.605.579,28% | 232.731,84 | 1.806.758.292.419.060,75 | 200.709,60 | -15,95% | -900.185.288.704,85% | 726,62 | 100,00 | — | 1,238618 | 7,438737132904e-10 | 1,435763 |
| 700 | 546,5427 | 1.203.808.412.058,50 | 493,3330 | -10,79% | -244.015.383.435,77% | 262.492,80 | 2.696.530.843.011.030,50 | 236.852,64 | -10,83% | -1.138.484.604.931,65% | 816,50 | 100,00 | — | 1,280778 | 5,814878787921e-10 | 1,419229 |

Berdasarkan tabel gabungan, FCFS memiliki makespan, energi, dan throughput
terbaik pada seluruh ukuran yang sudah lengkap. GA menjadi metode
metaheuristik yang lebih baik daripada MBA pada makespan dan energi, sedangkan
MBA melaporkan utilisasi 100%. Angka MBA yang sangat besar tetap perlu
ditafsirkan dengan hati-hati karena indikasi perbedaan skala waktu/perhitungan
di implementasinya.

Throughput MBA sekarang dicetak dalam notasi ilmiah dengan 12 digit presisi
(contoh `5.042000000000e-09 task/s`), sehingga nilainya tidak lagi tampil
sebagai `0,000000` akibat pembulatan. Nilainya tetap sangat kecil karena
makespan MBA sangat besar.
Utilisasi GA di atas 100% juga merupakan nilai yang dilaporkan implementasi
saat ini dan perlu diaudit sebelum dipakai sebagai klaim fisik.

Eksperimen dihentikan saat 800 task: GA run pertama sudah tersimpan
(`makespan 577,15 s`, `energy 277.084,80 J`, FCFS makespan `556,905 s`,
FCFS energy `267.367,20 J`), sedangkan MBA 800 dan ukuran 900–1000 belum
memiliki perbandingan tiga-run lengkap. Dataset `tasks-800.csv` sampai
`tasks-1000.csv` tetap tersedia di kedua folder.

Untuk melanjutkan dari hasil CSV tanpa mengulang run yang sudah lengkap:

```bash
python3 run_scalability_experiment.py --runs 3 --resume
```

Runner sekarang memperbarui `results/scalability_runs.csv`,
`results/scalability_summary.csv`, dan grafik setelah setiap run selesai.
