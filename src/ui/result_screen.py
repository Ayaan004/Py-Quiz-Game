"""Quiz session result and post-game question review screen."""
import customtkinter as ctk
from typing import Callable
from src.theme import COLORS, FONTS
from src.models import QuizSummary
from src.storage import StorageManager

class ResultScreen(ctk.CTkFrame):
    """Post-game performance screen with score breakdown and question-by-question review."""

    def __init__(
        self,
        parent,
        summary: QuizSummary,
        on_play_again: Callable[[], None],
        on_view_leaderboard: Callable[[], None],
        on_go_home: Callable[[], None],
        storage: StorageManager
    ):
        super().__init__(parent, fg_color="transparent")
        self.summary = summary
        self.on_play_again = on_play_again
        self.on_view_leaderboard = on_view_leaderboard
        self.on_go_home = on_go_home
        self.storage = storage

        # Save to storage leaderboard & lifetime stats
        self._record_results()
        self._build_ui()

    def _record_results(self):
        self.storage.add_score(
            player_name=self.summary.player_name,
            score=self.summary.total_score,
            accuracy=self.summary.accuracy_percentage,
            category=self.summary.category
        )
        self.storage.record_quiz_stats(
            questions_count=self.summary.total_questions,
            correct_count=self.summary.correct_count,
            score=self.summary.total_score,
            streak=self.summary.best_streak,
            duration_sec=self.summary.total_time_seconds
        )

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)

        # --- HERO BANNER ---
        hero_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=18, border_width=1, border_color=COLORS["border"])
        hero_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 15), ipady=15)
        hero_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero_card,
            text="SESSION COMPLETED 🎉",
            font=FONTS["badge"],
            text_color=COLORS["secondary"],
            fg_color=COLORS["bg_card_secondary"],
            corner_radius=8,
            padx=14,
            pady=4
        ).pack(pady=(12, 6))

        ctk.CTkLabel(
            hero_card,
            text=self.summary.rank_title,
            font=FONTS["display"],
            text_color=COLORS["primary"]
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            hero_card,
            text=f"Well played, {self.summary.player_name}! Here is your full performance breakdown:",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 15))

        # --- STATS GRID TILES (4 cards) ---
        stats_frame = ctk.CTkFrame(hero_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Total Score
        self._create_tile(
            stats_frame, 0,
            icon="🏆",
            title="TOTAL SCORE",
            value=f"{self.summary.total_score:,}",
            accent=COLORS["primary"]
        )

        # 2. Accuracy
        acc = self.summary.accuracy_percentage
        acc_color = COLORS["success"] if acc >= 70 else (COLORS["warning"] if acc >= 40 else COLORS["danger"])
        self._create_tile(
            stats_frame, 1,
            icon="🎯",
            title="ACCURACY",
            value=f"{acc}%",
            accent=acc_color
        )

        # 3. Correct Count
        self._create_tile(
            stats_frame, 2,
            icon="✓",
            title="CORRECT / TOTAL",
            value=f"{self.summary.correct_count} / {self.summary.total_questions}",
            accent=COLORS["secondary"]
        )

        # 4. Longest Streak
        self._create_tile(
            stats_frame, 3,
            icon="🔥",
            title="TOP STREAK",
            value=f"{self.summary.best_streak} in a row",
            accent=COLORS["warning"]
        )

        # --- ACTION BUTTONS ---
        action_box = ctk.CTkFrame(container, fg_color="transparent")
        action_box.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 15))
        action_box.grid_columnconfigure((0, 1, 2), weight=1)

        btn_again = ctk.CTkButton(
            action_box,
            text="🔄 Play Again",
            font=FONTS["title"],
            height=48,
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.on_play_again
        )
        btn_again.grid(row=0, column=0, sticky="ew", padx=5)

        btn_leader = ctk.CTkButton(
            action_box,
            text="🏆 Hall of Fame",
            font=FONTS["title"],
            height=48,
            corner_radius=12,
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            command=self.on_view_leaderboard
        )
        btn_leader.grid(row=0, column=1, sticky="ew", padx=5)

        btn_home = ctk.CTkButton(
            action_box,
            text="🏠 Main Menu",
            font=FONTS["title"],
            height=48,
            corner_radius=12,
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            command=self.on_go_home
        )
        btn_home.grid(row=0, column=2, sticky="ew", padx=5)

        # --- QUESTION REVIEW SECTION ---
        review_header = ctk.CTkLabel(
            container,
            text="Detailed Question Review",
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        )
        review_header.grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))

        # Review Cards
        review_box = ctk.CTkFrame(container, fg_color="transparent")
        review_box.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        review_box.grid_columnconfigure(0, weight=1)

        letters = ["A", "B", "C", "D"]
        for idx, ans in enumerate(self.summary.answers):
            q = ans.question
            is_cor = ans.is_correct
            status_color = COLORS["success"] if is_cor else COLORS["danger"]
            badge_text = "CORRECT ✓" if is_cor else ("TIMED OUT ⏱️" if ans.selected_index is None else "INCORRECT ✕")

            card = ctk.CTkFrame(
                review_box,
                fg_color=COLORS["bg_card"],
                corner_radius=12,
                border_width=1,
                border_color=status_color
            )
            card.grid(row=idx, column=0, sticky="ew", pady=6, ipady=8)
            card.grid_columnconfigure(0, weight=1)

            # Card Header
            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=15, pady=(8, 4))

            ctk.CTkLabel(
                top_line,
                text=f"Q{idx+1}. {q.category} ({q.difficulty})",
                font=FONTS["body_small"],
                text_color=COLORS["text_secondary"]
            ).pack(side="left")

            ctk.CTkLabel(
                top_line,
                text=f"{badge_text}  +{ans.points_awarded} pts ({ans.time_taken_seconds}s)",
                font=FONTS["body_bold"],
                text_color=status_color
            ).pack(side="right")

            # Question Text
            ctk.CTkLabel(
                card,
                text=q.question,
                font=FONTS["subtitle"],
                text_color=COLORS["text_primary"],
                wraplength=840,
                justify="left"
            ).pack(anchor="w", padx=15, pady=4)

            # Answers details
            detail_box = ctk.CTkFrame(card, fg_color=COLORS["bg_card_secondary"], corner_radius=8)
            detail_box.pack(fill="x", padx=15, pady=6)

            # Your answer
            if ans.selected_index is not None and 0 <= ans.selected_index < len(q.options):
                chosen_text = f"{letters[ans.selected_index]}. {q.options[ans.selected_index]}"
            else:
                chosen_text = "None (Timed out or skipped)"

            correct_text = f"{letters[q.correct_index]}. {q.correct_answer}"

            your_ans_lbl = ctk.CTkLabel(
                detail_box,
                text=f"Your Answer: {chosen_text}",
                font=FONTS["body"],
                text_color=status_color
            )
            your_ans_lbl.pack(anchor="w", padx=12, pady=(6, 2))

            if not is_cor:
                cor_ans_lbl = ctk.CTkLabel(
                    detail_box,
                    text=f"Correct Answer: {correct_text}",
                    font=FONTS["body_bold"],
                    text_color=COLORS["success"]
                )
                cor_ans_lbl.pack(anchor="w", padx=12, pady=(2, 6))

            # Explanation
            if q.explanation:
                ctk.CTkLabel(
                    card,
                    text=f"Explanation: {q.explanation}",
                    font=FONTS["body_small"],
                    text_color=COLORS["text_secondary"],
                    wraplength=840,
                    justify="left"
                ).pack(anchor="w", padx=15, pady=(2, 8))

    def _create_tile(self, parent, col, icon, title, value, accent):
        tile = ctk.CTkFrame(parent, fg_color=COLORS["bg_card_secondary"], corner_radius=12)
        tile.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")

        ctk.CTkLabel(tile, text=icon, font=FONTS["title_large"]).pack(pady=(10, 0))
        ctk.CTkLabel(tile, text=title, font=FONTS["badge"], text_color=COLORS["text_secondary"]).pack(pady=(2, 0))
        ctk.CTkLabel(tile, text=value, font=FONTS["subtitle"], text_color=accent).pack(pady=(2, 10))
