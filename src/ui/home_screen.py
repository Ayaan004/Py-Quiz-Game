"""Home / Start Screen for Quiz Game."""
import customtkinter as ctk
from typing import Callable
from src.theme import COLORS, FONTS
from src.question_bank import CATEGORIES, DIFFICULTIES
from src.storage import StorageManager

class HomeScreen(ctk.CTkFrame):
    """Home screen providing player configuration, category pickers, and quick stats."""

    def __init__(
        self,
        parent,
        on_start_quiz: Callable[[str, str, str, int], None],
        on_view_leaderboard: Callable[[], None],
        on_view_editor: Callable[[], None],
        storage: StorageManager
    ):
        super().__init__(parent, fg_color="transparent")
        self.on_start_quiz = on_start_quiz
        self.on_view_leaderboard = on_view_leaderboard
        self.on_view_editor = on_view_editor
        self.storage = storage

        self._build_ui()

    def _build_ui(self):
        # Grid layout for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container to handle smaller laptop displays gracefully
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)

        # --- HERO BANNER ---
        hero_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=18, border_width=1, border_color=COLORS["border"])
        hero_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 15), ipady=15)
        hero_card.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkLabel(
            hero_card,
            text="⚡ ULTIMATE TRIVIA CHALLENGE",
            font=FONTS["badge"],
            text_color=COLORS["primary"],
            fg_color=COLORS["bg_card_secondary"],
            corner_radius=8,
            padx=12,
            pady=4
        )
        badge.grid(row=0, column=0, pady=(10, 5))

        title = ctk.CTkLabel(
            hero_card,
            text="Quiz Master Pro",
            font=FONTS["display"],
            text_color=COLORS["text_primary"]
        )
        title.grid(row=1, column=0, pady=(0, 5))

        subtitle = ctk.CTkLabel(
            hero_card,
            text="Test your intellect with curated challenges, streaks, lifelines & live trivia",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.grid(row=2, column=0, pady=(0, 10))

        # --- QUICK STATS PILLS ---
        stats = self.storage.get_stats()
        stats_frame = ctk.CTkFrame(hero_card, fg_color="transparent")
        stats_frame.grid(row=3, column=0, pady=(5, 5))

        pills = [
            ("🎮 Games Played", str(stats.get("total_games", 0))),
            ("🏆 Best Score", f"{stats.get('best_score', 0):,}"),
            ("🔥 Top Streak", f"{stats.get('highest_streak', 0)}"),
        ]
        for idx, (label, val) in enumerate(pills):
            pill_box = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_card_secondary"], corner_radius=10)
            pill_box.grid(row=0, column=idx, padx=8, pady=4)
            ctk.CTkLabel(pill_box, text=f"{label}: ", font=FONTS["body_small"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(10, 2), pady=6)
            ctk.CTkLabel(pill_box, text=val, font=FONTS["body_bold"], text_color=COLORS["primary"]).pack(side="left", padx=(0, 10), pady=6)

        # --- CONFIGURATION CARD ---
        config_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=18, border_width=1, border_color=COLORS["border"])
        config_card.grid(row=1, column=0, sticky="ew", padx=10, pady=10, ipady=10)
        config_card.grid_columnconfigure((0, 1), weight=1)

        # 1. Player Name
        name_section = ctk.CTkFrame(config_card, fg_color="transparent")
        name_section.grid(row=0, column=0, columnspan=2, sticky="ew", padx=25, pady=(15, 10))
        ctk.CTkLabel(name_section, text="Player Name", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            name_section,
            placeholder_text="Enter your player alias (e.g. MasterMind)",
            font=FONTS["body"],
            height=42,
            corner_radius=10,
            border_color=COLORS["border"]
        )
        self.name_entry.insert(0, "Challenger")
        self.name_entry.pack(fill="x")

        # 2. Category Selection
        cat_section = ctk.CTkFrame(config_card, fg_color="transparent")
        cat_section.grid(row=1, column=0, columnspan=2, sticky="ew", padx=25, pady=10)
        ctk.CTkLabel(cat_section, text="Select Category", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 5))
        
        self.cat_menu = ctk.CTkOptionMenu(
            cat_section,
            values=CATEGORIES,
            font=FONTS["body_bold"],
            dropdown_font=FONTS["body"],
            height=42,
            corner_radius=10,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"]
        )
        self.cat_menu.set(CATEGORIES[0])
        self.cat_menu.pack(fill="x")

        # 3. Difficulty Selector
        diff_col = ctk.CTkFrame(config_card, fg_color="transparent")
        diff_col.grid(row=2, column=0, sticky="nsew", padx=25, pady=10)
        ctk.CTkLabel(diff_col, text="Difficulty Level", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        
        self.diff_seg = ctk.CTkSegmentedButton(
            diff_col,
            values=DIFFICULTIES,
            font=FONTS["body_bold"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            height=38,
            corner_radius=10
        )
        self.diff_seg.set("Any")
        self.diff_seg.pack(fill="x")

        # 4. Question Count
        count_col = ctk.CTkFrame(config_card, fg_color="transparent")
        count_col.grid(row=2, column=1, sticky="nsew", padx=25, pady=10)
        
        self.count_label = ctk.CTkLabel(count_col, text="Questions: 10", font=FONTS["subtitle"], text_color=COLORS["text_primary"])
        self.count_label.pack(anchor="w", pady=(0, 8))
        
        self.count_slider = ctk.CTkSlider(
            count_col,
            from_=5,
            to=20,
            number_of_steps=3,
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            progress_color=COLORS["primary"],
            command=self._on_slider_change
        )
        self.count_slider.set(10)
        self.count_slider.pack(fill="x", pady=6)

        # --- ACTION BUTTONS ---
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 20))
        action_frame.grid_columnconfigure((0, 1), weight=1)

        # Big Launch Button
        start_btn = ctk.CTkButton(
            action_frame,
            text="🚀 START QUIZ SESSION",
            font=FONTS["title"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=54,
            corner_radius=14,
            command=self._handle_start
        )
        start_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # Secondary Actions
        lead_btn = ctk.CTkButton(
            action_frame,
            text="🏆 Hall of Fame",
            font=FONTS["body_bold"],
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            height=42,
            corner_radius=10,
            command=self.on_view_leaderboard
        )
        lead_btn.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        editor_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Custom Questions",
            font=FONTS["body_bold"],
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            height=42,
            corner_radius=10,
            command=self.on_view_editor
        )
        editor_btn.grid(row=1, column=1, sticky="ew", padx=(6, 0))

    def _on_slider_change(self, val):
        count = int(val)
        self.count_label.configure(text=f"Questions: {count}")

    def _handle_start(self):
        player = self.name_entry.get().strip() or "Challenger"
        category = self.cat_menu.get()
        difficulty = self.diff_seg.get()
        count = int(self.count_slider.get())
        self.on_start_quiz(player, category, difficulty, count)
