import os
from models.state import State

class Board:
    def __init__(self):
        self.N = 0
        self.M = 0
        self.grid = []
        self.costs = []
        self.start_pos = None
        self.goal_pos = None
        self.max_num = -1
        self.num_positions = {}  # mapping digit -> (r, c)

    def parse_input(self, filepath):
        """Membaca papan dan cost dari file txt."""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            self.N, self.M = map(int, lines[0].split())

            # Baca grid map
            for i in range(1, self.N + 1):
                row = list(lines[i])
                self.grid.append(row)
                for j in range(self.M):
                    if row[j] == 'Z': self.start_pos = (i - 1, j)
                    elif row[j] == 'O': self.goal_pos = (i - 1, j)
                    elif row[j].isdigit():
                        val = int(row[j])
                        self.max_num = max(self.max_num, val)
                        self.num_positions[val] = (i - 1, j)

            # Baca matriks cost
            start_idx = self.N + 1
            for i in range(start_idx, start_idx + self.N):
                self.costs.append(list(map(int, lines[i].split())))

            if self.start_pos is None or self.goal_pos is None:
                return False

        except (ValueError, IndexError):
            return False

        return True

    def is_valid_pos(self, r, c):
        return 0 <= r < self.N and 0 <= c < self.M

    def slide(self, state, direction):
        """
        Simulator pergerakan es yang licin.
        direction: (delta_row, delta_col, 'Arah')
        """
        dr, dc, char_dir = direction
        r, c = state.r, state.c
        curr_target = state.target_num
        move_cost = 0

        # Cek kalau langsung mentok batu di sebelah
        if self.is_valid_pos(r + dr, c + dc) and self.grid[r + dr][c + dc] == 'X':
            return None

        while True:
            nr, nc = r + dr, c + dc

            # Jatuh keluar arena
            if not self.is_valid_pos(nr, nc): return None
            
            tile = self.grid[nr][nc]

            # Ngerem tepat sebelum batu
            if tile == 'X': break

            # Mati kena lava
            if tile == 'L': return None

            # Berhenti di goal kalau semua angka sudah selesai
            if tile == 'O':
                semua_selesai = (self.max_num == -1) or (curr_target > self.max_num)
                if semua_selesai:
                    move_cost += self.costs[nr][nc]
                    r, c = nr, nc
                    break

            # Cek urutan angka
            if tile.isdigit():
                val = int(tile)
                if val == curr_target:
                    curr_target += 1
                elif val > curr_target:
                    return None # Salah urutan (game over)

            # Tambah cost dari tile yang dilewati
            move_cost += self.costs[nr][nc]
            r, c = nr, nc

        # Kembalikan state baru di posisi ngerem
        return State(r, c, curr_target, state.path + char_dir, state.cost + move_cost)