"""Main application window controlling navigation between screens."""
import customtkinter as ctk
from src.theme import COLORS, FONTS, apply_theme
from src.storage import StorageManager
from src.question_bank import QuestionBank
from src.quiz_engine import QuizEngine
from src.sound_manager import sound_fx
from src.ui.home_screen import HomeScreen
from src.ui.quiz_screen import QuizScreen
from src.ui.result_screen import ResultScreen
from src.ui.leaderboard_screen import LeaderboardScreen
from src.ui.create_screen import CreateScreen
from src.ui.pdf_screen import PDFScreen

class MainWindow(ctk.CTk):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        apply_theme()

        # Window settings
        self.title("Quiz Master Pro - Professional Quiz Game")
        self.geometry("1024x720")
        self.minsize(860, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        # Core subsystems
        self.storage = StorageManager()
        self.question_bank = QuestionBank()
        self.active_engine = None
        self.current_theme = "dark"

        self._build_shell()
        self.show_home()

    def _build_shell(self):
        """Builds top persistent navigation bar and content viewport."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top App Bar
        navbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=56, corner_radius=0, border_width=1, border_color=COLORS["border"])
        navbar.grid(row=0, column=0, sticky="ew")
        navbar.grid_columnconfigure(1, weight=1)

        # Brand / Title
        brand_box = ctk.CTkFrame(navbar, fg_color="transparent")
        brand_box.grid(row=0, column=0, padx=20, pady=10)

        ctk.CTkLabel(brand_box, text="⚡", font=FONTS["title"], text_color=COLORS["primary"]).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(brand_box, text="QUIZ MASTER PRO", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(side="left")

        # Right Controls (Sound Toggle & Theme Toggle)
        controls_box = ctk.CTkFrame(navbar, fg_color="transparent")
        controls_box.grid(row=0, column=2, padx=20, pady=10)

        # PDF AI Quick Button
        self.pdf_nav_btn = ctk.CTkButton(
            controls_box,
            text="📄 PDF AI Quiz",
            width=110,
            height=32,
            font=FONTS["body_bold"],
            fg_color=COLORS["secondary"],
            text_color="#000000",
            hover_color=COLORS["secondary_hover"],
            corner_radius=8,
            command=self.show_pdf_quiz
        )
        self.pdf_nav_btn.pack(side="left", padx=6)

        # Sound Button
        self.sound_btn = ctk.CTkButton(
            controls_box,
            text="🔊 Sound ON",
            width=100,
            height=32,
            font=FONTS["body_small"],
            fg_color=COLORS["bg_card_secondary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            corner_radius=8,
            command=self._toggle_sound
        )
        self.sound_btn.pack(side="left", padx=6)

        # Theme Switcher
        self.theme_btn = ctk.CTkButton(
            controls_box,
            text="🌙 Theme",
            width=80,
            height=32,
            font=FONTS["body_small"],
            fg_color=COLORS["bg_card_secondary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            corner_radius=8,
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="left", padx=6)

        # Viewport Frame for dynamic screens
        self.viewport = ctk.CTkFrame(self, fg_color="transparent")
        self.viewport.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.viewport.grid_columnconfigure(0, weight=1)
        self.viewport.grid_rowconfigure(0, weight=1)

        self.current_screen = None

    def _switch_screen(self, screen_widget: ctk.CTkFrame):
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = screen_widget
        self.current_screen.grid(row=0, column=0, sticky="nsew")

    # Navigation Methods
    def show_home(self):
        screen = HomeScreen(
            parent=self.viewport,
            on_start_quiz=self.start_quiz,
            on_view_leaderboard=self.show_leaderboard,
            on_view_editor=self.show_editor,
            on_view_pdf=self.show_pdf_quiz,
            storage=self.storage
        )
        self._switch_screen(screen)

    def show_pdf_quiz(self):
        screen = PDFScreen(
            parent=self.viewport,
            question_bank=self.question_bank,
            on_start_custom_quiz=self.start_custom_quiz,
            on_go_home=self.show_home
        )
        self._switch_screen(screen)

    def start_quiz(self, player_name: str, category: str, difficulty: str, count: int):
        # Fetch / Sample questions
        questions = self.question_bank.get_filtered_questions(
            category=category,
            difficulty=difficulty,
            count=count
        )

        if not questions:
            # Fallback if no questions
            questions = self.question_bank.get_all_questions()[:count]

        self.active_engine = QuizEngine(
            player_name=player_name,
            category=category,
            difficulty=difficulty,
            questions=questions
        )

        screen = QuizScreen(
            parent=self.viewport,
            engine=self.active_engine,
            on_quiz_finished=self.show_results,
            on_quit_quiz=self.show_home
        )
        self._switch_screen(screen)

    def start_custom_quiz(self, player_name: str, questions: list, category: str = "PDF Quiz", difficulty: str = "Medium"):
        self.active_engine = QuizEngine(
            player_name=player_name,
            category=category,
            difficulty=difficulty,
            questions=questions
        )

        screen = QuizScreen(
            parent=self.viewport,
            engine=self.active_engine,
            on_quiz_finished=self.show_results,
            on_quit_quiz=self.show_home
        )
        self._switch_screen(screen)

    def show_results(self):
        if not self.active_engine:
            self.show_home()
            return

        summary = self.active_engine.get_summary()
        current_questions = list(self.active_engine.questions)
        is_pdf_or_custom = summary.category.startswith("PDF:")

        screen = ResultScreen(
            parent=self.viewport,
            summary=summary,
            on_play_again=lambda: (
                self.start_custom_quiz(
                    summary.player_name,
                    current_questions,
                    summary.category,
                    summary.difficulty
                ) if is_pdf_or_custom else self.start_quiz(
                    summary.player_name,
                    summary.category,
                    summary.difficulty,
                    summary.total_questions
                )
            ),
            on_view_leaderboard=self.show_leaderboard,
            on_go_home=self.show_home,
            storage=self.storage
        )
        self._switch_screen(screen)

    def show_leaderboard(self):
        screen = LeaderboardScreen(
            parent=self.viewport,
            storage=self.storage,
            on_go_home=self.show_home
        )
        self._switch_screen(screen)

    def show_editor(self):
        screen = CreateScreen(
            parent=self.viewport,
            question_bank=self.question_bank,
            on_go_home=self.show_home
        )
        self._switch_screen(screen)

    def _toggle_sound(self):
        is_on = sound_fx.toggle()
        self.sound_btn.configure(text="🔊 Sound ON" if is_on else "🔇 Muted")

    def _toggle_theme(self):
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
            self.theme_btn.configure(text="☀️ Theme")
        else:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
            self.theme_btn.configure(text="🌙 Theme")
