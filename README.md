# Tucil3_13524120_13524125

Program solver untuk permainan **Ice Sliding Puzzle** menggunakan algoritma pathfinding UCS, GBFS, dan A*. Karakter bergerak di atas permukaan es yang licin dan tidak berhenti sampai menabrak dinding atau rintangan.

## Requirement

- Python 3.8 atau lebih baru

## Cara Menjalankan

Jalankan dari folder `src/`:

```
cd src
python main.py
```

Program akan meminta input secara berurutan di terminal:

1. Path ke file `.txt` input (contoh: `../test/test1_simple.txt`)
2. Pilih algoritma: `UCS`, `GBFS`, atau `A*`
3. Jika memilih `A*`, pilih heuristik: `H1`, `H2`, atau `H3`

Setelah solusi ditemukan, program menawarkan:
- **Playback** — navigasi step by step dengan arrow kiri/kanan, ESC untuk lompat ke step tertentu, `q` untuk keluar
- **Simpan solusi** — menyimpan output ke file `.txt`

## Format Input

File `.txt` terdiri dari tiga bagian:

```
N M
<N baris grid>
<N baris matriks cost>
```

Simbol pada grid:
| Simbol | Keterangan |
|--------|-----------|
| `Z` | Posisi awal aktor |
| `O` | Titik tujuan |
| `X` | Rintangan, aktor berhenti tepat sebelumnya |
| `L` | Lava, menyebabkan game over jika dilewati |
| `*` | Tile kosong yang bisa dilewati |
| `0`-`9` | Tile angka, harus diinjak sesuai urutan |

## Algoritma dan Heuristik

| Algoritma | Keterangan |
|-----------|-----------|
| UCS | Uniform Cost Search, menjamin solusi optimal |
| GBFS | Greedy Best First Search, cepat tapi tidak selalu optimal |
| A* | Kombinasi cost aktual dan heuristik |

Heuristik untuk A*:
| Kode | Nama | Keterangan |
|------|------|-----------|
| H1 | `manhattan_goal` | Manhattan distance dari aktor ke goal|
| H2 | `manhattan_goal_angka` | Manhattan ke angka wajib          
                               berikutnya + Manhattan ke goal |
| H3 | `cheby` | Chebyshev distance ke goal |

## Struktur Repository

```
Tucil3_13524120_13524125/
├── src/
│   ├── main.py
│   ├── core/
│   │   └── board.py
│   ├── models/
│   │   └── state.py
│   ├── algorithms/
│   │   ├── ucs.py
│   │   ├── gbfs.py
│   │   └── astar.py
│   └── ui/
│       └── playback.py
├── test/
│   ├── test1_simple.txt
│   ├── test2_lava.txt
│   ├── test3_sequence.txt
│   ├── test4_obstacles.txt
│   └── test5_large.txt
└── doc/

```

## Author

| Nama | NIM |
|------|-----|
| [isi sendiri] | 13524120 |
| Muhammad Rafi Akbar | 13524125 |
