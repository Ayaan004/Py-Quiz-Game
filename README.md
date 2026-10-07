# ⚡ Quiz Master Pro

A professional, modern desktop Quiz Game application built with **Python** and **CustomTkinter**.

---

## 🌟 Key Features

- **🎨 Modern Dark & Light Mode UI**: Built with CustomTkinter featuring clean card containers, fluid typography, rounded buttons, and theme toggling.
- **📚 Curated Question Bank & Multi-Category Support**:
  - Python & Programming
  - Science & Technology
  - World History & Geography
  - General Knowledge
  - Pop Culture & Gaming
  - **Live Online Trivia 🌐**: Integrates dynamically with the Open Trivia Database API (with offline fallbacks).
- **⏱️ Visual Countdown Timer**:
  - Animated progress bar per question.
  - Smooth dynamic color transitions (Cyan $\rightarrow$ Amber $\rightarrow$ Red warning).
  - Ticking audio cues when time runs low.
- **⚡ Interactive Lifelines**:
  - **50:50**: Automatically eliminates 2 incorrect answer options.
  - **❄️ +15s Time Freeze**: Extends the clock by 15 seconds.
  - **💡 Hint**: Reveals an educational clue for the question.
- **🔥 Dynamic Scoring & Multiplier Streaks**:
  - Streak bonus multiplier (up to 2.0x for consecutive correct answers).
  - Quick-answer bonus points for speed.
- **🔊 Audio Feedback System**:
  - Pleasant ascending chimes on correct answers, descending buzzer on mistakes, and victory fanfares via Windows `winsound` executed in non-blocking background threads.
  - One-click mute toggle.
- **📝 Detailed Post-Quiz Review**:
  - View overall score, accuracy %, correct/incorrect breakdown, best streak, and rank titles (*Grandmaster Trivia Sage*, *Quiz Master*, etc.).
  - Review every single question answered, comparing your choice with the correct answer alongside deep explanations.
- **🏆 Persistent Hall of Fame & Leaderboard**:
  - Top 3 Podium display (Gold 🥇, Silver 🥈, Bronze 🥉).
  - JSON-backed persistent leaderboard tracking player scores, accuracy, and timestamps.
- **✏️ Custom Question Studio**:
  - Add your own custom quiz questions with custom answers, difficulty, hints, and explanations.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Installed packages:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Game
Launch the game directly from the project directory:
```bash
python main.py
```

---

## 📂 Project Structure

```
Quiz Game/
├── data/
│   ├── leaderboard.json        # Persistent high scores & rankings
│   ├── stats.json              # Aggregate lifetime player stats
│   └── custom_questions.json    # User-created custom questions
├── src/
│   ├── models.py               # Data models (Question, UserAnswer, QuizSummary)
│   ├── theme.py                # Color palette, font definitions, and tokens
│   ├── sound_manager.py        # Non-blocking audio feedback
│   ├── question_bank.py        # Question dataset & OpenTDB API integration
│   ├── storage.py              # Persistent JSON storage manager
│   ├── quiz_engine.py          # State machine, scoring, streaks & timer logic
│   └── ui/
│       ├── main_window.py      # Main window shell & screen navigation
│       ├── home_screen.py      # Start menu, category picker, stats cards
│       ├── quiz_screen.py      # Gameplay viewport, timer bar, lifelines, feedback
│       ├── result_screen.py    # Score report card & question review list
│       ├── leaderboard_screen.py # Podium hall of fame
│       └── create_screen.py    # Custom question studio
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```
