"""Service for extracting text from PDF documents and generating quiz questions via OpenRouter Free AI API."""
import json
import os
import re
import time
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Callable, Tuple
import pypdf
from src.models import Question

DEFAULT_API_KEY = "sk-or-v1-11f9199331d54e7be0fac95c20135a6f6f5a952f294376b3f31194ad7a634a"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"

RECOMMENDED_FREE_MODELS = [
    "inclusionai/ling-3.0-flash-sante:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "dots-studio/dots-3-note-preview:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free",
]


class PDFQuizService:
    """Handles PDF extraction and OpenRouter AI quiz generation."""

    def __init__(self, api_key: str = DEFAULT_API_KEY):
        self.api_key = api_key.strip()

    def extract_text_from_pdf(self, file_path: str, max_chars: int = 15000) -> Dict:
        """Extracts text content and metadata from a given PDF file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        try:
            reader = pypdf.PdfReader(file_path)
            total_pages = len(reader.pages)
            if total_pages == 0:
                raise ValueError("The PDF has 0 pages.")

            extracted_chunks = []
            total_extracted = 0

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    extracted_chunks.append(f"--- Page {page_num} ---\n{page_text}")
                    total_extracted += len(page_text)
                    if total_extracted >= max_chars:
                        break

            full_text = "\n\n".join(extracted_chunks).strip()
            if not full_text:
                raise ValueError("No readable text found in the PDF. The file may contain scanned images only.")

            # Truncate text cleanly if too long
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + "\n...[Content truncated for AI context]..."

            return {
                "filename": filename,
                "file_path": file_path,
                "total_pages": total_pages,
                "char_count": len(full_text),
                "text": full_text
            }
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF ({filename}): {str(e)}")

    def fetch_available_free_models(self) -> List[str]:
        """Fetches currently accessible free models from OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://quizmasterpro.local",
            "X-Title": "Quiz Master Pro"
        }
        try:
            req = urllib.request.Request(MODELS_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m["id"] for m in data.get("data", []) if ":free" in m.get("id", "")]
                if models:
                    # Sort to place recommended ones first if available
                    sorted_models = []
                    for rec in RECOMMENDED_FREE_MODELS:
                        if rec in models:
                            sorted_models.append(rec)
                    for m in models:
                        if m not in sorted_models:
                            sorted_models.append(m)
                    return sorted_models
        except Exception as e:
            print(f"Notice: Failed to fetch live models list ({e}), using default free models list.")

        return list(RECOMMENDED_FREE_MODELS)

    def generate_quiz(
        self,
        text_content: str,
        num_questions: int = 5,
        difficulty: str = "Medium",
        category_name: str = "PDF Study Quiz",
        selected_model: str = "auto",
        custom_instructions: str = "",
        status_callback: Optional[Callable[[str], None]] = None
    ) -> List[Question]:
        """Calls OpenRouter Free API to generate questions from PDF text."""
        if not text_content.strip():
            raise ValueError("No text provided for quiz generation.")

        if status_callback:
            status_callback("Analyzing PDF content and preparing AI prompt...")

        diff_instruction = f"Target difficulty level: {difficulty}." if difficulty.lower() != "any" else "Provide a balanced mix of Easy, Medium, and Hard questions."
        custom_extra = f"\nSpecific user instructions: {custom_instructions}" if custom_instructions.strip() else ""

        system_msg = (
            "You are a master educational quiz author and test designer. "
            "Your job is to read study material and craft engaging, accurate, high-quality multiple choice questions. "
            "You MUST output valid JSON only, without any markdown formatting, preambles, or conversational text."
        )

        prompt = f"""Based on the provided document excerpts, generate exactly {num_questions} multiple choice questions.
{diff_instruction}{custom_extra}

Requirements for each question:
1. "question": A clear, thought-provoking question directly based on facts or concepts in the document.
2. "options": An array of exactly 4 plausible answer choices. One is correct, and three are realistic distractors.
3. "correct_index": An integer (0, 1, 2, or 3) indicating the zero-based index of the correct answer in the "options" list.
4. "difficulty": "Easy", "Medium", or "Hard".
5. "explanation": A concise, instructive explanation of why the correct answer is right according to the text.
6. "hint": A subtle clue to help the user if they get stuck, without revealing the answer directly.

DOCUMENT TEXT:
\"\"\"
{text_content}
\"\"\"

RESPONSE FORMAT:
You MUST respond ONLY with a raw JSON array of objects conforming to this schema:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "difficulty": "Medium",
    "explanation": "Why this answer is correct...",
    "hint": "Clue to guide the learner..."
  }}
]
"""

        models_to_try = []
        if selected_model and selected_model != "auto" and selected_model != "Auto (Fastest Free)":
            models_to_try.append(selected_model)
        
        # Append candidate free models for fallback
        for m in RECOMMENDED_FREE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://quizmasterpro.local",
            "X-Title": "Quiz Master Pro"
        }

        for model in models_to_try:
            if status_callback:
                status_callback(f"Connecting to OpenRouter Free AI ({model.split('/')[1] if '/' in model else model})...")

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }

            try:
                req = urllib.request.Request(
                    OPENROUTER_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    raw_content = resp_data["choices"][0]["message"]["content"].strip()

                if status_callback:
                    status_callback("Parsing AI response and verifying question format...")

                questions = self._parse_json_questions(raw_content, category_name, default_difficulty=difficulty)
                if questions:
                    if status_callback:
                        status_callback(f"Successfully generated {len(questions)} questions!")
                    return questions
                else:
                    raise ValueError(f"AI returned invalid or empty question array from {model}")

            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code} on {model}: {err_body[:150]}"
                if status_callback:
                    status_callback(f"Model {model} was busy ({e.code}), trying alternate free model...")
                time.sleep(1)
                continue
            except Exception as e:
                last_error = f"Error with {model}: {str(e)}"
                if status_callback:
                    status_callback(f"Model {model} error: {str(e)[:80]}. Trying fallback...")
                time.sleep(1)
                continue

        raise RuntimeError(f"All free OpenRouter models failed. Last error: {last_error}")

    def _parse_json_questions(self, raw_text: str, category: str, default_difficulty: str) -> List[Question]:
        """Extracts JSON array from text and constructs valid Question objects."""
        # 1. Clean markdown code fences if present
        clean_text = raw_text.strip()
        if "```" in clean_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
            if match:
                clean_text = match.group(1).strip()

        # 2. Find outermost JSON array brackets [ ... ]
        start_idx = clean_text.find("[")
        end_idx = clean_text.rfind("]")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean_text = clean_text[start_idx : end_idx + 1]

        parsed_data = json.loads(clean_text)
        if not isinstance(parsed_data, list):
            raise ValueError("Expected a JSON array of question objects.")

        questions: List[Question] = []
        for idx, item in enumerate(parsed_data):
            q_text = str(item.get("question", "")).strip()
            options = [str(opt).strip() for opt in item.get("options", []) if str(opt).strip()]

            # Must have at least 2 options, ideally 4
            if not q_text or len(options) < 2:
                continue

            # Ensure 4 options if fewer by padding placeholder or fallback
            while len(options) < 4:
                options.append(f"Option {len(options)+1}")

            # Trim to 4 options
            options = options[:4]

            raw_idx = item.get("correct_index", 0)
            try:
                correct_idx = int(raw_idx)
            except (ValueError, TypeError):
                correct_idx = 0

            if correct_idx < 0 or correct_idx >= len(options):
                correct_idx = 0

            diff = str(item.get("difficulty", default_difficulty if default_difficulty != "Any" else "Medium")).capitalize()
            if diff not in ["Easy", "Medium", "Hard"]:
                diff = "Medium"

            explanation = str(item.get("explanation", f"Correct answer is {options[correct_idx]}")).strip()
            hint = str(item.get("hint", f"Option starts with '{options[correct_idx][0]}'.")).strip()

            q_obj = Question(
                id=f"pdf_{int(time.time())}_{idx}",
                question=q_text,
                options=options,
                correct_index=correct_idx,
                category=category,
                difficulty=diff,
                explanation=explanation,
                hint=hint
            )
            questions.append(q_obj)

        return questions
