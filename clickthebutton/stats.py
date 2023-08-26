from typing import List


class Stats:
    def __init__(self, streak: List, leaderboard: dict, sorted_leaderboard: List):
        self.streak = streak
        self.leaderboard = leaderboard
        self.sorted_leaderboard = sorted_leaderboard

    @property
    def total_clicks(self):
        return sum(self.leaderboard.values())

    @property
    def players(self):
        return len(self.leaderboard)
