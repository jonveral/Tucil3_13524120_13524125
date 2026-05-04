class State:
    def __init__(self, r, c, target_num, path, cost):
        self.r = r                      # Baris saat ini
        self.c = c                      # Kolom saat ini
        self.target_num = target_num    # Angka target selanjutnya yang harus diinjak
        self.path = path                # Riwayat jalan (misal: "RULU")
        self.cost = cost                # Total biaya yang sudah dihabiskan

    # Syarat agar bisa diurutkan dari cost termurah di dalam antrean (Priority Queue)
    def __lt__(self, other):
        return self.cost < other.cost

    # Syarat agar state ini bisa disimpan di dalam 'Set' (untuk memori visited)
    def __hash__(self):
        return hash((self.r, self.c, self.target_num))

    def __eq__(self, other):
        return (self.r, self.c, self.target_num) == (other.r, other.c, other.target_num)