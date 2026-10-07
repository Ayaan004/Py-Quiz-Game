"""Data models for Quiz Game."""
from dataclasses import dataclass, field
from typing import List, Optional
import time

@dataclass
class Question:
    """Represents a single quiz question with metadata."""
    id: str
    question: str
    options: List[str]
    correct_index: int
    category: str = "General Knowledge"
    difficulty: str = "Medium"  # Easy, Medium, Hard
    explanation: str = ""
    hint: str = ""

    @property
    def correct_answer(self) -> str:
        if 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "correct_index": self.correct_index,
            "category": self.category,
            "difficulty": self.difficulty,
            "explanation": self.explanation,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        return cls(
            id=str(data.get("id", str(time.time()))),
            question=data.get("question", ""),
            options=list(data.get("options", [])),
            correct_index=int(data.get("correct_index", 0)),
            category=data.get("category", "General Knowledge"),
            difficulty=data.get("difficulty", "Medium"),
            explanation=data.get("explanation", ""),
            hint=data.get("hint", "")
        )


@dataclass
class UserAnswer:
    """Records user's response to a question."""
    question: Question
    selected_index: Optional[int]  # None if timed out / skipped
    time_taken_seconds: float
    is_correct: bool
    points_awarded: int


@dataclass
class QuizSummary:
    """Final summary of a finished quiz session."""
    player_name: str
    category: str
    difficulty: str
    total_questions: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    total_score: int
    max_possible_score: int
    accuracy_percentage: float
    best_streak: int
    total_time_seconds: float
    answers: List[UserAnswer] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def rank_title(self) -> str:
        acc = self.accuracy_percentage
        if acc >= 90:
            return "Grandmaster Trivia Sage 👑"
        elif acc >= 75:
            return "Quiz Master 🌟"
        elif acc >= 60:
            return "Knowledge Scholar 🎓"
        elif acc >= 40:
            return "Apprentice Thinker 💡"
        else:
            return "Curious Novice 🌱"
