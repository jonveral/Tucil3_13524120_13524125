import heapq
import time
from models.state import State

def solve_ucs(board):
    """
    Menjalankan Uniform Cost Search (UCS).
    Mengembalikan (solusi_state, jumlah_iterasi, waktu_eksekusi)
    """
    start_time = time.time()
    
    # Bikin state awal dari Z
    initial_state = State(board.start_pos[0], board.start_pos[1], 0, "", 0)
    
    pq = []
    heapq.heappush(pq, initial_state)
    visited = set()
    iterasi = 0
    directions = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

    while pq:
        curr = heapq.heappop(pq)
        iterasi += 1

        # Cek kondisi menang: Sampai di 'O' dan semua angka beres
        all_nums_done = (board.max_num == -1) or (curr.target_num > board.max_num)
        if (curr.r, curr.c) == board.goal_pos and all_nums_done:
            exec_time = (time.time() - start_time) * 1000
            return curr, iterasi, exec_time

        # Filter visited
        state_id = (curr.r, curr.c, curr.target_num)
        if state_id in visited: continue
        visited.add(state_id)

        # Ekspansi ke 4 arah menggunakan fungsi slide dari papan
        for dr, dc, char_dir in directions:
            next_state = board.slide(curr, (dr, dc, char_dir))
            if next_state:
                heapq.heappush(pq, next_state)

    exec_time = (time.time() - start_time) * 1000
    return None, iterasi, exec_time