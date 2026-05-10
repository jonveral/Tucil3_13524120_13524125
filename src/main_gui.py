import sys
import os
import pygame
import tkinter as tk
from tkinter import filedialog

sys.path.insert(0, os.path.dirname(__file__))

from core.board import Board
from algorithms.ucs import solve_ucs
from algorithms.gbfs import solve_gbfs
from algorithms.astar import solve_astar, HEURISTICS
from algorithms.bfs import solve_bfs
from algorithms.dfs import solve_dfs
from ui.playback import build_steps, save_solution

TILE_MIN  = 16
TILE_MAX  = 96
TILE_DEF  = 64
SIDEBAR_W = 280
FPS       = 60

WARNA = {
    '*': (50, 50, 80),
    'X': (220, 220, 220),
    'L': (200, 40, 40),
    'O': (50, 180, 80),
    ' ': (30, 30, 50),
}
WARNA_ANGKA        = (210, 180, 40)
WARNA_BG           = (20, 20, 35)
WARNA_SIDEBAR      = (30, 30, 50)
WARNA_TEKS         = (230, 230, 230)
WARNA_TEKS_DIM     = (140, 140, 160)
WARNA_TOMBOL       = (60, 90, 160)
WARNA_TOMBOL_HOVER = (80, 120, 200)
WARNA_TOMBOL_AKTIF = (40, 160, 100)
WARNA_AKTOR        = (50, 120, 220)

def load_assets(asset_dir, tile_size):
    assets = {}
    nama_file = {
        'ice': 'ice.png', 'obstacle': 'obstacle.png',
        'lava': 'lava.png', 'goal': 'goal.png',
        'player': 'player.png',
    }
    for key, fname in nama_file.items():
        path = os.path.join(asset_dir, fname)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                assets[key] = pygame.transform.scale(img, (tile_size, tile_size))
            except Exception:
                assets[key] = None
        else:
            assets[key] = None

    bg_path = os.path.join(asset_dir, 'bg.png')
    if os.path.exists(bg_path):
        try:
            assets['bg'] = pygame.image.load(bg_path).convert()
        except Exception:
            assets['bg'] = None
    else:
        assets['bg'] = None
    return assets

def gambar_bg(surface, assets, area_w, area_h, cache):
    bg = assets.get('bg')
    if not bg:
        return
    if cache[0] is None or cache[1] != (area_w, area_h):
        cache[0] = pygame.transform.scale(bg, (area_w, area_h))
        cache[1] = (area_w, area_h)
    surface.blit(cache[0], (0, 0))

