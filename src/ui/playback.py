import os
import sys

if sys.platform == "win32":
    import msvcrt
else:
    import tty
    import termios

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_key():
    if sys.platform == "win32":
        key = msvcrt.getch()
        if key in (b'\x00', b'\xe0'):
            key2 = msvcrt.getch()
            if key2 == b'K':
                return 'LEFT'
            if key2 == b'M':
                return 'RIGHT'
            return 'OTHER'
        if key == b'\x1b':
            return 'ESC'
        if key == b'q':
            return 'QUIT'
        return 'OTHER'
    else:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'D':
                        return 'LEFT'
                    if ch3 == 'C':
                        return 'RIGHT'
                return 'ESC'
            if ch == 'q':
                return 'QUIT'
            return 'OTHER'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def build_steps(board, solution_state):
    from models.state import State

    arah_map = {
        'U': (-1, 0, 'U'),
        'D': (1, 0, 'D'),
        'L': (0, -1, 'L'),
        'R': (0, 1, 'R'),
    }

    steps = []
    curr = State(board.start_pos[0], board.start_pos[1], 0, "", 0)
    steps.append(('Initial', (curr.r, curr.c)))

    for ch in solution_state.path:
        next_s = board.slide(curr, arah_map[ch])
        steps.append((ch, (next_s.r, next_s.c)))
        curr = next_s

    return steps

def render_board(board, actor_pos):
    hasil = []
    for r in range(board.N):
        baris = ""
        for c in range(board.M):
            if (r, c) == actor_pos:
                baris += 'Z'
            elif board.grid[r][c] == 'Z':
                baris += '*'
            else:
                baris += board.grid[r][c]
        hasil.append(baris)
    return "\n".join(hasil)

def run_playback(board, solution_state, iterasi, exec_time):
    steps = build_steps(board, solution_state)
    total = len(steps) - 1
    i = 0

    while True:
        clear_screen()
        label, pos = steps[i]

        if i == 0:
            print("Initial")
        else:
            print(f"Step {i} : {label}")

        print(render_board(board, pos))
        print()
        print(f"[{i}/{total}]  <- -> : maju/mundur  |  ESC : lompat ke step  |  q : keluar")

        key = get_key()

        if key == 'RIGHT' and i < total:
            i += 1
        elif key == 'LEFT' and i > 0:
            i -= 1
        elif key == 'ESC':
            clear_screen()
            try:
                tujuan = int(input(f"Mau lompat ke step berapa? (0-{total}): "))
                if 0 <= tujuan <= total:
                    i = tujuan
            except ValueError:
                pass
        elif key == 'QUIT':
            break

def print_solution(board, solution_state, algo_name, iterasi, exec_time):
    print(f"\nSolusi Yang Ditemukan : {solution_state.path}")
    print(f"Cost dari Solusi      : {solution_state.cost}")
    print()

    steps = build_steps(board, solution_state)
    for idx, (label, pos) in enumerate(steps):
        if idx == 0:
            print("Initial")
        else:
            print(f"Step {idx} : {label}")
        print(render_board(board, pos))
        print()

    print(f">> Waktu eksekusi: {exec_time:.2f} ms")
    print(f">> Banyak iterasi yang dilakukan: {iterasi} iterasi")

def save_solution(board, solution_state, iterasi, exec_time, filepath):
    steps = build_steps(board, solution_state)
    lines = []
    lines.append(f"Solusi Yang Ditemukan : {solution_state.path}")
    lines.append(f"Cost dari Solusi      : {solution_state.cost}")
    lines.append("")
    for idx, (label, pos) in enumerate(steps):
        if idx == 0:
            lines.append("Initial")
        else:
            lines.append(f"Step {idx} : {label}")
        lines.append(render_board(board, pos))
        lines.append("")
    lines.append(f"Waktu eksekusi: {exec_time:.2f} ms")
    lines.append(f"Banyak iterasi: {iterasi} iterasi")

    with open(filepath, 'w') as f:
        f.write("\n".join(lines))
    print(f">> Solusi disimpan pada {filepath}")
