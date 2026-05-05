import heapq
import time
from models.state import State

def heuristic_manhattan(state, board):
    return abs(state.r - board.goal_pos[0]) + abs(state.c - board.goal_pos[1])

def solve_gbfs(board, heuristic=heuristic_manhattan):

    start_time = time.time()
    initial_state = State(board.start_pos[0], board.start_pos[1], 0, "", 0)
    h = heuristic(initial_state, board)

    # Priority queue (h, state) 
    pq = [(h, initial_state)]
    visited = set()
    iterasi = 0
    directions = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

    while pq:
        _, curr = heapq.heappop(pq)
        iterasi += 1

        all_nums_done = (board.max_num == -1) or (curr.target_num > board.max_num)
        if (curr.r, curr.c) == board.goal_pos and all_nums_done:
            exec_time = (time.time() - start_time) * 1000
            return curr, iterasi, exec_time

        state_id = (curr.r, curr.c, curr.target_num)
        if state_id in visited:
            continue
        visited.add(state_id)

        for dr, dc, char_dir in directions:
            next_state = board.slide(curr, (dr, dc, char_dir))
            if next_state:
                h = heuristic(next_state, board)
                heapq.heappush(pq, (h, next_state))

    exec_time = (time.time() - start_time) * 1000
    return None, iterasi, exec_time
