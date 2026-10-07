"""Curated questions repository and online trivia fetcher with offline fallback."""
import html
import json
import os
import random
import urllib.request
import urllib.parse
from typing import List, Optional
from src.models import Question

DEFAULT_QUESTIONS = [
    # ------------------ PYTHON & PROGRAMMING ------------------
    Question(
        id="py_1",
        question="What is the output of bool([]) in Python?",
        options=["False", "True", "None", "Error"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Easy",
        explanation="In Python, empty collections like lists [], dictionaries {}, and sets evaluate to False in a boolean context.",
        hint="Empty sequences are falsy."
    ),
    Question(
        id="py_2",
        question="Which built-in Python module is used to serialize and deserialize Python object structures?",
        options=["pickle", "json", "marshmallow", "marshal"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Medium",
        explanation="The 'pickle' module implements binary protocols for serializing and de-serializing a Python object structure.",
        hint="Think of preserving cucumbers in brine."
    ),
    Question(
        id="py_3",
        question="What does the GIL stand for in CPython implementation?",
        options=[
            "Global Interpreter Lock",
            "General Interface Library",
            "Global Instance Loop",
            "Generic Inheritance Layer"
        ],
        correct_index=0,
        category="Python & Programming",
        difficulty="Medium",
        explanation="The Global Interpreter Lock (GIL) is a mutex that prevents multiple native threads from executing Python bytecodes at once.",
        hint="It synchronizes the interpreter globally."
    ),
    Question(
        id="py_4",
        question="What is the time complexity of looking up a key in a standard Python dictionary on average?",
        options=["O(1)", "O(n)", "O(log n)", "O(n log n)"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Easy",
        explanation="Python dictionaries are implemented as hash tables, providing average-case O(1) constant time lookups.",
        hint="Hash tables provide instant constant time lookup."
    ),
    Question(
        id="py_5",
        question="Which PEP introduced type hints in Python?",
        options=["PEP 484", "PEP 8", "PEP 20", "PEP 572"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Hard",
        explanation="PEP 484 (Python 3.5) standardized type annotations for static analysis and IDE autocomplete.",
        hint="It is in the late 400s series."
    ),
    Question(
        id="py_6",
        question="What keyword is used to create an anonymous function in Python?",
        options=["lambda", "def", "anon", "fn"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Easy",
        explanation="The 'lambda' keyword allows defining small anonymous inline functions.",
        hint="Named after Alonzo Church's calculus."
    ),
    Question(
        id="py_7",
        question="What does the *args parameter allow in a Python function definition?",
        options=[
            "Accept any number of positional arguments",
            "Accept any number of keyword arguments",
            "Enforce strict type checking",
            "Unpack a dictionary only"
        ],
        correct_index=0,
        category="Python & Programming",
        difficulty="Easy",
        explanation="*args passes variable-length non-keyworded positional arguments to a function as a tuple.",
        hint="Look for positional arguments."
    ),
    Question(
        id="py_8",
        question="In Python, which dunder method is invoked by the 'len()' function?",
        options=["__len__", "__length__", "__size__", "__count__"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Easy",
        explanation="The __len__() special method is called by len() to determine the number of items in a container.",
        hint="It matches the exact function name."
    ),
    Question(
        id="py_9",
        question="What was the 'walrus operator' introduced in Python 3.8?",
        options=[":=", "->", "//=", "<>"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Medium",
        explanation="The assignment expression operator (:=) resembles the eyes and tusks of a walrus.",
        hint="Colon followed by equals sign."
    ),
    Question(
        id="py_10",
        question="Which data structure in Python is implemented as a doubly-linked list or array of blocks in collections?",
        options=["deque", "OrderedDict", "Counter", "namedtuple"],
        correct_index=0,
        category="Python & Programming",
        difficulty="Hard",
        explanation="collections.deque (double-ended queue) provides O(1) appends and pops from both ends.",
        hint="Double-ended queue."
    ),

    # ------------------ SCIENCE & TECHNOLOGY ------------------
    Question(
        id="sci_1",
        question="What is the speed of light in a vacuum (approx)?",
        options=["300,000 km/s", "150,000 km/s", "3,000,000 km/s", "30,000 km/s"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Easy",
        explanation="Light travels at approximately 299,792 kilometers per second in a vacuum (roughly 300,000 km/s).",
        hint="Around 3 x 10^8 meters per second."
    ),
    Question(
        id="sci_2",
        question="Which fundamental force is responsible for holding atomic nuclei together?",
        options=["Strong Nuclear Force", "Electromagnetic Force", "Gravity", "Weak Nuclear Force"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Medium",
        explanation="The Strong Nuclear Force binds quarks together to form protons/neutrons and binds nuclei together.",
        hint="It is the strongest of the four fundamental interactions."
    ),
    Question(
        id="sci_3",
        question="What does the James Webb Space Telescope primarily observe in?",
        options=["Infrared spectrum", "Ultraviolet spectrum", "X-ray spectrum", "Gamma rays"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Medium",
        explanation="JWST observes primarily in the infrared spectrum to peer through cosmic dust clouds and detect red-shifted light from the early universe.",
        hint="Heat radiation / red shifted frequencies."
    ),
    Question(
        id="sci_4",
        question="Which chemical element has the symbol 'Fe'?",
        options=["Iron", "Fluorine", "Francium", "Fermium"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Easy",
        explanation="'Fe' originates from the Latin name 'Ferrum', which means Iron.",
        hint="Latin name Ferrum."
    ),
    Question(
        id="sci_5",
        question="What phenomenon causes clocks to tick slower when moving at relativistic speeds?",
        options=["Time Dilation", "Length Contraction", "Gravitational Lensing", "Quantum Entanglement"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Medium",
        explanation="Special relativity predicts that moving clocks tick slower relative to a stationary observer, known as Time Dilation.",
        hint="Time stretches or dilates."
    ),
    Question(
        id="sci_6",
        question="Which cellular organelle produces the majority of chemical energy (ATP)?",
        options=["Mitochondria", "Ribosome", "Endoplasmic Reticulum", "Golgi Apparatus"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Easy",
        explanation="Mitochondria are often nicknamed the 'powerhouses of the cell' as they generate ATP through cellular respiration.",
        hint="The classic 'powerhouse' of the cell."
    ),
    Question(
        id="sci_7",
        question="What is the primary gas found in Earth's atmosphere?",
        options=["Nitrogen (approx 78%)", "Oxygen (approx 21%)", "Argon (approx 1%)", "Carbon Dioxide (0.04%)"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Easy",
        explanation="Earth's atmosphere is roughly 78% Nitrogen, 21% Oxygen, and small amounts of Argon and other gases.",
        hint="More than three-quarters of the air we breathe."
    ),
    Question(
        id="sci_8",
        question="Who is considered the pioneer of computer programming for writing the first algorithm for the Analytical Engine?",
        options=["Ada Lovelace", "Alan Turing", "Grace Hopper", "Charles Babbage"],
        correct_index=0,
        category="Science & Technology",
        difficulty="Medium",
        explanation="Ada Lovelace published the first algorithm intended to be carried out by a machine (the Analytical Engine) in 1843.",
        hint="Daughter of Lord Byron."
    ),

    # ------------------ WORLD HISTORY & GEOGRAPHY ------------------
    Question(
        id="hist_1",
        question="In what year did the Apollo 11 mission successfully land humans on the Moon?",
        options=["1969", "1965", "1972", "1961"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Easy",
        explanation="Neil Armstrong and Buzz Aldrin stepped onto the lunar surface on July 20, 1969.",
        hint="The summer of 69."
    ),
    Question(
        id="hist_2",
        question="What is the deepest oceanic trench on Earth?",
        options=["Mariana Trench", "Java Trench", "Puerto Rico Trench", "Philippine Trench"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Easy",
        explanation="The Mariana Trench in the western Pacific Ocean reaches a maximum known depth of nearly 11,000 meters (Challenger Deep).",
        hint="Located in the western Pacific."
    ),
    Question(
        id="hist_3",
        question="Which ancient civilization built the majestic city of Machu Picchu?",
        options=["Inca Civilization", "Maya Civilization", "Aztec Civilization", "Olmec Civilization"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Easy",
        explanation="Machu Picchu was constructed by the Inca Empire in the 15th century in Peru.",
        hint="Based in the Andes mountains."
    ),
    Question(
        id="hist_4",
        question="Which treaty formally ended World War I in 1919?",
        options=["Treaty of Versailles", "Treaty of Paris", "Treaty of Utrecht", "Treaty of Westphalia"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Medium",
        explanation="The Treaty of Versailles was signed on June 28, 1919, in the Hall of Mirrors at Versailles, France.",
        hint="Signed in a famous French palace."
    ),
    Question(
        id="hist_5",
        question="What is the capital city of Australia?",
        options=["Canberra", "Sydney", "Melbourne", "Brisbane"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Medium",
        explanation="Canberra was chosen as the compromise capital of Australia between rivals Sydney and Melbourne.",
        hint="It is not Sydney or Melbourne."
    ),
    Question(
        id="hist_6",
        question="Which river is traditionally recognized as the longest river in the world?",
        options=["Nile River", "Amazon River", "Yangtze River", "Mississippi River"],
        correct_index=0,
        category="World History & Geography",
        difficulty="Easy",
        explanation="The Nile River in northeastern Africa is traditionally recognized at approximately 6,650 km in length.",
        hint="Flows northward through Egypt."
    ),

    # ------------------ GENERAL KNOWLEDGE ------------------
    Question(
        id="gk_1",
        question="How many keys are on a standard acoustic grand piano?",
        options=["88 keys", "76 keys", "92 keys", "84 keys"],
        correct_index=0,
        category="General Knowledge",
        difficulty="Medium",
        explanation="A standard piano has 88 keys: 52 white keys and 36 black keys.",
        hint="Two repeating digits representing 7 octaves plus a minor third."
    ),
    Question(
        id="gk_2",
        question="Which metal is liquid at room temperature (standard ambient temperature and pressure)?",
        options=["Mercury", "Bromine", "Gallium", "Cesium"],
        correct_index=0,
        category="General Knowledge",
        difficulty="Easy",
        explanation="Mercury (Hg) is the only metallic element that is liquid at standard conditions for temperature and pressure.",
        hint="Also called quicksilver."
    ),
    Question(
        id="gk_3",
        question="Who wrote the tragedy play 'Hamlet'?",
        options=["William Shakespeare", "Christopher Marlowe", "John Milton", "Geoffrey Chaucer"],
        correct_index=0,
        category="General Knowledge",
        difficulty="Easy",
        explanation="'Hamlet' was written by William Shakespeare between 1599 and 1601.",
        hint="The Bard of Avon."
    ),
    Question(
        id="gk_4",
        question="What is the currency of Japan?",
        options=["Yen", "Won", "Yuan", "Ringgit"],
        correct_index=0,
        category="General Knowledge",
        difficulty="Easy",
        explanation="The Japanese Yen (¥) has been the official currency of Japan since 1871.",
        hint="Symbol ¥."
    ),
    Question(
        id="gk_5",
        question="How many bones are in the adult human skeleton?",
        options=["206", "195", "214", "220"],
        correct_index=0,
        category="General Knowledge",
        difficulty="Medium",
        explanation="An adult human has 206 distinct bones after several infant bones fuse together.",
        hint="Just over two hundred."
    ),

    # ------------------ POP CULTURE & GAMING ------------------
    Question(
        id="pop_1",
        question="Which classic video game franchise features the character 'Link'?",
        options=["The Legend of Zelda", "Final Fantasy", "Metroid", "Dragon Quest"],
        correct_index=0,
        category="Pop Culture & Gaming",
        difficulty="Easy",
        explanation="Link is the courageous protagonist of Nintendo's acclaimed franchise 'The Legend of Zelda'.",
        hint="He wields the Master Sword in Hyrule."
    ),
    Question(
        id="pop_2",
        question="What is the best-selling video game of all time with over 300 million copies sold?",
        options=["Minecraft", "Grand Theft Auto V", "Tetris", "Super Mario Bros."],
        correct_index=0,
        category="Pop Culture & Gaming",
        difficulty="Easy",
        explanation="Mojang's sandbox game Minecraft has sold well over 300 million copies worldwide.",
        hint="Blocky sandbox crafted by Notch."
    ),
    Question(
        id="pop_3",
        question="In Marvel Comics and the MCU, what rare metal is Captain America's shield composed of?",
        options=["Vibranium", "Adamantium", "Uru", "Mithril"],
        correct_index=0,
        category="Pop Culture & Gaming",
        difficulty="Medium",
        explanation="Captain America's iconic shield is forged from Vibranium mined in Wakanda.",
        hint="Associated with Wakanda."
    ),
    Question(
        id="pop_4",
        question="Who directed the landmark sci-fi films 'Interstellar', 'Inception', and 'Oppenheimer'?",
        options=["Christopher Nolan", "Denis Villeneuve", "Steven Spielberg", "Ridley Scott"],
        correct_index=0,
        category="Pop Culture & Gaming",
        difficulty="Easy",
        explanation="British-American director Christopher Nolan directed Inception, Interstellar, and the Oscar-winning Oppenheimer.",
        hint="Known for practical effects and non-linear timelines."
    )
]

CATEGORIES = [
    "All Categories",
    "Python & Programming",
    "Science & Technology",
    "World History & Geography",
    "General Knowledge",
    "Pop Culture & Gaming",
    "Live Online Trivia 🌐"
]

DIFFICULTIES = ["Any", "Easy", "Medium", "Hard"]


class QuestionBank:
    """Manages question loading, filtering, custom questions, and online fetching."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.custom_file = os.path.join(data_dir, "custom_questions.json")
        self._ensure_data_dir()
        self.custom_questions: List[Question] = self._load_custom_questions()

    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _load_custom_questions(self) -> List[Question]:
        if not os.path.exists(self.custom_file):
            return []
        try:
            with open(self.custom_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Question.from_dict(item) for item in data]
        except Exception:
            return []

    def save_custom_questions(self):
        """Persists custom questions to JSON."""
        try:
            with open(self.custom_file, "w", encoding="utf-8") as f:
                json.dump([q.to_dict() for q in self.custom_questions], f, indent=2)
        except Exception as e:
            print(f"Error saving custom questions: {e}")

    def add_custom_question(self, question: Question):
        self.custom_questions.append(question)
        self.save_custom_questions()

    def get_all_questions(self) -> List[Question]:
        return list(DEFAULT_QUESTIONS) + list(self.custom_questions)

    def get_categories(self) -> List[str]:
        cats = set(q.category for q in self.get_all_questions())
        sorted_cats = [c for c in CATEGORIES if c in cats or c.startswith("All") or "Live" in c]
        for c in sorted(cats):
            if c not in sorted_cats:
                sorted_cats.append(c)
        return sorted_cats

    def fetch_online_trivia(self, amount: int = 10, difficulty: str = "Any") -> List[Question]:
        """Fetches live questions from Open Trivia Database API."""
        try:
            url = f"https://opentdb.com/api.php?amount={amount}&type=multiple"
            if difficulty.lower() in ["easy", "medium", "hard"]:
                url += f"&difficulty={difficulty.lower()}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ProfessionalQuizGame/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                results = payload.get("results", [])
                
                fetched: List[Question] = []
                for idx, r in enumerate(results):
                    q_text = html.unescape(r["question"])
                    correct_ans = html.unescape(r["correct_answer"])
                    wrong_answers = [html.unescape(w) for w in r["incorrect_answers"]]
                    
                    options = wrong_answers + [correct_ans]
                    random.shuffle(options)
                    correct_idx = options.index(correct_ans)
                    
                    diff = r.get("difficulty", "medium").capitalize()
                    category = html.unescape(r.get("category", "General Knowledge"))

                    fetched.append(Question(
                        id=f"online_{idx}_{random.randint(100, 999)}",
                        question=q_text,
                        options=options,
                        correct_index=correct_idx,
                        category=category,
                        difficulty=diff,
                        explanation=f"The verified correct answer is '{correct_ans}'.",
                        hint=f"It begins with letter '{correct_ans[0]}'" if correct_ans else "Think carefully!"
                    ))
                if fetched:
                    return fetched
        except Exception as e:
            print(f"Online trivia fetch fallback: {e}")
        
        # Fallback to local questions if offline
        return self.get_filtered_questions("All Categories", difficulty, amount)

    def get_filtered_questions(
        self,
        category: str = "All Categories",
        difficulty: str = "Any",
        count: int = 10,
        shuffle: bool = True
    ) -> List[Question]:
        """Filters questions by category and difficulty, randomly sampled."""
        if category == "Live Online Trivia 🌐":
            return self.fetch_online_trivia(count, difficulty)

        pool = self.get_all_questions()

        if category and category != "All Categories":
            pool = [q for q in pool if q.category.lower() == category.lower()]

        if difficulty and difficulty != "Any":
            pool = [q for q in pool if q.difficulty.lower() == difficulty.lower()]

        if not pool:
            # Fallback if strict filter yields 0
            pool = self.get_all_questions()

        if shuffle:
            shuffled = list(pool)
            random.shuffle(shuffled)
            pool = shuffled

        # For each question, also shuffle options so option positions vary
        selected = pool[:count]
        prepared_questions: List[Question] = []
        for q in selected:
            options_copy = list(q.options)
            correct_val = q.options[q.correct_index]
            random.shuffle(options_copy)
            new_correct_idx = options_copy.index(correct_val)
            prepared_questions.append(Question(
                id=q.id,
                question=q.question,
                options=options_copy,
                correct_index=new_correct_idx,
                category=q.category,
                difficulty=q.difficulty,
                explanation=q.explanation,
                hint=q.hint
            ))

        return prepared_questions
