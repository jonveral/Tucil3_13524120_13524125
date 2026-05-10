import heapq
import time
from models.state import State

def manhattan_goal(state, board):
    return abs(state.r - board.goal_pos[0]) + abs(state.c - board.goal_pos[1])

def manhattan_goal_angka(state, board):
    dist_ke_goal = abs(state.r - board.goal_pos[0]) + abs(state.c - board.goal_pos[1])
    if board.max_num >= 0 and state.target_num <= board.max_num:
        pos_angka = board.num_positions.get(state.target_num)
        if pos_angka:
            dist_ke_angka = abs(state.r - pos_angka[0]) + abs(state.c - pos_angka[1])
            return dist_ke_angka + dist_ke_goal
    return dist_ke_goal

def cheby(state, board):
    dr = abs(state.r - board.goal_pos[0])
    dc = abs(state.c - board.goal_pos[1])
    return max(dr, dc)

HEURISTICS = {
    'H1': manhattan_goal,
    'H2': manhattan_goal_angka,
    'H3': cheby,
}

def solve_astar(board, heuristic=manhattan_goal, record_iterasi=0):
    start_time = time.time()

    r0, c0 = board.start_pos
    initial = State(r0, c0, 0, "", 0)
    h0 = heuristic(initial, board)

    counter = 0
    pq = [(h0, counter, initial)]
    visited = set()
    iterasi = 0
    log = []
    directions = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

    while pq:
        _, _, curr = heapq.heappop(pq)
        iterasi += 1

        if record_iterasi >= 0:
            step = record_iterasi if record_iterasi > 0 else 1
            if (iterasi - 1) % step == 0:
                log.append((iterasi, (curr.r, curr.c), curr.cost, curr.path))

        semua_angka_selesai = (board.max_num == -1) or (curr.target_num > board.max_num)
        if (curr.r, curr.c) == board.goal_pos and semua_angka_selesai:
            waktu = (time.time() - start_time) * 1000
            return curr, iterasi, waktu, log

        sid = (curr.r, curr.c, curr.target_num)
        if sid in visited:
            continue
        visited.add(sid)

        for arah in directions:
            next_s = board.slide(curr, arah)
            if next_s is None:
                continue
            g = next_s.cost
            h = heuristic(next_s, board)
            counter += 1
            heapq.heappush(pq, (g + h, counter, next_s))

    waktu = (time.time() - start_time) * 1000
    return None, iterasi, waktu, log
