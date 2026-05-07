import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.board import Board
from algorithms.ucs import solve_ucs
from algorithms.gbfs import solve_gbfs
from algorithms.astar import solve_astar, HEURISTICS
from ui.playback import print_solution, run_playback, save_solution

def main():
    print(">> Masukan file input :")
    filepath = input("   ").strip()

    board = Board()
    if not board.parse_input(filepath):
        print("Error: File tidak ditemukan atau format tidak valid.")
        return

    print(">> Algoritma apa yang anda pilih? (UCS/GBFS/A*)")
    algo = input("   ").strip().upper()

    solution = None
    iterasi = 0
    exec_time = 0.0

    if algo == "UCS":
        solution, iterasi, exec_time, _ = solve_ucs(board, record_iterasi=-1)

    elif algo == "GBFS":
        solution, iterasi, exec_time, _ = solve_gbfs(board, record_iterasi=-1)

    elif algo == "A*":
        print(">> Heuristic apa yang anda pilih? (H1/H2/H3)")
        h_choice = input("   ").strip().upper()
        heuristic = HEURISTICS.get(h_choice, HEURISTICS['H1'])
        solution, iterasi, exec_time, _ = solve_astar(board, heuristic, record_iterasi=-1)

    else:
        print("Algoritma tidak dikenal.")
        return

    if solution is None:
        print("\nTidak ditemukan solusi.")
        print(f">> Waktu eksekusi: {exec_time:.2f} ms")
        print(f">> Banyak iterasi yang dilakukan: {iterasi} iterasi")
        return

    print_solution(board, solution, algo, iterasi, exec_time)

    print(">> Apakah Anda ingin melakukan playback? (y/n) :")
    if input("   ").strip().lower() in ('ya', 'y'):
        run_playback(board, solution, iterasi, exec_time)

    print(">> Apakah Anda ingin menyimpan solusi? (y/n) :")
    if input("   ").strip().lower() in ('ya', 'y'):
        print(">> Masukan path file output :")
        out_path = input("   ").strip()
        save_solution(board, solution, iterasi, exec_time, out_path)

if __name__ == "__main__":
    main()
