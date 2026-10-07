"""Leaderboard and Hall of Fame screen."""
import customtkinter as ctk
from typing import Callable
from src.theme import COLORS, FONTS
from src.storage import StorageManager

class LeaderboardScreen(ctk.CTkFrame):
    """Hall of fame podium and persistent high scores table."""

    def __init__(
        self,
        parent,
        storage: StorageManager,
        on_go_home: Callable[[], None]
    ):
        super().__init__(parent, fg_color="transparent")
        self.storage = storage
        self.on_go_home = on_go_home

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)

        # Header bar with Back button
        header_bar = ctk.CTkFrame(container, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 15))
        header_bar.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header_bar,
            text="← Back to Menu",
            font=FONTS["body_bold"],
            width=120,
            height=36,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            command=self.on_go_home
        )
        back_btn.grid(row=0, column=0, sticky="w")

        title_lbl = ctk.CTkLabel(
            header_bar,
            text="🏆 Hall of Fame & Rankings",
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=15)

        # Top 3 Podium
        entries = self.storage.get_leaderboard()
        if len(entries) >= 1:
            podium_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
            podium_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15), ipady=12)
            podium_card.grid_columnconfigure((0, 1, 2), weight=1)

            podium_order = []
            if len(entries) >= 2:
                podium_order.append((entries[1], 2, "🥈 2nd Place", "#94A3B8"))
            if len(entries) >= 1:
                podium_order.append((entries[0], 1, "👑 1st Champion", "#F59E0B"))
            if len(entries) >= 3:
                podium_order.append((entries[2], 3, "🥉 3rd Place", "#B45309"))

            for idx, (data, rank, label, color) in enumerate(podium_order):
                box = ctk.CTkFrame(podium_card, fg_color=COLORS["bg_card_secondary"], corner_radius=12)
                box.grid(row=0, column=idx, padx=10, pady=8, sticky="nsew")

                ctk.CTkLabel(box, text=label, font=FONTS["subtitle"], text_color=color).pack(pady=(12, 2))
                ctk.CTkLabel(box, text=data.get("player", "Unknown"), font=FONTS["title"], text_color=COLORS["text_primary"]).pack(pady=2)
                ctk.CTkLabel(box, text=f"{data.get('score', 0):,} PTS", font=FONTS["body_bold"], text_color=COLORS["primary"]).pack(pady=2)
                ctk.CTkLabel(box, text=f"{data.get('accuracy', 0)}% Acc • {data.get('category', 'All')}", font=FONTS["body_small"], text_color=COLORS["text_secondary"]).pack(pady=(2, 12))

        # Full Leaderboard Table Card
        table_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        table_card.grid(row=2, column=0, sticky="ew", padx=10, pady=10, ipady=10)
        table_card.grid_columnconfigure(0, weight=1)

        # Table Header Row
        cols_frame = ctk.CTkFrame(table_card, fg_color=COLORS["bg_card_secondary"], corner_radius=8)
        cols_frame.pack(fill="x", padx=12, pady=(12, 6))
        cols_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Rank", "Player", "Score", "Accuracy", "Date"]
        for c_idx, h in enumerate(headers):
            anchor = "w" if c_idx in [0, 1] else "center"
            lbl = ctk.CTkLabel(cols_frame, text=h, font=FONTS["body_bold"], text_color=COLORS["text_secondary"])
            lbl.grid(row=0, column=c_idx, padx=10, pady=8, sticky="ew")

        # Table Content Rows
        if not entries:
            empty_lbl = ctk.CTkLabel(
                table_card,
                text="No games played yet! Be the first champion to top the leaderboard.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"]
            )
            empty_lbl.pack(pady=30)
        else:
            for r_idx, row in enumerate(entries):
                row_frame = ctk.CTkFrame(table_card, fg_color="transparent")
                row_frame.pack(fill="x", padx=12, pady=2)
                row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

                rank_str = f"#{r_idx+1}"
                if r_idx == 0:
                    rank_str = "🥇 #1"
                elif r_idx == 1:
                    rank_str = "🥈 #2"
                elif r_idx == 2:
                    rank_str = "🥉 #3"

                ctk.CTkLabel(row_frame, text=rank_str, font=FONTS["body_bold"], text_color=COLORS["primary"]).grid(row=0, column=0, padx=10, pady=6, sticky="ew")
                ctk.CTkLabel(row_frame, text=row.get("player", "Anonymous"), font=FONTS["body_bold"], text_color=COLORS["text_primary"]).grid(row=0, column=1, padx=10, pady=6, sticky="ew")
                ctk.CTkLabel(row_frame, text=f"{row.get('score', 0):,}", font=FONTS["body_bold"], text_color=COLORS["secondary"]).grid(row=0, column=2, padx=10, pady=6, sticky="ew")
                ctk.CTkLabel(row_frame, text=f"{row.get('accuracy', 0)}%", font=FONTS["body"], text_color=COLORS["text_secondary"]).grid(row=0, column=3, padx=10, pady=6, sticky="ew")
                ctk.CTkLabel(row_frame, text=row.get("date", "-"), font=FONTS["body_small"], text_color=COLORS["text_muted"]).grid(row=0, column=4, padx=10, pady=6, sticky="ew")
