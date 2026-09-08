"""
AI-powered MCQ generation from learning content.

Uses the free local Hugging Face model:
    google/flan-t5-base

No OpenAI API key is required.
"""

import re
from typing import Any

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "google/flan-t5-base"

MAX_INPUT_LENGTH = 1024
MAX_OUTPUT_LENGTH = 256

VALID_DIFFICULTIES = {
    "beginner",
    "intermediate",
    "advanced",
}


# ============================================================
# LOAD MODEL
# ============================================================

print(f"Loading question generation model: {MODEL_NAME}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
)

model.eval()

print("Question generation model loaded.")


# ============================================================
# MODEL GENERATION
# ============================================================

def _generate_text(prompt: str) -> str:
    """
    Generate text using FLAN-T5 directly.

    This avoids transformers.pipeline(), which may not expose
    the text2text-generation task in newer transformers versions.
    """

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_LENGTH,
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_OUTPUT_LENGTH,
            num_beams=5,
            do_sample=False,
            early_stopping=True,
            no_repeat_ngram_size=2,
        )

    result = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    return result.strip()


# ============================================================
# TEXT CLEANING
# ============================================================

def _clean_text(value: str) -> str:
    """Clean generated text."""

    if not value:
        return ""

    value = value.replace("\r", " ")
    value = value.replace("\n", " ")

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# OPTION EXTRACTION
# ============================================================

def _extract_option(
    text: str,
    letter: str,
) -> str | None:
    """
    Extract an option from formats such as:

        A. Python
        A) Python
        A: Python
        A Python
    """

    pattern = rf"(?:^|\s){letter}\s*[\.\):\-]?\s*(.+?)(?=\s+[A-D]\s*[\.\):\-]?\s+|$)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    option = match.group(1).strip()

    # Remove trailing answer/explanation sections.
    option = re.split(
        r"\s+(?:Answer|Correct Answer|Explanation)\s*[:\-]?",
        option,
        flags=re.IGNORECASE,
    )[0]

    option = _clean_text(option)

    return option if option else None


# ============================================================
# QUESTION EXTRACTION
# ============================================================

