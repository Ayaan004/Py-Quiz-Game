"""PDF Quiz Studio screen for uploading PDFs and generating interactive quizzes via OpenRouter."""
import os
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Callable, List, Optional

from src.theme import COLORS, FONTS
from src.models import Question
from src.question_bank import QuestionBank
from src.pdf_quiz_service import PDFQuizService, DEFAULT_API_KEY


class PDFScreen(ctk.CTkFrame):
    """UI Screen for uploading PDFs and generating AI quizzes using OpenRouter Free API."""

    def __init__(
        self,
        parent,
        question_bank: QuestionBank,
        on_start_custom_quiz: Callable[[str, List[Question], str, str], None],
        on_go_home: Callable[[], None]
    ):
        super().__init__(parent, fg_color="transparent")
        self.question_bank = question_bank
        self.on_start_custom_quiz = on_start_custom_quiz
        self.on_go_home = on_go_home

        self.service = PDFQuizService(api_key=DEFAULT_API_KEY)
        self.pdf_data: Optional[dict] = None
        self.generated_questions: List[Question] = []
        self.is_generating = False

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container for all sections
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        self.container.grid_columnconfigure(0, weight=1)

        # --- HEADER BAR ---
        header_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 12))
        header_bar.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header_bar,
            text="← Back to Menu",
            font=FONTS["body_bold"],
            width=130,
            height=38,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["border"],
            command=self.on_go_home
        )
        back_btn.grid(row=0, column=0, sticky="w")

        title_box = ctk.CTkFrame(header_bar, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w", padx=15)

        title_lbl = ctk.CTkLabel(
            title_box,
            text="📄 AI PDF Quiz Generator",
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Upload study notes, books, or papers & let OpenRouter Free AI create your customized quiz",
            font=FONTS["body_small"],
            text_color=COLORS["text_secondary"]
        )
        subtitle_lbl.pack(anchor="w")

        # Top Badge
        badge = ctk.CTkLabel(
            header_bar,
            text="⚡ OPENROUTER FREE API",
            font=FONTS["badge"],
            text_color=COLORS["secondary"],
            fg_color=COLORS["bg_card_secondary"],
            corner_radius=8,
            padx=10,
            pady=4
        )
        badge.grid(row=0, column=2, sticky="e")

        # --- STEP 1: PDF UPLOAD CARD ---
        upload_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        upload_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15), ipady=10)
        upload_card.grid_columnconfigure(0, weight=1)

        card_title = ctk.CTkLabel(
            upload_card,
            text="Step 1: Choose Your PDF Document",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        card_title.grid(row=0, column=0, sticky="w", padx=20, pady=(12, 6))

        # Upload Dropzone simulation
        dropzone = ctk.CTkFrame(upload_card, fg_color=COLORS["bg_card_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        dropzone.grid(row=1, column=0, sticky="ew", padx=20, pady=6, ipady=12)
        dropzone.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dropzone, text="📁", font=("Segoe UI", 34)).pack(pady=(6, 2))
        
        self.file_name_lbl = ctk.CTkLabel(
            dropzone,
            text="No PDF Selected Yet",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"]
        )
        self.file_name_lbl.pack()

        self.file_meta_lbl = ctk.CTkLabel(
            dropzone,
            text="Supports study guides, syllabus, research papers, lecture notes (.pdf)",
            font=FONTS["body_small"],
            text_color=COLORS["text_secondary"]
        )
        self.file_meta_lbl.pack(pady=(2, 8))

        btn_box = ctk.CTkFrame(dropzone, fg_color="transparent")
        btn_box.pack()

        self.browse_btn = ctk.CTkButton(
            btn_box,
            text="📂 Browse & Select PDF",
            font=FONTS["body_bold"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=10,
            height=38,
            command=self._browse_pdf
        )
        self.browse_btn.pack(side="left", padx=6)

        # Extracted Text Preview toggle
        self.preview_btn = ctk.CTkButton(
            btn_box,
            text="👁️ View Extracted Text",
            font=FONTS["body"],
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=10,
            height=38,
            state="disabled",
            command=self._toggle_text_preview
        )
        self.preview_btn.pack(side="left", padx=6)

        # Collapsible text preview box
        self.preview_box = ctk.CTkFrame(upload_card, fg_color="transparent")
        self.preview_textbox = ctk.CTkTextbox(
            self.preview_box,
            font=FONTS["code"],
            height=130,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.preview_textbox.pack(fill="both", expand=True, padx=20, pady=8)
        self.preview_visible = False

        # --- STEP 2: GENERATION CONFIGURATION CARD ---
        config_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        config_card.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 15), ipady=10)
        config_card.grid_columnconfigure((0, 1), weight=1)

        cfg_title = ctk.CTkLabel(
            config_card,
            text="Step 2: Quiz Generation Settings",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        cfg_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(12, 10))

        # 1. Number of questions
        count_box = ctk.CTkFrame(config_card, fg_color="transparent")
        count_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=6)
        self.count_label = ctk.CTkLabel(count_box, text="Questions to Generate: 5", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        self.count_label.pack(anchor="w", pady=(0, 4))
        
        self.count_slider = ctk.CTkSlider(
            count_box,
            from_=3,
            to=15,
            number_of_steps=12,
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            progress_color=COLORS["primary"],
            command=self._on_count_change
        )
        self.count_slider.set(5)
        self.count_slider.pack(fill="x", pady=4)

        # 2. Difficulty
        diff_box = ctk.CTkFrame(config_card, fg_color="transparent")
        diff_box.grid(row=1, column=1, sticky="nsew", padx=20, pady=6)
        ctk.CTkLabel(diff_box, text="Difficulty Level", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        
        self.diff_seg = ctk.CTkSegmentedButton(
            diff_box,
            values=["Easy", "Medium", "Hard", "Any"],
            font=FONTS["body"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            height=34,
            corner_radius=8
        )
        self.diff_seg.set("Medium")
        self.diff_seg.pack(fill="x", pady=4)

        # 3. Model Selection
        model_box = ctk.CTkFrame(config_card, fg_color="transparent")
        model_box.grid(row=2, column=0, sticky="nsew", padx=20, pady=6)
        ctk.CTkLabel(model_box, text="OpenRouter Free Model", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))

        self.model_options = [
            "Auto (Fastest Free)",
            "inclusionai/ling-3.0-flash-sante:free",
            "google/gemma-4-26b-a4b-it:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "dots-studio/dots-3-note-preview:free",
            "nvidia/nemotron-3.5-lightning:free",
            "cohere/north-mini-code:free"
        ]
        self.model_menu = ctk.CTkOptionMenu(
            model_box,
            values=self.model_options,
            font=FONTS["body"],
            height=36,
            corner_radius=8,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"]
        )
        self.model_menu.set(self.model_options[0])
        self.model_menu.pack(fill="x", pady=4)

        # 4. Custom Focus / Instructions
        focus_box = ctk.CTkFrame(config_card, fg_color="transparent")
        focus_box.grid(row=2, column=1, sticky="nsew", padx=20, pady=6)
        ctk.CTkLabel(focus_box, text="Custom Focus / Instructions (Optional)", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        
        self.focus_entry = ctk.CTkEntry(
            focus_box,
            placeholder_text="e.g. Focus on key definitions, summary concepts...",
            font=FONTS["body"],
            height=36,
            corner_radius=8
        )
        self.focus_entry.pack(fill="x", pady=4)

        # 5. OpenRouter API Key
        key_box = ctk.CTkFrame(config_card, fg_color="transparent")
        key_box.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(6, 12))
        
        key_lbl_box = ctk.CTkFrame(key_box, fg_color="transparent")
        key_lbl_box.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(key_lbl_box, text="OpenRouter API Key (Free Tier Active)", font=FONTS["body_small"], text_color=COLORS["text_secondary"]).pack(side="left")
        
        self.key_entry = ctk.CTkEntry(
            key_box,
            font=FONTS["code"],
            height=36,
            corner_radius=8,
            show="•"
        )
        self.key_entry.insert(0, DEFAULT_API_KEY)
        self.key_entry.pack(fill="x", pady=2)

        self.show_key_var = ctk.BooleanVar(value=False)
        self.show_key_chk = ctk.CTkCheckBox(
            key_box,
            text="Show API Key",
            font=FONTS["body_small"],
            variable=self.show_key_var,
            command=self._toggle_show_key,
            height=20,
            checkbox_width=18,
            checkbox_height=18
        )
        self.show_key_chk.pack(anchor="w", pady=(2, 0))

        # --- STEP 3: ACTION & LIVE STATUS CARD ---
        self.action_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        self.action_card.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 15), ipady=10)
        self.action_card.grid_columnconfigure(0, weight=1)

        self.generate_btn = ctk.CTkButton(
            self.action_card,
            text="✨ Generate Interactive Quiz from PDF",
            font=FONTS["title"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=50,
            corner_radius=12,
            command=self._start_generation
        )
        self.generate_btn.pack(fill="x", padx=20, pady=(15, 8))

        # Status & Progress Bar
        self.status_label = ctk.CTkLabel(
            self.action_card,
            text="Ready. Select a PDF document above to start.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(padx=20, pady=2)

        self.prog_bar = ctk.CTkProgressBar(
            self.action_card,
            mode="indeterminate",
            height=8,
            progress_color=COLORS["secondary"],
            corner_radius=4
        )
        # Hidden by default

        # --- STEP 4: GENERATED QUESTIONS RESULTS CONTAINER ---
        self.results_card = ctk.CTkFrame(self.container, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        self.results_card.grid_columnconfigure(0, weight=1)
        # Shown after generation succeeds

    def _on_count_change(self, val):
        count = int(val)
        self.count_label.configure(text=f"Questions to Generate: {count}")

    def _toggle_show_key(self):
        if self.show_key_var.get():
            self.key_entry.configure(show="")
        else:
            self.key_entry.configure(show="•")

    def _browse_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF Document",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.status_label.configure(text="Reading PDF file...")
            pdf_info = self.service.extract_text_from_pdf(file_path)
            self.pdf_data = pdf_info

            # Update UI
            file_size_kb = os.path.getsize(file_path) / 1024
            size_str = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{(file_size_kb/1024):.2f} MB"
            
            self.file_name_lbl.configure(text=f"📄 {pdf_info['filename']}")
            self.file_meta_lbl.configure(
                text=f"Pages: {pdf_info['total_pages']}  •  Size: {size_str}  •  Extracted Characters: {pdf_info['char_count']:,}"
            )
            self.preview_btn.configure(state="normal")
            
            # Fill preview text
            self.preview_textbox.delete("1.0", "end")
            self.preview_textbox.insert("1.0", pdf_info["text"])

            self.status_label.configure(
                text=f"Ready! Extracted {pdf_info['char_count']:,} characters from '{pdf_info['filename']}'. Click 'Generate Interactive Quiz'.",
                text_color=COLORS["success"]
            )
        except Exception as e:
            messagebox.showerror("PDF Read Error", str(e))
            self.status_label.configure(text=f"Failed to load PDF: {str(e)}", text_color=COLORS["danger"])

    def _toggle_text_preview(self):
        if not self.preview_visible:
            self.preview_box.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            self.preview_btn.configure(text="Hide Extracted Text")
            self.preview_visible = True
        else:
            self.preview_box.grid_forget()
            self.preview_btn.configure(text="👁️ View Extracted Text")
            self.preview_visible = False

    def _start_generation(self):
        if not self.pdf_data or not self.pdf_data.get("text"):
            messagebox.showwarning("No PDF Selected", "Please select a valid PDF file first.")
            return

        api_key = self.key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("API Key Required", "Please enter a valid OpenRouter API key.")
            return

        if self.is_generating:
            return

        self.service.api_key = api_key
        num_q = int(self.count_slider.get())
        diff = self.diff_seg.get()
        model = self.model_menu.get()
        if model.startswith("Auto"):
            model = "auto"
        custom_instructions = self.focus_entry.get().strip()

        # Update UI state
        self.is_generating = True
        self.generate_btn.configure(state="disabled", text="⏳ Generating Quiz with AI...")
        self.browse_btn.configure(state="disabled")
        self.prog_bar.pack(fill="x", padx=20, pady=(6, 12))
        self.prog_bar.start()

        # Run in worker thread
        threading.Thread(
            target=self._generation_worker,
            args=(num_q, diff, model, custom_instructions),
            daemon=True
        ).start()

    def _generation_worker(self, num_q: int, diff: str, model: str, custom_instructions: str):
        cat_name = f"PDF: {self.pdf_data['filename']}"
        text_content = self.preview_textbox.get("1.0", "end").strip() or self.pdf_data["text"]

        def update_status(msg: str):
            self.after(0, lambda: self.status_label.configure(text=msg, text_color=COLORS["text_primary"]))

        try:
            questions = self.service.generate_quiz(
                text_content=text_content,
                num_questions=num_q,
                difficulty=diff,
                category_name=cat_name,
                selected_model=model,
                custom_instructions=custom_instructions,
                status_callback=update_status
            )
            self.after(0, lambda: self._on_generation_success(questions))
        except Exception as e:
            self.after(0, lambda: self._on_generation_error(str(e)))

    def _on_generation_success(self, questions: List[Question]):
        self.is_generating = False
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.generate_btn.configure(state="normal", text="🔄 Regenerate / More Questions")
        self.browse_btn.configure(state="normal")
        self.generated_questions = questions

        self.status_label.configure(
            text=f"🎉 Successfully created {len(questions)} quiz questions from '{self.pdf_data['filename']}'!",
            text_color=COLORS["success"]
        )

        self._render_results_card()

    def _on_generation_error(self, err_msg: str):
        self.is_generating = False
        self.prog_bar.stop()
        self.prog_bar.pack_forget()
        self.generate_btn.configure(state="normal", text="✨ Retry Generation")
        self.browse_btn.configure(state="normal")

        self.status_label.configure(
            text=f"Generation failed: {err_msg[:120]}",
            text_color=COLORS["danger"]
        )
        messagebox.showerror("AI Generation Error", f"Failed to generate questions:\n\n{err_msg}")

    def _render_results_card(self):
        # Clear existing children in results_card
        for child in self.results_card.winfo_children():
            child.destroy()

        self.results_card.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 20), ipady=15)

        # Header with Play Buttons
        top_box = ctk.CTkFrame(self.results_card, fg_color="transparent")
        top_box.pack(fill="x", padx=20, pady=(15, 10))
        top_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_box,
            text=f"🎉 Generated Quiz Ready ({len(self.generated_questions)} Questions)",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        # Action Buttons
        actions_row = ctk.CTkFrame(self.results_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=20, pady=(0, 15))
        actions_row.grid_columnconfigure((0, 1), weight=1)

        play_now_btn = ctk.CTkButton(
            actions_row,
            text="🚀 PLAY THIS PDF QUIZ NOW!",
            font=FONTS["title"],
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            height=48,
            corner_radius=12,
            command=self._launch_quiz_now
        )
        play_now_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        save_bank_btn = ctk.CTkButton(
            actions_row,
            text="💾 Save Questions to Bank",
            font=FONTS["body_bold"],
            fg_color=COLORS["bg_card_secondary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            height=48,
            corner_radius=12,
            command=self._save_to_bank
        )
        save_bank_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # List of question preview cards
        for i, q in enumerate(self.generated_questions, start=1):
            q_card = ctk.CTkFrame(self.results_card, fg_color=COLORS["bg_card_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            q_card.pack(fill="x", padx=20, pady=6, ipady=8)

            q_head = ctk.CTkFrame(q_card, fg_color="transparent")
            q_head.pack(fill="x", padx=15, pady=(8, 4))

            ctk.CTkLabel(
                q_head,
                text=f"Q{i}. {q.question}",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
                wraplength=700,
                justify="left"
            ).pack(side="left")

            diff_pill = ctk.CTkLabel(
                q_head,
                text=q.difficulty,
                font=FONTS["badge"],
                text_color=COLORS["primary"],
                fg_color=COLORS["bg_card"],
                corner_radius=6,
                padx=8,
                pady=2
            )
            diff_pill.pack(side="right")

            # Options
            opt_frame = ctk.CTkFrame(q_card, fg_color="transparent")
            opt_frame.pack(fill="x", padx=15, pady=4)
            opt_frame.grid_columnconfigure((0, 1), weight=1)

            opt_prefixes = ["A", "B", "C", "D"]
            for o_idx, opt in enumerate(q.options):
                is_correct = (o_idx == q.correct_index)
                opt_row = o_idx // 2
                opt_col = o_idx % 2

                opt_box = ctk.CTkFrame(
                    opt_frame,
                    fg_color=COLORS["success_bg"] if is_correct else COLORS["bg_card"],
                    corner_radius=8,
                    border_width=1,
                    border_color=COLORS["success"] if is_correct else COLORS["border"]
                )
                opt_box.grid(row=opt_row, column=opt_col, sticky="ew", padx=4, pady=3, ipady=4)

                prefix_txt = f"✓ {opt_prefixes[o_idx]}: " if is_correct else f"{opt_prefixes[o_idx]}: "
                ctk.CTkLabel(
                    opt_box,
                    text=f"{prefix_txt}{opt}",
                    font=FONTS["body_bold"] if is_correct else FONTS["body"],
                    text_color=COLORS["success"] if is_correct else COLORS["text_primary"],
                    wraplength=340,
                    justify="left"
                ).pack(anchor="w", padx=10, pady=2)

            # Explanation & hint
            if q.explanation or q.hint:
                info_box = ctk.CTkFrame(q_card, fg_color="transparent")
                info_box.pack(fill="x", padx=15, pady=(4, 6))
                
                if q.explanation:
                    ctk.CTkLabel(
                        info_box,
                        text=f"💡 Explanation: {q.explanation}",
                        font=FONTS["body_small"],
                        text_color=COLORS["text_secondary"],
                        wraplength=700,
                        justify="left"
                    ).pack(anchor="w")

    def _launch_quiz_now(self):
        if not self.generated_questions:
            return
        cat_name = f"PDF: {self.pdf_data['filename']}" if self.pdf_data else "PDF Quiz"
        self.on_start_custom_quiz(
            "Challenger",
            self.generated_questions,
            cat_name,
            self.diff_seg.get()
        )

    def _save_to_bank(self):
        if not self.generated_questions:
            return
        for q in self.generated_questions:
            self.question_bank.add_custom_question(q)
        messagebox.showinfo(
            "Saved to Question Bank",
            f"Successfully saved {len(self.generated_questions)} questions to your permanent question bank!\n\nYou can also find them anytime under Custom Questions."
        )
