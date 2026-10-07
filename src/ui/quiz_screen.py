"""Active interactive Quiz gameplay screen."""
import customtkinter as ctk
from typing import Callable, List, Optional
from src.theme import COLORS, FONTS
from src.quiz_engine import QuizEngine
from src.sound_manager import sound_fx

class QuizScreen(ctk.CTkFrame):
    """Interactive quiz gameplay screen with timer, lifelines, option cards, and explanation."""

    def __init__(
        self,
        parent,
        engine: QuizEngine,
        on_quiz_finished: Callable[[], None],
        on_quit_quiz: Callable[[], None]
    ):
        super().__init__(parent, fg_color="transparent")
        self.engine = engine
        self.on_quiz_finished = on_quiz_finished
        self.on_quit_quiz = on_quit_quiz

        self.timer_job = None
        self.answered = False
        self.option_buttons: List[ctk.CTkButton] = []

        self._build_ui()
        self._load_current_question()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container so it fits all resolutions comfortably
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        self.container.grid_columnconfigure(0, weight=1)

        # --- TOP HEADER BAR ---
        header_bar = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        header_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10), ipady=8)
        header_bar.grid_columnconfigure(1, weight=1)

        # Quit button
        quit_btn = ctk.CTkButton(
            header_bar,
            text="✕ Quit",
            font=FONTS["body_bold"],
            width=70,
            height=32,
            fg_color="transparent",
            hover_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            border_width=1,
            border_color=COLORS["border"],
            command=self._handle_quit
        )
        quit_btn.grid(row=0, column=0, padx=(15, 10))

        # Center Badges (Progress & Category)
        center_box = ctk.CTkFrame(header_bar, fg_color="transparent")
        center_box.grid(row=0, column=1)

        self.progress_label = ctk.CTkLabel(
            center_box,
            text="Question 1/10",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        self.progress_label.pack(side="left", padx=8)

        self.category_badge = ctk.CTkLabel(
            center_box,
            text=f"•  {self.engine.category}",
            font=FONTS["body_small"],
            text_color=COLORS["primary_light"],
            fg_color=COLORS["bg_card_secondary"],
            corner_radius=8,
            padx=10,
            pady=2
        )
        self.category_badge.pack(side="left", padx=8)

        # Right Badges (Score & Streak)
        right_box = ctk.CTkFrame(header_bar, fg_color="transparent")
        right_box.grid(row=0, column=2, padx=(10, 15))

        self.streak_badge = ctk.CTkLabel(
            right_box,
            text="🔥 Streak: 0",
            font=FONTS["body_bold"],
            text_color=COLORS["warning"],
            fg_color=COLORS["warning_bg"],
            corner_radius=8,
            padx=10,
            pady=4
        )
        self.streak_badge.pack(side="left", padx=6)

        self.score_badge = ctk.CTkLabel(
            right_box,
            text="Score: 0",
            font=FONTS["body_bold"],
            text_color=COLORS["text_white"],
            fg_color=COLORS["primary"],
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.score_badge.pack(side="left", padx=6)

        # --- TIMER & LIFELINES BAR ---
        tools_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        tools_card.grid(row=1, column=0, sticky="ew", padx=10, pady=5, ipady=6)
        tools_card.grid_columnconfigure(0, weight=1)

        tools_inner = ctk.CTkFrame(tools_card, fg_color="transparent")
        tools_inner.pack(fill="x", padx=15, pady=4)

        # Timer Display
        timer_box = ctk.CTkFrame(tools_inner, fg_color="transparent")
        timer_box.pack(side="left")

        self.timer_icon_label = ctk.CTkLabel(timer_box, text="⏱️", font=FONTS["title"])
        self.timer_icon_label.pack(side="left", padx=(0, 6))

        self.timer_label = ctk.CTkLabel(timer_box, text="20s", font=FONTS["subtitle"], text_color=COLORS["secondary"])
        self.timer_label.pack(side="left")

        # Visual Timer Progress Bar
        self.timer_bar = ctk.CTkProgressBar(
            tools_inner,
            height=12,
            corner_radius=6,
            progress_color=COLORS["secondary"]
        )
        self.timer_bar.pack(side="left", fill="x", expand=True, padx=20)
        self.timer_bar.set(1.0)

        # Lifelines Toolbar
        lifelines_box = ctk.CTkFrame(tools_inner, fg_color="transparent")
        lifelines_box.pack(side="right")

        self.btn_5050 = ctk.CTkButton(
            lifelines_box,
            text="⚡ 50:50",
            width=80,
            height=32,
            font=FONTS["body_bold"],
            fg_color=COLORS["lifeline_5050"],
            hover_color=COLORS["primary_hover"],
            corner_radius=8,
            command=self._use_5050
        )
        self.btn_5050.pack(side="left", padx=4)

        self.btn_freeze = ctk.CTkButton(
            lifelines_box,
            text="❄️ +15s",
            width=80,
            height=32,
            font=FONTS["body_bold"],
            fg_color=COLORS["lifeline_freeze"],
            hover_color=COLORS["secondary_hover"],
            corner_radius=8,
            command=self._use_freeze
        )
        self.btn_freeze.pack(side="left", padx=4)

        self.btn_hint = ctk.CTkButton(
            lifelines_box,
            text="💡 Hint",
            width=80,
            height=32,
            font=FONTS["body_bold"],
            fg_color=COLORS["lifeline_hint"],
            hover_color=COLORS["warning_hover"],
            corner_radius=8,
            command=self._use_hint
        )
        self.btn_hint.pack(side="left", padx=4)

        # --- QUESTION CARD ---
        self.question_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=18, border_width=1, border_color=COLORS["border"])
        self.question_card.grid(row=2, column=0, sticky="ew", padx=10, pady=10, ipady=12)
        self.question_card.grid_columnconfigure(0, weight=1)

        self.diff_tag = ctk.CTkLabel(
            self.question_card,
            text="DIFFICULTY: MEDIUM",
            font=FONTS["badge"],
            text_color=COLORS["secondary"],
            fg_color=COLORS["bg_card_secondary"],
            corner_radius=6,
            padx=10,
            pady=3
        )
        self.diff_tag.pack(anchor="w", padx=20, pady=(12, 6))

        self.question_text_label = ctk.CTkLabel(
            self.question_card,
            text="Loading Question...",
            font=FONTS["title"],
            text_color=COLORS["text_primary"],
            wraplength=850,
            justify="left"
        )
        self.question_text_label.pack(fill="x", padx=20, pady=8)

        # Hint box (hidden initially)
        self.hint_card = ctk.CTkFrame(self.question_card, fg_color=COLORS["warning_bg"], corner_radius=10)
        self.hint_label = ctk.CTkLabel(
            self.hint_card,
            text="",
            font=FONTS["body_bold"],
            text_color=COLORS["warning_hover"],
            wraplength=800
        )
        self.hint_label.pack(padx=14, pady=8)

        # --- OPTIONS CONTAINER (4 Stacked Rows) ---
        self.options_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.options_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.options_frame.grid_columnconfigure(0, weight=1)

        self.option_buttons = []
        letters = ["A", "B", "C", "D"]
        for i in range(4):
            btn = ctk.CTkButton(
                self.options_frame,
                text=f"{letters[i]}. Option {i+1}",
                font=FONTS["body_bold"],
                anchor="w",
                height=52,
                corner_radius=12,
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["primary_hover"],
                text_color=COLORS["text_primary"],
                border_width=1,
                border_color=COLORS["border"],
                command=lambda idx=i: self._select_answer(idx)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=5)
            self.option_buttons.append(btn)

        # --- EXPLANATION & NEXT ACTION CARD ---
        self.footer_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        # Grid dynamically when answered

        self.feedback_banner = ctk.CTkLabel(
            self.footer_card,
            text="",
            font=FONTS["subtitle"],
            corner_radius=8,
            padx=14,
            pady=4
        )
        self.feedback_banner.pack(anchor="w", padx=20, pady=(12, 4))

        self.explanation_label = ctk.CTkLabel(
            self.footer_card,
            text="",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=820,
            justify="left"
        )
        self.explanation_label.pack(fill="x", padx=20, pady=(2, 10))

        self.next_btn = ctk.CTkButton(
            self.footer_card,
            text="Next Question ➔",
            font=FONTS["title"],
            height=46,
            corner_radius=10,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._advance_question
        )
        self.next_btn.pack(fill="x", padx=20, pady=(0, 14))

    def _load_current_question(self):
        """Prepares and displays the active question and starts countdown."""
        self._cancel_timer()
        self.answered = False
        self.engine.start_current_question()

        q = self.engine.current_question
        if not q:
            self._finish_quiz()
            return

        # Update Header Badges
        q_num = self.engine.current_index + 1
        total_q = self.engine.total_questions
        self.progress_label.configure(text=f"Question {q_num} of {total_q}")
        self.score_badge.configure(text=f"Score: {self.engine.score:,}")
        
        streak_text = f"🔥 Streak: {self.engine.streak}"
        if self.engine.streak >= 2:
            mult = 2.0 if self.engine.streak >= 4 else (1.5 if self.engine.streak == 3 else 1.25)
            streak_text += f" ({mult}x)"
        self.streak_badge.configure(text=streak_text)

        # Update Question Card
        self.diff_tag.configure(text=f"DIFFICULTY: {q.difficulty.upper()} • CATEGORY: {q.category}")
        self.question_text_label.configure(text=q.question)

        # Hide hint card by default
        self.hint_card.pack_forget()

        # Reset lifeline button states
        self.btn_5050.configure(state="normal" if not self.engine.lifeline_fifty_fifty_used else "disabled")
        self.btn_freeze.configure(state="normal" if not self.engine.lifeline_freeze_used else "disabled")
        self.btn_hint.configure(state="normal" if not self.engine.lifeline_hint_used else "disabled")

        # Hide footer card
        self.footer_card.grid_forget()

        # Reset option buttons
        letters = ["A", "B", "C", "D"]
        for idx, btn in enumerate(self.option_buttons):
            if idx < len(q.options):
                btn.configure(
                    text=f"  {letters[idx]}.  {q.options[idx]}",
                    state="normal",
                    fg_color=COLORS["bg_card"],
                    text_color=COLORS["text_primary"],
                    border_color=COLORS["border"],
                    border_width=1
                )
                btn.grid(row=idx, column=0, sticky="ew", pady=5)
            else:
                btn.grid_forget()

        # Start timer tick loop
        self._update_timer()

    def _update_timer(self):
        """Recursive loop running every 100ms to update progress bar and time remaining."""
        if self.answered:
            return

        remaining = self.engine.get_remaining_seconds()
        total_time = self.engine.per_question_time + self.engine.current_extra_time
        fraction = remaining / total_time if total_time > 0 else 0

        self.timer_label.configure(text=f"{int(remaining)}s")
        self.timer_bar.set(max(0.0, min(1.0, fraction)))

        # Color changes as time elapses
        if fraction > 0.45:
            self.timer_bar.configure(progress_color=COLORS["secondary"])
            self.timer_label.configure(text_color=COLORS["secondary"])
        elif fraction > 0.2:
            self.timer_bar.configure(progress_color=COLORS["warning"])
            self.timer_label.configure(text_color=COLORS["warning"])
        else:
            self.timer_bar.configure(progress_color=COLORS["danger"])
            self.timer_label.configure(text_color=COLORS["danger"])
            # Tick sound effect for urgent last seconds
            if int(remaining) <= 5 and int(remaining) > 0:
                sound_fx.play_tick()

        if remaining <= 0:
            # Time's up!
            self._handle_timeout()
            return

        self.timer_job = self.after(100, self._update_timer)

    def _cancel_timer(self):
        if self.timer_job:
            try:
                self.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    def _select_answer(self, selected_idx: int):
        if self.answered:
            return
        self.answered = True
        self._cancel_timer()

        q = self.engine.current_question
        result = self.engine.submit_answer(selected_idx)
        correct_idx = q.correct_index

        # Disable all option buttons and highlight results
        for idx, btn in enumerate(self.option_buttons):
            btn.configure(state="disabled")
            if idx == correct_idx:
                btn.configure(
                    fg_color=COLORS["success"],
                    text_color=COLORS["text_white"],
                    border_color=COLORS["success"]
                )
            elif idx == selected_idx and not result.is_correct:
                btn.configure(
                    fg_color=COLORS["danger"],
                    text_color=COLORS["text_white"],
                    border_color=COLORS["danger"]
                )

        if result.is_correct:
            sound_fx.play_correct()
            self.feedback_banner.configure(
                text=f"✓ CORRECT!  +{result.points_awarded} pts",
                fg_color=COLORS["success_bg"],
                text_color=COLORS["success"]
            )
        else:
            sound_fx.play_wrong()
            self.feedback_banner.configure(
                text="✕ INCORRECT",
                fg_color=COLORS["danger_bg"],
                text_color=COLORS["danger"]
            )

        self._show_footer(q.explanation)

    def _handle_timeout(self):
        if self.answered:
            return
        self.answered = True
        self._cancel_timer()

        q = self.engine.current_question
        self.engine.submit_answer(None)  # None indicates timeout/skipped
        sound_fx.play_wrong()

        # Highlight correct answer
        for idx, btn in enumerate(self.option_buttons):
            btn.configure(state="disabled")
            if idx == q.correct_index:
                btn.configure(
                    fg_color=COLORS["success"],
                    text_color=COLORS["text_white"],
                    border_color=COLORS["success"]
                )

        self.feedback_banner.configure(
            text="⏱️ TIME'S UP!",
            fg_color=COLORS["danger_bg"],
            text_color=COLORS["danger"]
        )
        self._show_footer(q.explanation)

    def _show_footer(self, explanation: str):
        expl_text = explanation if explanation else "No further explanation provided."
        self.explanation_label.configure(text=f"Insight: {expl_text}")
        
        is_last = (self.engine.current_index + 1) >= self.engine.total_questions
        self.next_btn.configure(text="View Final Results 🏆" if is_last else "Next Question ➔")
        self.footer_card.grid(row=4, column=0, sticky="ew", padx=10, pady=10)

    def _advance_question(self):
        has_next = self.engine.advance_to_next()
        if has_next:
            self._load_current_question()
        else:
            self._finish_quiz()

    def _finish_quiz(self):
        self._cancel_timer()
        sound_fx.play_complete()
        self.on_quiz_finished()

    # --- Lifeline Handlers ---
    def _use_5050(self):
        if self.answered or self.engine.lifeline_fifty_fifty_used:
            return
        eliminated = self.engine.use_fifty_fifty()
        self.btn_5050.configure(state="disabled")
        sound_fx.play_lifeline()
        for idx in eliminated:
            if idx < len(self.option_buttons):
                self.option_buttons[idx].configure(
                    state="disabled",
                    fg_color=COLORS["bg_input"],
                    text_color=COLORS["text_muted"]
                )

    def _use_freeze(self):
        if self.answered or self.engine.lifeline_freeze_used:
            return
        if self.engine.use_freeze_time(15):
            self.btn_freeze.configure(state="disabled")
            sound_fx.play_lifeline()
            # Visual feedback on timer label
            self.timer_label.configure(text=f"{int(self.engine.get_remaining_seconds())}s (+15s)")

    def _use_hint(self):
        if self.answered or self.engine.lifeline_hint_used:
            return
        hint_text = self.engine.use_hint()
        self.btn_hint.configure(state="disabled")
        sound_fx.play_lifeline()
        if hint_text:
            self.hint_label.configure(text=f"💡 HINT: {hint_text}")
            self.hint_card.pack(fill="x", padx=20, pady=(5, 10))

    def _handle_quit(self):
        self._cancel_timer()
        self.on_quit_quiz()
