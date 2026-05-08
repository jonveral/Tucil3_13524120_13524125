import time
from models.state import State

def solve_dfs(board, record_iterasi=0):
    start_time = time.time()
    initial_state = State(board.start_pos[0], board.start_pos[1], 0, "", 0)
    
    stack = [initial_state]
    visited = set()
    iterasi = 0
    log = []
    # Dibalik agar 'U' diproses pertama (karena stack mengambil dari belakang)
    directions = [(0, 1, 'R'), (0, -1, 'L'), (1, 0, 'D'), (-1, 0, 'U')]

    while stack:
        curr = stack.pop()
        iterasi += 1

        if record_iterasi >= 0:
            step = record_iterasi if record_iterasi > 0 else 1
            if (iterasi - 1) % step == 0:
                log.append((iterasi, (curr.r, curr.c), curr.cost, curr.path))

        all_nums_done = (board.max_num == -1) or (curr.target_num > board.max_num)
        if (curr.r, curr.c) == board.goal_pos and all_nums_done:
            exec_time = (time.time() - start_time) * 1000
            return curr, iterasi, exec_time, log

        state_id = (curr.r, curr.c, curr.target_num)
        if state_id in visited:
            continue
        visited.add(state_id)

        for dr, dc, char_dir in directions:
            next_state = board.slide(curr, (dr, dc, char_dir))
            if next_state:
                stack.append(next_state)

    exec_time = (time.time() - start_time) * 1000
    return None, iterasi, exec_time, log