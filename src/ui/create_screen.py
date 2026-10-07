"""Question studio for creating and managing custom quiz questions."""
import customtkinter as ctk
import time
from typing import Callable, List
from src.theme import COLORS, FONTS
from src.models import Question
from src.question_bank import QuestionBank, CATEGORIES

class CreateScreen(ctk.CTkFrame):
    """Custom question creation studio allowing users to add and manage custom questions."""

    def __init__(
        self,
        parent,
        question_bank: QuestionBank,
        on_go_home: Callable[[], None]
    ):
        super().__init__(parent, fg_color="transparent")
        self.bank = question_bank
        self.on_go_home = on_go_home
        self.correct_opt_var = ctk.IntVar(value=0)

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)

        # Header bar
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
            text="✏️ Custom Question Studio",
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=15)

        # Form Card
        form_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        form_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15), ipady=12)
        form_card.grid_columnconfigure((0, 1), weight=1)

        # 1. Question Text
        q_box = ctk.CTkFrame(form_card, fg_color="transparent")
        q_box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 8))
        ctk.CTkLabel(q_box, text="Question Text *", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.q_entry = ctk.CTkEntry(q_box, placeholder_text="Type your question here...", font=FONTS["body"], height=40)
        self.q_entry.pack(fill="x")

        # 2. Category & Difficulty
        cat_box = ctk.CTkFrame(form_card, fg_color="transparent")
        cat_box.grid(row=1, column=0, sticky="ew", padx=(20, 10), pady=8)
        ctk.CTkLabel(cat_box, text="Category", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        valid_cats = [c for c in CATEGORIES if not c.startswith("All") and "Live" not in c]
        self.cat_menu = ctk.CTkOptionMenu(cat_box, values=valid_cats, height=38, fg_color=COLORS["primary"])
        self.cat_menu.set(valid_cats[0])
        self.cat_menu.pack(fill="x")

        diff_box = ctk.CTkFrame(form_card, fg_color="transparent")
        diff_box.grid(row=1, column=1, sticky="ew", padx=(10, 20), pady=8)
        ctk.CTkLabel(diff_box, text="Difficulty", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.diff_seg = ctk.CTkSegmentedButton(diff_box, values=["Easy", "Medium", "Hard"], height=38, selected_color=COLORS["primary"])
        self.diff_seg.set("Medium")
        self.diff_seg.pack(fill="x")

        # 3. Four Options with Correct Radio Indicator
        opts_box = ctk.CTkFrame(form_card, fg_color="transparent")
        opts_box.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=8)
        ctk.CTkLabel(opts_box, text="Four Options (Select the Radio button for the Correct Answer) *", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 6))

        self.option_entries: List[ctk.CTkEntry] = []
        for i, letter in enumerate(["A", "B", "C", "D"]):
            row_frame = ctk.CTkFrame(opts_box, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)
            
            radio = ctk.CTkRadioButton(
                row_frame,
                text=f"Option {letter}",
                value=i,
                variable=self.correct_opt_var,
                font=FONTS["body_bold"],
                fg_color=COLORS["success"],
                hover_color=COLORS["success_hover"]
            )
            radio.pack(side="left", padx=(0, 10))

            entry = ctk.CTkEntry(row_frame, placeholder_text=f"Enter text for Option {letter}...", height=36)
            entry.pack(side="left", fill="x", expand=True)
            self.option_entries.append(entry)

        # 4. Explanation and Hint
        hint_box = ctk.CTkFrame(form_card, fg_color="transparent")
        hint_box.grid(row=3, column=0, sticky="ew", padx=(20, 10), pady=8)
        ctk.CTkLabel(hint_box, text="Hint (Optional)", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.hint_entry = ctk.CTkEntry(hint_box, placeholder_text="A helpful clue for the Hint lifeline...", height=36)
        self.hint_entry.pack(fill="x")

        expl_box = ctk.CTkFrame(form_card, fg_color="transparent")
        expl_box.grid(row=3, column=1, sticky="ew", padx=(10, 20), pady=8)
        ctk.CTkLabel(expl_box, text="Explanation (Optional)", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.expl_entry = ctk.CTkEntry(expl_box, placeholder_text="Why this answer is correct...", height=36)
        self.expl_entry.pack(fill="x")

        # Status & Submit
        self.status_lbl = ctk.CTkLabel(form_card, text="", font=FONTS["body_bold"], text_color=COLORS["danger"])
        self.status_lbl.grid(row=4, column=0, columnspan=2, pady=4)

        submit_btn = ctk.CTkButton(
            form_card,
            text="➕ Save & Add Question",
            font=FONTS["title"],
            height=46,
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_add
        )
        submit_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=(4, 15), sticky="ew")

        # Custom Questions List Section
        list_header = ctk.CTkLabel(
            container,
            text=f"Your Custom Questions ({len(self.bank.custom_questions)})",
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        )
        list_header.grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))

        self.list_box = ctk.CTkFrame(container, fg_color="transparent")
        self.list_box.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.list_box.grid_columnconfigure(0, weight=1)

        self._refresh_custom_list()

    def _refresh_custom_list(self):
        for widget in self.list_box.winfo_children():
            widget.destroy()

        if not self.bank.custom_questions:
            ctk.CTkLabel(
                self.list_box,
                text="No custom questions created yet. Use the form above to add your own!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"]
            ).pack(pady=20)
            return

        for idx, q in enumerate(self.bank.custom_questions):
            card = ctk.CTkFrame(self.list_box, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=4, ipady=4)
            card.grid_columnconfigure(0, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=6)

            info_box = ctk.CTkFrame(inner, fg_color="transparent")
            info_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info_box,
                text=f"{idx+1}. {q.question}",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=650
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_box,
                text=f"Correct: {q.correct_answer}  •  {q.category}  •  {q.difficulty}",
                font=FONTS["body_small"],
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))

            del_btn = ctk.CTkButton(
                inner,
                text="Delete ✕",
                font=FONTS["body_small"],
                width=80,
                height=28,
                fg_color=COLORS["danger_bg"],
                text_color=COLORS["danger"],
                hover_color=COLORS["danger"],
                command=lambda target_id=q.id: self._handle_delete(target_id)
            )
            del_btn.pack(side="right", padx=6)

    def _handle_add(self):
        q_text = self.q_entry.get().strip()
        if not q_text:
            self.status_lbl.configure(text="Please enter question text.", text_color=COLORS["danger"])
            return

        options = [entry.get().strip() for entry in self.option_entries]
        if any(not opt for opt in options):
            self.status_lbl.configure(text="All 4 option fields must be filled out.", text_color=COLORS["danger"])
            return

        correct_idx = self.correct_opt_var.get()
        category = self.cat_menu.get()
        difficulty = self.diff_seg.get()
        hint = self.hint_entry.get().strip()
        expl = self.expl_entry.get().strip()

        new_q = Question(
            id=f"custom_{int(time.time())}",
            question=q_text,
            options=options,
            correct_index=correct_idx,
            category=category,
            difficulty=difficulty,
            explanation=expl,
            hint=hint
        )

        self.bank.add_custom_question(new_q)

        # Clear form
        self.q_entry.delete(0, "end")
        for entry in self.option_entries:
            entry.delete(0, "end")
        self.hint_entry.delete(0, "end")
        self.expl_entry.delete(0, "end")
        self.correct_opt_var.set(0)

        self.status_lbl.configure(text="✓ Custom question saved successfully!", text_color=COLORS["success"])
        self._refresh_custom_list()

    def _handle_delete(self, q_id: str):
        self.bank.custom_questions = [q for q in self.bank.custom_questions if q.id != q_id]
        self.bank.save_custom_questions()
        self._refresh_custom_list()