def gambar_tile(surface, assets, tile, r, c, off_x, off_y, tile_size):
    x = off_x + c * tile_size
    y = off_y + r * tile_size
    rect = pygame.Rect(x, y, tile_size, tile_size)

    if tile in ('*', 'Z', 'O') or tile.isdigit():
        base = WARNA['*']
    elif tile == 'X':
        base = WARNA['X']
    elif tile == 'L':
        base = WARNA['L']
    else:
        base = WARNA['*']

    pygame.draw.rect(surface, base, rect)

    if tile in ('*', 'Z', 'O') or tile.isdigit():
        if assets.get('ice'):
            surface.blit(assets['ice'], rect)
    elif tile == 'X' and assets.get('obstacle'):
        surface.blit(assets['obstacle'], rect)
    elif tile == 'L' and assets.get('lava'):
        surface.blit(assets['lava'], rect)

    if tile == 'O':
        if assets.get('goal'):
            surface.blit(assets['goal'], rect)
        else:
            pad = max(4, tile_size // 8)
            pygame.draw.rect(surface, WARNA['O'],
                             pygame.Rect(x + pad, y + pad, tile_size - pad*2, tile_size - pad*2))
    elif tile.isdigit():
        font = pygame.font.Font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'Minecraft.ttf'), max(8, tile_size // 2))
        label = font.render(tile, False, WARNA_ANGKA)
        surface.blit(label, (x + (tile_size - label.get_width()) // 2,
                             y + (tile_size - label.get_height()) // 2))

    pygame.draw.rect(surface, (0, 0, 0), rect, 1)

def gambar_papan(surface, assets, board, off_x, off_y, tile_size):
    for r in range(board.N):
        for c in range(board.M):
            tile = board.grid[r][c]
            if tile == 'Z':
                tile = '*'
            gambar_tile(surface, assets, tile, r, c, off_x, off_y, tile_size)

def gambar_aktor(surface, assets, aktor_px, tile_size):
    if assets.get('player'):
        half = tile_size // 2
        surface.blit(assets['player'], (int(aktor_px[0]) - half, int(aktor_px[1]) - half))
    else:
        pygame.draw.circle(surface, WARNA_AKTOR,
                           (int(aktor_px[0]), int(aktor_px[1])),
                           max(4, tile_size // 2 - 4))

class Tombol:
    def __init__(self, rect, teks, font, aktif=False):
        self.rect = pygame.Rect(rect)
        self.teks = teks
        self.font = font
        self.aktif = aktif

    def gambar(self, surface, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        warna = WARNA_TOMBOL_AKTIF if self.aktif else (WARNA_TOMBOL_HOVER if hover else WARNA_TOMBOL)
        pygame.draw.rect(surface, warna, self.rect, border_radius=6)
        label = self.font.render(self.teks, False, WARNA_TEKS)
        surface.blit(label, (self.rect.x + (self.rect.w - label.get_width()) // 2,
                             self.rect.y + (self.rect.h - label.get_height()) // 2))

    def diklik(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))


def pilih_file():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Pilih file input",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    return path

def pilih_file_simpan():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename(
        title="Simpan solusi",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    return path

def dialog_range_iterasi(total_iterasi):
    """Menampilkan dialog custom untuk input range iterasi. Return string input atau None jika dibatalkan."""
    result = [None]

    win = tk.Tk()
    win.title("Simpan Iterasi")
    win.resizable(False, False)
    win.configure(bg="#1e1e2e")

    WIN_DW, WIN_DH = 380, 210
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{WIN_DW}x{WIN_DH}+{(sw - WIN_DW) // 2}+{(sh - WIN_DH) // 2}")

    FONT_JUDUL  = ("Segoe UI", 13, "bold")
    FONT_TEKS   = ("Segoe UI", 10)
    FONT_TOMBOL = ("Segoe UI", 10, "bold")
    C_CARD      = "#2a2a3e"
    C_BORDER    = "#44475a"
    C_TEKS      = "#cdd6f4"
    C_DIM       = "#6272a4"
    C_AKSEN     = "#89b4fa"
    C_OK        = "#a6e3a1"
    C_CANCEL    = "#f38ba8"

    frame = tk.Frame(win, bg=C_CARD, bd=0, highlightthickness=1, highlightbackground=C_BORDER)
    frame.place(x=12, y=12, width=WIN_DW - 24, height=WIN_DH - 24)

    tk.Label(frame, text="Simpan Iterasi", font=FONT_JUDUL,
             bg=C_CARD, fg=C_AKSEN).place(x=16, y=12)

    tk.Label(frame, text=f"Iterasi tersedia:  1 – {total_iterasi}", font=FONT_TEKS,
             bg=C_CARD, fg=C_DIM).place(x=16, y=42)

    tk.Label(frame, text="Range (contoh: 1-50), kosongkan untuk semua:", font=FONT_TEKS,
             bg=C_CARD, fg=C_TEKS).place(x=16, y=68)

    entry_var = tk.StringVar()
    entry = tk.Entry(frame, textvariable=entry_var, font=FONT_TEKS,
                     bg="#313244", fg=C_TEKS, insertbackground=C_TEKS,
                     relief="flat", bd=6)
    entry.place(x=16, y=92, width=WIN_DW - 56, height=30)
    entry.focus()

    def on_ok(_=None):
        result[0] = entry_var.get()
        win.destroy()

    def on_cancel(_=None):
        win.destroy()

    win.bind("<Return>", on_ok)
    win.bind("<Escape>", on_cancel)

    btn_ok = tk.Button(frame, text="Simpan", font=FONT_TOMBOL,
                       bg=C_OK, fg="#1e1e2e", relief="flat", cursor="hand2",
                       activebackground="#94d3a2", activeforeground="#1e1e2e",
                       command=on_ok)
    btn_ok.place(x=16, y=138, width=100, height=32)

    btn_cancel = tk.Button(frame, text="Batal", font=FONT_TOMBOL,
                           bg=C_CANCEL, fg="#1e1e2e", relief="flat", cursor="hand2",
                           activebackground="#e57373", activeforeground="#1e1e2e",
                           command=on_cancel)
    btn_cancel.place(x=126, y=138, width=100, height=32)

    win.grab_set()
    win.wait_window()
    return result[0]

def hitung_tile_size_fit(board, area_w, area_h):
    margin = 20
    ts_w = (area_w - margin) // board.M
    ts_h = (area_h - margin) // board.N
    return max(TILE_MIN, min(TILE_MAX, min(ts_w, ts_h)))

def main():
    pygame.init()
    pygame.display.set_caption("Ice Sliding Puzzle Solver")

    src_dir    = os.path.dirname(__file__)
    asset_dir  = os.path.join(src_dir, '..', 'assets')
    output_dir = os.path.join(src_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    font_path   = os.path.join(asset_dir, 'Minecraft.ttf')
    font_kecil  = pygame.font.Font(font_path, 10)
    font_sedang = pygame.font.Font(font_path, 12)
    font_besar  = pygame.font.Font(font_path, 14)

    board           = None
    filepath        = ""
    algo_pilihan    = "UCS"
    h_pilihan       = "H1"
    solution        = None
    steps           = []
    step_idx        = 0
    iterasi         = 0
    exec_time       = 0.0
    log_iterasi     = []
    pesan_status    = "Pilih file input dan tekan Solve."
    auto_play       = False
    auto_play_timer = 0.0
    tile_size       = TILE_DEF
    bg_cache        = [None, (0, 0)]

    assets = load_assets(asset_dir, tile_size)

    aktor_px        = [0.0, 0.0]
    aktor_target_px = [0.0, 0.0]
    LERP_SPEED      = 12.0

    pan_x          = 0
    pan_y          = 0
    dragging_board = False
    drag_start     = (0, 0)
    pan_start      = (0, 0)

    WIN_W = 7 * TILE_DEF + SIDEBAR_W
    WIN_H = max(7 * TILE_DEF, 600)
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)

    sx = 10
    tombol_pilih_file = Tombol((0, 0, 1, 34), "Pilih File Input", font_sedang)
    tombol_ucs        = Tombol((0, 0, 1, 30), "UCS",  font_kecil, aktif=True)
    tombol_gbfs       = Tombol((0, 0, 1, 30), "GBFS", font_kecil)
    tombol_astar      = Tombol((0, 0, 1, 30), "A*",   font_kecil)
    tombol_bfs        = Tombol((0, 0, 1, 30), "BFS",  font_kecil)
    tombol_dfs        = Tombol((0, 0, 1, 30), "DFS",  font_kecil)
    tombol_h1         = Tombol((0, 0, 1, 28), "H1", font_kecil, aktif=True)
    tombol_h2         = Tombol((0, 0, 1, 28), "H2", font_kecil)
    tombol_h3         = Tombol((0, 0, 1, 28), "H3", font_kecil)
    tombol_solve      = Tombol((0, 0, 1, 36), "SOLVE", font_besar)
    tombol_save       = Tombol((0, 0, 1, 30), "Simpan Solusi .txt", font_kecil)
    tombol_save_iter  = Tombol((0, 0, 1, 30), "Simpan Iterasi .txt", font_kecil)
    tombol_prev       = Tombol((0, 0, 40, 30), "<", font_sedang)
    tombol_next       = Tombol((0, 0, 40, 30), ">", font_sedang)
    tombol_play       = Tombol((0, 0, 1, 30), "Play", font_kecil)
    KECEPATAN_PLAY    = 1.5

    clock  = pygame.time.Clock()
    layout = {}

    def update_layout():
        win_w, win_h = screen.get_size()
        bx = win_w - SIDEBAR_W + sx
        bw = SIDEBAR_W - 2 * sx
        w5 = (bw - 16) // 5
        gap = 8

        y = 10
        layout['judul_y'] = y;          y += 22 + gap
        tombol_pilih_file.rect = pygame.Rect(bx, y, bw, 34); y += 34 + 4
        layout['namafile_y'] = y;       y += 18 + gap
        layout['algo_label_y'] = y;     y += 16 + 4
        tombol_ucs.rect   = pygame.Rect(bx,             y, w5, 30)
        tombol_gbfs.rect  = pygame.Rect(bx + w5 + 5,   y, w5, 30)
        tombol_astar.rect = pygame.Rect(bx + 2*(w5+5), y, w5, 30)
        tombol_bfs.rect   = pygame.Rect(bx + 3*(w5+5), y, w5, 30)
        tombol_dfs.rect   = pygame.Rect(bx + 4*(w5+5), y, w5, 30); y += 30 + gap
        layout['h_label_y'] = y;        y += 16 + 4
        tombol_h1.rect = pygame.Rect(bx,             y, w5, 28)
        tombol_h2.rect = pygame.Rect(bx + w5 + 5,   y, w5, 28)
        tombol_h3.rect = pygame.Rect(bx + 2*(w5+5), y, w5, 28); y += 28 + gap
        tombol_solve.rect = pygame.Rect(bx, y, bw, 36); y += 36 + gap
        layout['status_y'] = y
        layout['info_y']   = y + 18

        pb_y = win_h - 120
        tombol_prev.rect = pygame.Rect(bx, pb_y, 40, 30)
        tombol_next.rect = pygame.Rect(bx + bw - 40, pb_y, 40, 30)
        tombol_play.rect = pygame.Rect(bx + 45, pb_y, bw - 90, 30)
        tombol_save.rect      = pygame.Rect(bx, win_h - 72, bw, 30)
        tombol_save_iter.rect = pygame.Rect(bx, win_h - 36, bw, 30)
        layout['bx'] = bx
        layout['bw'] = bw

    def set_algo(nama):
        nonlocal algo_pilihan
        algo_pilihan = nama
        tombol_ucs.aktif   = (nama == "UCS")
        tombol_gbfs.aktif  = (nama == "GBFS")
        tombol_astar.aktif = (nama == "A*")
        tombol_bfs.aktif   = (nama == "BFS")
        tombol_dfs.aktif   = (nama == "DFS")

    def set_h(nama):
        nonlocal h_pilihan
        h_pilihan = nama
        tombol_h1.aktif = (nama == "H1")
        tombol_h2.aktif = (nama == "H2")
        tombol_h3.aktif = (nama == "H3")

    def snap_aktor_to(r, c, off_x, off_y):
        aktor_px[0] = off_x + c * tile_size + tile_size / 2
        aktor_px[1] = off_y + r * tile_size + tile_size / 2
        aktor_target_px[0] = aktor_px[0]
        aktor_target_px[1] = aktor_px[1]

    def hitung_offset():
        win_w, win_h = screen.get_size()
        area_w  = win_w - SIDEBAR_W
        papan_w = board.M * tile_size
        papan_h = board.N * tile_size
        off_x = (area_w - papan_w) // 2 + pan_x
        off_y = (win_h  - papan_h) // 2 + pan_y
        return off_x, off_y

    def jalankan_solve():
        nonlocal solution, steps, step_idx, iterasi, exec_time, log_iterasi, pesan_status, auto_play
        if board is None:
            pesan_status = "Belum ada file yang dipilih!"
            return
        pesan_status = "Sedang mencari solusi..."
        pygame.display.flip()

        if algo_pilihan == "UCS":
            solution, iterasi, exec_time, log_iterasi = solve_ucs(board, record_iterasi=0)
        elif algo_pilihan == "GBFS":
            solution, iterasi, exec_time, log_iterasi = solve_gbfs(board, record_iterasi=0)
        elif algo_pilihan == "A*":
            h = HEURISTICS.get(h_pilihan, HEURISTICS['H1'])
            solution, iterasi, exec_time, log_iterasi = solve_astar(board, h, record_iterasi=0)
        elif algo_pilihan == "BFS":
            solution, iterasi, exec_time, log_iterasi = solve_bfs(board, record_iterasi=0)
        elif algo_pilihan == "DFS":
            solution, iterasi, exec_time, log_iterasi = solve_dfs(board, record_iterasi=0)
        if solution:
            steps    = build_steps(board, solution)
            step_idx = 0
            auto_play = False
            pesan_status = f"Solusi ditemukan! ({len(solution.path)} langkah)"
            off_x, off_y = hitung_offset()
            snap_aktor_to(*board.start_pos, off_x, off_y)
        else:
            steps = []
            pesan_status = "Tidak ditemukan solusi."

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        update_layout()
        mouse_pos = pygame.mouse.get_pos()

        if auto_play and steps and step_idx < len(steps) - 1:
            auto_play_timer += dt
            if auto_play_timer >= 1.0 / KECEPATAN_PLAY:
                auto_play_timer = 0.0
                step_idx += 1
                if step_idx >= len(steps) - 1:
                    auto_play = False

        if dragging_board:
            aktor_px[0] = aktor_target_px[0]
            aktor_px[1] = aktor_target_px[1]
        else:
            aktor_px[0] += (aktor_target_px[0] - aktor_px[0]) * min(1.0, LERP_SPEED * dt)
            aktor_px[1] += (aktor_target_px[1] - aktor_px[1]) * min(1.0, LERP_SPEED * dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if steps:
                    if event.key == pygame.K_RIGHT and step_idx < len(steps) - 1:
                        step_idx += 1
                    elif event.key == pygame.K_LEFT and step_idx > 0:
                        step_idx -= 1

            elif event.type == pygame.MOUSEWHEEL:
                win_w, win_h = screen.get_size()
                if mouse_pos[0] < win_w - SIDEBAR_W:
                    lama = tile_size
                    tile_size = max(TILE_MIN, min(TILE_MAX, tile_size + event.y * 4))
                    if tile_size != lama:
                        assets = load_assets(asset_dir, tile_size)
                        if board:
                            off_x, off_y = hitung_offset()
                            aktor_pos = board.start_pos if not steps else steps[step_idx][1]
                            snap_aktor_to(*aktor_pos, off_x, off_y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                win_w, win_h = screen.get_size()
                if event.button in (2, 3) and event.pos[0] < win_w - SIDEBAR_W:
                    dragging_board = True
                    drag_start = event.pos
                    pan_start  = (pan_x, pan_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (2, 3):
                    dragging_board = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_board:
                    dx = event.pos[0] - drag_start[0]
                    dy = event.pos[1] - drag_start[1]
                    pan_x = pan_start[0] + dx
                    pan_y = pan_start[1] + dy


            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_pilih_file.diklik(event):
                    path = pilih_file()
                    if path:
                        b = Board()
                        if b.parse_input(path):
                            board    = b
                            filepath = path
                            solution = None
                            steps    = []
                            step_idx = 0
                            pesan_status = f"File dimuat: {os.path.basename(path)}"

                            win_w, win_h = screen.get_size()
                            area_w    = win_w - SIDEBAR_W
                            tile_size = hitung_tile_size_fit(board, area_w, win_h)
                            assets    = load_assets(asset_dir, tile_size)

                            pan_x = 0
                            pan_y = 0
                            off_x, off_y = hitung_offset()
                            snap_aktor_to(*board.start_pos, off_x, off_y)
                        else:
                            pesan_status = "Gagal membaca file!"

                elif tombol_ucs.diklik(event):   set_algo("UCS")
                elif tombol_gbfs.diklik(event):  set_algo("GBFS")
                elif tombol_astar.diklik(event): set_algo("A*")
                elif tombol_bfs.diklik(event):   set_algo("BFS")
                elif tombol_dfs.diklik(event):   set_algo("DFS")
                elif tombol_h1.diklik(event):    set_h("H1")
                elif tombol_h2.diklik(event):    set_h("H2")
                elif tombol_h3.diklik(event):    set_h("H3")
                elif tombol_solve.diklik(event): jalankan_solve()
                elif tombol_prev.diklik(event) and step_idx > 0:
                    step_idx -= 1
                    auto_play = False
                elif tombol_next.diklik(event) and steps and step_idx < len(steps) - 1:
                    step_idx += 1
                    auto_play = False
                elif tombol_play.diklik(event) and steps:
                    auto_play = not auto_play
                    auto_play_timer = 0.0
                    if auto_play and step_idx >= len(steps) - 1:
                        step_idx = 0
                elif tombol_save.diklik(event) and solution:
                    nama_dasar = os.path.splitext(os.path.basename(filepath))[0]
                    algo_tag   = algo_pilihan.replace("*", "star") + (f"_{h_pilihan}" if algo_pilihan == "A*" else "")
                    savepath   = os.path.join(output_dir, f"{nama_dasar}_{algo_tag}_solution.txt")
                    save_solution(board, solution, iterasi, exec_time, savepath)
                    pesan_status = f"Disimpan: {os.path.basename(savepath)}"
                elif tombol_save_iter.diklik(event) and log_iterasi:
                    jawab = dialog_range_iterasi(iterasi)
                    if jawab is not None:
                        nama_dasar = os.path.splitext(os.path.basename(filepath))[0]
                        algo_tag   = algo_pilihan.replace("*", "star") + (f"_{h_pilihan}" if algo_pilihan == "A*" else "")
                        if jawab.strip() == "":
                            subset    = log_iterasi
                            range_tag = "semua"
                        else:
                            try:
                                parts = jawab.strip().split('-')
                                lo, hi = int(parts[0]), int(parts[1])
                                subset    = [(n, pos, c, p) for n, pos, c, p in log_iterasi
                                             if lo <= n <= hi]
                                range_tag = f"{lo}-{hi}"
                            except Exception:
                                subset    = log_iterasi
                                range_tag = "semua"
                        savepath = os.path.join(output_dir, f"{nama_dasar}_{algo_tag}_iterasi_{range_tag}.txt")
                        lines = [f"Log Iterasi - {algo_pilihan}", ""]
                        for n, (r, c), cost, path in subset:
                            lines.append(f"Iterasi {n}: pos=({r},{c})  cost={cost}  path={path}")
                        with open(savepath, 'w') as f:
                            f.write("\n".join(lines))
                        pesan_status = f"Iterasi disimpan: {os.path.basename(savepath)}"

        # render
        screen.fill(WARNA_BG)
        win_w, win_h = screen.get_size()
        area_w = win_w - SIDEBAR_W

        if board:
            off_x, off_y = hitung_offset()
            aktor_pos = board.start_pos if not steps else steps[step_idx][1]
            aktor_target_px[0] = off_x + aktor_pos[1] * tile_size + tile_size / 2
            aktor_target_px[1] = off_y + aktor_pos[0] * tile_size + tile_size / 2

            gambar_bg(screen, assets, area_w, win_h, bg_cache)
            gambar_papan(screen, assets, board, off_x, off_y, tile_size)
            gambar_aktor(screen, assets, aktor_px, tile_size)

            hint = font_kecil.render("Scroll: zoom  |  Klik kanan + geser: pan", False, WARNA_TEKS_DIM)
            screen.blit(hint, (8, win_h - hint.get_height() - 6))
        else:
            teks = font_besar.render("Pilih file input di sidebar kanan", False, WARNA_TEKS_DIM)
            screen.blit(teks, (area_w // 2 - teks.get_width() // 2,
                               win_h // 2 - teks.get_height() // 2))

        # sidebar
        pygame.draw.rect(screen, WARNA_SIDEBAR, pygame.Rect(area_w, 0, SIDEBAR_W, win_h))
        pygame.draw.line(screen, (60, 60, 90), (area_w, 0), (area_w, win_h), 2)

        bx = layout['bx']
        bw = layout['bw']

        judul = font_besar.render("Ice Sliding Puzzle", False, WARNA_TEKS)
        screen.blit(judul, (area_w + (SIDEBAR_W - judul.get_width()) // 2, layout['judul_y']))

        tombol_pilih_file.gambar(screen, mouse_pos)

        nama_tampil = os.path.basename(filepath) if filepath else "-"
        screen.blit(font_kecil.render(nama_tampil, False, WARNA_TEKS_DIM), (bx, layout['namafile_y']))

        screen.blit(font_kecil.render("Algoritma:", False, WARNA_TEKS_DIM), (bx, layout['algo_label_y']))
        tombol_ucs.gambar(screen, mouse_pos)
        tombol_gbfs.gambar(screen, mouse_pos)
        tombol_astar.gambar(screen, mouse_pos)
        tombol_bfs.gambar(screen, mouse_pos)
        tombol_dfs.gambar(screen, mouse_pos)

        if algo_pilihan == "A*":
            screen.blit(font_kecil.render("Heuristik:", False, WARNA_TEKS_DIM), (bx, layout['h_label_y']))
            tombol_h1.gambar(screen, mouse_pos)
            tombol_h2.gambar(screen, mouse_pos)
            tombol_h3.gambar(screen, mouse_pos)

        tombol_solve.gambar(screen, mouse_pos)
        screen.blit(font_kecil.render(pesan_status, False, WARNA_TEKS), (bx, layout['status_y']))

        if solution:
            y = layout['info_y']
            def info(lbl, val):
                nonlocal y
                screen.blit(font_kecil.render(lbl, False, WARNA_TEKS_DIM), (bx, y))
                screen.blit(font_kecil.render(str(val), False, WARNA_TEKS), (bx + 95, y))
                y += 18

            info("Algoritma :", algo_pilihan + (f" ({h_pilihan})" if algo_pilihan == "A*" else ""))
            info("Cost      :", solution.cost)
            info("Iterasi   :", iterasi)
            waktu_str = f"{exec_time:.4f} ms" if exec_time < 1.0 else f"{exec_time:.2f} ms"
            info("Waktu     :", waktu_str)
            info("Langkah   :", len(solution.path))

            path_str = solution.path
            maks = bw // 9
            if len(path_str) > maks:
                path_str = path_str[:maks - 3] + "..."
            screen.blit(font_kecil.render(path_str, False, WARNA_ANGKA), (bx, y))
            y += 20

            if steps:
                lbl_step, _ = steps[step_idx]
                info_step = f"Step {step_idx}/{len(steps)-1}"
                if step_idx > 0:
                    info_step += f"  ({lbl_step})"
                screen.blit(font_sedang.render(info_step, False, WARNA_TEKS), (bx, y + 5))

        if steps:
            tombol_prev.gambar(screen, mouse_pos)
            tombol_play.teks = "Pause" if auto_play else "Play"
            tombol_play.gambar(screen, mouse_pos)
            tombol_next.gambar(screen, mouse_pos)

        if solution:
            tombol_save.gambar(screen, mouse_pos)
            tombol_save_iter.gambar(screen, mouse_pos)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
