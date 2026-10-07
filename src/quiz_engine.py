"""Quiz logic, scoring calculations, lifeline state, and game engine."""
import time
import random
from typing import List, Optional, Set
from src.models import Question, UserAnswer, QuizSummary

class QuizEngine:
    """Manages active quiz session state, lifelines, scoring, and history."""

    DIFFICULTY_BASE_POINTS = {
        "easy": 100,
        "medium": 150,
        "hard": 200,
    }

    TIME_PER_QUESTION = {
        "easy": 25,
        "medium": 20,
        "hard": 15,
        "any": 20
    }

    def __init__(
        self,
        player_name: str,
        category: str,
        difficulty: str,
        questions: List[Question]
    ):
        self.player_name = player_name.strip() or "Player 1"
        self.category = category
        self.difficulty = difficulty.capitalize()
        self.questions = questions
        
        # State
        self.current_index = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.answers: List[UserAnswer] = []
        
        # Timing
        self.per_question_time = self.TIME_PER_QUESTION.get(self.difficulty.lower(), 20)
        self.question_start_time = 0.0
        self.total_quiz_start_time = time.time()
        
        # Lifeline states (each can be used once per quiz)
        self.lifeline_fifty_fifty_used = False
        self.lifeline_freeze_used = False
        self.lifeline_hint_used = False
        
        # Current active question modifiers
        self.eliminated_option_indices: Set[int] = set()
        self.current_extra_time = 0
        self.hint_revealed = False

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)

    def start_current_question(self):
        """Resets per-question ephemeral modifiers and records start time."""
        self.question_start_time = time.time()
        self.eliminated_option_indices.clear()
        self.current_extra_time = 0
        self.hint_revealed = False

    def get_remaining_seconds(self) -> float:
        """Calculates current remaining seconds for active question."""
        elapsed = time.time() - self.question_start_time
        total_allowed = self.per_question_time + self.current_extra_time
        remaining = total_allowed - elapsed
        return max(0.0, remaining)

    def submit_answer(self, option_index: Optional[int]) -> UserAnswer:
        """
        Validates user choice, updates score & streak, records history.
        Pass option_index=None for timeout or skip.
        """
        q = self.current_question
        if not q:
            raise ValueError("No active question to submit.")

        time_taken = (time.time() - self.question_start_time)
        is_correct = (option_index is not None and option_index == q.correct_index)
        points = 0

        if is_correct:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak

            # Difficulty base
            base = self.DIFFICULTY_BASE_POINTS.get(q.difficulty.lower(), 120)

            # Streak multiplier: 1x, 1.25x, 1.5x, 2.0x max
            if self.streak == 1:
                multiplier = 1.0
            elif self.streak == 2:
                multiplier = 1.25
            elif self.streak == 3:
                multiplier = 1.5
            else:
                multiplier = 2.0

            # Time bonus: faster answer yields up to +50 bonus pts
            allowed = self.per_question_time + self.current_extra_time
            ratio_left = max(0.0, (allowed - time_taken) / allowed)
            time_bonus = int(ratio_left * 50)

            points = int((base * multiplier) + time_bonus)
            self.score += points
        else:
            self.streak = 0

        user_ans = UserAnswer(
            question=q,
            selected_index=option_index,
            time_taken_seconds=round(time_taken, 2),
            is_correct=is_correct,
            points_awarded=points
        )
        self.answers.append(user_ans)
        return user_ans

    def advance_to_next(self) -> bool:
        """Moves to the next question. Returns True if next question exists."""
        self.current_index += 1
        if not self.is_finished:
            self.start_current_question()
            return True
        return False

    # Lifelines
    def use_fifty_fifty(self) -> List[int]:
        """
        Eliminates 2 incorrect option indices.
        Returns list of eliminated indices.
        """
        if self.lifeline_fifty_fifty_used or not self.current_question:
            return []
        self.lifeline_fifty_fifty_used = True
        
        q = self.current_question
        incorrect_indices = [i for i in range(len(q.options)) if i != q.correct_index]
        random.shuffle(incorrect_indices)
        eliminated = incorrect_indices[:2]
        self.eliminated_option_indices = set(eliminated)
        return eliminated

    def use_freeze_time(self, extra_seconds: int = 15) -> bool:
        """Adds extra seconds to current question."""
        if self.lifeline_freeze_used:
            return False
        self.lifeline_freeze_used = True
        self.current_extra_time += extra_seconds
        return True

    def use_hint(self) -> str:
        """Reveals hint for current question."""
        if self.lifeline_hint_used or not self.current_question:
            return ""
        self.lifeline_hint_used = True
        self.hint_revealed = True
        hint_text = self.current_question.hint or f"Think about: {self.current_question.category}"
        return hint_text

    def get_summary(self) -> QuizSummary:
        """Generates full session summary."""
        correct = sum(1 for a in self.answers if a.is_correct)
        skipped = sum(1 for a in self.answers if a.selected_index is None)
        wrong = len(self.answers) - correct - skipped
        total_q = len(self.questions)
        
        accuracy = (correct / total_q * 100.0) if total_q > 0 else 0.0
        max_possible = total_q * 250  # rough upper ceiling with 2x multipliers
        total_time = time.time() - self.total_quiz_start_time

        return QuizSummary(
            player_name=self.player_name,
            category=self.category,
            difficulty=self.difficulty,
            total_questions=total_q,
            correct_count=correct,
            wrong_count=wrong,
            skipped_count=skipped,
            total_score=self.score,
            max_possible_score=max_possible,
            accuracy_percentage=round(accuracy, 1),
            best_streak=self.best_streak,
            total_time_seconds=round(total_time, 1),
            answers=self.answers
        )
