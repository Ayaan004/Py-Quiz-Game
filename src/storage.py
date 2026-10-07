"""Storage management for persistent leaderboard and player statistics."""
import json
import os
import time
from typing import List, Dict, Any

class StorageManager:
    """Handles JSON persistence for leaderboard and lifetime statistics."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.leaderboard_file = os.path.join(data_dir, "leaderboard.json")
        self.stats_file = os.path.join(data_dir, "stats.json")
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.leaderboard_file):
            default_leaderboard = [
                {"player": "Alex_Vanguard", "score": 1250, "accuracy": 90.0, "category": "Python & Programming", "date": "2026-10-01"},
                {"player": "CyberNeo", "score": 980, "accuracy": 80.0, "category": "Science & Technology", "date": "2026-10-02"},
                {"player": "Luna_Star", "score": 750, "accuracy": 70.0, "category": "General Knowledge", "date": "2026-10-03"}
            ]
            self._save_json(self.leaderboard_file, default_leaderboard)

        if not os.path.exists(self.stats_file):
            default_stats = {
                "total_games": 0,
                "total_questions_answered": 0,
                "total_correct": 0,
                "best_score": 0,
                "highest_streak": 0,
                "total_time_played_sec": 0
            }
            self._save_json(self.stats_file, default_stats)

    def _load_json(self, filepath: str) -> Any:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return [] if "leaderboard" in filepath else {}

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        entries = self._load_json(self.leaderboard_file)
        if not isinstance(entries, list):
            entries = []
        entries.sort(key=lambda x: x.get("score", 0), reverse=True)
        return entries[:50]

    def add_score(self, player_name: str, score: int, accuracy: float, category: str):
        board = self.get_leaderboard()
        date_str = time.strftime("%Y-%m-%d %H:%M")
        board.append({
            "player": player_name.strip() or "Anonymous Player",
            "score": score,
            "accuracy": round(accuracy, 1),
            "category": category,
            "date": date_str
        })
        board.sort(key=lambda x: x.get("score", 0), reverse=True)
        self._save_json(self.leaderboard_file, board[:50])

    def get_stats(self) -> Dict[str, Any]:
        stats = self._load_json(self.stats_file)
        if not isinstance(stats, dict):
            stats = {}
        return stats

    def record_quiz_stats(self, questions_count: int, correct_count: int, score: int, streak: int, duration_sec: float):
        stats = self.get_stats()
        stats["total_games"] = stats.get("total_games", 0) + 1
        stats["total_questions_answered"] = stats.get("total_questions_answered", 0) + questions_count
        stats["total_correct"] = stats.get("total_correct", 0) + correct_count
        stats["best_score"] = max(stats.get("best_score", 0), score)
        stats["highest_streak"] = max(stats.get("highest_streak", 0), streak)
        stats["total_time_played_sec"] = stats.get("total_time_played_sec", 0) + duration_sec
        self._save_json(self.stats_file, stats)