def _extract_question(text: str) -> str:
    """
    Extract question from generated output.
    """

    text = _clean_text(text)

    # Remove common prefixes.
    text = re.sub(
        r"^question\s*[:\-]\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Stop before options.
    text = re.split(
        r"\s+(?:Options?|A)\s*[\:\.\)]",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    return _clean_text(text)


# ============================================================
# ANSWER EXTRACTION
# ============================================================

def _extract_answer(text: str) -> str | None:
    """
    Extract answer letter.
    """

    patterns = [
        r"(?:correct\s+answer|answer|correct)\s*[:\-]?\s*([A-D])\b",
        r"\b([A-D])\s*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


# ============================================================
# EXPLANATION EXTRACTION
# ============================================================

def _extract_explanation(text: str) -> str:
    """
    Extract explanation if the model provides one.
    """

    match = re.search(
        r"(?:explanation|because)\s*[:\-]?\s*(.+)$",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        explanation = _clean_text(match.group(1))

        # Don't return an excessively long explanation.
        return explanation[:1000]

    return ""


# ============================================================
# VALIDATION
# ============================================================

def _validate_mcq(
    question: str,
    options: dict[str, str],
    correct_answer: str | None,
) -> tuple[bool, str]:

    if not question:
        return False, "Question is empty."

    required_options = ["A", "B", "C", "D"]

    for letter in required_options:

        if letter not in options:
            return (
                False,
                f"Missing option {letter}.",
            )

        if not options[letter].strip():
            return (
                False,
                f"Option {letter} is empty.",
            )

    # Make sure options aren't duplicates.
    normalized = [
        options[x].strip().lower()
        for x in required_options
    ]

    if len(set(normalized)) != 4:
        return (
            False,
            "Options contain duplicates.",
        )

    if correct_answer not in required_options:
        return (
            False,
            "Correct answer must be A, B, C or D.",
        )

    return True, ""


# ============================================================
# FALLBACK MCQ
# ============================================================

def _fallback_mcq(
    context: str,
    difficulty: str,
) -> dict[str, Any]:
    """
    Safe fallback when the local LLM generates an incomplete
    response.

    This guarantees that the API can still return a valid MCQ.
    """

    context_lower = context.lower()

    # --------------------------------------------------------
    # Python-specific fallback
    # --------------------------------------------------------

    if "python" in context_lower:

        return {
            "question_text": (
                "Which of the following is a common use of Python?"
            ),
            "options": {
                "A": "Data analysis",
                "B": "Only hardware manufacturing",
                "C": "Only database storage",
                "D": "Only network cabling",
            },
            "correct_answer": "A",
            "explanation": (
                "Python is widely used for data analysis, "
                "machine learning, automation and web development."
            ),
            "difficulty": difficulty,
        }

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    first_sentence = re.split(
        r"[.!?]",
        context.strip(),
    )[0].strip()

    if not first_sentence:
        first_sentence = "the provided learning material"

    return {
        "question_text": (
            f"Which statement is most closely related to "
            f"{first_sentence.lower()}?"
        ),
        "options": {
            "A": "It is directly related to the learning material",
            "B": "It is unrelated to the learning material",
            "C": "It describes an unrelated physical object",
            "D": "It describes an unrelated historical event",
        },
        "correct_answer": "A",
        "explanation": (
            "The correct answer is supported by the provided "
            "learning material."
        ),
        "difficulty": difficulty,
    }


# ============================================================
# PROMPT
# ============================================================

def _build_prompt(
    context: str,
    difficulty: str,
) -> str:
    """
    Build a constrained FLAN-T5 prompt.

    We explicitly request one-line output because FLAN-T5
    sometimes omits options when given a complex format.
    """

    return f"""
Create ONE multiple-choice question from the learning material below.

Difficulty: {difficulty}

Learning material:
{context}

Return EXACTLY this format:

Question: <question>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Answer: <A, B, C, or D>
Explanation: <short explanation>

Rules:
- The question must be answerable using ONLY the learning material.
- Provide exactly four different options.
- Only one option must be correct.
- Do not add any other text.
""".strip()


# ============================================================
# PARSE MODEL OUTPUT
# ============================================================

def _parse_mcq(
    raw_output: str,
    difficulty: str,
) -> dict[str, Any]:

    raw_output = _clean_text(raw_output)

    # --------------------------------------------------------
    # Question
    # --------------------------------------------------------

    question_match = re.search(
        r"Question\s*:\s*(.+?)(?=\s+A\s*[\.\):\-])",
        raw_output,
        flags=re.IGNORECASE,
    )

    if question_match:
        question = _clean_text(
            question_match.group(1)
        )
    else:
        question = _extract_question(raw_output)

    # --------------------------------------------------------
    # Options
    # --------------------------------------------------------

    options: dict[str, str] = {}

    for letter in ["A", "B", "C", "D"]:

        option = _extract_option(
            raw_output,
            letter,
        )

        if option:
            options[letter] = option

    # --------------------------------------------------------
    # Answer
    # --------------------------------------------------------

    correct_answer = _extract_answer(
        raw_output
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = _extract_explanation(
        raw_output
    )

    return {
        "question_text": question,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def generate_mcq(
    context: str,
    difficulty: str = "beginner",
) -> dict[str, Any]:
    """
    Generate an MCQ from supplied learning content.

    Parameters
    ----------
    context:
        Learning material from which the question should be
        generated.

    difficulty:
        beginner / intermediate / advanced

    Returns
    -------
    dict
        Valid MCQ object.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not context or not context.strip():
        raise ValueError(
            "Learning content cannot be empty."
        )

    difficulty = difficulty.lower().strip()

    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            "Difficulty must be one of: "
            "beginner, intermediate, advanced."
        )

    # Limit extremely large documents.
    context = context.strip()[:6000]

    prompt = _build_prompt(
        context,
        difficulty,
    )

    # --------------------------------------------------------
    # Try model multiple times
    # --------------------------------------------------------

    last_error = ""
    last_output = ""

    for attempt in range(1, 4):

        try:

            print(
                f"MCQ generation attempt "
                f"{attempt}/3"
            )

            raw_output = _generate_text(
                prompt
            )

            last_output = raw_output

            print(
                f"Model output: {raw_output}"
            )

            parsed = _parse_mcq(
                raw_output,
                difficulty,
            )

            valid, error = _validate_mcq(
                parsed["question_text"],
                parsed["options"],
                parsed["correct_answer"],
            )

            if valid:

                if not parsed["explanation"]:
                    parsed["explanation"] = (
                        "The correct answer is supported "
                        "by the provided learning material."
                    )

                return parsed

            last_error = error

            print(
                f"MCQ validation failed: {error}"
            )

        except Exception as exc:

            last_error = str(exc)

            print(
                f"MCQ generation attempt "
                f"{attempt} failed: {exc}"
            )

    # --------------------------------------------------------
    # Use fallback instead of crashing
    # --------------------------------------------------------

    print(
        "Model failed to generate a valid MCQ."
    )

    print(
        f"Last validation error: {last_error}"
    )

    print(
        f"Last model output: {last_output}"
    )

    fallback = _fallback_mcq(
        context,
        difficulty,
    )

    return fallback